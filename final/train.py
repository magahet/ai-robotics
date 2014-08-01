#!/usr/bin/env python

import sys
import argparse
from predict import *
from scipy import optimize


def evaluation_function(params, centroid_data, forcast, start, length):
    '''Wrapper around prediction and scoring functions for optimizer'''
    prediction = track_and_predict(centroid_data, forcast, start=start,
                                   length=length, params=params)
    end = min(len(prediction) + args.start + args.length, len(centroid_data))
    return mse(prediction, centroid_data[args.start + length:end])


def train(data, forcast, start, length):
    x0 = (0.1, 0.1, 0.1)
    args = (data, forcast, start, length)
    lower = (0.0001, 0.0001, 0.0001)
    upper = (10.0, 10.0, 1.0)
    res = optimize.anneal(evaluation_function, x0, args=args, lower=lower,
                          upper=upper)
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Train the hexbug tracker to find optimal parameters.')
    parser.add_argument('centroid_file', help='file containing hexbug centroid data')
    parser.add_argument('--forcast', '-f', type=int, default=0,
                        help='number of frames to predict')
    parser.add_argument('--start', '-s', type=int, default=0,
                        help='starting frame')
    parser.add_argument('--end', '-e', type=int, default=0,
                        help='ending frame')
    parser.add_argument('--length', '-l', type=int, default=0,
                        help='number of frames')

    args = parser.parse_args()
    with open(args.centroid_file) as _file:
        centroid_data = eval(_file.read())
    if args.length:
        length = args.length
    elif args.end and args.start:
        length = args.end - args.start
    else:
        length = len(centroid_data) - args.start
    optimal_params = train(centroid_data, args.forcast, args.start, length)
    params = list(optimal_params[0])
    print params

    print 'Optimal parameters for given data subset:'
    print 'Measurement error: {}'.format(params[0])
    print 'Process error: {}'.format(params[1])
    print 'Absorption factor: {}'.format(params[2])
    print
    print 'Run the following to perform tracking/prediction with these parameters:'
    print './predict.py -f {} -s {} -l {} -m {:.2f} -p {:.2f} -a {:.2f} -t {}'.format(
        args.forcast, args.start, args.length, params[0], params[1], params[2],
        args.centroid_file)


# pymode:lint_ignore=W404,W402
