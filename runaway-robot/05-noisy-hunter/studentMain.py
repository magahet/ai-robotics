# ----------
# Part Five
#
# This time, the sensor measurements from the runaway Traxbot will be VERY
# noisy (about twice the target's stepsize). You will use this noisy stream
# of measurements to localize and catch the target.
#
# ----------
# YOUR JOB
#
# Complete the next_move function, similar to how you did last time.
#
# ----------
# GRADING
#
# Same as part 3 and 4. Again, try to catch the target in as few steps as possible.

from robot import *
from math import *
from matrix import *
import random


def next_move(hunter_position, hunter_heading, target_measurement, max_distance, OTHER=None):
    # This function will be called after each time the target moves.

    # The OTHER variable is a place for you to store any historical information about
    # the progress of the hunt (or maybe some localization information). Your return format
    # must be as follows in order to be graded properly.

    OTHER = {} if not OTHER else OTHER

    # use the estimate_next_pos function to build the target robot model
    target_position, model_data = estimate_next_pos(
        target_measurement, OTHER.get('model'))

    distance_to_target = distance_between(hunter_position, target_position)

    # move to target if close enough
    if distance_to_target <= max_distance:
        distance = min(max_distance, distance_to_target)
        turning = get_heading(
            hunter_position, target_position) - hunter_heading
    # project targets position 2 additional time steps out and move there
    else:
        target_position2, model_data2 = estimate_next_pos(
            target_position, model_data)
        target_position3, model_data3 = estimate_next_pos(
            target_position2, model_data2)
        distance = min(
            max_distance, distance_between(hunter_position, target_position3))
        turning = get_heading(
            hunter_position, target_position3) - hunter_heading

    # store model data
    OTHER = {'model': model_data}

    #return turning, distance, OTHER
    return turning, distance, OTHER


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
    measurement_noise = 2.0 * distance_est if distance_est else 10.0
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


def distance_between(point1, point2):
    """Computes distance between point1 and point2. Points are (x, y) pairs."""
    x1, y1 = point1
    x2, y2 = point2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def demo_grading(hunter_bot, target_bot, next_move_fcn, OTHER=None):
    """Returns True if your next_move_fcn successfully guides the hunter_bot
    to the target_bot. This function is here to help you understand how we
    will grade your submission."""
    max_distance = 0.97 * \
        target_bot.distance  # 0.98 is an example. It will change.
    separation_tolerance = 0.02 * target_bot.distance  # hunter must be within 0.02 step size to catch target
    caught = False
    ctr = 0
    #For Visualization
    import turtle
    window = turtle.Screen()
    window.bgcolor('white')
    chaser_robot = turtle.Turtle()
    chaser_robot.shape('arrow')
    chaser_robot.color('blue')
    chaser_robot.resizemode('user')
    chaser_robot.shapesize(0.3, 0.3, 0.3)
    broken_robot = turtle.Turtle()
    broken_robot.shape('turtle')
    broken_robot.color('green')
    broken_robot.resizemode('user')
    broken_robot.shapesize(0.3, 0.3, 0.3)
    size_multiplier = 15.0  # change size of animation
    chaser_robot.hideturtle()
    chaser_robot.penup()
    chaser_robot.goto(
        hunter_bot.x * size_multiplier, hunter_bot.y * size_multiplier - 100)
    chaser_robot.showturtle()
    broken_robot.hideturtle()
    broken_robot.penup()
    broken_robot.goto(
        target_bot.x * size_multiplier, target_bot.y * size_multiplier - 100)
    broken_robot.showturtle()
    measuredbroken_robot = turtle.Turtle()
    measuredbroken_robot.shape('circle')
    measuredbroken_robot.color('red')
    measuredbroken_robot.penup()
    measuredbroken_robot.resizemode('user')
    measuredbroken_robot.shapesize(0.1, 0.1, 0.1)
    broken_robot.pendown()
    chaser_robot.pendown()
    #End of Visualization
    # We will use your next_move_fcn until we catch the target or time expires.
    while not caught and ctr < 1000:
        # Check to see if the hunter has caught the target.
        hunter_position = (hunter_bot.x, hunter_bot.y)
        target_position = (target_bot.x, target_bot.y)
        separation = distance_between(hunter_position, target_position)
        if separation < separation_tolerance:
            print "You got it right! It took you ", ctr, " steps to catch the target."
            caught = True

        # The target broadcasts its noisy measurement
        target_measurement = target_bot.sense()

        # This is where YOUR function will be called.
        turning, distance, OTHER = next_move_fcn(hunter_position, hunter_bot.heading, target_measurement, max_distance, OTHER)

        # Don't try to move faster than allowed!
        if distance > max_distance:
            distance = max_distance

        # We move the hunter according to your instructions
        hunter_bot.move(turning, distance)

        # The target continues its (nearly) circular motion.
        target_bot.move_in_circle()
        #Visualize it
        measuredbroken_robot.setheading(target_bot.heading * 180 / pi)
        measuredbroken_robot.goto(target_measurement[0] * size_multiplier, target_measurement[1] * size_multiplier - 100)
        measuredbroken_robot.stamp()
        broken_robot.setheading(target_bot.heading * 180 / pi)
        broken_robot.goto(target_bot.x * size_multiplier,
                          target_bot.y * size_multiplier - 100)
        chaser_robot.setheading(hunter_bot.heading * 180 / pi)
        chaser_robot.goto(hunter_bot.x * size_multiplier,
                          hunter_bot.y * size_multiplier - 100)
        #End of visualization
        ctr += 1
        if ctr >= 1000:
            print "It took too many steps to catch the target."
    return caught


