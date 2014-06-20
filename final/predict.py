#!/usr/bin/env python


import turtle


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


with open('centroid_data-20') as _file:
    centroid_data = [[int(t) for t in l.split(',')] for l in _file.readlines()]

bb = BoundingBox(centroid_data)
print bb
print (100, 100) in bb
print (2000, 100) not in bb

#print min_x, max_x, min_y, max_y, len(centroid_data)

#visualize(smooth(centroid_data))
