from fluxo.fluxo_core.fluxos_executor import FluxosExecutor
from fluxo.fluxo_core.fluxos_executor import logging

if __name__ == '__main__':
    fluxos_executor = FluxosExecutor()
    try:
        fluxos_executor.execute_fluxos()
    except KeyboardInterrupt:
        logging.warning('Program interrupted by the user')