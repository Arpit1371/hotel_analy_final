from django.shortcuts import render


# Create your views here.
from django.http import HttpResponse

import openpyxl
from .models import TimeZone
from datetime import datetime


def index(request):

    return HttpResponse("Hi welcome to TimeZone page")

def update(request):

    ###change accordingly the file name
    file_name = 'TimeZone.xlsx'
    wb = openpyxl.load_workbook(file_name)
    sheet = wb.active

    ## as the data is already updated till 13560 rows change it to 0 if new file
    start = 13561
    for row in sheet.iter_rows(min_row=start, values_only=True):
        timezone = TimeZone()

        timezone.store_id = row[0]
        timezone.time_zone = row[1]

        # set other fields as needed
        timezone.save()

    return HttpResponse('TimeZOne database Updated successfully')

