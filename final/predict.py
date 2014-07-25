#!/usr/bin/env python


import turtle
import sys
from robot import *
from matrix import *
import random
from scipy.spatial.distance import euclidean


measurement_noise = 1


def smooth(path, weight_data=0.2, weight_smooth=0.5, tolerance=0.000001):

    # Make a deep copy of path into newpath
    newpath = [[0 for col in range(len(path[0]))] for row in range(len(path))]
    for i in range(len(path)):
        for j in range(len(path[0])):
            newpath[i][j] = path[i][j]

    delta = tolerance
    i = 0
    while delta >= tolerance:
        delta = 0.0
        i += 1
        for j in range(len(newpath[0])):
            last = newpath[i % len(path)][j]
            newpath[i % len(path)][j] += weight_data * (path[i % len(path)][j] - newpath[i % len(path)][j]) \
                + weight_smooth * (newpath[(i - 1) % len(path)][j] + newpath[(i + 1) % len(path)][j] -
                                   (2.0 * newpath[i % len(path)][j]))
            delta += abs(newpath[i % len(path)][j] - last)
    return newpath


#class PredictionModel(object):
    #'''Model of predicted robot'''

    #def __init__(self, num_particles=50, environment_constraints=None):
        #self.bot = robot(x, y)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    '''Rescale point. Function originally created by Adam Luchjenbroers'''
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def norm_factors_gen(centroid_data, max_x, max_y):
    orig_max_x = max([p[0] for p in centroid_data])
    orig_max_y = max([p[1] for p in centroid_data])
    orig_min_x = min([p[0] for p in centroid_data if p > 0])
    orig_min_y = min([p[1] for p in centroid_data if p > 0])
    for p in centroid_data:
        yield (translate(p[0], orig_min_x, orig_max_x, 0, max_x),
               translate(p[1], orig_min_y, orig_max_y, 0, max_y))


def setup_robot(color, start=(0,0), speed='normal'):
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


def visualize(centroid_data, max_x=800, max_y=600):
    turtle.setup(max_x, max_y)
    window = turtle.Screen()
    window.bgcolor('white')
    target_robot = setup_robot('blue', start, 'slowest')
    prediction_robot = setup_robot('blue', start, 'slowest')

    OTHER = None
    for x, y in norm_factors(centroid_data, max_x, max_y)
        if (x, y) == (-1, -1):
            continue
        #print x, y
        x -= base_x
        y = base_y - y
        #target_robot.setheading(hunter_bot.heading * 180 / pi)
        target_robot.goto(x * size_multiplier, y * size_multiplier)
        (x1, y1), OTHER = estimate_next_pos((x, y), OTHER)
        print OTHER
        prediction_robot.goto(x * size_multiplier, y * size_multiplier)
        prediction_robot.pendown()
        for i in range(5):
            (x1, y1), OTHER = estimate_next_pos((x1, y1), OTHER)
            prediction_robot.goto(x1 * size_multiplier, y1 * size_multiplier)
        prediction_robot.penup()

    turtle.done()


class BoundingBox(object):
    '''Defines constrains of the box'''

    def __init__(self, data):
        self.max_x = max([d[0] for d in data])
        self.min_x = min([d[0] for d in data])
        self.max_y = max([d[1] for d in data])
        self.min_y = min([d[1] for d in data])

    def __contains__(self, point):
        return all([
            point[0] >= self.min_x,
            point[0] <= self.max_x,
            point[1] >= self.min_y,
            point[1] <= self.max_y
        ])

    def __repr__(self):
        return ((self.min_x, self.max_x), (self.min_y, self.max_y))

    def __str__(self):
        return str(self.__repr__())


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
        measurement_noise)

    turning, turning_var = update(
        OTHER.get('turning', turning_est),
        OTHER.get('turning_var', 10.0),
        turning_est,
        measurement_noise)

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


with open(sys.argv[1]) as _file:
    centroid_data = eval(_file.read())

#bb = BoundingBox(centroid_data)
#print bb
#print (100, 100) in bb
#print (2000, 100) not in bb

#print min_x, max_x, min_y, max_y, len(centroid_data)

visualize(centroid_data)

# pymode:lint_ignore=W404,W402
