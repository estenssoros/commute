import pandas as pd
import datetime as dt
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from aws import connect_dynamodb
from time import time


def morning_afternoon(t):
    if t.hour < 12:
        return 'm'
    else:
        return 'a'


def fix_time(t):
    return dt.datetime(2016, 11, 11, t.hour, t.minute)


def make_df():
    table = connect_dynamodb()
    t1 = time()
    data = list(table.scan())
    print 'operation took: {0} seconds'.format(time() - t1)
    df = pd.DataFrame(data)
    df['time'] = df.apply(lambda x:  dt.datetime.fromtimestamp(x['time']), axis=1)
    df['month_day'] = df.apply(lambda x: '{0}_{1}'.format(x['time'].month, x['time'].day), axis=1)
    df['dow'] = df.apply(lambda x: x['time'].isoweekday(), axis=1)
    df['m/a'] = df.apply(lambda x: morning_afternoon(x['time']), axis=1)
    df['time'] = df.apply(lambda x: fix_time(x['time']), axis=1)
    return df


def graph():
    df = make_df()
    df.set_index('time', inplace=True)
    weekdays = list(range(1, 6))
    week_dict = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday',  5: 'Friday'}
    for weekday in weekdays:
        day_df = df[(df['dow'] == weekday) & (df['m/a'] == 'm')]
        fig, ax = plt.subplots(1, 1)

        data_days = pd.unique(day_df['month_day']).tolist()
        data_days.sort()
        for data_day in data_days:
            day_df[day_df['month_day'] == data_day][['duration']].plot(ax=ax)
        ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
        plt.title(week_dict[weekday], y=1.05)
        plt.savefig('images/{0}.png'.format(week_dict[weekday]))
        plt.show()
        plt.close()

    # month_days = pd.unique(df['month_day'])
    # for month_day in month_days:
    #
    #     new_df = df[df['month_day'] == month_day]
    #     morning_df = new_df[new_df['m/a'] == 'm']
    #     afternoon_df = new_df[new_df['m/a'] == 'a']
    #     if len(morning_df) > 0 and len(afternoon_df) > 0:
    #         fig, axs = plt.subplots(1, 2)
    #         morning_df[['duration']].plot(ax=axs[0])
    #         afternoon_df[['duration']].plot(ax=axs[1])
    #         for ax in axs:
    #             ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    #         plt.title(month_day)
    #         plt.show()

if __name__ == '__main__':
    graph()
