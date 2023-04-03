from django.shortcuts import render
from collections import defaultdict
# Create your views here.
from django.http import HttpResponse
import random
import os
from django.core.files.storage import FileSystemStorage
from storestatus.models import StoreStatus
import datetime
from Timezone.models import TimeZone
from menuhours.models import InputData
from storestatus.models import StoreStatus
import pytz
from collections import defaultdict
from dateutil import parser

### Home PAGE
def index(request):
    #data = pd.read_excel('storestatus.xlsx')


    return render(request, 'home.html')

#### PAGE that Generates 3 random ids
def data(request):
    object_ids = list(TimeZone.objects.values_list('store_id', flat=True))
    random_ids = random.sample(object_ids, 3)
    context = {'random_ids': random_ids}
    return render(request, 'all_data.html', context )


##### Report page
def report(request):
    HttpResponse('Running')

    id = request.POST.get('text', 'default')





    #### finding timezone and its utc offset

    timezon = None
    try:
        timezone_obj = TimeZone.objects.get(store_id=id)
        timezon = timezone_obj.time_zone
    except TimeZone.DoesNotExist:
        timezon = pytz.timezone('America/Chicago')

    # calculate the UTC offset for the specified timezone

    time_now = datetime.datetime.now(pytz.timezone(timezon) )
    utc_offset = time_now.utcoffset().total_seconds() / 60 / 60





    ##################################### END

    ## finding all the timestamp ,arranged in descending(latest first) and they are in UTC

    latest_timestamp_object = StoreStatus.objects.latest('timestamp_utc')
    latest_timestamp = latest_timestamp_object.timestamp_utc




    active_state = StoreStatus.objects.filter(store_id=id, status='active').order_by('-timestamp_utc')

    if(len(active_state) == 0 ):
        return HttpResponse('No data available of this hotel site but usual timings are ')


    ################################################# END

    ## finding start and end time in local time

# Create a dictionary with default values of 24 hours and keys as day=[ 0 to 6 ]

    timing_dict = defaultdict(lambda: {'open': '00:00', 'close': '23:59'})

    # Get the actual opening hours if available
    timing_array = InputData.objects.filter(store_id=id)
    for timing in timing_array:
        timing_dict[timing.store_day] = {'open': timing.start_time_local.strftime('%H:%M'),
                                         'close': timing.end_time_local.strftime('%H:%M')}




    #################################################### END

    ### we have : timing_dict with days(in number) as keys , activestate - list of timestamp in utc ,
    ##  utc_offset  , latest_timestamp in utc


    ## I will be changing all the time in local time to ease calculation and understanding as in
    ## in utc it may cause diffent section of time period that may cause hectic understanding/handling

    # changing timestamp
    timestamp_local = []
    for i in range(len(active_state)) :
        timestamp_local.append( active_state[i].timestamp_utc + datetime.timedelta(hours= utc_offset ) )




    latest_timestamp_local = latest_timestamp + datetime.timedelta(hours= utc_offset )

    uptime_last_hour , downtime_last_hour = computeuptimedowntime(1 , latest_timestamp_local , timestamp_local  , timing_dict)


    uptime_last_day, downtime_last_day = computeuptimedowntime(2, latest_timestamp_local, timestamp_local, timing_dict)
    uptime_last_week, downtime_last_week = computeuptimedowntime(3, latest_timestamp_local, timestamp_local,   timing_dict)



    context = {
        'uptime_lasthour': uptime_last_hour,
        'downtime_lasthour': downtime_last_hour,
        'uptime_lastday': uptime_last_day,
        'downtime_lastday': downtime_last_day,
        'uptime_lastweek': uptime_last_week,
        'downtime_lasthour': downtime_last_week,
        'id': id,
        # replace 'created_at' with the name of the field that stores the creation date of your model
    }

    return render(request, 'Output.html' , context)



####
#####
#################################################################################################
################# HELPER FUNCTIONS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
##############

def daytoint(st):
    if(st.lower() == "monday"):
        return 0
    elif(st.lower() == "tuesday"):
        return 1
    elif(st.lower() == "wednesday"):
        return 2
    elif(st.lower() == "thursday"):
        return 3
    elif(st.lower() == "friday"):
        return 4
    elif(st.lower() == "saturday"):
        return 5
    elif(st.lower() == "sunday"):
        return 6
    else:
        return None

