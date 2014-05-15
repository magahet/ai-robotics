import random


w = [random.random() for i in range(5)]

index = random.randrange(len(w))

b = 0

p3 = []

for i in range(len(w)):
    b += random.random() * 2 * max(w)
    while w[index] < b:
        b -= w[index]
        index += 1
        index %= len(w)
    else:
        p3.append(w[index])

print w
print p3
