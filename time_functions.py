import datetime as dt
import sys
from progressbar import ProgressBar, Counter, Bar
import time


def test_time():
    now = dt.datetime.today()
    m_open = dt.datetime(now.year, now.month, now.day, 5, 00, 00, 00)
    m_close = dt.datetime(now.year, now.month, now.day, 10, 0, 00, 00)
    a_open = dt.datetime(now.year, now.month, now.day, 16, 0, 00, 00)
    a_close = dt.datetime(now.year, now.month, now.day, 19, 0, 00, 00)

    if (now > m_open and now < m_close) or (m > a_open and now < a_close):
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