def totaltimefunc( type , current , timing , timingdic ):
    ### total time is accountable for calculation i.e. = uptime + downtime
    totaltime = 0
    # downtime = totaltime - uptime
    current_time = current

    if (type == 1 or type == 2):
        if (type == 1):
            from_time = (current_time - datetime.timedelta(hours=1))


        else:
            from_time = (current_time - datetime.timedelta(days=1))

        while (current_time > from_time):

            current_day = current_time.strftime("%A")

            open_time = datetime.datetime.strptime(timingdic[current_day]['open'], '%H:%M').replace(tzinfo=pytz.utc)
            open_time = current_time.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)

            close_time = datetime.datetime.strptime(timingdic[current_day]['close'], '%H:%M').replace(tzinfo=pytz.utc)
            close_time = current_time.replace(hour=open_time.hour, minute=close_time.minute, second=0, microsecond=0)



            open_time = max(open_time, from_time)

            if (current_time > close_time):
                current_time = close_time

            if (current_time <= from_time):
                break

            elif (open_time < current_time <= close_time):
                totaltime = totaltime + (current_time - max(open_time, from_time)).seconds / 60
                current_time = open_time

            ## we have calculated for that current day change to 1 day earlier midnight

            previous_day = current - datetime.timedelta(days=1)
            # Set the time to 23:59 on the previous day
            previous_day_2359 = previous_day.replace(hour=23, minute=59, second=59)
            current_time = previous_day_2359

    else:  ## type == 3 or any incorrect input
        for i in range(6):
            open_time = timingdic[i]['open']
            open_time = datetime.datetime.strptime(timingdic[i]['open'], '%H:%M').replace(tzinfo=pytz.utc)

            close_time = timingdic[i]['close']
            close_time = datetime.datetime.strptime(timingdic[i]['close'], '%H:%M').replace(tzinfo=pytz.utc)
            totaltime = totaltime + (close_time - open_time).seconds / 60
    return totaltime



def computeuptimedowntime(type  ,  current , timing , timingdic):     # uptime/downtime will be in minutes
    ## timing are timestamp array in local time with the latest first arranged order
    ## timingdic is a dictionary with keys as day 0 for monday contains time in local time
    ## to find day = timing[0].timestamp.strftime("%A")
    ## current = latesttimestamp in local time

    ### i will assume the timestamp active implies the store was active for t+30 minutes and t-30 minutes


    current_time = current

    if(type == 1 ): ### computing for an hour
        from_time = (current_time - datetime.timedelta(hours=1) )




    elif (type == 2):  ## computing for DAY
        from_time =  ( current_time - datetime.timedelta(days=1) )

    else:  ## computing for a WEEK
        from_time = ( current_time - datetime.timedelta(days = 7) )

    uptime = 0


    for t in timing:

        # if curent> t+30min reduce to t+30
        temp = (current_time - datetime.timedelta(minutes=30) )
        if((t) < temp ):
            current_time = t +  datetime.timedelta(minutes=30)
        ##

        if(current_time <= from_time ):
            break


        ## now if current time is more than working hour reduce to max working time/ close time
        current_day_str = current_time.strftime("%A")
        current_day = daytoint(current_day_str)


        open_time = datetime.datetime.strptime(timingdic[current_day]['open'], '%H:%M')
        open_time = current_time.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)



        close_time = datetime.datetime.strptime(timingdic[current_day]['close'], '%H:%M')
        close_time = current_time.replace(hour=close_time.hour, minute=close_time.minute, second=0, microsecond=0)
        current_time = min(current_time, current_time.replace(hour=close_time.hour, minute=close_time.minute) )

        #####



        open_time = max( open_time , from_time )  ### Its important

        thirty_minutes_ago_oft = t - datetime.timedelta(minutes=30)

        if( current_time > t ):
            if(open_time > t ):
                uptime = uptime + ( t+datetime.timedelta(minutes=30) - open_time  ).seconds / 60
                current_time = current_time.replace(hour=open_time.hour, minute=open_time.minute)


#id 3072450101185099776

            elif( t >= open_time + datetime.timedelta(minutes=30)  ):
                uptime = uptime + min(30 , (current_time - t).seconds  / 60 )
                uptime  = uptime + 30
                current_time = t - datetime.timedelta(minutes=30)
            else:
                uptime = uptime + min(30 , (current_time - t).seconds / 60 )
                uptime = uptime + min(30 , (t- open_time).seconds / 60 )
                current_time = t - datetime.timedelta(minutes=30)


        elif( current_time < t and current_time > thirty_minutes_ago_oft  ):
            if(open_time > thirty_minutes_ago_oft ):
                minti = open_time
            else:
                minti = thirty_minutes_ago_oft

            uptime = uptime + min(30 , ( current_time - minti).seconds / 60 )

            current_time = minti





    ######### Now calculate downtime from totaltime

    totaltime = totaltimefunc( type , current , timing , timingdic )
    return uptime , (totaltime - uptime )
















