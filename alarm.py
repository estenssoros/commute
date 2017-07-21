import datetime as dt
import json
import os
import re
import sys
import time

import googlemaps
from twilio.rest import Client

address_book = {'me': '13032299207',
                'allan': '17796612766'}


def twilio_message(to, msg):
    account_sid = os.environ['TWILIO_ACT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    message = client.messages.create(to=to, from_='17206139570', body=msg)
    print message.sid


def get_to_from():
    with open('addresses.json', 'r') as f:
        add_dict = json.load(f)
    if dt.datetime.today().hour < 12:
        return add_dict['home'], add_dict['work']
    else:
        return add_dict['work'], add_dict['home']


def distance_matrix_api():
    origin, destination = get_to_from()
    gmaps = googlemaps.Client(key=os.environ['GOOGLE_KEY'])
    args = {'mode': 'driving',
            'units': 'imperial',
            'departure_time': dt.datetime.today(),
            'traffic_model': 'best_guess',
            'avoid': 'tolls'}
    response = gmaps.distance_matrix(origin, destination, **args)
    elements = response['rows'][0]['elements'][0]
    duration = elements['duration_in_traffic']['value']
    distance = elements['distance']['value']
    traffic = duration - elements['duration']['value']
    data = {'distance': distance,
            'duration': duration,
            'origin': origin,
            'destination': destination,
            'traffic': traffic}
    return data


def seconds_to_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def check_arrival_time(sched):
    dm = distance_matrix_api()
    now = dt.datetime.now()
    arrival = now + dt.timedelta(seconds=dm['duration'])
    repeat = True
    if arrival >= sched:
        msg = arrival.strftime('Depart now to arrive at: %-I:%M:%S %p\n\n')
        msg += 'origin: {}\n'.format(dm['origin'])
        msg += 'destination: {}'.format(dm['destination'])
        if dm['traffic'] > 5 * 60:
            traffic_time = seconds_to_time(dm['traffic'])
            msg += '\nTraffic: {}'.format(traffic_time)
        twilio_message(address_book['me'], msg)
        repeat = False
    else:
        print arrival.strftime('Current arrival time: %-I:%M:%S %p')
    return repeat


time_re = re.compile(r'(?P<hour>[0-9]+):(?P<minute>[0-9]+)')


def string_to_datetime(s):
    t_dict = [m.groupdict() for m in time_re.finditer(s)][0]
    t_dict = {k: int(t_dict[k]) for k in t_dict}
    now = dt.datetime.today()
    return dt.datetime(now.year, now.month, now.day, **t_dict)


def main():

    sched = string_to_datetime(sys.argv[1])
    while check_arrival_time(sched):
        time.sleep(60)


if __name__ == '__main__':
    main()
