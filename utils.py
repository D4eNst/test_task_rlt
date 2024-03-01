import calendar
from datetime import timedelta, datetime


def generate_time_range(dt_from: datetime, dt_upto: datetime, time_interval: str) -> dict[str, int]:
    format_str = "%Y-%m-%dT%H:%M:%S"
    current_date = dt_from
    # Я не учел что данные за некоторые дни могут отсутствовтаь
    # Поэтому изменил список на словарь
    # это упростит вставку данных из запроса и решит эту проблему
    time_range = {}

    while current_date <= dt_upto:
        time_range[current_date.strftime(format_str)] = 0
        if time_interval == 'hour':
            current_date += timedelta(hours=1)
        elif time_interval == 'day':
            current_date += timedelta(days=1)
        elif time_interval == 'month':
            _, last_day = calendar.monthrange(current_date.year, current_date.month)
            current_date = current_date.replace(day=last_day) + timedelta(days=1)

    return time_range


def get_pipline(dt_from: datetime, dt_upto: datetime, format_str: str) -> list:
    return [
        {
            "$match": {
                "dt": {
                    "$gte": dt_from,
                    "$lte": dt_upto
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": format_str,
                        "date": '$dt'
                    }
                },
                "sum": {
                    "$sum": '$value'
                }
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
