import turtle


class Normalizer(object):

    def __init__(self, data, max_x, max_y):
        '''Find data range properties for x and y'''
        self.original_data = data[:]
        orig_min_x = min([p[0] for p in data if p > 0])
        orig_max_x = max([p[0] for p in data])
        orig_min_y = min([p[1] for p in data if p > 0])
        orig_max_y = max([p[1] for p in data])
        self._range = {
            'x': {
                'min': orig_min_x,
                'max': orig_max_x,
                'span': orig_max_x - orig_min_x,
                'tmax': max_x
            },
            'y': {
                'min': orig_min_y,
                'max': orig_max_y,
                'span': orig_max_y - orig_min_y,
                'tmax': max_y
            },
        }

    @property
    def data(self):
        '''Rescaled data'''
        for p in self.original_data:
            if p == [-1, -1]:
                yield p
            else:
                yield (self.translate(p[0], self._range['x']),
                       self.translate(p[1], self._range['y']))

    def translate(self, value, _range):
        '''Rescale point'''
        valueScaled = float(value - _range['min']) / float(_range['span'])
        return int(valueScaled * _range['tmax'])


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
