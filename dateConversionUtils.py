from datetime import timedelta
from dateutil import tz
import datetime
import operationSheets
import pytz
from pytz import all_timezones


def format_date_col(date):
    try:
        fmt = '%Y-%m-%d %H:%M:%S'
        dt = datetime.datetime.fromtimestamp(int(date) / 1000)
        dt = dt.astimezone(pytz.utc)
        dt = dt.replace(tzinfo=pytz.utc)
        dt = dt.strftime(fmt)

    except Exception as e:
        print("Exception format_date_col:", e)
        dt = date

    return dt


def getDateRangeFollowers():
    fmt = '%Y/%m/%d %H:%M:%S'

    # convert to utc
    dateNow = datetime.datetime.now().astimezone(pytz.utc)
    dateNow = dateNow.replace(tzinfo=pytz.utc)

    print("dateNow_UTC: " + str(dateNow.strftime(fmt)))

    sinceDate = dateNow - timedelta(days=1)
    sinceDate = sinceDate.replace(hour=00, minute=00, second=00)
    timestampSinceDate = int(sinceDate.timestamp()) * 1000

    endDate = dateNow - timedelta(days=1)
    endDate = endDate.replace(hour=23, minute=59, second=59)
    timestampEndDate = int(endDate.timestamp()) * 1000

    print('Since Date UTC: ' + str(sinceDate.strftime(fmt)))
    print("int SinceDateTimeStamp UTC: " + str(timestampSinceDate))

    print('End Date UTC: ' + str(endDate.strftime(fmt)))
    print("int EndDateTimeStamp UTC: " + str(timestampEndDate))

    return timestampSinceDate, timestampEndDate


def getDateRange():
    fmt = '%Y/%m/%d %H:%M:%S'

    # convert to utc
    dateNow = datetime.datetime.now().astimezone(pytz.utc)
    dateNow = dateNow.replace(tzinfo=pytz.utc)

    print("dateNow_UTC: " + str(dateNow.strftime(fmt)))

    if (dateNow.day == 1):
        sinceDate = dateNow - timedelta(days=1)
        sinceDate = sinceDate.replace(day=1, hour=0, minute=0, second=0)
        timestampSinceDate = int(sinceDate.timestamp()) * 1000

        endDate = dateNow - timedelta(days=1)
        endDate = endDate.replace(hour=23, minute=59, second=59)
        timestampEndDate = int(endDate.timestamp()) * 1000

    else:
        sinceDate = dateNow.replace(day=1, hour=00, minute=00, second=00)
        timestampSinceDate = int(sinceDate.timestamp()) * 1000

        endDate = dateNow - timedelta(days=1)
        endDate = endDate.replace(hour=23, minute=59, second=59)
        timestampEndDate = int(endDate.timestamp()) * 1000

    # sinceDate=datetime.datetime(2020,10,31,0,0,0)
    # sinceDate = sinceDate.replace(tzinfo=pytz.utc)
    # timestampSinceDate = int(sinceDate.timestamp()) * 1000
    #
    #
    # endDate=datetime.datetime(2020,10,31,23,59,59)
    # endDate = endDate.replace(tzinfo=pytz.utc)
    # timestampEndDate = int(endDate.timestamp()) * 1000

    print('Since Date UTC: ' + str(sinceDate.strftime(fmt)))
    print("int SinceDateTimeStamp UTC: " + str(timestampSinceDate))

    print('End Date UTC: ' + str(endDate.strftime(fmt)))
    print("int EndDateTimeStamp UTC: " + str(timestampEndDate))

    return timestampSinceDate, timestampEndDate


