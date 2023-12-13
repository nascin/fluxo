import os
import atexit
import multiprocessing
import importlib
import asyncio
import schedule
import logging
from fluxo.settings import PathFilesPython
from fluxo.fluxo_core.database.db import _verify_if_db_exists
from fluxo.fluxo_core.database.app import App as ModelApp
from fluxo.fluxo_core.database.fluxo import Fluxo as ModelFluxo

logging.basicConfig(
    format='%(asctime)s - %(levelname)s ===> %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO  
)


class FluxosExecutor:
    '''
    Represents a 'FluxosExecutor' object responsible for executing Fluxo files in parallel processes.

    Attributes:
    - path (str): The path to the directory containing Fluxo files.
    - processes (list): A list to store the multiprocessing.Process instances.
    - _coroutines (list): A list to store coroutine information in the form of (task, fluxo_info).
    - _tasks_scheduler_pending (list): A list to store pending tasks for the task scheduler.

    Methods:
    - cleanup_processes(): Terminates all running processes when the program exits.
    - _schedule_task(): Runs an asynchronous task.
    - execute_fluxos(): Executes Fluxo files in parallel processes.
    - run_scheduler(): Schedules the execution of asynchronous tasks based on the specified intervals.
    - execute_tasks(): Executes asynchronous tasks defined in a module.

    '''
    _coroutines: list = [] # [(task, fluxo_info)]

    def __init__(self) -> None:
        '''
        Initializes a new 'FluxosExecutor' instance.

        The instance is configured with the path to the directory containing Fluxo files,
        an empty list to store multiprocessing.Process instances, and the verification
        of the existence of the database.

        The _cleanup_processes method is registered to be executed on program exit.
        The _change_app_status_to_false is registered to be executed on program exit.
        '''
        self.path = PathFilesPython.PATH_FILES_PYTHON
        self.processes = []
        _verify_if_db_exists()

        # Register the functions to be executed on program exit
        atexit.register(self._cleanup_processes)
        atexit.register(self._change_app_status_to_false)

    def execute_fluxos(self):
        '''
        Executes Fluxo files in parallel processes.
        '''
        self._change_app_status_to_true() # Change status to True in database

        for file in os.listdir(self.path):
            if file.endswith(".py"):
                process = multiprocessing.Process(
                    target=FluxosExecutor.execute_tasks, args=(self.path, file))
                self.processes.append(process)
                process.start()

        for process in self.processes:
            process.join()

    @staticmethod
    def run_scheduler():
        '''
        Schedules the execution of asynchronous tasks based on the specified intervals.
        '''
        for task, fluxo_info in FluxosExecutor._coroutines:
            if fluxo_info.interval.get('minutes'):
                schedule.every(fluxo_info.interval.get('minutes')).minutes.at(
                    fluxo_info.interval.get('at')).do(FluxosExecutor._schedule_task, task)
            elif fluxo_info.interval.get('hours'):
                schedule.every(fluxo_info.interval.get('hours')).hours.at(
                    fluxo_info.interval.get('at')).do(FluxosExecutor._schedule_task, task)
            elif fluxo_info.interval.get('days'):
                schedule.every(fluxo_info.interval.get('days')).days.at(
                    fluxo_info.interval.get('at')).do(FluxosExecutor._schedule_task, task)

        jobs_pending = [schedule.get_jobs()]
        while True:
            try:
                schedule.run_pending()
            except KeyboardInterrupt:
                for job in jobs_pending:
                    schedule.cancel_job(job)
                logging.info(f'Canceled pending tasks in flow [{FluxosExecutor._coroutines[0][1].name}]')
                
                break

    @staticmethod
    def execute_tasks(path, file):
        '''
        Executes asynchronous tasks defined in a module.

        Parameters:
        - path (str): The path to the directory containing the module.
        - file (str): The name of the module file (excluding the '.py' extension).
        '''
        try:
            # Remove the '.py' extension to get the module name
            name_module = file[:-3]

            # Dynamically import the module
            dir_base = os.path.basename(path)
            module = importlib.import_module(f"{dir_base}.{name_module}")

            # Search for asynchronous functions in the module
            for name_attribute in dir(module):
                attribute = getattr(module, name_attribute)
                if asyncio.iscoroutinefunction(attribute):
                    # Check if the function is decorated with @Task
                    if hasattr(attribute, 'task_info'):

                        task_info = attribute.task_info
                        fluxo_info = task_info.get('fluxo')
                        fluxo_register_db = ModelFluxo.get_by_name(
                            fluxo_info.name)

                        if fluxo_register_db is None:  # Check if fluxo exists in the database
                            fluxo = ModelFluxo(
                                name=fluxo_info.name,
                                interval=fluxo_info.interval,
                                list_names_tasks=[task_info.get('name')])
                            fluxo.save()
                        else: # Update Fluxo in database
                            fluxo_register_db.name = fluxo_info.name
                            fluxo_register_db.interval = fluxo_info.interval
                            fluxo_register_db.active = fluxo_info.active
                            fluxo_register_db.list_names_tasks.append(task_info.get('name'))
                            fluxo_register_db.update(
                                **fluxo_register_db.__dict__)
                                
                        if ModelFluxo.get_by_name(fluxo_info.name).active: # Check if fluxo.active is True
                            FluxosExecutor._coroutines.append((attribute, fluxo_info))
                    else:
                        raise Exception("The function is not decorated with @Task")

            if FluxosExecutor._coroutines:
                FluxosExecutor.run_scheduler()

        except Exception as e:
            raise Exception(f"Error executing task in module")

    def _cleanup_processes(self):
        '''
        Terminates all running processes.
        '''
        if isinstance(self, FluxosExecutor):
            logging.info('Terminating all processes')
            try:
                for process in self.processes:
                    process.terminate()
            except Exception as err:
                print(f'===> {err}')

    def _change_app_status_to_true(self):
        '''
        Changes the application status to True in the database.

        If the application already exists, its status is updated to True.
        Otherwise, a new application with active status set to True is created and saved.
        '''
        app = ModelApp.get()
        if app:
            app.update(app.id, True)
        else:
            app = ModelApp(active=True)
            app.save()

    def _change_app_status_to_false(self):
        '''
        Changes the application status to False in the database.

        If the application exists, its status is updated to False.
        '''
        app = ModelApp.get()
        app.update(app.id, False)

    @staticmethod
    def _schedule_task(task):
        '''
        Runs an asynchronous task.

        Parameters:
        - task: The asynchronous task to be executed.
        '''
        asyncio.run(task())