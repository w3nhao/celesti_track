import rebound
import math

pi = math.pi

# Initialize a simulation
sim = rebound.Simulation()

# Set the units for the simulation
sim.units = ('yr', 'AU', 'Msun')

# Add celestial bodies to the simulation
# For this example, I'll add the Sun and a planet.
# You can loop over your collection of celestial bodies to add them.
sim.add(m=1.0)  # Sun
sim.add(m=0.001, x=1, y=0, z=0, vx=0, vy=2*pi, vz=0)  # Planet, for demonstration purposes

# Initialize arrays to store interval states
times = []
states = []

# Set the time span and interval for which you want to extract states
end_time = 10.0  # in years
interval = 0.1  # interval for extracting states

# Simulate and store interval states
current_time = 0
while current_time <= end_time:
    sim.integrate(current_time)
    
    # Extract states
    states.append([(particle.x, particle.y, particle.z, particle.vx, particle.vy, particle.vz) for particle in sim.particles])
    times.append(current_time)
    
    current_time += interval

# Now, the `times` array contains the time intervals and `states` array contains the state of the system at those times.
print(times)
print(states)
