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
    distance_est = distance_between(m1, measurement)
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
    #For Visualization
    import turtle  # You need to run this locally to use the turtle module
    window = turtle.Screen()
    window.bgcolor('white')
    size_multiplier = 25.0  # change Size of animation
    broken_robot = turtle.Turtle()
    broken_robot.shape('turtle')
    broken_robot.color('green')
    broken_robot.resizemode('user')
    broken_robot.shapesize(0.1, 0.1, 0.1)
    measured_broken_robot = turtle.Turtle()
    measured_broken_robot.shape('circle')
    measured_broken_robot.color('red')
    measured_broken_robot.resizemode('user')
    measured_broken_robot.shapesize(0.1, 0.1, 0.1)
    prediction = turtle.Turtle()
    prediction.shape('arrow')
    prediction.color('blue')
    prediction.resizemode('user')
    prediction.shapesize(0.1, 0.1, 0.1)
    prediction.penup()
    broken_robot.penup()
    measured_broken_robot.penup()
    #End of Visualization
    while not localized and ctr <= 1000:
        ctr += 1
        measurement = target_bot.sense()
        position_guess, OTHER = estimate_next_pos_fcn(measurement, OTHER)
        target_bot.move_in_circle()
        true_position = (target_bot.x, target_bot.y)
        error = distance_between(position_guess, true_position)
        #print target_bot.turning, OTHER.get('turning', 0)
        if error <= distance_tolerance:
            print "You got it right! It took you ", ctr, " steps to localize."
            localized = True
        if ctr == 1000:
            print "Sorry, it took you too many steps to localize the target."
        #More Visualization
        measured_broken_robot.setheading(target_bot.heading * 180 / pi)
        measured_broken_robot.goto(measurement[0] * size_multiplier,
                                   measurement[1] * size_multiplier - 200)
        measured_broken_robot.stamp()
        broken_robot.setheading(target_bot.heading * 180 / pi)
        broken_robot.goto(target_bot.x * size_multiplier,
                          target_bot.y * size_multiplier - 200)
        broken_robot.stamp()
        prediction.setheading(target_bot.heading * 180 / pi)
        prediction.goto(position_guess[0] * size_multiplier,
                        position_guess[1] * size_multiplier - 200)
        prediction.stamp()
        #End of Visualization
    return localized


'''
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
        #print 'true:', target_bot.heading
        print true_position, position_guess, error - distance_tolerance
        if error <= distance_tolerance:
            print "You got it right! It took you ", ctr, " steps to localize."
            localized = True
        if ctr == 5000:
            print "Sorry, it took you too many steps to localize the target."
    return localized
'''

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
