import math
import numpy as np
from integrators import EulerIntegrator, RK4Integrator
from dataclasses import dataclass, field, asdict
from typing import Optional
import hashlib
import numpy as np
import os 

class Particle:
    def __init__(self, simulation, m, x, y, z, vx, vy, vz, name=None):
        self.name = name
        self.sim = simulation   
        self.m = m
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz

    def update_position(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def update_velocity(self, vx, vy, vz):
        self.vx, self.vy, self.vz = vx, vy, vz
        
        
class Simulator:
    
    G_AU_Msun_Yr = 4 * math.pi ** 2  # Gravitational constant in AU^3/(Msun*year^2)
    G_standard = 6.67430e-11  # Gravitational constant in m^3/(kg*s^2)
    
    def __init__(self, dt, integrator='RK4', use_standard_G=False):
        self.t = 0
        self.dt = dt
        self.particles = []
        self.use_standard_G = use_standard_G
        self.G = self.G_standard if use_standard_G else self.G_AU_Msun_Yr
        self.integrator = self._create_integrator(integrator)
        self.states = {'positions': [], 'velocities': []}


    # Factory function to create integrators
    def _create_integrator(self, name):
        if name == 'RK4':
            return RK4Integrator(self)
        elif name == 'Euler':
            return EulerIntegrator(self)
        else:
            raise ValueError(f"Unknown integrator: {name}")
    
    def add(self, m, x, y, z, vx, vy, vz, name=None):
        # Add a new particle to the simulation
        particle = Particle(self, m, x, y, z, vx, vy, vz, name)
        self.particles.append(particle)
        
    def move_to_com(self):
        # Move the particles to the center of mass frame
        # Calculate the center of mass of the system
        total_mass = sum([p.m for p in self.particles])
        x = sum([p.m * p.x for p in self.particles]) / total_mass
        y = sum([p.m * p.y for p in self.particles]) / total_mass
        z = sum([p.m * p.z for p in self.particles]) / total_mass
        
        for particle in self.particles:
            particle.x -= x
            particle.y -= y
            particle.z -= z
            
    def run(self, tmax):
        # Run the simulation for a given amount of time
        particle_masses = np.array([p.m for p in self.particles])
        
        if self.t == 0:
            initial_positions = np.array([[p.x, p.y, p.z] for p in self.particles])
            initial_velocities = np.array([[p.vx, p.vy, p.vz] for p in self.particles])
            self.states['positions'].append(initial_positions)
            self.states['velocities'].append(initial_velocities)
        
        while self.t < tmax:
            last_positions, last_velocities = self.states['positions'][-1], self.states['velocities'][-1]
            
            new_positions, new_velocities = self.integrator.step(self.dt, last_positions, last_velocities, particle_masses)
            self.t += self.dt
            
            self.states['positions'].append(new_positions)
            self.states['velocities'].append(new_velocities)
        
        return self.states
            
    def reset(self):
        # Reset the simulation to the initial state
        self.t = 0
        self.states = {'positions': [], 'velocities': []}
            
    def sample(self, idxs: list):
        return np.array([self.states['positions'][i] for i in idxs]), np.array([self.states['velocities'][i] for i in idxs])
        
    def status(self):
        # Print the status of the simulation
        pass

@dataclass
class SimConfig:
    celestial_init_states: dict
    dt: float = 1e-3
    integrator: str = "RK4"
    record_steps: int = 1
    move_to_com: bool = True
    use_standard_G: bool = False
    theory: Optional[str] = field(default=None)
    filename: Optional[str] = field(default=None)
    
    def __post_init__(self):
        default_svae_dir = os.path.join(os.getcwd(), "data/simulations")
        os.makedirs(default_svae_dir, exist_ok=True)
        
        if not self.filename:
            setting_str = str(asdict(self))
            hash_obj = hashlib.sha256(setting_str.encode())
            self.filename = os.path.join(default_svae_dir, f"sim_{hash_obj.hexdigest()}.bin")

def init_simulation(config: SimConfig):
    sim = Simulator(config.dt, integrator=config.integrator)
    
    for key, body in config.celestial_init_states.items():
        sim.add(**body, name=key)
    
    sim.move_to_com() if config.move_to_com else None
    
    return sim

def save_simulation(filename, simulation_config, states, end_time):
    np.savez_compressed(filename, simulation_config=simulation_config, states=states, end_time=end_time)

def load_simulation(filename):
    # Load the simulation configuration and state from a file
    npzfile = np.load(filename, allow_pickle=True)
    simulation_config = npzfile['simulation_config'].item()    
    sim = init_simulation(simulation_config)

    states, end_time = npzfile['states'].item(), npzfile['end_time']
    sim.t, sim.states = states, end_time
    
    return sim

def plot_states(states):
    # Plot the positions and velocities of the particles in the simulation
    pass

if __name__ == '__main__':
    from utils import generate_sample_idxs
    import json
    
    # new_celestials = fetch_solar_system_bodies()
    # json_str = json.dumps(new_celestials, ensure_ascii=False, indent=4, separators=(',', ':'), sort_keys=False, default=lambda x: format(x, ".15g"))
    # with open("solar_system_data.json", "w") as file:
    #     file.write(json_str) 
    
    n_samples = 64
    position_axes = ["x", "y", "z"]
    velocity_axes = ["vx", "vy", "vz"]

    celestial_init_states = json.load(open("solar_system_data.json", "r"))
    celestial_masses = [body["m"] for body in celestial_init_states.values()]
    celestial_names = [body for body in celestial_init_states.keys()]

    config = SimConfig(celestial_init_states, dt=0.1, record_steps=1)
    sim = init_simulation(config)
    
    sim_archive = sim.run(1000)["positions"]

    sample_idxs = generate_sample_idxs(n_samples, len(sim_archive), interval="equal")
    sample_snapshots = [sim_archive[i] for i in sample_idxs]

    celestial_names = [body for body in config.celestial_init_states.keys()]

    orbits = np.stack([sample_snapshots[:, i, :] for i in range(len(celestial_names))], axis=1)

    orbit_coord_metadata = {
        'celestial_names': celestial_names,
        'celestial_masses': celestial_masses,
        'simulation_config': asdict(config),
        'time_step': n_samples,
        'axes': position_axes,
    }
    
    # save orbits
        
    # save simulation

