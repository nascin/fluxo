from fluxo.fluxo_core.flows_executor import FlowsExecutor
from fluxo.logging import logger


if __name__ == '__main__':
    flows_executor = FlowsExecutor()
    try:
        flows_executor.execute_parallel_flows()
    except KeyboardInterrupt:
        logger.warning('Program interrupted by the user')