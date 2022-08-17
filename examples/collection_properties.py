#!/usr/bin/env python3

from symcad.core import Assembly
from symcad.parts import Sphere

# Add a number of blue and green balls to an assembly
assembly = Assembly('BallContainer')
for idx in range(10):
   blue_ball = Sphere('BlueBall' + str(idx))
   green_ball = Sphere('GreenBall' + str(idx))
   assembly.add_part(blue_ball.set_geometry(radius_m=0.1),
                     ['blue_balls', 'even_balls' if idx % 2 == 0 else 'odd_balls'])
   assembly.add_part(green_ball.set_geometry(radius_m=0.1),
                     ['green_balls', 'even_balls' if idx % 2 == 0 else 'odd_balls'])

# Retrieve the center of gravity of only the green balls
print('\nGreen Balls CG_X: ', assembly.center_of_gravity(['green_balls']).x)

# Retrieve the center of gravity of only the even balls
print('\nEven Balls CG_X: ', assembly.center_of_gravity(['even_balls']).x)

# Retrieve the center of gravity of the green balls and the even balls
print('\nGreen and Even Balls CG_X: ', assembly.center_of_gravity(['green_balls', 'even_balls']).x)
