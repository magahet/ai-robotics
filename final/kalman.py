# Fill in the matrices P, F, H, R and I at the bottom
#
# This question requires NO CODING, just fill in the
# matrices where indicated. Please do not delete or modify
# any provided code OR comments. Good luck!

from math import *
from matrix import *


########################################

class KalmanFilterModel2D(object):

    def __init__(self, a=0.1, dt=1, initial_err=1000, measurement_noise=0.1):
        # initial state (location and velocity)
        self.x = None
        self.u = matrix([[0.], [0.], [0.], [0.]])  # external motion
        self.P = matrix([[0, 0, 0, 0],
                         [0, 0, 0, 0],
                         [0, 0, initial_err, 0],
                         [0, 0, 0, initial_err]])
        self.F = matrix([[1, 0, dt, 0],
                         [0, 1, 0, dt],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])
        t2 = (dt ** 2)
        t3 = (dt ** 3) / 2
        t4 = (dt ** 4) / 4
        Q = matrix([[t4, 0, t3, 0],
                    [0, t4, 0, t3],
                    [t3, 0, t2, 0],
                    [0, t3, 0, t2]])
        self.Q = Q * a
        self.H = matrix([[1, 0, 0, 0],
                         [0, 1, 0, 0]])
        self.R = matrix([[measurement_noise, 0],
                         [0, measurement_noise]])
        self.I = matrix([[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])

    def set_state(self, x, y, dx, dy):
        self.x = matrix([[x], [y], [dx], [dy]])

    def predict(self):
        if self.x is None:
            return None
        self.x = (self.F * self.x) + self.u
        self.P = self.F * self.P * self.F.transpose() + self.Q
        return self.state

    def update(self, measurement):
        if self.x is None:
            self.x = matrix([[measurement[0]], [measurement[1]], [0.], [0.]])
            return
        Z = matrix([measurement])
        y = Z.transpose() - (self.H * self.x)
        S = self.H * self.P * self.H.transpose() + self.R
        K = self.P * self.H.transpose() * S.inverse()
        self.x = self.x + (K * y)
        self.P = (self.I - (K * self.H)) * self.P

    @property
    def state(self):
        return tuple([self.x.value[i][0] for i in range(self.x.dimx)])

    def __str__(self):
        if self.x is None:
            return 'None'
        return str(self.x.value)


if __name__ == '__main__':
    measurements = [[5., 10.], [6., 8.], [7., 6.], [8., 4.], [9., 2.], [10., 0.]]
    measurements = [[5., 10.], [6., 8.], [-1, -1], [8., 4.], [-1, -1], [10., 0.]]
    initial_xy = [4., 12.]
    forcast = 5

    model = KalmanFilterModel2D()
    for m in measurements:
        model.predict()
        if m != [-1, -1]:
            model.update(m)
        print 'model:', model

    for i in range(forcast):
        model.predict()
        print 'model:', model


# pymode:lint_ignore=W404,W402
