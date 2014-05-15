import math
import numpy


def calc(mu, var, x):
    return (1 / math.sqrt(2 * math.pi * var)) * numpy.exp((-0.5 * (x - mu) ** 2) / var)


def mu(m, g, s, r):
    return (1.0 / (s + r)) * (r * m + s * g)


def s(m, g, s, r):
    return 1.0 / ((1.0 / s) + (1.0 / r))
