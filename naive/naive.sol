pragma solidity >=0.8.2;

contract NaiveApproach {
    // // Data Structures
    struct Trace {
        uint256 traceId;
        string traceLocation;
        bytes32 startTraceHash;
    }

    struct Task {
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
    uint256 voteThreshold = 3; // defines how many votes are needed to check for quorum

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
    mapping(uint256 => bool[]) taskVotes; // required by reconstruction, added on voting
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
        taskOwnerMap[taskId] = msg.sender;

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

    function addTraces(uint256 taskId, Trace[] calldata traces) external {
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

    // --- Vote functions ---
    function vote(
        uint256 taskId,
        bool correct
    ) external {
        if (checkTraceVoter(msg.sender, taskId, traceId)) {
            revert("Same trace can not be voted by the same account twice!");
        }
        traceVotedBy[taskId][traceId] = msg.sender;
    
        mapping(uint256 => bool) taskVotes; // required by reconstruction, added on voting
        if taskId >= 0{
          taskVotes[taskId].push(correct);

        }
        if (checkForMajority(taskId)) {
            emit VoteForSequenceRequested(taskId);
            // temporary remove
            removeOpenTask(taskId);
        }
    }

    function checkForMajority(uint256 taskId)
        internal
        view
        returns (bool)
    {
        uint256 voteLength = taskVotes[taskId].length;
        if (traceLen < voteThreshold){
          return false;

        }
        uint256 counterTrue = 0;
        uint256 counterFalse = 0;
        for (uint256 i = startIndex; i < traceLen; i++) {
          if(taskVotes[taskId][i] == true){
            counterTrue += 1; 
          }else{
            counterFalse += 1; 
          }
        }

        if(counterTrue > counterFalse){
          return true;
        }else{
          return false;
        }
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
        if (worker == traceVotedBy[taskId][traceId]) {
            return true;
        }
        return false;
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

