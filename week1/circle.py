# -*- coding: utf-8 -*-
from math import pi

try:
    r = int(input('Please enter the radius of the circle: '))
    print(r * r * pi)
except ValueError as e:
    print('Please a number!!!')
