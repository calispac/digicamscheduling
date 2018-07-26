import numpy as np
import astropy.units as u
from astropy.coordinates import EarthLocation
from astropy.time import Time
from digicamscheduling.io import reader
from digicamscheduling.core import gamma_source, moon, sun
from digicamscheduling.core.environement import interpolate_environmental_limits, is_above_environmental_limits
from digicamscheduling.utils import time
from digicamscheduling.display.plot import plot_elevation, plot_source
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from tqdm import tqdm
import os


def main(sources_filename, location_filename, environment_filename,
         start_date, end_date, time_steps, output_path, show=False):

    sources = reader.read_catalog(sources_filename)
    coordinates = reader.read_location(filename=location_filename)
    location = EarthLocation(**coordinates)

    alt_trees, az_trees = reader.read_environmental_limits(
        environment_filename)
    alt_trees = alt_trees * u.deg
    az_trees = az_trees * u.deg
    env_limits = interpolate_environmental_limits(alt_trees,
                                                  az_trees)

    start_date = Time(start_date)  # time should be 00:00
    end_date = Time(end_date)  # time should be 00:00

    date = time.compute_time(date_start=start_date, date_end=end_date,
                             time_steps=time_steps, location=location,
                             only_night=True)

    moon_position = moon.compute_moon_position(date=date, location=location)
    moon_elevation = moon_position.alt
    moon_phase = moon.compute_moon_phase(date=date)
    sun_position = sun.compute_sun_position(date=date, location=location)
    sun_elevation = sun_position.alt

    observability = (sun_elevation < -12 * u.deg) * np.cos(moon_elevation)
    observability *= (1 - moon_phase) * (moon_elevation < 0 * u.deg)

    fig_1 = plt.figure()
    axes_1 = fig_1.add_subplot(111)
    fig_2 = plt.figure()
    axes_2 = fig_2.add_subplot(111)

    color = iter(cm.rainbow(np.linspace(0, 1, num=len(sources))))

    for i, source in tqdm(enumerate(sources), total=len(sources),
                          desc='Source'):

        c = next(color)

        temp = gamma_source.compute_source_position(date=date,
                                                    location=location,
                                                    ra=source['ra'],
                                                    dec=source['dec'])
        source_elevation = temp.alt
        source_azimuth = temp.az
        is_above_trees = is_above_environmental_limits(
            source_elevation, source_azimuth, env_limits)
        moon_separation = temp.separation(moon_position)

        source_visibility = is_above_trees * np.sin(source_elevation)
        source_visibility *= observability * (moon_separation > 10 * u.deg)

        label = source['name']
        plot_elevation(date, source_elevation, axes=axes_1, color=c,
                       label=label)
        plot_source(date, source_visibility,
                    axes=axes_2, color=c, y_label='visibility []',
                    ylim=[0, 1], label=label)

    fig_1.savefig(os.path.join(output_path, 'elevation.png'))
    fig_2.savefig(os.path.join(output_path, 'visibility.png'))

    if show:

        plt.show()


if __name__ == '__main__':

    start_date = '2018-06-26'
    end_date = '2018-07-10'
    time_step = 1 * u.minute
    output_path = 'figures/'
    show = False

    location_filename = 'digicamscheduling/config/location_krakow.txt'
    sources_filename = 'digicamscheduling/config/catalog.txt'
    environment_filename = 'digicamscheduling/config/environmental_limitation.txt'

    main(location_filename=location_filename,
         sources_filename=sources_filename,
         environment_filename=environment_filename,
         start_date=start_date,
         end_date=end_date,
         time_steps=time_step,
         output_path=output_path,
         show=show)