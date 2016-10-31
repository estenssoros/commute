import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from aws import connect_dynamodb


def morning_afternoon(t):
    if t.hour < 12:
        return 'm'
    else:
        return 'a'


def make_df():
    table = connect_dynamodb()
    df = pd.DataFrame()
    for i in table.scan():
        df = df.append(i, ignore_index=True)
    df['time'] = df.apply(lambda x:  dt.datetime.fromtimestamp(x['time']), axis=1)
    df['month_day'] = df.apply(lambda x: '{0}_{1}'.format(x['time'].month, x['time'].day), axis=1)
    df['m/a'] = df.apply(lambda x: morning_afternoon(x['time']), axis=1)
    return df


def graph():
    df = make_df()
    print 'gathered df'
    df.set_index('time', inplace=True)
    month_days = pd.unique(df['month_day'])
    for month_day in month_days:

        new_df = df[df['month_day'] == month_day]
        morning_df = new_df[new_df['m/a'] == 'm']
        afternoon_df = new_df[new_df['m/a'] == 'a']
        if len(morning_df) > 0 and len(afternoon_df) > 0:
            fig, axs = plt.subplots(2, 1)
            morning_df[['duration']].plot(ax=axs[0])
            afternoon_df[['duration']].plot(ax=axs[1])
            plt.title(month_day)
            plt.show()

if __name__ == '__main__':
    pass