def getTimeZones(Red):
    timeZones = None
    try:
        rangeNameSettings = "Accounts Final!A1:Z"
        timeZones = operationSheets.readTimeZonesSheetTab(rangeNameSettings)

        if (Red == 'FACEBOOK'):
            timeZones = timeZones[timeZones['Channel'] == 'FB']
            timeZones['Account on Sprinklr'] = timeZones['Account on Sprinklr'].str.strip()
            timeZones['Time Zone'] = timeZones['Time Zone'].str.strip()
            timeZones = timeZones[['Account on Sprinklr', 'Time Zone']].set_index('Account on Sprinklr').to_dict()[
                'Time Zone']

        if (Red == 'INSTAGRAM'):
            timeZones = timeZones[timeZones['Channel'] == 'IG']
            timeZones['Account on Sprinklr'] = timeZones['Account on Sprinklr'].str.strip()
            timeZones['Time Zone'] = timeZones['Time Zone'].str.strip()
            timeZones = timeZones[['Account on Sprinklr', 'Time Zone']].set_index('Account on Sprinklr').to_dict()[
                'Time Zone']

        if (Red == 'TWITTER'):
            timeZones = timeZones[timeZones['Channel'] == 'TW']
            timeZones['Account on Sprinklr'] = timeZones['Account on Sprinklr'].str.strip()
            timeZones['Time Zone'] = timeZones['Time Zone'].str.strip()
            timeZones = timeZones[['Account on Sprinklr', 'Time Zone']].set_index('Account on Sprinklr').to_dict()[
                'Time Zone']

        if (Red == 'YOUTUBE'):
            timeZones = timeZones[timeZones['Channel'] == 'YT']
            timeZones['Account on Sprinklr'] = timeZones['Account on Sprinklr'].str.strip()
            timeZones['Time Zone'] = timeZones['Time Zone'].str.strip()
            timeZones = timeZones[['Account on Sprinklr', 'Time Zone']].set_index('Account on Sprinklr').to_dict()[
                'Time Zone']

    except Exception as e:
        print(e)

    timeZones['N/A'] = None
    return timeZones


def mapCityTimeZone(location):
    if location != 'nan':
        location = location.split(', ')[0]
        location = location.replace(' ', '_')
        for zone in all_timezones:
            if location in zone:
                return zone

    return ""


def assignTimeZoneDate(dateUTC, timeZone):
    if (timeZone):
        fmt = '%Y-%m-%d %H:%M:%S'
        converted = datetime.datetime.strptime(dateUTC, fmt)
        converted = converted.replace(tzinfo=pytz.utc)

        converted = converted.astimezone(pytz.timezone(timeZone)).strftime(fmt)
        return converted

    return ""

def assignTimeZoneLONDON(dateUTC):
    if (dateUTC is not None):
        fmt = '%Y-%m-%d %H:%M:%S'
        converted = datetime.datetime.strptime(dateUTC, fmt)
        converted = converted.replace(tzinfo=pytz.utc)

        converted = converted.astimezone(pytz.timezone('Europe/London')).strftime(fmt)
        return converted

    return ""



def getEquivalentAccounts():
    equivalentAccounts = None
    try:
        rangeNameSettings = "Accounts Final!A1:Z"
        equivalentAccounts = operationSheets.readTimeZonesSheetTab(rangeNameSettings)
        equivalentAccounts = equivalentAccounts[['Account', 'Account on Sprinklr']]
        equivalentAccounts['Account'] = equivalentAccounts['Account'].str.strip()
        equivalentAccounts['Account on Sprinklr'] = equivalentAccounts['Account on Sprinklr'].str.strip()
        equivalentAccounts = equivalentAccounts[['Account', 'Account on Sprinklr']].set_index('Account').to_dict()[
            'Account on Sprinklr']

    except Exception as e:
        print(e)

    return equivalentAccounts


def fixedDates():

    fmt = '%Y/%m/%d %H:%M:%S'

    sinceDate=datetime.datetime(2021,1,1,0,0,0)
    sinceDate = sinceDate.replace(tzinfo=pytz.utc)
    timestampSinceDate = int(sinceDate.timestamp()) * 1000


    endDate=datetime.datetime(2021,7,31,23,59,59)
    endDate = endDate.replace(tzinfo=pytz.utc)
    timestampEndDate = int(endDate.timestamp()) * 1000


    print('FIXED SINCE DATE UTC: ' + str(sinceDate.strftime(fmt)))
    print("int FIXED SINCE DATE UTC: " + str(timestampSinceDate))

    print('FIXED END DATE UTC: ' + str(endDate.strftime(fmt)))
    print("int FIXED END DATE UTC: " + str(timestampEndDate))

    return timestampSinceDate, timestampEndDate