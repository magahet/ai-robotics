N = 5
p = [1.0 / N for i in range(N)]
print p

w = ['green', 'green', 'red', 'green', 'red']


moves = 2
sense_error = 0.1

d = {
    True: 1 - sense_error,
    False: sense_error,
}

np = [d[w[i] == 'red'] * p[i] for i in range(len(p))]
s = sum(np)
p = [i / s for i in np]
print p
    
pp = [0] + p[:-1]
pp[-1] += p[-1]

p = pp[:]

print p
print sum([p[i] for i in range(len(p)) if w[i] == 'red'])