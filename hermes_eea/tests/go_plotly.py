import os
import sys
import numpy as np
import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from spacepy import pycdf
from spacepy.pycdf import lib
from astropy.time import Time

"""
Purpose: To closely previous versions of the EEA output CDF with new ones.
"""


def iso_obj_to_epoch(trange):
    """
    ISO to CDF EPOCH:
    cdflib.epochs.CDFepoch.parse('2012-01-01T01:01:01.000000000')

    :param trange: a list, typically 2, of datetime objects
    :return:18 digit epoch times for CDF
    """
    converted = []
    for t in trange:
        # dateString = t.strftime("%Y-%m-%dT%H:%M:%S.000000000")
        dateString = t.strftime("%Y-%m-%dT%H:%M:%S.%f000")
        try:
            c = cdflib.epochs.CDFepoch.parse(dateString)
            converted.append(c)
        except ValueError as e:
            print(t + " This time range value doesn't look too kosher...", file=stderr)
        # exit(1)
    return converted


def read_data(file):
    try:
        cdffile = cdf = pycdf.CDF(file)
        length = len(cdffile["Epoch"][:])
        print("file len:", length)
        return cdffile
    except Exception:
        if not os.path.exists(file):
            print(file + " does not exist")
            return None


def diff(a, b):
    if abs(a + b) != 0:
        return abs((a - b) / ((a + b) / 2.0))
    else:
        return 0


def tolerance(y1, y2, tolerance):
    """
    only show the data points that differ greater than some tolerance
    Parameters
    ----------
    y1 variable x from golden file
    y2 variable x from artifact
    tolerance may be different for each var
    Returns
    -------

    """

    yy1 = []
    yy2 = []
    x3 = []

    for i in range(0, len(y1)):
        if diff(y1[i], y2[i]) >= tolerance:
            print(y1[i], y2[i], diff(y1[i], y2[i]))
            yy1.append(y1[i])
            yy2.append(y2[i])
            x3.append(i)

    return [np.array(yy1), np.array(yy2), np.array(x3)]


def prepare_data(var, far=1600):
    y1 = mycdf[var][0:far]
    y2 = newcdf[var][0:far]  # len(y1.shape) == 1

    return [y1, y2]


def draw_plot(y1, y2, x_axis, variable):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=x_axis,
            y=y1,
            mode="markers+lines",
            marker=dict(color="red", size=12),
            name="golden",
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=x_axis,
            y=y2,
            mode="markers+lines",
            marker=dict(color="orange", size=12),
            name="newfile",
        ),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(title_text=variable)

    # Set x-axis title
    fig.update_xaxes(title_text="n")

    fig.show()


def arange_plot(nth, variables, tol):
    var = nth
    variable = variables[var]
    x_axis_length = mycdf[variables[var]].shape[0]
    orgx = np.arange(0, x_axis_length, 1)

    [y1, y2] = prepare_data(variable, x_axis_length)
    x = 1
    for n in y1.shape:
        x = x * n
    flat_y1 = y1.reshape((x))
    flat_y2 = y2.reshape((x))
    [tol_y1, tol_y2, remaining_x] = tolerance(flat_y1, flat_y2, tol)

    draw_plot(tol_y1, tol_y2, remaining_x, variable)


def datetime_plot(nth, variables, tol):
    var = nth
    variable = variables[var]
    x_axis_length = mycdf[variables[var]].shape[0]
    [y1, y2] = prepare_data(variable, x_axis_length)
    y1_epochs = [lib.datetime_to_tt2000(e) for e in y1]
    y2_epochs = [lib.datetime_to_tt2000(e) for e in y1]

    [tol_y1, tol_y2, remaining_x] = tolerance(y1_epochs, y2_epochs, tol)
    draw_plot(tol_y1, tol_y2, remaining_x, variable)


if __name__ == "__main__":
    golden = "hermes_eea/tests/hermes_eea_l1_20000101T170901_v1.0.0.cdf"
    artifact = "/Users/rstrub/Downloads/processed-files/hermes_eea_l1_20000101T170901_v1.0.0.cdf"

    newcdf = read_data(artifact)
    mycdf = read_data(golden)
    if mycdf == None:
        print("Could not read:", golden)
        exit(1)
    mylist = [item[0] for item in list(mycdf.items())]
    newlist = [item[0] for item in list(newcdf.items())]
    # list variables from both files:
    for item in mylist:
        try:
            print(
                item,
                len(mycdf[item[:]]),
                mycdf[item].shape,
                len(newcdf[item[:]]),
                newcdf[item].shape,
                mycdf[item].meta["VAR_TYPE"],
                newcdf[item].meta["VAR_TYPE"],
            )
        except KeyError:
            print("Files have different variables:")
            for item in mylist:
                if item not in newlist:
                    print("old has: ", item)
            for item in newlist:
                if item not in mylist:
                    print("new has: ", item)
            exit(1)

    variables = mylist

    # Epoch difference >= 1.0:
    datetime_plot(0, variables, 1.0)

    # Stats difference >= 0:
    arange_plot(1, variables, 0.0)
    # steptimes difference >= 0:
    arange_plot(2, variables, 1.0)
    arange_plot(3, variables, 1.0)

    # hermes_eea_accum difference > ...:
    arange_plot(4, variables, 0.0000001)
    newcdf.close()
    mycdf.close()
