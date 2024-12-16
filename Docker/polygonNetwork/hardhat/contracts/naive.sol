pragma solidity >=0.8.2;

contract NaiveContract {

    struct Task {
        uint256 taskId;
        string code;
        string expectedResult;
    }

    struct Vote {
        bool voteValue;
        address voter;
    }

    struct Workload {
        uint256 taskId;
        string code;
        string expectedResult;
    }

    struct Certificate {
        uint256 certId;
        uint256 taskId;
        bytes32 codeHash;
        bytes32 certificateHash;
    }

    Task[] public tasks;
    uint256[] public openTasks;
    
    Certificate[] public certificates;
    mapping(uint256 => address) taskOwnerMap;
    mapping(uint256 => uint256) taskCertMap;
    mapping(uint256 => Certificate) taskCertMapFull;
    mapping(bytes32 => Certificate) codeHashCert;
    mapping(bytes32 => Certificate) certHashMap;
    mapping(uint256 => Vote[]) public taskVotes;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(uint256 => uint256) public taskFailCounter; // Tracks task failures
    mapping(uint256 => address[]) public workersPerTask;
    uint256 public voteThreshold = 3; // Number of votes required to finalize a task
    uint256 public failThreshold = 3; // Number of times a task can fail before closing

    // Events
    event TaskAdded(address indexed from, uint256 taskId);
    event TaskFailed(uint256 taskId, string message);
    event WorkloadGet(address requester, Workload workload);
    event TaskReopened(uint256 taskId);
    event TaskClosed(uint256 taskId);
    event TaskRemoved(uint256 taskId);
    event VoteCast(uint256 taskId, bool voteValue);
    event CertificateCreated(uint256 certId, uint256 taskId);


    function setVoteThreshold(uint256 newThreshold) external {
        require(newThreshold > 0, "Threshold must be greater than zero");
        // Assign the new threshold value
        voteThreshold = newThreshold;
    }
    
    function getVoteThreshold() public view returns (uint256) {
      return voteThreshold;
    }


    // --- TASK Management ---
    function getTasks() public view returns (Task[] memory) {
        return tasks;
    }

    // Task specific functions
    // Add a new task
    function addTask(Task calldata task) external returns (uint256) {
        uint256 taskId = tasks.length;
        tasks.push(task);
        tasks[taskId].taskId = taskId;
        openTasks.push(taskId);
        taskOwnerMap[taskId] = msg.sender;

        emit TaskAdded(msg.sender, taskId);
        return taskId;
    }

    // Remove a task from the open tasks list
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


    // --- Workload functions ---
    // // Request random workload
    function getWorkloadSeq() external {
        uint256 randomTaskId = getOpenTask();

        emit WorkloadGet(
            msg.sender,
            Workload(
                randomTaskId,
                tasks[randomTaskId].code,
                tasks[randomTaskId].expectedResult
            )
        );
    }
  
    function random(uint256 range) public view returns (uint256) {
        return uint256(blockhash(block.number - 1)) % range;
    }


    // Vote for a task
    function vote(uint256 taskId, bool voteValue) external {
        if (checkTraceVoter(msg.sender, taskId)){
            revert("Worker has already voted for this task.");
        }

        hasVoted[taskId][msg.sender] = true;
        workersPerTask[taskId].push(msg.sender);
        taskVotes[taskId].push(Vote(voteValue, msg.sender));
        emit VoteCast(taskId, voteValue);

        if (taskVotes[taskId].length >= voteThreshold) {
            finalizeTask(taskId);
        }
    }

    // Finalize the task based on votes
    function finalizeTask(uint256 taskId) internal {
        uint256 trueVotes = 0;
        uint256 falseVotes = 0;

        for (uint256 i = 0; i < taskVotes[taskId].length; i++) {
            if (taskVotes[taskId][i].voteValue) {
                trueVotes++;
            } else {
                falseVotes++;
            }
        }

        // Check majority decision
        if (falseVotes > trueVotes) {
            taskFailCounter[taskId]++;
            if (taskFailCounter[taskId] < failThreshold) {
                removeTaskVotes(taskId);
                // Reopen task for another round of voting
                emit TaskReopened(taskId);
            } else {
                // Close task permanently
                removeOpenTask(taskId);
                emit TaskFailed(taskId, "Task failed after reaching the fail threshold.");
            }
        } else {
            // Task succeeded, close it and create certificate
            createCertificate(taskId);
            removeOpenTask(taskId);
            emit TaskClosed(taskId);
        }
    }

    function removeTaskVotes(uint256 taskId) internal {
        uint256 voteCount = taskVotes[taskId].length;
        
        for (uint256 i = 0; i < voteCount; i++) {
            delete taskVotes[taskId][i];
        }

        // After looping, reset the array length
        delete taskVotes[taskId];

        // Reset the hasVoted mapping for all traces (inefficient loop)
        uint256 voterLen = workersPerTask[taskId].length;
        for (uint256 j = 0; j < voterLen; j++) {
            address voter = workersPerTask[taskId][j];
            hasVoted[taskId][voter] = false;
        }
        delete workersPerTask[taskId];

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
        uint256 taskId
    ) internal view returns (bool) {
        if (hasVoted[taskId][worker]) {
            return true;
        }
        return false;
    }

    // --- CERTIFICATE FUNCTIONS ---
    function createCertificate(
        uint256 taskId
    ) internal {
        if (taskCertMap[taskId] != 0) {
            // certificate already exists
            return;
        }
        Task memory task = tasks[taskId];
        uint256 certId = tasks.length + 1;
        bytes32 codeHash = sha256(abi.encodePacked(task.code));

        bytes32 certHash = sha256(
            abi.encodePacked(codeHash)
        );

        Certificate memory cert = Certificate(
            certId,
            taskId,
            codeHash,
            certHash
        );

        certificates.push(cert);
        emit CertificateCreated(certId, taskId);
        taskCertMap[taskId] = certId;
        // add entry to search maps
        taskCertMapFull[taskId] = cert;
        codeHashCert[cert.codeHash] = cert;
        certHashMap[cert.certificateHash] = cert;
        taskCertMap[taskId] = certId;
        // remove task from task list
        removeOpenTask(taskId);
    }

    function getCertificates() public view returns (Certificate[] memory) {
        return certificates;
    }

    function getCert(uint256 taskId) public view returns (Certificate memory){

        Certificate memory foundCert = taskCertMapFull[taskId];
        if (foundCert.taskId == taskId) {
            return foundCert;
        }
        revert("No certificate found!");

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


    // Get open tasks
    function getOpenTasks() public view returns (uint256[] memory) {
        return openTasks;
    }

    // Get task votes
    function getTaskVotes(uint256 taskId) public view returns (Vote[] memory) {
        return taskVotes[taskId];
    }

}
