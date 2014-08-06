#!/usr/bin/env python
'''This module provides functions for tracking and predicting the hexbug's path
given a centroid data file. It can be called as a command line utility and will
output the specified number of predicted steps. If the length or end parameters
are set, the output will include the L2 error between the prediction and the
remaining points. If the turtle parameter is set, a visualization will be
rendered of the actual, tracked, and predicted paths.'''


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
    '''Establishes settings for a turtle for the visualization'''
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


def update_model_after_collision(model, bb, absorption_factor=0.1):
    '''Modifies the model state based on the constraints of the bounding box'''
    x, y, dx, dy, d2x, d2y = model.state
    # bb.bounce will determine the new position based on the physics of
    # bouncing of the wall. The absorption_factor reduces the distance traveled
    # after the impact.
    nx, ny = bb.bounce((x, y), absorption_factor * 2)
    if nx != x:
        x = nx
        dx = -dx * absorption_factor
        d2x = -d2x * absorption_factor
    if ny != y:
        y = ny
        dy = -dy * absorption_factor
        d2y = -d2y * absorption_factor
    model.set_state(x, y, dx, dy, d2x, d2y, reset_p=True)
    return model


def track_and_predict(centroid_data, forecast=0, visualize=False, start=0,
                      length=0, params=None):
    '''Track and then predict the hexbug path based on provided centroid data.
    The forecast parameter controls how many prediction points are generated.
    visualize will enable the turtle drawing. start and length determine what
    subset of the centroid data to perform tracking on. params is a tuple of
    measurement noise, process noise, and absorption factor. These control the
    behavior of the tracking/prediction model.'''
    if params is not None:
        measurement_noise, process_noise, absorption_factor = params
    else:
        # Default parameters
        measurement_noise = 0.1
        process_noise = 0.1
        absorption_factor = 0.1

    # The bounding box constrains the model to the max and min of x and y as
    # observed in the centroid data.
    bb = BoundingBox(centroid_data)

    # Take a subset of the data to track.
    if start or length:
        end = start + length if length else -1
        data = centroid_data[start:end]

    # Setup the turtle environment for the visualization
    if visualize:
        turtle.setworldcoordinates(bb.min_x, bb.max_y, bb.max_x, bb.min_y)
        window = turtle.Screen()
        window.bgcolor('white')

    # Initialize the Kalman filter model with the given measurement and process
    # noise.
    model = kalman.KalmanFilterModel2DCAM(rp=measurement_noise, sa=process_noise)

    # Observe the maximum velocity of the model during tracking. This is used
    # during the prediction phase to constrain the model to the max observed
    # velocity.
    max_v = [0.0, 0.0]

    # Tracking phase processes the centroid data to train the model.
    started = False
    for x, y in data:
        # Kalman prediction phase
        state = model.predict()

        # Determine if the predicted position is outside the established
        # bounding box. If so, utilize the physics heuristics to predict the
        # model's actions after the collision.
        if state is not None and (state[0], state[1]) not in bb:
            model = update_model_after_collision(model, bb, absorption_factor)

        # Setup the initial position of the target and prediction turtles.
        if not started and visualize:
            target_robot = setup_turtle('blue', (x, y), 'fast')
            prediction_robot = setup_turtle('red', (x, y), 'fast')
            started = True

        # If the centroid data is valid, perform the Kalman update phase and
        # update the target turtle position.
        if (x, y) != (-1, -1):
            model.update((x, y))
            if visualize:
                target_robot.goto(x, y)

        # Update the max observed velocity from the current model state.
        mx, my, mdx, mdy, _, _ = model.state
        max_v = [max(mdx, max_v[0]), max(mdy, max_v[1])]

        # Update the prediction turtle position
        if visualize:
            prediction_robot.goto(mx, my)

    # Change the target turtle color during the prediction phase to make it
    # clear in the visualization that the predicted path is no longer receiving
    # position updates from the centroid data. This is only valid if the subset
    # of data being tracked is less then the complete centroid data.
    if visualize:
        target_robot.color('green')

    # Prediction phase.
    prediction = []
    for i in range(forecast):
        # Apply the process transition to the last state.
        x, y, dx, dy, d2x, d2y = model.predict()

        # Constrain the model velocity to the max observed during tracking.
        if [dx, dy] > max_v:
            model.set_state(x, y, min(dx, max_v[0]), min(dy, max_v[1]), d2x, d2y)

        # Constrain the model based on the limits of the bounding box. Apply
        # physics heuristics to the state if a collision occurs.
        if (x, y) not in bb:
            model = update_model_after_collision(model, bb, absorption_factor)

        # Update the turtle visualization to show the predicted path, and if
        # available, the actual path from the remaining centroid data.
        if visualize:
            if end + i < len(centroid_data) - 1:
                p = centroid_data[end + i]
                if p != [-1, -1]:
                    target_robot.goto(p[0], p[1])
            prediction_robot.goto(x, y)

        # Apply an explicit bounding box constraint to the returned prediction.
        # This is necessary for running the randomized optimization engine, as
        # it will attempt to use model parameters that allow the physics model
        # to overshoot the bounding box.
        predicted_point = bb.trunc(model.state[:2])
        prediction.append(list(predicted_point))

    # Pause after completing the visualization until the turtle window is
    # closed.
    if visualize:
        turtle.done()

    # Return the list of predicted points.
    return prediction


def l2(prediction, actual):
    '''Computes the L2 error of the predicted and actual points'''
    sq_dist_sum = 0
    for i in range(len(prediction)):
        if actual[i] != [-1, -1]:
            sq_dist_sum += euclidean(prediction[i], actual[i]) ** 2
    return sqrt(sq_dist_sum)


def save_data(path, data):
    '''Save prediction points to file'''
    with open(path, 'w') as _file:
        _file.write(str(data).replace('],', '],\n'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predict the hexbug path.')
    parser.add_argument('centroid_file', help='file containing hexbug centroid data')
    parser.add_argument('--forecast', '-f', type=int, default=0,
                        help='number of frames to predict')
    parser.add_argument('--output', '-o', help='file to output predictions')
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

    # Read centroid data from file.
    with open(args.centroid_file) as _file:
        centroid_data = eval(_file.read())

    # Determine subset of data to track.
    if args.length:
        length = args.length
    elif args.end and args.start:
        length = args.end - args.start
    else:
        length = len(centroid_data) - args.start

    # Perform tracking and prediction.
    prediction = track_and_predict(centroid_data, args.forecast, args.turtle,
                                   args.start, length, params)

    # Save predictions to a file
    if args.output:
        save_data(args.output, prediction)

    # Print results.
    print 'Prediction'
    print '##########'
    print prediction

    # Print L2 error if the prediction points overlap remaining centroid data.
    if length < len(centroid_data) - args.start:
        end = min(len(prediction) + args.start + args.length, len(centroid_data))
        print
        print 'L2:', l2(prediction, centroid_data[args.start + length:end])


# pymode:lint_ignore=W404,W402
