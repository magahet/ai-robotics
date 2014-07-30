#!/usr/bin/env python

import turtle
import sys
from robot import *
from matrix import *
import random
from scipy.spatial.distance import euclidean
from utils import *
import argparse
from kalman import KalmanFilterModel2D


MEASUREMENT_NOISE = pi / 2


def visualize(centroid_data, max_x=800, max_y=600, forcast=0):
    '''Draw hexbug path along with the predicted path'''
    #turtle.setup(max_x, max_y)
    #turtle.setworldcoordinates(0, max_y, max_x, 0)
    #bb = BoundingBox(centroid_data)
    bb = BoundingBox(((165, 84), (684, 420)))
    print bb
    turtle.setworldcoordinates(bb.min_x, bb.max_y, bb.max_x, bb.min_y)
    window = turtle.Screen()
    window.bgcolor('white')

    #OTHER = None
    #normalized_data = Normalizer(centroid_data, max_x, max_y)
    started = False
    model = KalmanFilterModel2D(measurement_noise=0.001)
    #for x, y in normalized_data.data:
    for x, y in centroid_data[-50:]:
        model.predict()
        if not started:
            target_robot = setup_turtle('blue', (x, y), 'slowest')
            prediction_robot = setup_turtle('red', (x, y), 'slowest')
            started = True

        if (x, y) != (-1, -1):
            model.update((x, y))
            target_robot.goto(x, y)
        mx, my, _, _ = model.state
        prediction_robot.goto(mx, my)
        print model.state
    for i in range(forcast):
        x, y, dx, dy = model.predict()
        if (x, y) not in bb:
            nx, ny = bb.bounce((x, y))
            if nx != x:
                x = nx
                dx = -dx
            if ny != y:
                y = ny
                dy = -dy
            model.set_state(x, y, dx, dy)
        prediction_robot.goto(x, y)
        print model.state

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
        if measurement != (-1, -1):
            measurements.append(measurement)
        return measurement, {'measurements': measurements}

    # use the magic of trig to get distance and turning estimates
    m0, m1 = measurements

    heading_est0 = bearing(m0, m1)
    if measurement == (-1, -1):
        distance_est = OTHER.get('distance', 0)
        heading_est1 = heading_est0 + OTHER.get('turning', 0)
        r = robot(m1[0], m1[1], heading_est1, OTHER.get('turning', 0), distance_est)
        r.move_in_circle()
        x, y = r.x, r.y
    else:
        distance_est = euclidean(m1, measurement)
        heading_est1 = bearing(m1, measurement)
        x, y = measurement
    turning_est = heading_est1 - heading_est0

    # handle edge case of crossing from quadrant 4 to 1
    if heading_est0 > 3 * (pi / 2) and heading_est1 < pi / 2:
        turning_est += (2 * pi)

    # use the magic of bayes to update posterior belief of distance and turning
    distance, distance_var = update(
        OTHER.get('distance', distance_est),
        OTHER.get('distance_var', MEASUREMENT_NOISE),
        distance_est,
        MEASUREMENT_NOISE / 10)

    turning, turning_var = update(
        OTHER.get('turning', turning_est),
        OTHER.get('turning_var', MEASUREMENT_NOISE),
        turning_est,
        MEASUREMENT_NOISE / 10)

    # setup a model robot and move it to make our prediction
    r = robot(x, y, heading_est1, turning, distance)
    r.move_in_circle()

    # save current model attributes into OTHER
    OTHER = {
        'measurements': [m1, (x, y)],
        'distance': distance,
        'distance_var': distance_var + MEASUREMENT_NOISE,
        'turning': turning,
        'turning_var': turning_var + MEASUREMENT_NOISE
    }
    print OTHER

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
