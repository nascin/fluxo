import os
import traceback
import asyncio
import importlib
from datetime import datetime
from fluxo.fluxo_core.fluxo import Fluxo
from fluxo.fluxo_core.database.fluxo import Fluxo as ModelFluxo
from fluxo.fluxo_core.database.task import Task as ModelTask
from fluxo.uttils import current_time_formatted
from fluxo.fluxo_core.scheduler import TaskScheduler


class Task:
    '''
    Represents a 'Task' object associated with a 'Fluxo' for executing asynchronous functions.

    Attributes:
    - task_info (dict): A dictionary containing information about the task, including its name, associated 'Fluxo',
      start time, and end time.

    Methods:
    - __init__(name: str, fluxo: Fluxo, start_time: datetime = None, end_time: datetime = None): Initializes a new 'Task' instance.
    - __call__(func): Decorator method that wraps an asynchronous function, records task information in the database,
      and handles execution details.
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

            try:
                # Call the original function
                new_task.start_time = current_time_formatted()
                new_task.update(**new_task.__dict__)

                result = await func(*args, **kwargs)

                new_task.end_time = current_time_formatted()
                new_task.execution_date = current_time_formatted()
                new_task.update(**new_task.__dict__)

                return result
            except Exception as err:
                error = traceback.format_exc()
                new_task.error = f'[Error in task: {new_task.name}]' + \
                    '\n' + error
                new_task.end_time = current_time_formatted()
                new_task.execution_date = current_time_formatted()
                new_task.update(**new_task.__dict__)

        setattr(wrapper, 'task_info', self.task_info)
        return wrapper


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
                            interval=fluxo_info.interval)
                        fluxo.save()

                    else:
                        if fluxo_register_db.interval != fluxo_info.interval:
                            fluxo_register_db.interval = fluxo_info.interval
                            fluxo_register_db.update(
                                **fluxo_register_db.__dict__)
                            
                    if ModelFluxo.get_by_name(fluxo_info.name).active: # Check if fluxo.active is True
                        coroutines.append((attribute, fluxo_info))

                else:
                    print("The function is not decorated with @Task")

        if coroutines:
            task_scheduler = TaskScheduler(coroutines)
            task_scheduler.run_scheduler()

    except Exception as e:
        print(f"Error executing task in module {module}: {e}")
