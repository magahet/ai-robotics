# ----------
# Part Two
#
# Now we'll make the scenario a bit more realistic. Now Traxbot's
# sensor measurements are a bit noisy (though its motions are still
# completetly noise-free and it still moves in an almost-circle).
# You'll have to write a function that takes as input the next
# noisy (x, y) sensor measurement and outputs the best guess
# for the robot's next position.
#
# ----------
# YOUR JOB
#
# Complete the function estimate_next_pos. You will be considered
# correct if your estimate is within 0.01 stepsizes of Traxbot's next
# true position.
#
# ----------
# GRADING
#
# We will make repeated calls to your estimate_next_pos function. After
# each call, we will compare your estimated position to the robot's true
# position. As soon as you are within 0.01 stepsizes of the true position,
# you will be marked correct and we will tell you how many steps it took
# before your function successfully located the target bot.

# These import steps give you access to libraries which you may (or may
# not) want to use.
from robot import *  # Check the robot.py tab to see how this works.
from math import *
from matrix import *  # Check the matrix.py tab to see how this works.
import random

# This is the function you have to write. Note that measurement is a
# single (x, y) point. This function will have to be called multiple
# times before you have enough information to accurately predict the
# next position. The OTHER variable that your function returns will be
# passed back to your function the next time it is called. You can use
# this to keep track of important information over time.


def estimate_next_pos(measurement, OTHER=None):
    """Estimate the next (x, y) position of the wandering Traxbot
    based on noisy (x, y) measurements."""
    #print measurement, OTHER

    def update(mean1, var1, mean2, var2):
        new_mean = (1.0 / (var1 + var2)) * (var2 * mean1 + var1 * mean2)
        new_var = 1.0 / ((1.0 / var1) + (1.0 / var2))
        return [new_mean, new_var]

    # You must return xy_estimate (x, y), and OTHER (even if it is None)
    # in this order for grading purposes.

    OTHER = {} if not OTHER else OTHER
    measurements = OTHER.get('measurements', [])

    if len(measurements) < 2:
        measurements.append(measurement)
        return measurement, {'measurements': measurements}

    m0, m1 = measurements
    o = distance_between(m0, measurement) / 2.0
    distance_est = distance_between(m1, measurement)
    r = o / distance_est if o < distance_est else distance_est / o
    turning_est = pi - 2 * asin(r)
    x, y = measurement
    x0, y0 = m1
    bearing_est = atan2((y - y0), (x - x0))

    distance, distance_var = update(
        OTHER.get('distance', 0.0),
        OTHER.get('distance_var', 10000.0),
        distance_est,
        measurement_noise)

    turning, turning_var = update(
        OTHER.get('turning', 0.0),
        OTHER.get('turning_var', 10000.0),
        turning_est,
        measurement_noise)

    r = robot(x, y, bearing_est, turning, distance)
    #print 'guess0:', r.x, r.y, r.heading, r.turning, r.distance
    r.move_in_circle()
    #print 'guess:', r.x, r.y, r.heading, r.turning, r.distance

    #print turning, turning_var, distance, distance_var

    OTHER = {
        'measurements': [m1, measurement],
        'distance': distance,
        'distance_var': distance_var,
        'turning': turning,
        'turning_var': turning_var,
    }

    return (r.x, r.y), OTHER

# A helper function you may find useful.


def distance_between(point1, point2):
    """Computes distance between point1 and point2. Points are (x, y) pairs."""
    x1, y1 = point1
    x2, y2 = point2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# This is here to give you a sense for how we will be running and grading
# your code. Note that the OTHER variable allows you to store any
# information that you want.


def demo_grading(estimate_next_pos_fcn, target_bot, OTHER=None):
    localized = False
    distance_tolerance = 0.01 * target_bot.distance
    ctr = 0
    # if you haven't localized the target bot, make a guess about the next
    # position, then we move the bot and compare your guess to the true
    # next position. When you are close enough, we stop checking.
    while not localized and ctr <= 5000:
        ctr += 1
        measurement = target_bot.sense()
        position_guess, OTHER = estimate_next_pos_fcn(measurement, OTHER)
        target_bot.move_in_circle()
        true_position = (target_bot.x, target_bot.y)
        error = distance_between(position_guess, true_position)
        print true_position, position_guess, error - distance_tolerance
        if error <= distance_tolerance:
            print "You got it right! It took you ", ctr, " steps to localize."
            localized = True
        if ctr == 5000:
            print "Sorry, it took you too many steps to localize the target."
    return localized

# This is a demo for what a strategy could look like. This one isn't very good.


def naive_next_pos(measurement, OTHER=None):
    """This strategy records the first reported position of the target and
    assumes that eventually the target bot will eventually return to that
    position, so it always guesses that the first position will be the next."""
    if not OTHER:  # this is the first measurement
        OTHER = measurement
    xy_estimate = OTHER
    return xy_estimate, OTHER

# This is how we create a target bot. Check the robot.py file to understand
# How the robot class behaves.
test_target = robot(2.1, 4.3, 0.5, 2 * pi / 34.0, 1.5)
measurement_noise = 0.05 * test_target.distance
test_target.set_noise(0.0, 0.0, measurement_noise)

demo_grading(estimate_next_pos, test_target)

# pymode:lint_ignore=W404,W402
