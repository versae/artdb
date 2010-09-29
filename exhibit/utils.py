# -*-*- coding: utf-8 -*-


def clean_years(request):
    year_range = range(1600, 1801)
    year_from = 1675
    year_to = 1700
    if request.GET and "from" in request.GET and "to" in request.GET:
        try:
            year_from = int(request.GET.get("from", 0))
            year_to = int(request.GET.get("to", 0))
        except ValueError:
            pass
    if (abs(year_from - year_to) > 25 or year_from not in year_range
        or year_to not in year_range):
        year_from = 1675
        year_to = 1700
    return year_range, year_from, year_to
