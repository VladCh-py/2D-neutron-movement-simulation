# 2D-neutron-movement-simulation

2d Monte-carlo Neutrons movement simulation.py allows you to simulate the motion of neutrons in a 2D space with three media:
1. environment - environment with absorption and scattering;
  2. reflector - an area with a large scattering cross-section*;
  3. vacuum -environment with negligible absorption and scattering coefficients.

Neutrons are born with a random position and a random direction inside a given medium.
When a neutron is born, its free path is generated (from the exponential law). The neutron moves in a straight line 
the entire free run. After that, the probability of possible outcomes is calculated (absorption/scattering
at a random angle relative to the previous movement) and the interaction is played out. During the program operation, the output is 
the motion of neutrons in media and a histogram showing the flow 
(calculated as the number of neutrons per unit area) of netrons along the abscissa axis.


*In this version, it is possible to use the reflector in a different way: If you uncomment the code pieces below, the neutron may reflect off the reflector.
absolutely elastic (while maintaining the equality of angles of incidence and reflection).

Folder "Pictures" contains screenshots of the program operation.
