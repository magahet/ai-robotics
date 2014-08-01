class BoundingBox(object):
    '''Defines constraints of the box'''

    def __init__(self, data):
        self.max_x = max([d[0] for d in data if d[0] > 0])
        self.min_x = min([d[0] for d in data if d[0] > 0])
        self.max_y = max([d[1] for d in data if d[1] > 0])
        self.min_y = min([d[1] for d in data if d[1] > 0])

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

    def trunc(self, point):
        x = min(self.max_x, point[0])
        x = max(self.min_x, x)
        y = min(self.max_y, point[1])
        y = max(self.min_y, y)
        return (int(x), int(y))

    def bounce(self, point, absorption_factor=0.1):
        x, y = point
        if point[0] < self.min_x:
            x = absorption_factor * (self.min_x - point[0]) + self.min_x
        elif point[0] > self.max_x:
            x = absorption_factor * (self.max_x - point[0]) + self.max_x
        if point[1] < self.min_y:
            y = absorption_factor * (self.min_y - point[1]) + self.min_y
        elif point[1] > self.max_y:
            y = absorption_factor * (self.max_y - point[1]) + self.max_y
        return (x, y)
