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
    mapping(bytes32 => Certificate) codeHashCert;
    mapping(bytes32 => Certificate) certHashMap;

    // Events
    event TaskAdded(address indexed from, uint256 taskId);
    event TaskFailed(uint256 taskId, string message);
    event WorkloadGet(address requester, Workload workload);
    event TaskRemoved(uint256 taskId);
    event VoteForSequenceRequested(uint256 taskId);
    event CertificateCreated(uint256 certId, uint256 taskId);

    // Modifiers
    modifier onlyTaskOwner(uint256 taskId) {
        require(msg.sender == tasks[taskId].owner, "Only task owner can call this function");
        _;
    }
    // --- TASK Management ---
    function getTasks() public view returns (Task[] memory) {
        return tasks;
    }

    // Task specific functions
    function addTask(Task calldata task) external returns (uint256) {
        uint256 taskId = tasks.length;
        tasks.push(task);
        tasks[taskId].taskId = taskId;
        openTasks.push(taskId);

        uint256 lenTraces = task.traces.length;
        for (uint256 i = 0; i < lenTraces; i++) {
            Trace memory currentTrace = task.traces[i];
            taskTraceMap[taskId][currentTrace.traceId] = currentTrace;
            traceHashMap[taskId][currentTrace.startTraceHash] = currentTrace;
            openTracesMap[taskId].push(currentTrace.traceId);
        }
        emit TaskAdded(msg.sender, taskId);
        return taskId;
    }

    function addTraces(uint256 taskId, Trace[] calldata traces) external onlyTaskOwner(taskId) {
        for (uint256 i = 0; i < traces.length; i++) {
            Trace memory currentTrace = traces[i];
            assert(currentTrace.traceId > 0);
            tasks[taskId].traces.push(currentTrace);
            taskTraceMap[taskId][currentTrace.traceId] = currentTrace;
            traceHashMap[taskId][currentTrace.startTraceHash] = currentTrace;
            openTracesMap[taskId].push(currentTrace.traceId);
        }
    }

    function removeOpenTask(uint256 taskId) internal {
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
//    function uploadConflictsNew(uint256 taskId, bytes32[] calldata conflicts) public {
//        uint256 len = conflicts.length;
//        uint256[] storage openTraces = openTracesMap[taskId];
//        bool taskAlreadyOpen = (openTraces.length > 0);
//
//        for (uint256 i = 0; i < len; i++) {
//            uint256 traceId = traceHashMap[taskId][conflicts[i]].traceId;
//            openTraces.push(traceId);
//        }
//
//        if (!taskAlreadyOpen && len > 0) {
//            openTasks.push(taskId);
//        }
//    }
    function uploadConflicts(uint256 taskId, bytes32[] calldata conflicts)
        public
    {
        uint256 len = conflicts.length;
        for (uint256 i = 0; i < len; i++) {
            uint256 traceId = traceHashMap[taskId][conflicts[i]].traceId;
            openTracesMap[taskId].push(traceId);
        }
        if (len > 0) {
            openTasks.push(taskId);
        }
    }
    function uploadPossibleSequence(
        uint256 taskId,
        bytes32[] calldata sequence,
        string memory sequenceString
    ) public {
        sequenceCounter[taskId]++;
        sequenceVote[taskId][sequenceString]++;
        sequenceMap[taskId][sequenceString] = sequence;

        // Use a mapping to track the existence of sequenceString
        bool isNewSequence = (sequenceVote[taskId][sequenceString] == 1);

        if (isNewSequence) {
            posSequences[taskId].push(sequenceString);
        }

        if (sequenceCounter[taskId] >= sequenceThreshold) {
            uint256 lenSV = posSequences[taskId].length;
            bool quorumReached = false;

            for (uint256 i = 0; i < lenSV; i++) {
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

    function checkPossibleSequences(uint256 taskId, string memory sequenceRef) internal {
        bytes32[] storage constructedSequence = sequenceMap[taskId][sequenceRef];
        if (constructedSequence.length == 0){
            return;
        }
        bytes32 targetSequence = tasks[taskId].targetSequence;
        bytes32 constructedHash = sha256(abi.encodePacked(constructedSequence));
        if (constructedHash == targetSequence) {
            // Valid sequence, create certificate
            uint256 lenSeq = constructedSequence.length;
            createCertificate(taskId, constructedSequence[0], constructedSequence[lenSeq - 1]);
        } else{
            // Sequence mismatch
            removeOpenTask(taskId);
            emit TaskFailed(taskId, "Sequence mismatch!");
        }
    }

    // --- Vote functions ---
    function vote(
        uint256 taskId,
        uint256 traceId,
        bytes32 targetHash
    ) external {
        require(!checkTraceVoter(msg.sender, taskId, traceId), "Same trace cannot be voted by the same account twice!");
        traceVotedBy[taskId][traceId] = msg.sender;

        Trace memory sourceTrace = taskTraceMap[taskId][traceId];
        Trace memory targetTrace = traceHashMap[taskId][targetHash];

        bool isPotentialOutput = targetTrace.traceId == 0;
        // adding [startHash, targetHash]
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
            removeOpenTask(taskId);
        }
    }

    function checkRdyToReconstruct(uint256 taskId)
        internal
        view
        returns (bool)
    {
        uint256 len = tasks[taskId].traces.length - 1;
        return taskSequence[taskId].length > len;
    }

    // --- Workload functions ---
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

    function getOpenTasks() public view returns (uint256[] memory) {
        return openTasks;
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

    function getOpenTask() public view returns (uint256) {
        uint256 randomTaskId = 0;
        uint256 taskCount = openTasks.length;
        if (taskCount == 0) {
            revert("Please try again later we currently have no open tasks");
        } else if (taskCount == 1) {
            return openTasks[0];
        } else {
            uint256 randomIndex = uint256(keccak256(abi.encodePacked(block.timestamp, requester))) % taskCount;
            randomTaskId = openTasks[randomIndex];
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

    // --- CERTIFICATE FUNCTIONS ---
    function createCertificate(
        uint256 taskId,
        bytes32 startHash,
        bytes32 targetHash
    ) internal {
        if (taskCertMap[taskId] != 0) {
            // certificate already exists
            return;
        }
        Task memory task = tasks[taskId];
        uint256 certId = tasks.length + 1;
        bytes32 codeHash = sha256(abi.encodePacked(task.code));
        bytes32 sequenceHash = task.targetSequence;

        // certHash = h( code, input, result )
        bytes32 certHash = sha256(
            abi.encodePacked(codeHash, startHash, targetHash)
        );

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
        // add entry to search maps
        codeHashCert[cert.codeHash] = cert;
        certHashMap[cert.certificateHash] = cert;
        taskCertMap[taskId] = certId;
        // remove task from task list
        removeOpenTask(taskId);
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

