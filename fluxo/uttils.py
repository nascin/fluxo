from datetime import datetime


def convert_str_to_datetime(data_str: str):
    if data_str is None:
        return None
    else:
        return datetime.strptime(data_str, "%d/%m/%Y %H:%M:%S")