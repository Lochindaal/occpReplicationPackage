// TraceManager.sol

contract TraceManager {
    struct Trace {
        string traceLocation;
        bytes32 startTraceHash;
    }

    // Functions for managing traces, if required
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
    // Events related to trace management
}
