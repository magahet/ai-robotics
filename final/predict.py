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


def track_and_predict(centroid_data, forcast=0, visualize=False, start=0, end=0):
    '''Draw hexbug path along with the predicted path'''
    bb = BoundingBox(centroid_data)
    if start or end:
        end = end if end else -1
        data = centroid_data[start:end]
    if visualize:
        turtle.setworldcoordinates(bb.min_x, bb.max_y, bb.max_x, bb.min_y)
        window = turtle.Screen()
        window.bgcolor('white')

    started = False
    model = KalmanFilterModel2D(a=0.1, measurement_noise=1)
    for x, y in data:
        model.predict()
        if not started and visualize:
            target_robot = setup_turtle('blue', (x, y), 'fast')
            prediction_robot = setup_turtle('red', (x, y), 'fast')
            started = True

        if (x, y) != (-1, -1):
            model.update((x, y))
            if visualize:
                target_robot.goto(x, y)
        mx, my, _, _ = model.state
        if visualize:
            prediction_robot.goto(mx, my)
    target_robot.color('green')
    prediction = []
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
        if visualize:
            if end + i < len(centroid_data) - 1:
                p = centroid_data[end + i]
                print p
                if p != [-1, -1]:
                    target_robot.goto(p[0], p[1])
            prediction_robot.goto(x, y)
        prediction.append([int(i) for i in model.state[:2]])

    if visualize:
        turtle.done()
    return prediction


def mse(prediction, actual):
    print len(prediction), len(actual)
    return sqrt(sum([euclidean(prediction[i], actual[i]) ** 2 for
                     i in range(len(prediction))]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predict the hexbug path.')
    parser.add_argument('centroid_file', help='file containing hexbug centroid data')
    parser.add_argument('--forcast', '-f', type=int, default=0,
                        help='number of frames to predict')
    parser.add_argument('--turtle', '-t', action='store_true',
                        help='enable turtle visualization')
    parser.add_argument('--start', '-s', type=int, default=0,
                        help='starting frame')
    parser.add_argument('--end', '-e', type=int, default=0,
                        help='ending frame')

    args = parser.parse_args()
    with open(args.centroid_file) as _file:
        centroid_data = eval(_file.read())
    prediction = track_and_predict(centroid_data, args.forcast, args.turtle,
                                   args.start, args.end)
    print 'Prediction'
    print '##########'
    print prediction

    if args.end < len(centroid_data):
        print
        print 'MSE:', mse(prediction,
                          centroid_data[args.end:min(len(prediction) + args.end,
                                                     len(centroid_data) - args.end)])


# pymode:lint_ignore=W404,W402
