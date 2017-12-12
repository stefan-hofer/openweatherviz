import urllib3


def download_synop():
    begin = input('Please enter the start time of the query of the format \
                  (YYYYMMDDHHmm): ')
    end = input('Please enter the end time of the query of the format \
                (YYYYMMDDHHmm). If you enter 'N' then it will use current time \
                as the end time: ')
    if end == 'N' or 'n':
        string = '&begin='+str(begin)


http = urllib3.PoolManager()
path = '/mnt/test/stefan_hofer/Synop_data/'
url = 'http://www.ogimet.com/cgi-bin/getsynop?begin=201712120000&lang=eng&header=yes&state=Pol'
with http.request('GET', url, preload_content=False) as r, open(path, 'wb') \
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
