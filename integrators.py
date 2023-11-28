from abc import ABC, abstractmethod
import numba as nb
import numpy as np

# # # purely numpy implementation for acceleration calculation
def numpy_calc_acceleration(self, positions, masses, G):
    r_vec = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
    r_mag = np.linalg.norm(r_vec, axis=2)
    r_mag_with_inf = np.where(r_mag == 0, np.inf, r_mag)
    r_hat = np.divide(r_vec, r_mag_with_inf[:, :, np.newaxis], out=np.zeros_like(r_vec), where=r_mag_with_inf[:, :, np.newaxis] != 0)
    
    force_magnitudes = G * masses[np.newaxis, :] * masses[:, np.newaxis] / r_mag_with_inf**2
    np.fill_diagonal(force_magnitudes, 0)
    force_vectors = force_magnitudes[:, :, np.newaxis] * r_hat
    total_forces = np.sum(force_vectors, axis=1)
    acc = total_forces / masses[:, np.newaxis]
    
    return acc

# # # numba implementation for acceleration calculation
@nb.jit(nopython=True)
def calc_acceleration(positions, masses, G):
    n = len(masses)
    acc = np.zeros_like(positions)
    for i in range(n):
        for j in range(n):
            if i != j:
                r_vec = positions[j] - positions[i]
                r_mag = np.sqrt(r_vec[0]**2 + r_vec[1]**2 + r_vec[2]**2)
                r_hat = r_vec / r_mag
                force_magnitude = G * masses[i] * masses[j] / r_mag**2
                acc[i] += force_magnitude * r_hat / masses[i]
    return acc

class Integrator(ABC):
    
    @abstractmethod
    def step(self, particles):
        raise NotImplementedError
    
# Concrete RK4 integrator
class RK4Integrator(Integrator):
    def __init__(self, sim):
        self.sim = sim
        self.G = sim.G

    
    def step(self, dt, positions, velocities, masses):
        # check all params dtype as float64
        assert positions.dtype == velocities.dtype == masses.dtype == np.float64, "All params must be float64"
        
        k1_vel = calc_acceleration(positions, masses, self.G)
        k1_pos = velocities

        next_pos = positions + 0.5 * dt * k1_pos
        next_vel = velocities + 0.5 * dt * k1_vel
        k2_vel = calc_acceleration(next_pos, masses, self.G)
        k2_pos = next_vel

        next_pos = positions + 0.5 * dt * k2_pos
        next_vel = velocities + 0.5 * dt * k2_vel
        k3_vel = calc_acceleration(next_pos, masses, self.G)
        k3_pos = next_vel

        next_pos = positions + dt * k3_pos
        next_vel = velocities + dt * k3_vel
        k4_vel = calc_acceleration(next_pos, masses, self.G)
        k4_pos = next_vel

        new_positions = positions + (dt / 6.0) * (k1_pos + 2.0 * k2_pos + 2.0 * k3_pos + k4_pos)
        new_velocities = velocities + (dt / 6.0) * (k1_vel + 2.0 * k2_vel + 2.0 * k3_vel + k4_vel)

        return new_positions, new_velocities

# Concrete Euler integrator
class EulerIntegrator(Integrator):
    def __init__(self, sim):
        self.sim = sim
        self.G = sim.G
            
    def step(self, dt, positions, velocities, masses):
        assert positions.dtype == velocities.dtype == masses.dtype == np.float64, "All params must be float64"
        
        new_velocities = velocities + dt * calc_acceleration(positions, masses, self.G)
        new_positions = positions + dt * new_velocities
        return new_positions, new_velocities

# WHFast integrator
class WHFastIntegrator(Integrator):
    def __init__(self, sim):
        self.sim = sim
        self.G = sim.G

    def step(self, dt, positions, velocities, masses):
        pass


# Factory function to create integrators
def create_integrator(name, sim):
    if name == 'RK4':
        return RK4Integrator(sim)
    elif name == 'Euler':
        return EulerIntegrator(sim)
    elif name == 'WHFast':
        pass
    else:
        raise ValueError(f"Unknown integrator: {name}")