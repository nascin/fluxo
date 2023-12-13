

class Fluxo:
    '''
    Represents a 'Fluxo' object with attributes such as name, interval, and active status.

    Attributes:
    - name (str): The name of the 'Fluxo'.
    - interval (dict): The interval information for the 'Fluxo'.
    - active (bool): A flag indicating whether the 'Fluxo' is active or not.
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
