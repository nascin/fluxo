import asyncio
import schedule


class TaskScheduler:
    def __init__(self, coroutines: list):
        '''
        Initializes the TaskScheduler with a list of tuples containing asynchronous tasks and their associated 'Fluxo' information.

        Parameters:
        - coroutines (list): A list of tuples containing asynchronous tasks and their associated 'Fluxo' information.
        '''
        self.coroutines = coroutines

    def schedule_task(self, task):
        '''
        Runs an asynchronous task.

        Parameters:
        - task: The asynchronous task to be executed.
        '''
        asyncio.run(task())

    def run_scheduler(self):
        '''
        Schedules the execution of asynchronous tasks based on the specified intervals.
        '''
        for task, fluxo_info in self.coroutines:
            if fluxo_info.interval.get('minutes'):
                schedule.every(fluxo_info.interval.get('minutes')).minutes.at(
                    fluxo_info.interval.get('at')).do(self.schedule_task, task)
            elif fluxo_info.interval.get('hours'):
                schedule.every(fluxo_info.interval.get('hours')).hours.at(
                    fluxo_info.interval.get('at')).do(self.schedule_task, task)
            elif fluxo_info.interval.get('days'):
                schedule.every(fluxo_info.interval.get('days')).days.at(
                    fluxo_info.interval.get('at')).do(self.schedule_task, task)

        while True:
            schedule.run_pending()
