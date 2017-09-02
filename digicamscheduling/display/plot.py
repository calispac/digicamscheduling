import matplotlib.pyplot as plt
import astropy.units as u


def plot_azimuth(date, azimuth, axis=None, **kwargs):

    if axis is None:
        fig = plt.figure()
        axis = fig.add_subplot(111)

    axis.plot_date(date.plot_date, azimuth, linestyle='-', marker='None', **kwargs)
    axis.set_xlabel('UTC time')
    axis.set_ylabel('azimuth [deg]')
    axis.legend(loc='best')
    plt.gcf().autofmt_xdate()

    return axis


def plot_elevation(date, elevation, axis=None, **kwargs):

    if axis is None:
        fig = plt.figure()
        axis = fig.add_subplot(111)

    axis.plot_date(date.plot_date, elevation, linestyle='-', marker='None', **kwargs)
    axis.set_xlabel('UTC time')
    axis.set_ylabel('elevation [deg]')
    axis.set_ylim([0, 90])
    axis.legend(loc='upper left')
    plt.gcf().autofmt_xdate()

    return axis


def plot_trajectory(azimuth, elevation, axis=None, **kwargs):

    if axis is None:
        fig = plt.figure()
        axis = fig.add_subplot(111, projection='polar')

    axis.plot(azimuth.to('radian'), (90 * u.deg - elevation).to('deg'), **kwargs)
    axis.set_rmax(90)
    axis.legend(loc='best')

    return axis