'''
def demo_grading(hunter_bot, target_bot, next_move_fcn, OTHER=None):
    """Returns True if your next_move_fcn successfully guides the hunter_bot
    to the target_bot. This function is here to help you understand how we
    will grade your submission."""
    max_distance = 0.97 * \
        target_bot.distance  # 0.97 is an example. It will change.
    separation_tolerance = 0.02 * target_bot.distance  # hunter must be within 0.02 step size to catch target
    caught = False
    ctr = 0

    # We will use your next_move_fcn until we catch the target or time expires.
    while not caught and ctr < 1000:

        # Check to see if the hunter has caught the target.
        hunter_position = (hunter_bot.x, hunter_bot.y)
        target_position = (target_bot.x, target_bot.y)
        separation = distance_between(hunter_position, target_position)
        if separation < separation_tolerance:
            print "You got it right! It took you ", ctr, " steps to catch the target."
            caught = True

        # The target broadcasts its noisy measurement
        target_measurement = target_bot.sense()

        # This is where YOUR function will be called.
        turning, distance, OTHER = next_move_fcn(hunter_position, hunter_bot.heading, target_measurement, max_distance, OTHER)

        # Don't try to move faster than allowed!
        if distance > max_distance:
            distance = max_distance

        # We move the hunter according to your instructions
        hunter_bot.move(turning, distance)

        # The target continues its (nearly) circular motion.
        target_bot.move_in_circle()

        ctr += 1
        if ctr >= 1000:
            print "It took too many steps to catch the target."
    return caught
'''


def angle_trunc(a):
    """This maps all angles to a domain of [-pi, pi]"""
    while a < 0.0:
        a += pi * 2
    return ((a + pi) % (pi * 2)) - pi


def get_heading(hunter_position, target_position):
    """Returns the angle, in radians, between the target and hunter positions"""
    hunter_x, hunter_y = hunter_position
    target_x, target_y = target_position
    heading = atan2(target_y - hunter_y, target_x - hunter_x)
    heading = angle_trunc(heading)
    return heading


def naive_next_move(hunter_position, hunter_heading, target_measurement, max_distance, OTHER):
    """This strategy always tries to steer the hunter directly towards where the target last
    said it was and then moves forwards at full speed. This strategy also keeps track of all
    the target measurements, hunter positions, and hunter headings over time, but it doesn't
    do anything with that information."""
    if not OTHER:  # first time calling this function, set up my OTHER variables.
        measurements = [target_measurement]
        hunter_positions = [hunter_position]
        hunter_headings = [hunter_heading]
        OTHER = (measurements, hunter_positions, hunter_headings)
                 # now I can keep track of history
    else:  # not the first time, update my history
        OTHER[0].append(target_measurement)
        OTHER[1].append(hunter_position)
        OTHER[2].append(hunter_heading)
        measurements, hunter_positions, hunter_headings = OTHER  # now I can always refer to these variables

    heading_to_target = get_heading(hunter_position, target_measurement)
    heading_difference = heading_to_target - hunter_heading
    turning = heading_difference  # turn towards the target
    distance = max_distance  # full speed ahead!
    return turning, distance, OTHER


target = robot(0.0, 10.0, 0.0, 2 * pi / 30, 1.5)
measurement_noise = 2.0 * target.distance  # VERY NOISY!!
target.set_noise(0.0, 0.0, measurement_noise)

hunter = robot(-10.0, -10.0, 0.0)

print demo_grading(hunter, target, next_move)

# pymode:lint_ignore=W404,W402
