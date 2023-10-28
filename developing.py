import rebound
from utils import sim_logger, retry_on_exception

# sim_logger.setLevel("DEBUG")

# @retry_on_exception(n_retry=10, delay_s=1, debug=True)
# def fetch_solar_system_bodies(bodies, date):
#     sim = rebound.Simulation()
    
#     # Add bodies based on the given date
#     for body in bodies:
#         sim.add(body, date=date)
    
#     # Moving to the center of momentum frame
#     sim.move_to_com()
    
#     # Extract parameters and save to dict
#     data = {}
#     for i, p in enumerate(sim.particles):
#         body_data = {
#             "m": p.m,
#             "x": p.x, "y": p.y, "z": p.z,
#             "vx": p.vx, "vy": p.vy, "vz": p.vz
#         }
#         data[bodies[i]] = body_data  # Using the body name as the key

#     return data

# bodies = ["Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
# date = "2023-10-26 00:00:00"  # example date

# a = fetch_solar_system_bodies(bodies, date)
