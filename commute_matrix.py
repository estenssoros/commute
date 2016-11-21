import matplotlib.path as mplPath
import pandas as pd
import numpy as np
import folium
import subprocess
from progressbar import ProgressBar, Bar, Percentage, AdaptiveETA
import googlemaps
import os


def get_boundary_points():
    p1 = (39.702248, -104.987396)
    p2 = (39.691106, -104.974581)
    p3 = (39.691106, -104.959347)
    p4 = (39.718136, -104.959347)
    p5 = (39.718136, -104.940903)
    p6 = (39.758320, -104.940903)
    p7 = (39.771182, -104.940903)
    p8 = (39.771182, -104.973331)
    p9 = (39.754689, -104.994373)
    p10 = (39.761634, -105.004886)
    p11 = (39.767492, -104.997945)
    p12 = (39.783419, -104.998255)
    p13 = (39.783419, -105.052862)
    p14 = (39.740712, -105.053053)
    p15 = (39.740758, -105.012972)
    points = [p1, p2, p3, p4, p5, p6, p7, p8,
              p9, p10, p11, p12, p13, p14, p15, p1]
    return points


def get_valid_points():
    points = get_boundary_points()
    bbPath = mplPath.Path(np.array(points))

    lat_bounds = min([x[0] for x in points]), max([x[0] for x in points])
    lng_bounds = min([x[1] for x in points]), max([x[1] for x in points])

    valid_points = []
    for lat in np.linspace(*lat_bounds):
        for lng in np.linspace(*lng_bounds):
            if bbPath.contains_point((lat, lng)):
                valid_points.append((lat, lng))
    return valid_points


def make_df():
    gmaps = googlemaps.Client(key=os.environ['GMAPS_API_KEY'])
    points = get_valid_points()

    df = pd.DataFrame()
    bar = ProgressBar(widgets=[Percentage(), Bar(), AdaptiveETA()])
    work = '1100 McCaslin Blvd #100, Superior, CO 80027, USA'
    for point in bar(points):
        lat, lng = point
        resp = gmaps.distance_matrix(point, work)
        dist = resp['rows'][0]['elements'][0]['distance']['value']
        dur = resp['rows'][0]['elements'][0]['duration']['value']
        row = {'lat': lat, 'lng': lng, 'distance': dist, 'duration': dur}
        df = df.append(row, ignore_index=True)
    df.to_pickle('data/df.pickle')


def check_for_files():
    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists('data/df.pickle'):
        make_df()
    return pd.read_pickle('data/df.pickle')
if __name__ == '__main__':
    df = check_for_files()
    points = get_boundary_points()

    lat_bounds = min([x[0] for x in points]), max([x[0] for x in points])
    lng_bounds = min([x[1] for x in points]), max([x[1] for x in points])

    location = [np.mean(lat_bounds), np.mean(lng_bounds)]
    my_map = folium.Map(location=location,
                        tiles='Stamen Toner',
                        zoom_start=12)
    colors = ['green', 'yellow', 'orange', 'red']

    df['bin'] = pd.cut(df['duration'], 4)
    bins = pd.unique(df['bin']).tolist()
    bins.sort()
    color_dict = dict(zip(bins, colors))
    df['color'] = df.apply(lambda x: color_dict[x['bin']], axis=1)
    for i, r in df.iterrows():
        coord = r['lat'],r['lng']
        color = r['color']
        folium.CircleMarker(coord, fill_color=color, radius=80).add_to(my_map)
    my_map.save("./map.html")
    subprocess.Popen(['open', 'map.html'])
