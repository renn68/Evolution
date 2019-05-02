from noise import pnoise2
import random
random.seed()
octaves = random.random()
# octaves = (random.random() * 0.5) + 0.5
freq = 16.0 * octaves
a = []
for y in range(30):
    a.append([])
    for x in range(40):
        n = int(pnoise2(x / freq, y / freq, 1) * 10 + 3)
        if n >= 1:
            n = 1
        else:
            n = 0
        a[y].append(n)

for y in range(30):
    print(a[y])
