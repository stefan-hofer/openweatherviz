from datetime import datetime
import glob
import urllib3
import os
from os.path import expanduser
import pandas as pd
import shutil



def url_synop(lang='eng', header='yes'):
    begin = str(input('Please enter the start time of the query of the format'
                      '(YYYYMMDDHHmm): '))
    end = str(input('Please enter the end time of the query of the format'
                    '(YYYYMMDDHHmm). If you enter "N" then it will use current'
                    'time as the end time: '))
    # state='Austri' for Austrian stations
    state = str(input('If you want to download synops from a specific country'
                      'only then please specify the three letter acronym'
                      '(e.g. "Pol"). If no country enter "N": '))
    list_names = ['begin', 'end', 'lang', 'header', 'state']
    lis = [x for x in [begin, end, lang, header, state]]
    dic = {}
    for name, val in zip(list_names, lis):
        if (val == 'N' or val == 'n'):
            pass
        else:
            dic[name] = val
    url = 'http://www.ogimet.com/cgi-bin/getsynop?'
    i = 0
    for key, value in dic.items():
        # print(key)
        # print(value)
        if i == 0:
            url += key
        else:
            url += '&'+key
        url += '='+value
        i += 1
        print(url)

    return dic, url


def url_last_hour(state=None, lang='eng', header='yes'):
    '''
    Function to create the url for latest (full hour) synop download from
    Ogimet.

    Arguments:
    ----------
    state = None, lang = 'eng', header = 'yes'

    Returns:
    --------
    url (to download file)
    path (to save the file)

    Examples:
    ---------
    from synop_download import url_last_hour
    url, path = url_last_hour()

    '''
    # Create the dates and strings
    now = datetime.utcnow()
    now = datetime(now.year, now.month, now.day, now.hour, 29)
    end_str = now.strftime('%Y%m%d%H%M')
    save_str = datetime(now.year, now.month, now.day, now.hour, 00)
    save_str = save_str.strftime('%Y%m%d%H%M')
    start = datetime(now.year, now.month, now.day, now.hour-1, 31)
    start_str = start.strftime('%Y%m%d%H%M')
    # set up the paths and test for existence
    path = expanduser('~') + '/Documents/Synop_data'
    try:
        os.listdir(path)
    except FileNotFoundError:
        os.mkdir(path)
        print('Created the path {}'.format(path))

    if state is None:
        path = path + '/synop_' + save_str + '.csv'
    else:
        path = path + '/synop_' + save_str + '_' + state + '.csv'

    list_names = ['begin', 'end', 'lang', 'header', 'state']
    lis = [x for x in [start_str, end_str, lang, header, state]]
    dic = {}
    for name, val in zip(list_names, lis):
        if (val == 'N' or val == 'n' or val is None):
            pass
        else:
            dic[name] = val
    url = 'http://www.ogimet.com/cgi-bin/getsynop?'
    i = 0
    for key, value in dic.items():
        # print(key)
        # print(value)
        if i == 0:
            url += key
        else:
            url += '&'+key
        url += '='+value
        i += 1
        print(url)

    return url, path


def url_any_hour(year=None, month=None, day=None, hour=None, state=None, lang='eng',
                 header='yes'):
    '''
    Function to create the url for provided (full hour) synop download from
    Ogimet.

    Arguments:
    ----------
    year=None, month=None, day=None, hour=None, state=None, state = None, lang =
    'eng', header = 'yes'

    Returns:
    --------
    url (to download file)
    path (to save the file)

    Examples:
    ---------
    from synop_download import url_any_hour
    url, path = url_any_hour()

    '''
    # Create the dates and strings
    now = datetime(year, month, day, hour, 29)
    end_str = now.strftime('%Y%m%d%H%M')
    save_str = datetime(year, month, day, hour, 00)
    save_str = save_str.strftime('%Y%m%d%H%M')
    start = datetime(year, month, day, hour-1, 31)
    start_str = start.strftime('%Y%m%d%H%M')
    # set up the paths and test for existence
    path = expanduser('~') + '/Documents/Synop_data'
    try:
        os.listdir(path)
    except FileNotFoundError:
        os.mkdir(path)
        print('Created the path {}'.format(path))

    if state is None:
        path = path + '/synop_' + save_str + '.csv'
    else:
        path = path + '/synop_' + save_str + '_' + state + '.csv'

    list_names = ['begin', 'end', 'lang', 'header', 'state']
    lis = [x for x in [start_str, end_str, lang, header, state]]
    dic = {}
    for name, val in zip(list_names, lis):
        if (val == 'N' or val == 'n' or val is None):
            pass
        else:
            dic[name] = val
    url = 'http://www.ogimet.com/cgi-bin/getsynop?'
    i = 0
    for key, value in dic.items():
        # print(key)
        # print(value)
        if i == 0:
            url += key
        else:
            url += '&'+key
        url += '='+value
        i += 1
        print(url)

    return url, path


