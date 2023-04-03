from django.shortcuts import render


# Create your views here.
from django.http import HttpResponse

import openpyxl
from .models import InputData
from datetime import datetime


def index(request):
    return render(request, 'HI this is menu hours page')


def update(request):
    ###change accordingly the file name
    file_name = 'businesstime.xlsx'
    wb = openpyxl.load_workbook(file_name)
    sheet = wb.active

    ## as the data is already updated till 86199 rows change it to 0 if new file
    start = 86200
    for row in sheet.iter_rows(min_row=start, values_only=True):
        object = InputData()

        object.store_id = row[0]
        object.store_day = row[1]
        object.start_time_local = row[2]
        object.end_time_local = row[3]


        # set other fields as needed
        object.save()

    return HttpResponse('Hotel hours database Updated successfully')
