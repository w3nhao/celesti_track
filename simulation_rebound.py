from dataclasses import dataclass, field, asdict
from typing import Optional
import rebound
import hashlib
import numpy as np
import json
import os 

from utils import generate_sample_idxs

@dataclass
class SimConfig:
    celestial_init_states: dict
    dt: float = 1e-1
    units: tuple = ("yr", "AU", "Msun")
    integrator: str = "whfast"
    record_steps: int = 1
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
    sim = rebound.Simulation()
    sim.units = config.units
    sim.integrator = config.integrator
    sim.dt = config.dt
    
    for key, body in config.celestial_init_states.items():
        sim.add(**body)
    
    # Move to the center of mass frame
    sim.move_to_com()
    
    sim.automateSimulationArchive(config.filename, step=config.record_steps, deletefile=True)
    
    return sim

def run_simulation(sim, tmax):
    print(f"Running simulation for {tmax} years, each step is {sim.dt} years")
    print(f"Totally steps: {int(tmax/sim.dt) + 1} (including initial step)")
    sim.integrate(tmax)
    return sim

def particle_to_dict(particle: rebound.Particle):
    m = particle.m
    x, y, z = particle.xyz
    vx, vy, vz = particle.vxyz
    return {"m": m, "x": x, "y": y, "z": z, "vx": vx, "vy": vy, "vz": vz}

def stack_positions_or_velocities(data: dict, keys: list[str] = ["x", "y", "z"]):
    # name: celestial body name
    return np.stack([np.column_stack([data[name][k] for k in keys]) for name in list(data.keys())], axis=0)

def isolate_neptune(data: dict, name: str = "Neptune", keys: list[str] = ["x", "y", "z"]):
    neptune = data[name]
    rest = {k: v for k, v in data.items() if k != name}
    neptune_orbit = np.column_stack([neptune[k] for k in keys])
    rest_orbit = stack_positions_or_velocities(rest, keys)
    all_orbit = stack_positions_or_velocities(data, keys)
    return neptune_orbit, rest_orbits, all_orbits


if "__main__" == __name__:
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
    sim = run_simulation(sim, tmax=2e2)
    del sim

    sim_archive = rebound.SimulationArchive(config.filename)
    sample_idxs = generate_sample_idxs(n_samples, len(sim_archive), interval="equal")
    sample_snapshots = [sim_archive[i] for i in sample_idxs]

    celestial_names = [body for body in config.celestial_init_states.keys()]

    # Extract data from snapshots
    snapshots_data = [{name: particle_to_dict(body) for name, body in zip(celestial_names, snapshot.particles)} 
                    for snapshot in sample_snapshots]

    # Initialize data structures for positions and velocities
    celestial_positions = {name: {axis: [] for axis in position_axes} for name in celestial_names}
    celestial_velocities = {name: {axis: [] for axis in velocity_axes} for name in celestial_names}

    # Populate data structures with data from snapshots
    for snapshot in snapshots_data:
        for name in celestial_names:
            for p_axis, v_axis in zip(position_axes, velocity_axes):
                celestial_positions[name][p_axis].append(snapshot[name][p_axis])
                celestial_velocities[name][v_axis].append(snapshot[name][v_axis])

    # stack the positions and velocities as numpy arrays [nbodies, nsteps, axes]
    # orbit_velocities_np = stack_positions_or_velocities(celestial_velocities, velocity_axes)
    # orbit_positions_np = stack_positions_or_velocities(celestial_positions, position_axes)

    neptune_orbit, rest_orbits, all_orbits = isolate_neptune(celestial_positions)
    
    orbit_coord_metadata = {
        'celestial_names': celestial_names,
        'celestial_masses': celestial_masses,
        'simulation_config': asdict(config),
        'time_step': n_samples,
        'axes': position_axes,
    }

    # save 
    orbits_save_dir = os.path.join(os.getcwd(), "data/orbit_coordinates")
    os.makedirs(orbits_save_dir, exist_ok=True)
    orbits_save_path = os.path.join(orbits_save_dir, config.filename.split("/")[-1].replace(".bin", ".npz"))
    print(f"Saving orbits to {orbits_save_path}")
    np.savez_compressed(orbits_save_path, metadata=orbit_coord_metadata, neptune=neptune_orbit, rest=rest_orbits, all=all_orbits)
    
