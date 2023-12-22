import traceback
from fluxo.logging import logger
from datetime import datetime
from fluxo.fluxo_core.flow import Flow
from fluxo.fluxo_core.database.flow import ModelFlow
from fluxo.fluxo_core.database.task import ModelTask
from fluxo.fluxo_core.database.log_execution_flow import ModelLogExecutionFlow
from fluxo.uttils import current_time_formatted, convert_str_to_datetime, convert_datetime_to_str


class Task:
    '''
    Represents a task in a workflow, enabling the execution of asynchronous functions
    with logging and error handling.

    Parameters:
        - name (str): The name of the task.
        - flow (Flow): The associated flow to which the task belongs.
        - start_time (datetime, optional): The start time of the task.
        - end_time (datetime, optional): The end time of the task.

    Example:
        ```
        from fluxo import Flow
        from fluxo import Task

        flow = Flow(name='My Flow 1', interval={'minutes': 1, 'at': ':00'})

        @Task('My Task 1', flow=flow)
        async def My_func():
            print('My_func executed!')
        ```

    '''
    def __init__(
        self,
        name: str,
        flow: Flow,
        start_time: datetime = None,
        end_time: datetime = None
    ):
        self.task_info = {
            'name': name,
            'flow': flow,
            'start_time': start_time,
            'end_time': end_time,
        }

    def __call__(self, func):
        '''
        Decorates an asynchronous function to enable logging and error handling.

        Parameters:
            - func: The asynchronous function to be decorated.

        Returns:
            - wrapper: The decorated asynchronous function.

        The decorated function is executed with logging, error handling, and updates to the database
        for tracking task execution.
        '''
        async def wrapper(*args, **kwargs):
            # Retrieve the 'Flow' information from the database
            flow_register_db = ModelFlow.get_by_name(
                self.task_info.get('flow').name)

            # Create a new 'ModelTask' instance and save it to the database
            task = ModelTask(name=self.task_info.get(
                'name'), flow_id=flow_register_db.id)
            new_task = task.save()

            # Params to update LogExecutionFlow
            _params = {
                'id_flow': flow_register_db.id,
                'id_task': new_task.id
            }

            try:
                # Call the original function
                new_task.start_time = current_time_formatted()
                new_task.update(**new_task.__dict__)
                self._newlog_execution_flow(**_params)

                # Function executed
                result = await func(*args, **kwargs)

                new_task.end_time = current_time_formatted()
                new_task.execution_date = new_task.end_time

                new_task.update(**new_task.__dict__)
                self._update_log_execution_flow(**_params)

                logger.info(f'Task [{new_task.name}] executed successfully')

                return result
            except Exception as err:
                error = traceback.format_exc()
                new_task.error = f'[Error in task: {new_task.name}]' + \
                    '\n' + error
                new_task.end_time = current_time_formatted()
                new_task.execution_date = new_task.end_time

                new_task.update(**new_task.__dict__)
                self._update_log_execution_flow(**_params)

                logger.info(f'Task [{new_task.name}] executed with error')

        setattr(wrapper, 'task_info', self.task_info)
        return wrapper
    
    def _newlog_execution_flow(self, **kwargs):
        '''
        Create the log of flow execution with task information.

        Parameters:
            - kwargs: Additional keyword arguments.

        This method create the log of flow execution in the database.
        '''
        log_flow = ModelLogExecutionFlow.get_by_idflow_and_endtime_is_none(kwargs['id_flow'])
        flow = ModelFlow.get_by_id(kwargs['id_flow'])

        # If LogExecutionFlow is not in the database, create a new instance and save it
        if log_flow is None:
            log_flow = ModelLogExecutionFlow(
                name=flow.name,
                id_flow=flow.id,
                start_time=current_time_formatted()
            )
            log_flow = log_flow.save()
    
    def _update_log_execution_flow(self, **kwargs):
        '''
        Updates the log of flow execution with task information.

        Parameters:
            - kwargs: Additional keyword arguments.

        This method updates the log of flow execution in the database
        with information about the associated task.
        '''
        log_flow = ModelLogExecutionFlow.get_by_idflow_and_endtime_is_none(kwargs['id_flow'])
        flow = ModelFlow.get_by_id(kwargs['id_flow'])
        task = ModelTask.get_by_id(kwargs['id_task'])

        # When tasks by log_flow is None, update the log with the current task information
        if log_flow.ids_task is None:
            log_flow.ids_task = [task.id]
            if log_flow.start_time is None:
                log_flow.start_time = task.start_time
            log_flow = log_flow.update(**log_flow.__dict__)
        else:
            # When the number of tasks in the log is less than the total tasks in the fluxo,
            # update the log with the current task information
            if len(log_flow.ids_task) < len(flow.list_names_tasks):
                log_flow.ids_task.append(task.id)
                log_flow = log_flow.update(**log_flow.__dict__)

        # When all tasks in the flow are completed, update the log with end time and handle errors
        if len(log_flow.ids_task) == len(flow.list_names_tasks):
            list_end_time_tasks = []
            for id_task in log_flow.ids_task:
                task = ModelTask.get_by_id(id_task)
                list_end_time_tasks.append(convert_str_to_datetime(task.end_time))

                # If a task has an error, update the error log in the flow log
                if task.error:
                    if log_flow.ids_error_task is None:
                        log_flow.ids_error_task = [task.id]
                    else:
                        log_flow.ids_error_task.append(task.id)

            log_flow.end_time = convert_datetime_to_str(max(list_end_time_tasks))
            log_flow.update(**log_flow.__dict__)
