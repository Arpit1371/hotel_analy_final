from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

import openpyxl
from .models import StoreStatus
from datetime import datetime

def index(request):


    return HttpResponse("Hi welcome to storestatus page")

def update(request):
    wb = openpyxl.load_workbook('storestatus.xlsx')
    sheet = wb.active
    start = 1048577
    for row in sheet.iter_rows(min_row=start, values_only=True):
        storestat = StoreStatus()

        storestat.store_id = row[0]
        storestat.status = row[1]
        storestat.timestamp_utc = datetime.strptime(str(row[2]), '%Y-%m-%d %H:%M:%S.%f %Z')

        # set other fields as needed
        storestat.save()

    return HttpResponse("Hi welcome to storestatus page")

