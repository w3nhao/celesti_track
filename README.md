# N-Body Celestials Simulation

### Description

This is a simple N-body simulation of Celestials. 




#### Remaining Questions
1. 2D vs 3D

2. System invariance and consistency of state  
Regardless of how and where the bodies are initialized, the states of these initialized points should also be consistent.
- potential solution:
    - center of mass frame
    - fixing the initial positions of the bodies
    - use invariant encodings of the state

3. Collision detection

#### Celestial Bodies
1. Properties
    - mass (m)
    - position (x, y, z)
    - velocity (vx, vy, vz)

2. Default Units
    - \( G = 1 \)
    - \( M_{\text{planet}} = 1 \)
    - \( M_{\text{star}} = 1 \)

    A one star and one planet system is used as the default system.  

2. Solar-sys like Units
    - \( Yr = 365.25 \) days (Julian)
    - \( AU = 1.495978707 \times 10^{11} \) m
    - \( M_{\text{sun}} = 1.98855 \times 10^{30} \) kg
    - \( G = 4 \pi^2 \left( \frac{AU^3}{M_{\text{sun}} \times Yr^2} \right) = 39.47841760435743 \)

    [Details explaination](https://rebound.readthedocs.io/en/latest/ipython_examples/Units/) about the units and gravitational constant.


##### Compared with data in Hamiltonian NN
1. Properies (State)
    - mass (m)
    - position (x, y)
    - velocity (vx, vy)

2. Energy
    - kinetic energy
    - potential energy

3. Default Units
    - \( G = 1 \)
    - \( M_{\text{celestial}} = 1 \)

4. Return Values
    - Position and Velocity of the bodies in time steps (x, y, vx, vy)
    - Derivatives of the position and velocity of the bodies in time steps (dx/dt, dy/dt, dvx/dt, dvy/dt)
    - Energy of the system in time steps (e = potential + kinetic)

### Additional Notes

A more advanced implementation: Using the [Rebound](https://rebound.readthedocs.io/en/latest/) library to calculate the gravitational interactions between the bodies. The simulation is done in 3D, but the output is a 2D projection of the orbits on the XY plane.   

#### Celestial Bodies
1. Properties
    - mass (m)
    - position (x, y, z)
    - velocity (vx, vy, vz)