#!/usr/bin/env python

import turtle
import sys
from robot import *
from matrix import *
import random
from scipy.spatial.distance import euclidean
from utils import *
import argparse


MEASUREMENT_NOISE = 1


def visualize(centroid_data, max_x=800, max_y=600, forcast=0):
    '''Draw hexbug path along with the predicted path'''
    turtle.setup(max_x, max_y)
    turtle.setworldcoordinates(0, max_y, max_x, 0)
    window = turtle.Screen()
    window.bgcolor('white')

    OTHER = None
    normalized_data = Normalizer(centroid_data, max_x, max_y)
    started = False
    for x, y in normalized_data.data:
        if not started:
            target_robot = setup_turtle('blue', (x, y), 'slowest')
            prediction_robot = setup_turtle('red', (x, y), 'slowest')
            started = True

        if (x, y) == (-1, -1):
            continue
        #print (x, y)
        target_robot.goto(x, y)
        (x1, y1), OTHER = estimate_next_pos((x, y), OTHER)
        prediction_robot.goto(x, y)
        prediction_robot.pendown()
        for i in range(forcast):
            (x1, y1), OTHER = estimate_next_pos((x1, y1), OTHER)
            prediction_robot.goto(x1, y1)
        prediction_robot.penup()

    turtle.done()


def estimate_next_pos(measurement, OTHER=None):
    """Estimate the next position based on noisy (x, y) measurements."""

    def update(mean1, var1, mean2, var2):
        '''Calculate the posterior belief of a Gaussian random variable'''
        new_mean = (1.0 / (var1 + var2)) * (var2 * mean1 + var1 * mean2)
        new_var = 1.0 / ((1.0 / var1) + (1.0 / var2))
        return [new_mean, new_var]

    def bearing(p1, p2):
        '''Calculate bearing based on two points'''
        a = atan2(p2[1] - p1[1], p2[0] - p1[0])
        a += 2 * pi if a < 0.0 else 0.0
        return a

    OTHER = {} if not OTHER else OTHER
    measurements = OTHER.get('measurements', [])

    # not enough data to make an estimate
    if len(measurements) < 2:
        measurements.append(measurement)
        return measurement, {'measurements': measurements}

    # use the magic of trig to get distance and turning estimates
    m0, m1 = measurements
    distance_est = euclidean(m1, measurement)
    heading_est0 = bearing(m0, m1)
    heading_est1 = bearing(m1, measurement)
    turning_est = heading_est1 - heading_est0

    # handle edge case of crossing from quadrant 4 to 1
    if heading_est0 > 3 * (pi / 2) and heading_est1 < pi / 2:
        turning_est += (2 * pi)

    x, y = measurement

    # use the magic of bayes to update posterior belief of distance and turning
    distance, distance_var = update(
        OTHER.get('distance', distance_est),
        OTHER.get('distance_var', 10.0),
        distance_est,
        MEASUREMENT_NOISE)

    turning, turning_var = update(
        OTHER.get('turning', turning_est),
        OTHER.get('turning_var', 10.0),
        turning_est,
        MEASUREMENT_NOISE)
    print 'turning:', turning, turning_var

    # setup a model robot and move it to make our prediction
    r = robot(x, y, heading_est1, turning, distance)
    r.move_in_circle()

    # save current model attributes into OTHER
    OTHER = {
        'measurements': [m1, measurement],
        'distance': distance,
        'distance_var': distance_var,
        'turning': turning,
        'turning_var': turning_var
    }

    # return our predicted robot position
    return (r.x, r.y), OTHER


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predict the hexbug path.')
    parser.add_argument('centroid_file', help='file containing hexbug centroid data')
    parser.add_argument('--forcast', '-f', type=int, default=0,
                        help='number of frames to predict')
    parser.add_argument('--size_x', '-x', type=int, default=800,
                        help='horizontal size of visualization')
    parser.add_argument('--size_y', '-y', type=int, default=600,
                        help='vertical size of visualization')

    args = parser.parse_args()
    with open(args.centroid_file) as _file:
        centroid_data = eval(_file.read())
    visualize(centroid_data, max_x=args.size_x, max_y=args.size_y,
              forcast=args.forcast)


# pymode:lint_ignore=W404,W402
