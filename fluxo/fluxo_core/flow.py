

class Flow:
    '''
    Represents a 'Flow' object with attributes such as name, interval, and active status.

    Attributes:
        - name (str): The name of the 'Flow'.
        - interval (dict): The interval information for the 'Flow'.
        - active (bool): A flag indicating whether the 'Flow' is active or not.

    Example:
        ```
        from fluxo import Flow, Task, Minutes

        interval = Minutes(1, 30).format()
        flow = Flow(name='My Flow 1', interval=interval)

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
