import time
import rebound
from functools import wraps
import numpy as np
from .loggers import sim_logger_instance as sim_logger

DEFAULT_CELESTIALS = ["Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

def retry_on_exception(n_retry, delay_s, debug=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts <= n_retry:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if debug:
                        sim_logger.debug(f"Attempt {attempts} failed with error: {e}")
                    if attempts > n_retry:
                        # If max retries reached, raise the final exception
                        raise e
                    time.sleep(delay_s)
        return wrapper
    return decorator

@retry_on_exception(n_retry=10, delay_s=1, debug=True)
def fetch_solar_system_bodies(bodies=DEFAULT_CELESTIALS, date="2023-10-26 00:00:00", units=("AU", "yr", "Msun")):
    """ 
    Fetch the solar system bodies from rebound based on the given date.
    All bodies are added to the simulation and then moved to the center of momentum frame.
    The center of momentum frame is the frame in which the total momentum of the system is zero.
    
    Args:
        bodies (list): list of bodies to fetch 
        date (str): date to fetch the bodies from
        
    Returns:
        dict: dictionary containing the fetched bodies' parameters
        
    Example:
        solar_system_data = fetch_solar_system_bodies()
        
        print(solar_system_data)
    """
    sim = rebound.Simulation()
    
    sim_logger.info(f"Fetching bodies: {bodies}")
    sim_logger.info(f"Fetching bodies on date: {date}")
    
    # log the units of the simulation
    sim.units = units
    sim_logger.info(f"Units of the simulation: {sim.units}")
    sim_logger.info(f"Gravity constant of the simulation: {sim.G}")
    
    # Add bodies based on the given date
    for body in bodies:
        sim.add(body, date=date)
        
        # sim_logger.debug(f"Mass of {body}: {sim.particles[-1].m}")

    # # Moving to the center of momentum frame
    # sim.move_to_com()
    
    # Extract parameters and save to dict
    data = {}
    for i, p in enumerate(sim.particles):
        body_data = {
            "m": p.m,
            "x": p.x, "y": p.y, "z": p.z,
            "vx": p.vx, "vy": p.vy, "vz": p.vz
        }
        data[bodies[i]] = body_data  # Using the body name as the key
        
    return data

def generate_sample_idxs(n, total_steps, interval="equal"):
    if interval == "equal":
        step_size = (total_steps-1) // (n-1)
        idxs = np.arange(0, step_size*n, step_size)
    
    elif interval == "log":
        # Generate n-1 gaps that grow logarithmically, then find the cumulative sum
        gaps = np.logspace(0, np.log10(total_steps), n) - 1
        gaps = gaps / gaps.sum() * (total_steps - n) 
        idxs = np.insert(np.cumsum(gaps), 0, 0).astype(int)
    
    elif interval == "exp":
        # Generate n-1 gaps that grow exponentially
        base = (total_steps / n) ** (1/(n-1))
        gaps = base ** np.arange(n-1)
        gaps = gaps / gaps.sum() * (total_steps - n)
        idxs = np.insert(np.cumsum(gaps), 0, 0).astype(int)
    
    elif interval == "random":
        idxs = np.sort(np.random.choice(total_steps, n, replace=False))
    
    else:
        raise ValueError(f"Unknown interval type: {interval}")

    return idxs.tolist()