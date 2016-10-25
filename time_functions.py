import datetime as dt
import sys
from progressbar import ProgressBar, Counter, Bar
import time


def test_time():
    now = dt.datetime.today()
    if (now.hour > 5 and now.hour < 9) or (now.hour > 16 and now.hour < 19):
        return True
    else:
        return False


def print_time():
    if sys.platform == 'linux2':
        hours = 4
    else:
        hours = 0
    t = dt.datetime.today() - dt.timedelta(hours=hours)
    print 'Current time is: {0}'.format(t.strftime('%r'))


def sleep_min():
    sleept = 60 - dt.datetime.today().second
    bar = ProgressBar(widgets=[Counter(), '/{} '.format(sleept), Bar()])
    for i in bar(range(sleept)):
        time.sleep(1)
