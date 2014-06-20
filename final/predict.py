#!/usr/bin/env python


import turtle
import time


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


def visualize(centroid_data):
    base_y = 500
    base_x = 600
    x, y = centroid_data.pop(0)
    x -= base_x
    y = base_y - y
    #For Visualization
    window = turtle.Screen()
    window.bgcolor('white')
    chaser_robot = turtle.Turtle()
    #chaser_robot.shape('circle')
    chaser_robot.color('blue')
    chaser_robot.resizemode('user')
    chaser_robot.shapesize(0.3, 0.3, 0.3)
    size_multiplier = 1  # change size of animation
    chaser_robot.hideturtle()
    chaser_robot.penup()
    chaser_robot.goto(x * size_multiplier, y * size_multiplier)
    chaser_robot.showturtle()
    chaser_robot.pendown()
    #End of Visualization

    for x, y in centroid_data:
        x -= base_x
        y = base_y - y
        print x, y
        #chaser_robot.setheading(hunter_bot.heading * 180 / pi)
        chaser_robot.goto(x * size_multiplier, y * size_multiplier)

    while True:
        time.sleep(1)


with open('centroid_data-20') as _file:
    centroid_data = [[int(t) for t in l.split(',')] for l in _file.readlines()]

max_x = max([d[0] for d in centroid_data])
min_x = min([d[0] for d in centroid_data])
max_y = max([d[1] for d in centroid_data])
min_y = min([d[1] for d in centroid_data])
print min_x, max_x, min_y, max_y, len(centroid_data)

visualize(smooth(centroid_data))
