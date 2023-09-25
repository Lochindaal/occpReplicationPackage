// WorkloadManager.sol

import "./TraceManager.sol";


contract WorkloadManager {

    TraceManager public traceManager;

    constructor(){
        traceManager = TraceManager();
    }

    // Functions for assigning and retrieving workloads
    function getWorkloadSeq() external {
        uint256 randomTaskId = getOpenTask();
        uint256 traceLen = openTracesMap[randomTaskId].length;
        if (traceLen == 0) {
            revert("No open traces");
        }

        uint256 randomTraceId = traceManager.getNextTrace(msg.sender, randomTaskId);

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


    // Events related to workload management
    event WorkloadGet(address requester, Workload workload);
}
