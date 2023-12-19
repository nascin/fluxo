import os
import atexit
import multiprocessing
import importlib
import asyncio
import schedule
import logging
import signal
from typing import List, Optional
from fluxo.settings import PathFilesPython, Db
from fluxo.uttils import current_time_formatted
from fluxo.fluxo_core.database.db import _verify_if_db_exists
from fluxo.fluxo_core.database.app import ModelApp
from fluxo.fluxo_core.database.flow import ModelFlow
from fluxo.fluxo_core.database.task import ModelTask
from fluxo.fluxo_core.database.log_execution_flow import ModelLogExecutionFlow

logging.basicConfig(
    format='%(asctime)s - %(levelname)s ===> %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO  
)


class FlowsExecutor:
    '''
    Represents a 'FlowsExecutor' object responsible for executing Flow files in parallel processes.

    Attributes:
        - path (str): The path to the directory containing Fluxo files.

    Methods:
        - execute_parallel_flows(): Executes Flow files in parallel processes.
        - stop_flow_execution(): Stops the execution of the specified flows.
    '''
    _coroutines: list = [] # [(task, flow_info)]

    def __init__(self, path=PathFilesPython.PATH_FILES_PYTHON) -> None:
        '''
        Initializes a new 'FlowsExecutor' instance.

        The instance is configured with the path to the directory containing Flow files,
        an empty list to store multiprocessing.Process instances, and the verification
        of the existence of the database.
        '''
        self.path = path
        self.processes = []

        # Register the functions to be executed on program exit
        atexit.register(self._cleanup_processes)
        atexit.register(FlowsExecutor._change_app_status_to_false)
  
    def execute_parallel_flows(self, flows: Optional[List[ModelFlow]] = None):
        '''
        Executes Flow files in parallel processes.
        '''
        # Check if the database doesn't exist
        if not self._db_exists():
            # Verify and create the database if it doesn't exist
            _verify_if_db_exists()
            FlowsExecutor._change_app_status_to_true() # Change status to True in database

            for file in os.listdir(self.path):
                if file.endswith(".py"):
                    process = multiprocessing.Process(
                        target=FlowsExecutor._execute_async_tasks_first_time, args=(self.path, file))
                    self.processes.append(process)
                    process.start()
        else:
            FlowsExecutor._change_app_status_to_true() # Change status to True in database
            # If flows is None, then all flows will be executed
            if flows is None:
                all_flows = ModelFlow.get_all()
                for flow in all_flows:
                    process = multiprocessing.Process(
                        target=FlowsExecutor._execute_async_tasks_from_flow, args=(self.path, flow))
                    self.processes.append(process)
                    process.start()
            else:
                for flow in flows:
                    process = multiprocessing.Process(
                        target=FlowsExecutor._execute_async_tasks_from_flow, args=(self.path, flow))
                    self.processes.append(process)
                    process.start()

        #for process in self.processes:
        #    process.join()

    def stop_flow_execution(self, flows: List[ModelFlow]):
        '''
        Stops the execution of the specified flows.

        Parameters:
            - flows (List[ModelFlow]): The list of ModelFlow objects representing flows to be stopped.

        This method iterates through the provided list of flows and attempts to stop their execution.
        If a flow is currently running, it terminates the associated process using the process ID (PID).
        If the process is not found or if there are permission issues, exceptions are raised.
        
        Note: This method updates the running status and process information in the database.
        '''
        for flow in flows:
            flow = ModelFlow.get_by_id(flow.id)
            if flow:
                if flow.running:
                    pid = flow.running_process.get('process_pid')
                    try:
                        flow.running_process = None
                        flow.running = False
                        flow.update(**flow.__dict__)
                        logging.info(f'Canceled pending TASK {flow.list_names_tasks} in FLOW [{flow.name}]')
                        os.kill(pid, signal.SIGTERM)
                    except ProcessLookupError:
                        raise Exception(f'The process with PID {pid} was not found')
                    except PermissionError:
                        raise Exception(f'You are not allowed to terminate the process with PID {pid}.')

    @staticmethod
    def _execute_async_tasks_from_flow(path, flow: Optional[ModelFlow] = None):
        '''
        Executes asynchronous tasks defined in a module.

        Parameters:
            - path (str): The path to the directory containing the module.
            - flow (str): Flow and its tasks to be executed.
        '''
        for file in os.listdir(path):
            if file.endswith('.py'):
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
                                flow_info = task_info.get('flow')
                                flow_register_db = ModelFlow.get_by_name(flow_info.name)

                                if flow_register_db is None:  # Check if fluxo exists in the database
                                    new_flow = ModelFlow(
                                        name=flow_info.name,
                                        interval=flow_info.interval,
                                        list_names_tasks=[task_info.get('name')],
                                        running=False
                                    )
                                    flow = new_flow.save()

                                if flow.name == flow_info.name:
                                    flow.interval = flow_info.interval
                                    flow.active = flow_info.active
                                    flow.update(**flow.__dict__)
                                    
                                    if flow.active: # Check if fluxo.active is True
                                        FlowsExecutor._coroutines.append((attribute, flow_info))

                    if FlowsExecutor._coroutines:
                        flow.running = True
                        # Sets the running process to the flow, storing the PID of the current process.
                        flow.running_process = {'process_pid': os.getpid()}
                        flow.update(**flow.__dict__)
                        FlowsExecutor._schedule_async_tasks()

                except Exception as e:
                    raise Exception(f"Error executing task in module")

    @staticmethod
    def _execute_async_tasks_first_time(path, file):
        '''
        Executes asynchronous tasks defined in a module for the first time.

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
                        flow_info = task_info.get('flow')
                        flow = ModelFlow.get_by_name(flow_info.name)

                        if flow is None:  # Check if fluxo exists in the database
                            flow = ModelFlow(
                                name=flow_info.name,
                                interval=flow_info.interval,
                                list_names_tasks=[task_info.get('name')],
                                running=False
                            )
                            flow = flow.save()
                        else:
                            flow.name = flow_info.name # Update Flow in database
                            flow.interval = flow_info.interval
                            flow.active = flow_info.active
                            flow.list_names_tasks.append(task_info.get('name'))
                            flow.update(**flow.__dict__)
                                
                        if flow.active: # Check if flow.active is True
                            FlowsExecutor._coroutines.append((attribute, flow_info))

            if FlowsExecutor._coroutines:
                flow = ModelFlow.get_by_name(FlowsExecutor._coroutines[0][1].name)
                flow.running = True
                # Sets the running process to the flow, storing the PID of the current process.
                flow.running_process = {'process_pid': os.getpid()}
                flow.update(**flow.__dict__)
                FlowsExecutor._schedule_async_tasks()

        except Exception as e:
            raise Exception(f"Error executing task in module")

    @staticmethod
    def _schedule_async_tasks():
        '''
        Schedules the execution of asynchronous tasks based on the specified intervals.
        '''
        for task, flow_info in FlowsExecutor._coroutines:
            if flow_info.interval.get('minutes'):
                schedule.every(flow_info.interval.get('minutes')).minutes.at(
                    flow_info.interval.get('at')).do(FlowsExecutor._run_asynchronous_task, task)
            elif flow_info.interval.get('hours'):
                schedule.every(flow_info.interval.get('hours')).hours.at(
                    flow_info.interval.get('at')).do(FlowsExecutor._run_asynchronous_task, task)
            elif flow_info.interval.get('days'):
                schedule.every(flow_info.interval.get('days')).days.at(
                    flow_info.interval.get('at')).do(FlowsExecutor._run_asynchronous_task, task)
                
        jobs_pending = [schedule.get_jobs()]

        condition = True
        while condition:
            try:
                schedule.run_pending()
            except KeyboardInterrupt:
                for job in jobs_pending:
                    schedule.cancel_job(job)
                condition = False

                _tasks, flow = zip(*FlowsExecutor._coroutines)

                flow = flow[0]
                FlowsExecutor._update_tasks_in_db_if_keyboardinterrupt(flow.name)
                FlowsExecutor._stop_flow_execution(flow.name)

    def _cleanup_processes(self):
        '''
        Terminates all running processes.
        '''
        logging.info('Terminating all processes')
        try:
            for process in self.processes:
                process.join()
        except Exception as err:
            print(f'===> {err}')

    def _db_exists(self):
        '''
        Verifies if the database file exists at the specified path.

        Returns:
            True or None
        '''
        return os.path.exists(Db.PATH)
    
    @staticmethod
    def _update_tasks_in_db_if_keyboardinterrupt(flow_name):
        flow = ModelFlow.get_by_name(flow_name)
        tasks = ModelTask.get_all_by_fluxo_id(flow.id)

        for task in tasks:
            if task.end_time is None:
                task.error = 'KeyboardInterrupt'
                task.end_time = current_time_formatted()
                task.execution_date = task.end_time
                task.update(**task.__dict__)

    @staticmethod
    def _stop_flow_execution(flow_name: str):
        '''
        Stops the execution of the specified flow.

        Parameters:
            - flow_name: Name of ModelFlow objects representing flow to be stopped.

        This method iterates through the provided flow_name and attempts to stop their execution.
        If a flow is currently running, it terminates the associated process using the process ID (PID).
        If the process is not found or if there are permission issues, exceptions are raised.
        
        Note: This method updates the running status and running_process information in the database.
        '''
        flow = ModelFlow.get_by_name(flow_name)
        log_flow = ModelLogExecutionFlow.get_by_idflow_and_endtime_is_none(flow.id)
        if flow:
            if flow.running:
                pid = flow.running_process.get('process_pid')
                try:
                    flow.running_process = None
                    flow.running = False
                    flow.update(**flow.__dict__)
                    if log_flow:
                        log_flow.delete(log_flow.id)
                        
                    logging.info(f'Canceled pending TASK {flow.list_names_tasks} in FLOW [{flow.name}]')
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    raise Exception(f'The process with PID {pid} was not found')
                except PermissionError:
                    raise Exception(f'You are not allowed to terminate the process with PID {pid}.')

    @staticmethod
    def _change_app_status_to_true():
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

    @staticmethod
    def _change_app_status_to_false():
        '''
        Changes the application status to False in the database.

        If the application exists, its status is updated to False.
        '''
        app = ModelApp.get()
        if app:
            app.update(app.id, False)

    @staticmethod
    def _run_asynchronous_task(task):
        '''
        Runs an asynchronous task.

        Parameters:
        - task: The asynchronous task to be executed.
        '''
        asyncio.run(task())
