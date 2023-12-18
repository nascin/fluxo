

class Flow:
    '''
    Represents a 'Flow' object with attributes such as name, interval, and active status.

    Attributes:
        - name (str): The name of the 'Flow'.
        - interval (dict): The interval information for the 'Flow'.
        - active (bool): A flag indicating whether the 'Flow' is active or not.

    Example:
        ```
        from fluxo.fluxo_core.flow import Flow
        from fluxo.fluxo_core.task import Task

        flow = Flow(name='My Flow 1', interval={'minutes': 1, 'at': ':00'})

        @Task('My Task 1', flow=flow)
        async def My_func():
            print('My_func executed!')
        ```
    '''
    def __init__(
        self,
        name: str,
        interval: dict = None,
        active: bool = True
    ):
        self.name = name
        self.interval = interval
        self.active = active
