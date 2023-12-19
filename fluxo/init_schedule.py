from fluxo.fluxo_core.flows_executor import FlowsExecutor
from fluxo.fluxo_core.flows_executor import logging


if __name__ == '__main__':
    flows_executor = FlowsExecutor()
    try:
        flows_executor.execute_parallel_flows()
    except KeyboardInterrupt:
        logging.warning('Program interrupted by the user')