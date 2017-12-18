from datetime import datetime
import urllib3
import os
from os.path import expanduser
import shutil


def download_synop(lang='eng', header='yes'):
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
        print(key)
        print(value)
        if i == 0:
            url += key
        else:
            url += '&'+key
        url += '='+value
        i += 1
        print(url)

    return dic, url


def url_last_hour(state=None, lang='eng', header='yes'):
    # Create the dates and strings
    now = datetime.utcnow()
    now = datetime(now.year, now.month, now.day, now.hour, 30)
    end_str = now.strftime('%Y%m%d%H%M')
    save_str = datetime(now.year, now.month, now.day, now.hour, 00)
    save_str = save_str.strftime('%Y%m%d%H%M')
    start = datetime(now.year, now.month, now.day, now.hour-1, 30)
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
        print(key)
        print(value)
        if i == 0:
            url += key
        else:
            url += '&'+key
        url += '='+value
        i += 1
        print(url)

    return url, path


def download_and_save(path, url):
    http = urllib3.PoolManager()
    with http.request('GET', url, preload_content=False) as r, open(path, 'wb') \
            as out_file:
                shutil.copyfileobj(r, out_file)


if __name__ == 'main':
    url, path = url_last_hour(state=None)
    download_and_save(path, url)
