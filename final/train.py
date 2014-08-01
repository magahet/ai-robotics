#!/usr/bin/env python
'''This module utilizes a randomized optimization engine to find good model
parameters for the tracking and prediction tool. Specifiably, it uses
simulated annealing with the tracking and prediction function as it's
evaluation function. It searches for an optimal balance of measurement and
process noise along with the absorption factor parameter. The result is the
set of these parameters that minimizes the L2 error between the prediction
and remaining centroid data points.'''


import sys
import argparse
from predict import *
from scipy import optimize


def evaluation_function(params, centroid_data, forecast, start, length):
    '''Wrapper around prediction and scoring functions for optimizer'''
    # Run the tracking and prediction function with the current set of
    # parameters.
    prediction = track_and_predict(centroid_data, forecast, start=start,
                                   length=length, params=params)

    # Return the L2 error between the predicted and actual points
    end = min(len(prediction) + args.start + args.length, len(centroid_data))
    return l2(prediction, centroid_data[args.start + length:end])


def train(data, forecast, start, length):
    '''Performs simulated annealing to find optimal parameters for the tracking
    and prediction tool'''

    # Set initial parameters for (measurement noise, process noise, absorption
    # factor).
    x0 = (0.1, 0.1, 0.1)

    # Set additional arguments required for the tracking and prediction
    # function.
    args = (data, forecast, start, length)

    # Set the lower and upper limits on the search space for each parameter.
    lower = (0.0001, 0.0001, 0.0001)
    upper = (10.0, 10.0, 1.0)

    # Perform the optimization algorithm and return the results
    res = optimize.anneal(evaluation_function, x0, args=args, lower=lower,
                          upper=upper)
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Train the hexbug tracker to find optimal parameters.')
    parser.add_argument('centroid_file', help='file containing hexbug centroid data')
    parser.add_argument('--forecast', '-f', type=int, default=0,
                        help='number of frames to predict')
    parser.add_argument('--start', '-s', type=int, default=0,
                        help='starting frame')
    parser.add_argument('--end', '-e', type=int, default=0,
                        help='ending frame')
    parser.add_argument('--length', '-l', type=int, default=0,
                        help='number of frames')

    args = parser.parse_args()

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

    # Perform optimization process and  print out optimal parameters
    optimal_params = train(centroid_data, args.forecast, args.start, length)
    params = list(optimal_params[0])

    print 'Optimal parameters for given data subset:'
    print 'Measurement error: {}'.format(params[0])
    print 'Process error: {}'.format(params[1])
    print 'Absorption factor: {}'.format(params[2])
    print
    print 'Run the following to perform tracking/prediction with these parameters:'
    print './predict.py -f {} -s {} -l {} -m {:.2f} -p {:.2f} -a {:.2f} -t {}'.format(
        args.forecast, args.start, args.length, params[0], params[1], params[2],
        args.centroid_file)


# pymode:lint_ignore=W404,W402
