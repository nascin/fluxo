import os
import atexit
import multiprocessing
from fluxo.settings import PathFilesPython
from fluxo.fluxo_core.task import execute_tasks
from fluxo.fluxo_core.database.db import _verify_if_db_exists



class FluxosExecutor:
    '''
    Represents a 'FluxosExecutor' object responsible for executing Fluxo files in parallel processes.

    Attributes:
    - path (str): The path to the directory containing Fluxo files.
    - processes (list): A list to store the multiprocessing.Process instances.

    Methods:
    - cleanup_processes(): Terminates all running processes when the program exits.
    - execute_fluxos(): Executes Fluxo files in parallel processes.
    '''
    def __init__(self) -> None:
        '''
        Initializes a new 'FluxosExecutor' instance.

        The instance is configured with the path to the directory containing Fluxo files,
        an empty list to store multiprocessing.Process instances, and the verification
        of the existence of the database.

        The cleanup_processes method is registered to be executed on program exit.
        '''
        self.path = PathFilesPython.PATH_FILES_PYTHON
        self.processes = []
        _verify_if_db_exists()

        # Register the cleanup function to be executed on program exit
        atexit.register(self._cleanup_processes)

    def _cleanup_processes(self):
        '''
        Terminates all running processes.
        '''
        print("Terminating all processes.")
        for process in self.processes:
            process.terminate()

    def execute_fluxos(self):
        '''
        Executes Fluxo files in parallel processes.
        '''
        for file in os.listdir(self.path):
            if file.endswith(".py"):
                process = multiprocessing.Process(
                    target=execute_tasks, args=(self.path, file,))
                self.processes.append(process)
                process.start()

        for process in self.processes:
            process.join()


if __name__ == '__main__':
    fluxos_executor = FluxosExecutor()
    fluxos_executor.execute_fluxos()