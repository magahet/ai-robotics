#!/usr/bin/env python

import turtle
import sys
from robot import *
from matrix import *
import random
from scipy.spatial.distance import euclidean
from utils import *
import argparse
import kalman

def setup_turtle(color, start=(0, 0), speed='normal'):
    robot = turtle.Turtle()
    robot.speed(speed)
    robot.color(color)
    robot.resizemode('user')
    robot.shapesize(0.3, 0.3, 0.3)
    robot.hideturtle()
    robot.penup()
    robot.goto(start[0], start[1])
    robot.showturtle()
    robot.pendown()
    return robot


def update_model_after_collision(model, bb, absorbtion_factor=0.1):
    x, y, dx, dy, d2x, d2y = model.state
    nx, ny = bb.bounce((x, y), absorbtion_factor * 2)
    if nx != x:
        x = nx
        dx = -dx * absorbtion_factor
        d2x = -d2x * absorbtion_factor
    if ny != y:
        y = ny
        dy = -dy * absorbtion_factor
        d2y = -d2y * absorbtion_factor
    model.set_state(x, y, dx, dy, d2x, d2y, reset_p=True)
    return model


def track_and_predict(centroid_data, forcast=0, visualize=False, start=0,
                      length=0, params=None):
    '''Draw hexbug path along with the predicted path'''
    if params is not None:
        measurement_noise, process_noise, absorbtion_factor = params
    else:
        measurement_noise = 0.1
        process_noise = 0.1
        absorbtion_factor = 0.1

    bb = BoundingBox(centroid_data)
    if start or length:
        end = start + length if length else -1
        data = centroid_data[start:end]
    if visualize:
        turtle.setworldcoordinates(bb.min_x, bb.max_y, bb.max_x, bb.min_y)
        window = turtle.Screen()
        window.bgcolor('white')

    started = False
    model = kalman.KalmanFilterModel2DCAM(rp=measurement_noise, sa=process_noise)
    max_v = [0.0, 0.0]
    for x, y in data:
        state = model.predict()
        if state is not None and (state[0], state[1]) not in bb:
            model = update_model_after_collision(model, bb, absorbtion_factor)
        if not started and visualize:
            target_robot = setup_turtle('blue', (x, y), 'fast')
            prediction_robot = setup_turtle('red', (x, y), 'fast')
            started = True

        if (x, y) != (-1, -1):
            model.update((x, y))
            if visualize:
                target_robot.goto(x, y)
        mx, my, mdx, mdy, _, _ = model.state
        max_v = [max(mdx, max_v[0]), max(mdy, max_v[1])]
        if visualize:
            prediction_robot.goto(mx, my)
    if visualize:
        target_robot.color('green')
    prediction = []
    for i in range(forcast):
        x, y, dx, dy, d2x, d2y = model.predict()
        if [dx, dy] > max_v:
            model.set_state(x, y, min(dx, max_v[0]), min(dy, max_v[1]), d2x, d2y)
        if (x, y) not in bb:
            model = update_model_after_collision(model, bb, absorbtion_factor)
        if visualize:
            if end + i < len(centroid_data) - 1:
                p = centroid_data[end + i]
                if p != [-1, -1]:
                    target_robot.goto(p[0], p[1])
            prediction_robot.goto(x, y)
        predicted_point = bb.trunc(model.state[:2])
        prediction.append(predicted_point)

    if visualize:
        turtle.done()
    return prediction


def mse(prediction, actual):
    sq_dist_sum = 0
    for i in range(len(prediction)):
        if actual[i] != [-1, -1]:
            sq_dist_sum += euclidean(prediction[i], actual[i]) ** 2
    return sqrt(sq_dist_sum)


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
    parser.add_argument('--length', '-l', type=int, default=0,
                        help='number of frames')
    parser.add_argument('--measurement_error', '-m', type=float, default=0.001,
                        help='measurement error')
    parser.add_argument('--process_error', '-p', type=float, default=0.001,
                        help='process error')
    parser.add_argument('--absorption_factor', '-a', type=float, default=0.001,
                        help='absorption factor')
    args = parser.parse_args()
    params = (args.measurement_error, args.process_error, args.absorption_factor)
    with open(args.centroid_file) as _file:
        centroid_data = eval(_file.read())
    if args.length:
        length = args.length
    elif args.end and args.start:
        length = args.end - args.start
    else:
        length = len(centroid_data) - args.start
    prediction = track_and_predict(centroid_data, args.forcast, args.turtle,
                                   args.start, length, params)
    print 'Prediction'
    print '##########'
    print prediction

    if length < len(centroid_data) - args.start:
        print
        print 'MSE:', mse(prediction,
                          centroid_data[args.start + length:min(len(prediction) + args.start + args.length,
                                                                len(centroid_data))])


# pymode:lint_ignore=W404,W402
