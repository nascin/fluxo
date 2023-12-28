

class Minutes:
    '''
    A class representing time in minutes and seconds.

    Args:
        - minutes (int): The number of minutes.
        - seconds (int): The number of seconds (0 to 59).

    Attributes:
        - minutes (int): The number of minutes.
        - seconds (str): The formatted representation of seconds as a two-digit string.

    Methods:
        - format(): Returns a dictionary with 'minutes' and 'at' keys representing the time.

    Example:
    >>> time = Minutes(5, 30)
    >>> time.format()
    {'minutes': 5, 'at': ':30'}
    '''
    def __init__(self, minutes: int, seconds: int) -> None:
        if not isinstance(minutes, int):
            raise ValueError("Minutes must be an integer.")
        
        if not (isinstance(seconds, int) and 0 <= seconds <= 59):
            raise ValueError("Seconds must be a int representing a two-digit integer between 0 and 59.")
        
        if not seconds >= 10:
            seconds = ''.join(['0',str(seconds)])

        self.minutes = minutes
        self.seconds = seconds

    def format(self):
        return {'minutes': self.minutes, 'at': f':{self.seconds}'}
    

class Hours:
    '''
    A class representing time in hours and minutes.

    Args:
        - hours (int): The number of hours.
        - minutes (int): The number of minutes (0 to 59).

    Attributes:
        - hours (int): The number of hours.
        - minutes (str): The formatted representation of minutes as a two-digit string.

    Methods:
        - format(): Returns a dictionary with 'hours' and 'at' keys representing the time.

    Example:
    >>> time = Hours(3, 45)
    >>> time.format()
    {'hours': 3, 'at': ':45'}
    '''
    
    def __init__(self, hours: int, minutes: int) -> None:
        if not isinstance(hours, int):
            raise ValueError("Hours must be an integer.")
        
        if not (isinstance(minutes, int) and 0 <= minutes <= 59):
            raise ValueError("Minutes must be a int representing a two-digit integer between 0 and 59.")
        
        if not minutes >= 10:
            minutes = ''.join(['0',str(minutes)])

        self.hours = hours
        self.minutes = minutes

    def format(self):
        return {'hours': self.hours, 'at': f':{self.minutes}'}
    

class Days:
    '''
    A class representing time in days, hours, and minutes.

    Args:
        - days (int): The number of days.
        - hours_minutes (tuple): A tuple representing hours and minutes (0 to 23 and 0 to 59, respectively).
    
    Attributes:
        - days (int): The number of days.
        - hours (str): The formatted representation of hours as a two-digit string.
        - minutes (str): The formatted representation of minutes as a two-digit string.

    Methods:
    - format(): Returns a dictionary with 'days' and 'at' keys representing the time.

    Example:
    >>> time = Days(5, (18, 30))
    >>> time.format()
    {'days': 5, 'at': '18:30'}
    '''
    def __init__(self, days: int, hours_minutes: tuple) -> None:
        hours = hours_minutes[0]
        minutes = hours_minutes[1]

        if not isinstance(days, int):
            raise ValueError("Days must be an integer.")
        
        if not (isinstance(hours_minutes, tuple) and 0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError("Hours and Minutes must be a tuple representing hours and minutes between (0,0) and (23,59).")
        
        if not (isinstance(hours, int) and isinstance(minutes, int)):
            raise ValueError('Values in tuple must be integer.')
        
        if not hours >= 10:
            hours = ''.join(['0',str(hours)])

        if not minutes >= 10:
            minutes = ''.join(['0',str(minutes)])

        self.days = days
        self.hours = hours
        self.minutes = minutes

    def format(self):
        return {'days': self.days, 'at': f'{self.hours}:{self.minutes}'}