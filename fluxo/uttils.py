from datetime import datetime


def convert_str_to_datetime(data_str: str):
    return datetime.strptime(data_str, "%d/%m/%Y %H:%M:%S")