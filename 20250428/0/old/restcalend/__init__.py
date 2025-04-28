#!/usr/bin/env python3
import calendar
import sys


def month_to_rest(year, month):
    # Получаем календарь в виде строки
    cal = calendar.month(year, month)
    lines = cal.split('\n')

    # Извлекаем название месяца и год из первой строки
    title = lines[0].strip()

    # Получаем заголовок дней недели (вторая строка)
    days_header = lines[1].strip()

    # Получаем сами дни (оставшиеся строки)
    weeks = [line.strip() for line in lines[2:] if line.strip()]

    # Формируем reST таблицу
    rst = []
    rst.append(f".. table:: {title}")
    rst.append("")
    rst.append("    " + " ".join(["=="]*7))
    rst.append("    " + days_header)
    rst.append("    " + " ".join(["=="]*7))

    for week in weeks:
        # Форматируем числа, чтобы все занимали 2 символа
        formatted_week = []
        for day in week.split():
            formatted_week.append(f"{day:>2}")
        rst.append("    " + " ".join(formatted_week))

    rst.append("    " + " ".join(["=="]*7))

    return '\n'.join(rst)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: restcalend.py year month")
        sys.exit(1)

    try:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        print(month_to_rest(year, month))
    except ValueError:
        print("Error: year and month must be integers")
