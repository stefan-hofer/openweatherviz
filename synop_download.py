import urllib3
import os
from os.path import expanduser



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


http = urllib3.PoolManager()
# set up the paths and test for existence
path = expanduser('~') + '/Documents/Synop_data'
try:
    os.listdir(path)
except:
    os.mkdir(path)
with http.request('GET', url, preload_content=False) as r, open(path+'/test.txt', 'wb') \
        as out_file:
            shutil.copyfileobj(r, out_file)


# WMOIND,YEAR,MONTH,DAY,HOUR,MIN,REPORT
#
# Dates of begin and end of time interval have the format YYYYMMDDHHmm
#
# Where
#
# YYYY Year (four digits)
# MM (month, two digits)
# DD (day, two digits)
# HH (hour , two digits)
# mm (minute, two digits)
#
# Arguments
#
# begin=YYYYMMDDHHmm  (mandatory)
# end=YYYYMMDDHHmm  (default is current time)
# lang=eng (english, optional)
# header=yes (include a first line with the name of columns)
# state=Begin_of_state_string
# block=First_digits_of_WMO_IND
# ship=yes (to get ship reports for a time interval over the whole world)
#
# If 'state' and 'block' are not selected, then is supossed all the world.
#
# Better some examples:
#
# 1) All synops AFTER 200912160000 for states begining with 'Pol, i.e. 'Poland'
#
# http://www.ogimet.com/cgi-bin/getsynop?begin=200912160000&state=Pol&lang=eng
#
# 2) All synops for 15-dec-2009 . Poland
#
#  http://www.ogimet.com/cgi-bin/getsynop?begin=200912150000&end=200912152359&state=Pol
#
# 3) All synops for WMO index begining with '123' FROM 200912010000 TILL 200912040000
#
#   http://www.ogimet.com/cgi-bin/getsynop?block=123&begin=200912010000&end=200912040000
#
# 4) All ships from 06 UTC to 07 UTC on 8 Jun 2011
#
#   http://www.ogimet.com/cgi-bin/getsynop?begin=201106080600&end=201106080700&ship=yes
#
# 5) All synop and synop-mobil from a land station from 06 UTC to 07 UTC on 8 Jun 2011
#
#   http://www.ogimet.com/cgi-bin/getsynop?begin=201106080600&end=201106080700
#
#
# There are some limits:
#
# -No more than 200000 synops in a petition. :-)
#
# You can play with libraries like curl to get directly your desired file.
#
# curl "http://www.ogimet.com/cgi-bin/getsynop?block=123&begin=200912010000&end=200912040000" -o "your_desired_file_name"
#
# Same using wget
#
# wget "http://www.ogimet.com/cgi-bin/getsynop?block=123&begin=200912010000&end=200912040000" -O "your_desired_file_name"
#
# Enjoy! And please, don't abuse.
