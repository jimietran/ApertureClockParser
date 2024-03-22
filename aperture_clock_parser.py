import decimal
import json
from datetime import datetime, timedelta


def get_time_period(hour):
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 23:
        return "Evening"
    else:
        return "Late Night"


def calculate_hour_difference(start_time, end_time):
    difference_in_seconds = (end_time - start_time).total_seconds()
    difference_in_hours = decimal.Decimal(difference_in_seconds / 3600)
    return float(round(difference_in_hours, 1))


def calculate_hours_per_time_period(start_time, end_time):
    hours_per_period = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Late Night": 0}
    current_time = start_time
    while current_time < end_time:
        next_time = min(current_time + timedelta(hours=1), end_time)
        current_period = get_time_period(current_time.hour)
        hours_in_current_period = calculate_hour_difference(current_time, next_time)
        hours_per_period[current_period] += hours_in_current_period
        current_time = next_time
    return hours_per_period


def convert_datetime(date):
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


def split_into_separate_days(start_date, end_date):
    if end_date.date() > start_date.date():
        separated_days = [(start_date, start_date.replace(hour=23, minute=59, second=59))]
        next_day = start_date + timedelta(days=1)
        while next_day.date() < end_date.date():
            separated_days.append((next_day.replace(hour=0, minute=0, second=0), next_day.replace(hour=23, minute=59, second=59)))
            next_day += timedelta(days=1)
        separated_days.append((end_date.replace(hour=0, minute=0, second=0), end_date))
        return separated_days
    else:
        return [(start_date, end_date)]


class ApertureClockParser:
    def __init__(self, input_file, output_file):
        with open(input_file) as file:
            self.data = json.load(file)
        self.output_file = output_file

    def parse(self):
        employees = {}
        for employee in self.data['employees']:
            employees[employee["id"]] = {"employee_id": employee["id"],
                                         "first_name": employee["first_name"] if employee.get("first_name") else None,
                                         "last_name": employee["last_name"] if employee.get("last_name") else None,
                                         "labour": []}
        for clock in self.data['clocks']:
            if clock.get("clock_in_datetime") and clock.get("clock_out_datetime"):
                start_date = convert_datetime(clock["clock_in_datetime"])
                end_date = convert_datetime(clock["clock_out_datetime"])
                if start_date < end_date:
                    days = split_into_separate_days(start_date, end_date)
                    for start, end in days:
                        labour_date = start.strftime("%Y-%m-%d")
                        total_hours = calculate_hour_difference(start, end)
                        hours_per_period = calculate_hours_per_time_period(start, end)
                        labour_by_time_period = {"period1": hours_per_period["Morning"],
                                                 "period2": hours_per_period["Afternoon"],
                                                 "period3": hours_per_period["Evening"],
                                                 "period4": hours_per_period["Late Night"]}
                        employees[clock["employee_id"]]["labour"].append({"date": labour_date,
                                                                          "total": total_hours,
                                                                          "labour_by_time_period": labour_by_time_period})

        with open(self.output_file, "w") as file:
            json.dump(list(employees.values()), file)
        return


parser = ApertureClockParser("clocks.json", "labour_hours.json")
parser.parse()