def url_timeseries(year=None, month=None, day=None, hour=None,
                   year_end=None, month_end=None, day_end=None, hour_end=None,
                   station=None, state=None, lang='eng',
                   header='yes'):
    '''
    Function to download a time series of SYNOP observations from a station or a
    block of station (i.e. station = 11, will download all stations starting with 11)

    Arguments:
    ----------
    year=None, month=None, day=None, hour=None,
    year_end=None, month_end=None, day_end=None, hour_end=None,
    station=None, state=None, lang='eng',
    header='yes'

    Returns:
    --------
    url (to download file)
    path (to save the file)

    Examples:
    ---------
    from synop_download import url_any_hour
    url, path = url_timeseries(2018,2,22,0,2018,2,23,17,'04301')

    '''
    station = str(station)
    # Create the dates and strings
    now = datetime(year_end, month_end, day_end, hour_end, 00)
    end_str = now.strftime('%Y%m%d%H%M')

    save_str_end = datetime(year_end, month_end, day_end, hour_end, 00)
    save_str_end = save_str_end.strftime('%Y%m%d%H%M')

    start = datetime(year, month, day, hour, 00)
    start_str = start.strftime('%Y%m%d%H%M')

    save_str = datetime(year, month, day, hour, 00)
    save_str = save_str.strftime('%Y%m%d%H%M')
    # set up the paths and test for existence
    path = expanduser('~') + '/Documents/Synop_data/StationData/' + station + '/'
    try:
        os.listdir(path)
    except FileNotFoundError:
        os.makedirs(path)
        print('Created the path {}'.format(path))

    # Where to save the file
    path = path + 'synop_' + station + '_' + save_str + '-' + save_str_end + '.csv'

    list_names = ['block', 'begin', 'end', 'lang', 'header', 'state']
    lis = [x for x in [station, start_str, end_str, lang, header, state]]
    dic = {}
    for name, val in zip(list_names, lis):
        if (val == 'N' or val == 'n' or val is None):
            pass
        else:
            dic[name] = val
    url = 'http://www.ogimet.com/cgi-bin/getsynop?'
    i = 0
    for key, value in dic.items():
        # print(key)
        # print(value)
        if i == 0:
            url += key
        else:
            url += '&'+key
        url += '='+value
        i += 1
        print(url)

    return url, path


def download_and_save(path, url):
    '''
    Function to download and save the file from the url created by either
    url_last_hour() or url_synop().

    Arguments:
    ----------
    path (where to save file on disk)
    url (to download file)

    Returns:
    --------
    File on disk

    Examples:
    ---------
    from synop_download import url_last_hour
    url, path = url_last_hour()
    download_and_save(path, url)

    '''

    if os.path.exists(path):
        print('Using an existing file stored in {}.'.format(path))
    else:
        http = urllib3.PoolManager()
        with http.request('GET', url, preload_content=False) as r, open(path, 'wb') \
                as out_file:
                    shutil.copyfileobj(r, out_file)
        print('Saved file to {}.'.format(path))


if __name__ == 'main':
    url, path = url_last_hour(state=None)
    download_and_save(path, url)
