from datetime import datetime, date


def date_to_datetime(field_value: date, to_max_time: bool = False) -> datetime:
        time = datetime.max.time() if to_max_time else datetime.min.time()
        field_value = datetime.combine(field_value, time)
        return field_value
