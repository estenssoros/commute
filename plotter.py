import pandas as pd
import datetime as dt
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from aws import connect_dynamodb
from time import time


def morning_afternoon(t):
    if t.hour < 12:
        return 'morning'
    else:
        return 'afternoon'


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
        plt.ylabel('commute time in seconds')
        plt.show()
        plt.close()


def graph_5(tod, df=None):
    if df is None:
        df = make_df()
    weekdays = list(range(1, 6))
    week_dict = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday',  5: 'Friday'}
    fig, axs = plt.subplots(1, 5, sharey=True, figsize=(20, 4))

    for weekday, ax in zip(weekdays, axs.flatten()):
        day_df = df[(df['dow'] == weekday) & (df['m/a'] == tod)]
        data_days = pd.unique(day_df['month_day']).tolist()
        data_days.sort()
        for data_day in data_days:
            day_df[day_df['month_day'] == data_day][['duration']].plot(ax=ax)
            ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
            ax.set_title(week_dict[weekday], y=1.05)
            ax.legend_.remove()

    plt.ylabel('commute time in seconds')
    plt.tight_layout()
    plt.savefig('images/{0}.png'.format(tod))
    plt.show()
    plt.close()


def main():
    df = make_df()
    df.set_index('time', inplace=True)
    for tod in ['morning', 'afternoon']:
        graph_5(tod, df=df)

if __name__ == '__main__':
    main()
