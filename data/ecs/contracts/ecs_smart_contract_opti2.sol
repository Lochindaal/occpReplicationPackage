pragma solidity >=0.8.2;

contract ECSSequencer {
    // // Data Structures
    struct Trace {
        uint256 traceId;
        string traceLocation;
        bytes32 startTraceHash;
    }

    struct Task {
        address owner;
        uint256 taskId;
        string code;
        Trace[] traces;
        bytes32 targetSequence;
    }

    struct Workload {
        uint256 taskId;
        uint256 traceId;
        string code;
        string traceLocation;
    }

    struct Certificate {
        uint256 certId;
        uint256 taskId;
        bytes32 codeHash;
        bytes32 sequenceHash;
        bytes32 certificateHash;
    }

    struct SequenceVote {
        bytes32 startTraceHash;
        bytes32 targetTraceHash;
        uint256 startTraceId;
        uint256 targetTraceId;
        bool possibleResult;
        bool possibleError;
    }

    Task[] public tasks;
    uint256[] openTasks;
    Certificate[] public certificates;
    uint256 sequenceThreshold = 3; // defines how many votes are needed to check for quorum

    // MAPPINGS
    // - Task/Trace mappings
    mapping(uint256 => address) taskOwnerMap;
    mapping(uint256 => mapping(uint256 => Trace)) taskTraceMap; // required by vote, filled by addTask/Trace
    mapping(uint256 => mapping(bytes32 => Trace)) traceHashMap; // trequired by vote, filled by addTask/Trace
    mapping(uint256 => mapping(uint256 => address)) traceVotedBy;
    mapping(uint256 => uint256[]) openTracesMap;
    mapping(uint256 => uint256) lastIndex;
    // - Vote / Sequence mappings
    mapping(uint256 => SequenceVote[]) taskSequence; // required by reconstruction, added on voting
    mapping(uint256 => mapping(bytes32 => bytes32[])) inputTracesHash; // required by checkRdyToRecon added on voting
    mapping(uint256 => mapping(bytes32 => mapping(bytes32 => uint256))) inputTracesHashVotes;
    mapping(uint256 => uint256) sequenceCounter;
    mapping(uint256 => mapping(string => uint256)) sequenceVote;
    mapping(uint256 => mapping(string => bytes32[])) sequenceMap;
    mapping(uint256 => string[]) posSequences;
    // - Certificate mappings
    mapping(uint256 => uint256) taskCertMap;
//    mapping(bytes32 => Certificate) codeHashCert;
    mapping(bytes32 => Certificate) certHashMap;

    // Events
    event TaskAdded(address indexed from, uint256 taskId);
    event TaskFailed(uint256 taskId, string message);
    event WorkloadGet(address requester, Workload workload);
    event TaskRemoved(uint256 taskId);
    event VoteForSequenceRequested(uint256 taskId);
    event CertificateCreated(uint256 certId, uint256 taskId);


    // Should work without additional stuff:
    // --- CERTIFICATE FUNCTIONS ---
    function createCertificate(
        uint256 taskId,
        bytes32 startHash,
        bytes32 targetHash
    ) internal {
        require(taskCertMap[taskId] == 0, "Certificate already exists");

        Task memory task = tasks[taskId];
        uint256 certId = certificates.length;
        bytes32 codeHash = sha256(bytes(task.code));
//        bytes32 codeHash = sha256(abi.encodePacked(task.code));
        bytes32 sequenceHash = task.targetSequence;

        // certHash = h( code, input, result )
        bytes32 certHash = sha256(abi.encodePacked(codeHash, startHash, targetHash));

        Certificate memory cert = Certificate(
            certId,
            taskId,
            codeHash,
            sequenceHash,
            certHash
        );

        certificates.push(cert);
        emit CertificateCreated(certId, taskId);
        taskCertMap[taskId] = certId;
        certHashMap[cert.certificateHash] = cert;
        removeOpenTask(taskId);
    }


    function checkTraceVoter(
        address worker,
        uint256 taskId,
        uint256 traceId
    ) internal view returns (bool) {
        return worker == traceVotedBy[taskId][traceId];
    }


    function vote(
        uint256 taskId,
        uint256 traceId,
        bytes32 targetHash
    ) external {
        require(!checkTraceVoter(msg.sender, taskId, traceId), "Same trace cannot be voted by the same account twice!");

        Trace storage sourceTrace = taskTraceMap[taskId][traceId];
        Trace storage targetTrace = traceHashMap[taskId][targetHash];

        bool isPotentialOutput = targetTrace.traceId == 0;

        taskSequence[taskId].push(
            SequenceVote(
                sourceTrace.startTraceHash,
                targetHash,
                sourceTrace.traceId,
                isPotentialOutput ? 0 : targetTrace.traceId,
                isPotentialOutput,
                false
            )
        );

        inputTracesHashVotes[taskId][targetHash][sourceTrace.startTraceHash] += 1;
        inputTracesHash[taskId][targetHash].push(sourceTrace.startTraceHash);

        if (checkRdyToReconstruct(taskId)) {
            emit VoteForSequenceRequested(taskId);
            // temporary remove
//            isOpenTask[taskId] = false;
            removeOpenTask(taskId);
            emit TaskRemoved(taskId);
        }
    }

    // Task specific functions
    function addTask(Task memory task) external {
        uint256 taskId = tasks.length;
        tasks.push(Task(msg.sender, taskId, task.code, task.traces, task.targetSequence));

        for (uint256 i = 0; i < task.traces.length; i++) {
            Trace memory currentTrace = task.traces[i];
            taskTraceMap[taskId][currentTrace.traceId] = currentTrace;
            traceHashMap[taskId][currentTrace.startTraceHash] = currentTrace;
            openTracesMap[taskId].push(currentTrace.traceId);
        }
        emit TaskAdded(msg.sender, taskId);
    }

    function addTraces(uint256 taskId, Trace[] memory traces) external {
        require(msg.sender == tasks[taskId].owner, "Only the task owner can add traces.");
        for (uint256 i = 0; i < traces.length; i++) {
            Trace memory currentTrace = traces[i];
            require(currentTrace.traceId > 0, "Trace ID must be greater than 0");

            tasks[taskId].traces.push(currentTrace);
            taskTraceMap[taskId][currentTrace.traceId] = currentTrace;
            traceHashMap[taskId][currentTrace.startTraceHash] = currentTrace;
            openTracesMap[taskId].push(currentTrace.traceId);
        }
    }


    function uploadPossibleSequence(
        uint256 taskId,
        bytes32[] calldata sequence,
        string memory sequenceString
    ) public {
        uint256 taskSequenceCounter = sequenceCounter[taskId];
        uint256 sequenceStringVote = sequenceVote[taskId][sequenceString];

        // Update sequenceVote and sequenceMap
        sequenceVote[taskId][sequenceString] = sequenceStringVote + 1;
        sequenceMap[taskId][sequenceString] = sequence;

        // Check if the sequenceString was already in posSequences
        if (sequenceStringVote == 0) {
            posSequences[taskId].push(sequenceString);
        }

        // Increment the task's sequenceCounter
        taskSequenceCounter++;

        // Update sequenceCounter
        sequenceCounter[taskId] = taskSequenceCounter;

        // Check for quorum only if the threshold is reached
        if (taskSequenceCounter >= sequenceThreshold) {
            uint256 lenPosSeq = posSequences[taskId].length;
            bool quorumReached = false;

            for (uint256 i = 0; i < lenPosSeq; i++) {
                string memory curSeq = posSequences[taskId][i];
                if (sequenceVote[taskId][curSeq] > 1) {
                    quorumReached = true;
                    checkPossibleSequences(taskId, curSeq);
                    break;
                }
            }

            if (!quorumReached) {
                // No quorum
                removeOpenTask(taskId);
                emit TaskFailed(taskId, "No quorum on sequence reached!");
            }
        }
    }

    function checkPossibleSequences(uint256 taskId, string memory sequenceRef)
    internal
    {
        bytes32[] memory constructedSequence = sequenceMap[taskId][sequenceRef];

        if (constructedSequence.length == 0) {
            // Empty sequence, nothing to check
            return;
        }

        bytes32 targetSequence = tasks[taskId].targetSequence;
        bytes32 constructedHash = sha256(abi.encodePacked(constructedSequence));

        if (constructedHash == targetSequence) {
            createCertificate(
                taskId,
                constructedSequence[0],
                constructedSequence[constructedSequence.length - 1]
            );
        } else {
            // Sequence mismatch
            removeOpenTask(taskId);
            emit TaskFailed(taskId, "Sequence mismatch!");
        }
    }

    function checkRdyToReconstruct(uint256 taskId) internal view returns (bool) {
        uint256 len = tasks[taskId].traces.length -1;
        return taskSequence[taskId].length > len;
    }

    //---111111111111111111111111111------------END-----111111-----11111111111111111111---

    // --- TASK Management ---
    function getTasks() public view returns (Task[] memory) {
        return tasks;
    }

    mapping(uint256 => bool) public isOpenTask;

    function removeOpenTask(uint256 taskId) internal {
        if (isOpenTask[taskId]) {
            isOpenTask[taskId] = false;
            emit TaskRemoved(taskId);
        }
    }

    function removeOpenTaskOld(uint256 taskId) internal {
        uint256 len = openTasks.length;
        if (len == 0) {
            return;
        }

        if (openTasks[len - 1] == taskId) {
            openTasks.pop();
        } else {
            for (uint256 i = 0; i < len; i++) {
                if (openTasks[i] == taskId) {
                    openTasks[i] = openTasks[len - 1];
                    openTasks.pop();
                    break;
                }
            }
        }
        emit TaskRemoved(taskId);
    }

    function uploadConflicts(uint256 taskId, bytes32[] calldata conflicts)
        public
    {
        uint256 len = conflicts.length;
        for (uint256 i = 0; i < len; i++) {
            uint256 traceId = traceHashMap[taskId][conflicts[i]].traceId;
            openTracesMap[taskId].push(traceId);
        }
        if (len > 0) {
//            isOpenTask[taskId] = true;
            openTasks.push(taskId);
        }
    }




    // --- Workload functions ---

    // NEW
    function getWorkloadSeq() external {
        // Find an open task with open traces
        (uint256 randomTaskId, uint256 randomTraceId) = getRandomOpenTrace(msg.sender);

        // Check if a valid task and trace were found
        require(randomTaskId != 0 && randomTraceId != 0, "No open traces");

        // Emit the WorkloadGet event
        emit WorkloadGet(
            msg.sender,
            Workload(
                randomTaskId,
                randomTraceId,
                tasks[randomTaskId].code,
                taskTraceMap[randomTaskId][randomTraceId].traceLocation
            )
        );
    }

    function getRandomOpenTrace(address requester) internal view returns (uint256, uint256) {
        uint256 taskCount = openTasks.length;

        // Random number generation is a complex topic in Solidity.
        // You may need to use an external random number generator.
        // For simplicity, we'll use a basic modulo operation here.
        uint256 randomIndex = uint256(keccak256(abi.encodePacked(block.timestamp, requester))) % taskCount;
        uint256 randomTaskId = openTasks[randomIndex];

        uint256[] storage openTraces = openTracesMap[randomTaskId];
        uint256 traceCount = openTraces.length;

        if (traceCount == 0) {
            return (0, 0);
        }

        // Again, we use a basic modulo operation for randomness.
        uint256 randomTraceIndex = uint256(keccak256(abi.encodePacked(block.timestamp, requester, randomTaskId))) % traceCount;
        uint256 randomTraceId = openTraces[randomTraceIndex];

        return (randomTaskId, randomTraceId);
    }
    // END NEW
    // // Request random workload
    function getWorkloadSeq() external {
        uint256 randomTaskId = getOpenTask();
        uint256 traceLen = openTracesMap[randomTaskId].length;
        if (traceLen == 0) {
            revert("No open traces");
        }
        uint256 randomTraceId = getNextTrace(msg.sender, randomTaskId);

        emit WorkloadGet(
            msg.sender,
            Workload(
                randomTaskId,
                randomTraceId,
                tasks[randomTaskId].code,
                taskTraceMap[randomTaskId][randomTraceId].traceLocation
            )
        );
    }

    // HELPER Functions
    function getOpenTraces(uint256 taskId)
        public
        view
        returns (uint256[] memory)
    {
        return openTracesMap[taskId];
    }

    function getLastIndex(uint256 taskId) public view returns (uint256) {
        return lastIndex[taskId];
    }

    function getTaskSequence(uint256 taskId)
        public
        view
        returns (SequenceVote[] memory)
    {
        return taskSequence[taskId];
    }

    function getTaskTraceMap(uint256 taskId, uint256 traceId)
        public
        view
        returns (Trace memory)
    {
        return taskTraceMap[taskId][traceId];
    }

    function getSequenceCounter(uint256 taskId) public view returns (uint256) {
        return sequenceCounter[taskId];
    }

    // -------------------

    function getNextTrace(address worker, uint256 taskId)
        internal
        returns (uint256)
    {
        // Task memory t = tasks[taskId];
        uint256 startIndex = lastIndex[taskId];
        uint256 traceLen = openTracesMap[taskId].length;
        if (startIndex == traceLen - 1) {
            revert("No open traces");
        }
        for (uint256 i = startIndex; i < traceLen; i++) {
            uint256 traceId = openTracesMap[taskId][i];
            if (traceId != 0) {
                lastIndex[taskId] = i;
                if (traceVotedBy[taskId][traceId] != worker) {
                    delete openTracesMap[taskId][i];
                    return traceId;
                }
            }
        }
        revert("No open traces");
    }

    function random(uint256 range) public view returns (uint256) {
        return uint256(blockhash(block.number - 1)) % range;
    }

    function getOpenTask() public view returns (uint256) {
        uint256[] memory openTaskIds;

        for (uint256 i = 0; i < tasks.length; i++) {
            if (isOpenTask[i]) {
                openTaskIds.push(i);
            }
        }

        if (openTaskIds.length == 0) {
            revert("Please try again later, we currently have no open tasks");
        } else if (openTaskIds.length == 1) {
            return openTaskIds[0];
        } else {
            uint256 randomIndx = random(openTaskIds.length);
            return openTaskIds[randomIndx];
        }
    }

    function getOpenTask() public view returns (uint256) {
        uint256 randomTaskId = 0;
        uint256 openTaskLen = openTasks.length;
        if (openTaskLen == 0) {
            revert("Please try again later we currently have no open tasks");
        } else if (openTaskLen == 1) {
            return openTasks[0];
        } else {
            uint256 randomIndx = random(openTaskLen);
            randomTaskId = openTasks[randomIndx];
        }
        return randomTaskId;
    }

    function checkTraceVoter(
        address worker,
        uint256 taskId,
        uint256 traceId
    ) internal view returns (bool) {
        return worker == traceVotedBy[taskId][traceId];
    }



    function getCertificates() public view returns (Certificate[] memory) {
        return certificates;
    }

    function getCertificate(bytes32 certHash)
        public
        view
        returns (Certificate memory)
    {
        Certificate memory foundCert = certHashMap[certHash];
        if (foundCert.certificateHash == certHash) {
            return foundCert;
        }
        revert("No certificate found!");
    }
}

