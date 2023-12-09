from datetime import datetime, timedelta


def convert_str_to_datetime(data_str: str):
    if data_str is None:
        return None
    else:
        return datetime.strptime(data_str, "%d/%m/%Y %H:%M:%S")

  
def current_time_formatted():
    '''
    Returns the current time formatted as a string.

    Returns:
    str: The formatted current time.
    '''
    current_time = datetime.now()
    format_str = "%d/%m/%Y %H:%M:%S"
    formatted_time = current_time.strftime(format_str)
    return formatted_time


def add_minutes_to_utc_time(minutes: int, time=None):
    '''
    Adds a specified number of minutes to a given time or the current time.

    Parameters:
    - minutes (int): The number of minutes to add.
    - time (str): The time to which minutes should be added. Defaults to None.

    Returns:
    str: The formatted time after adding the specified minutes.
    '''
    if time is None:
        time = current_time_formatted()

    # Convert a string to a datetime object
    time = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")

    new_time = time + timedelta(minutes=minutes)
    format_str = "%d/%m/%Y %H:%M:%S"
    formatted_time = new_time.strftime(format_str)
    return formatted_time
