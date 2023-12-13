import os
import traceback
import asyncio
import importlib
from datetime import datetime
from fluxo.fluxo_core.fluxo import Fluxo
from fluxo.fluxo_core.database.fluxo import Fluxo as ModelFluxo
from fluxo.fluxo_core.database.task import Task as ModelTask
from fluxo.fluxo_core.database.log_execution_fluxo import LogExecutionFluxo as ModelLogExecutionFluxo
from fluxo.uttils import current_time_formatted, convert_str_to_datetime, convert_datetime_to_str
from fluxo.fluxo_core.scheduler import TaskScheduler


class Task:
    '''
    Represents a 'Task' object associated with a 'Fluxo' for executing asynchronous functions.

    Attributes:
    - task_info (dict): A dictionary containing information about the task, including its name, associated 'Fluxo',
      start time, and end time.
    '''
    def __init__(
        self,
        name: str,
        fluxo: Fluxo,
        start_time: datetime = None,
        end_time: datetime = None
    ):
        '''
        Initializes a new 'Task' instance.

        Parameters:
        - name (str): The name of the task.
        - fluxo (Fluxo): The associated 'Fluxo' for the task.
        - start_time (datetime): The start time of the task. Defaults to None.
        - end_time (datetime): The end time of the task. Defaults to None.
        '''
        self.task_info = {
            'name': name,
            'fluxo': fluxo,
            'start_time': start_time,
            'end_time': end_time,
        }

    def __call__(self, func):
        '''
        Decorator method that wraps an asynchronous function, records task information in the database,
        and handles execution details.

        Parameters:
        - func: The asynchronous function to be decorated.

        Returns:
        async function: The decorated asynchronous function.
        '''
        async def wrapper(*args, **kwargs):
            # Retrieve the 'Fluxo' information from the database
            fluxo_register_db = ModelFluxo.get_by_name(
                self.task_info.get('fluxo').name)

            # Create a new 'ModelTask' instance and save it to the database
            task = ModelTask(name=self.task_info.get(
                'name'), fluxo_id=fluxo_register_db.id)
            new_task = task.save()

            # Params to update LogExecutionFluxo
            _params = {
                'id_fluxo': fluxo_register_db.id,
                'id_task': new_task.id
            }

            try:
                # Call the original function
                new_task.start_time = current_time_formatted()
                new_task.update(**new_task.__dict__)

                # Function executed
                result = await func(*args, **kwargs)

                new_task.end_time = current_time_formatted()
                new_task.execution_date = new_task.end_time

                new_task.update(**new_task.__dict__)
                self._update_log_execution_fluxo(**_params)

                return result
            except Exception as err:
                error = traceback.format_exc()
                new_task.error = f'[Error in task: {new_task.name}]' + \
                    '\n' + error
                new_task.end_time = current_time_formatted()
                new_task.execution_date = new_task.end_time

                new_task.update(**new_task.__dict__)
                self._update_log_execution_fluxo(**_params)

        setattr(wrapper, 'task_info', self.task_info)
        return wrapper
    
    def _update_log_execution_fluxo(self, **kwargs):
        '''
        Update the log of fluxo execution with information about the completed tasks.

        This method retrieves information about the fluxo, task, and log execution from the database,
        updates the log with the completed task details, and handles error scenarios.

        Args:
            **kwargs: Keyword arguments containing 'id_fluxo' (fluxo ID) and 'id_task' (task ID).

        Returns:
            None
        '''
        log_fluxo = ModelLogExecutionFluxo.get_by_idfluxo_and_endtime_is_none(kwargs['id_fluxo'])
        fluxo = ModelFluxo.get_by_id(kwargs['id_fluxo'])
        task = ModelTask.get_by_id(kwargs['id_task'])

        # If LogExecutionFluxo is not in the database, create a new instance and save it
        if log_fluxo is None:
            log_fluxo = ModelLogExecutionFluxo(
                name=fluxo.name,
                id_fluxo=fluxo.id
            )
            log_fluxo = log_fluxo.save()

        # When tasks by log_fluxo is None, update the log with the current task information
        if log_fluxo.ids_task is None:
            log_fluxo.ids_task = [task.id]
            if log_fluxo.start_time is None:
                log_fluxo.start_time = task.start_time
            log_fluxo = log_fluxo.update(**log_fluxo.__dict__)
        else:
            # When the number of tasks in the log is less than the total tasks in the fluxo,
            # update the log with the current task information
            if len(log_fluxo.ids_task) < len(fluxo.list_names_tasks):
                log_fluxo.ids_task.append(task.id)
                log_fluxo = log_fluxo.update(**log_fluxo.__dict__)

        # When all tasks in the fluxo are completed, update the log with end time and handle errors
        if len(log_fluxo.ids_task) == len(fluxo.list_names_tasks):
            list_end_time_tasks = []
            for id_task in log_fluxo.ids_task:
                task = ModelTask.get_by_id(id_task)
                list_end_time_tasks.append(convert_str_to_datetime(task.end_time))

                # If a task has an error, update the error log in the fluxo log
                if task.error:
                    if log_fluxo.ids_error_task is None:
                        log_fluxo.ids_error_task = [task.id]
                    else:
                        log_fluxo.ids_error_task.append(task.id)

            log_fluxo.end_time = convert_datetime_to_str(max(list_end_time_tasks))
            log_fluxo.update(**log_fluxo.__dict__)


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

        coroutines = []

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
                        coroutines.append((attribute, fluxo_info))

                else:
                    raise Exception("The function is not decorated with @Task")

        if coroutines:
            task_scheduler = TaskScheduler(coroutines)
            task_scheduler.run_scheduler()

    except Exception as e:
        raise Exception(f"Error executing task in module")
