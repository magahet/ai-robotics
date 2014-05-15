colors = [['red', 'green', 'green', 'red', 'red'],
          ['red', 'red', 'green', 'red', 'red'],
          ['red', 'red', 'green', 'green', 'red'],
          ['red', 'red', 'red', 'red', 'red']]

measurements = ['green', 'green', 'green', 'green', 'green']


motions = [[0, 0], [0, 1], [1, 0], [1, 0], [0, 1]]

sensor_right = 0.7

p_move = 0.8


def show(p):
    for i in range(len(p)):
        print p[i]


def calculate():

    #DO NOT USE IMPORT
    #ENTER CODE BELOW HERE
    #ANY CODE ABOVE WILL CAUSE
    #HOMEWORK TO BE GRADED
    #INCORRECT

    def sense(p, Z):
        d = {
            True: sensor_right,
            False: 1 - sensor_right,
        }
        q = [[cell * d[Z == colors[i][j]] for j, cell in enumerate(
            row)] for i, row in enumerate(p)]
        alpha = sum([sum(row) for row in q])
        q = [[cell / alpha for cell in row] for row in q]
        return q

    def move(p, m):
        height = len(p)
        width = len(p[0])
        q = init(colors, 0)
        y, x = m
        for i in range(height):
            for j in range(width):
                q[i][j] = p[(i - y) % height][(
                    j - x) % width] * p_move + p[i][j] * (1 - p_move)
        return q

    def init(colors, fixed=None):
        if fixed is not None:
            p = fixed
        else:
            p = 1.0 / sum([len(l) for l in colors])
        return [[p for i in range(len(colors[0]))] for j in range(len(colors))]

    p = init(colors)

    for i in range(len(motions)):
        p = move(p, motions[i])
        p = sense(p, measurements[i])

    #Your probability array must be printed
    #with the following code.

    show(p)
    return p
