import numpy as np
#import matplotlib.pyplot as plt


# def generate_s_curve_velocity_profile(total_pulses, steps):
#     """
#     Generate an S-curve velocity profile based on encoder position.
    
#     :param total_pulses: Total encoder pulses corresponding to the desired movement.
#     :param steps: Number of discrete steps to divide the total movement into.
#     :return: Arrays of encoder positions and the corresponding velocity.
#     """
#     positions = np.linspace(0, total_pulses, steps)
#     # S-curve formula adjusted for position-based profile
#     velocity = np.gradient(10 * (positions/total_pulses)**3 - 15 * (positions/total_pulses)**4 + 6 * (positions/total_pulses)**5)
    
#     return positions, velocity


# def adjust_pwm_based_on_position(current_position, positions, velocities, max_pwm_frequency):
#     """
#     Adjust PWM frequency based on the current encoder position using the velocity profile.
    
#     :param current_position: Current encoder position.
#     :param positions: Array of encoder positions for the velocity profile.
#     :param velocities: Array of desired velocities at each position.
#     :param max_pwm_frequency: Maximum PWM frequency for the motor.
#     :return: PWM frequency to set.
#     """
#     # Find the closest position in the profile and get the corresponding velocity
#     closest_idx = np.abs(positions - current_position).argmin()
#     desired_velocity = velocities[closest_idx]
    
#     # Placeholder for conversion from velocity to PWM frequency
#     # This needs to be calibrated for your specific hardware
#     pwm_frequency = max_pwm_frequency * desired_velocity / np.max(velocities)
    
#     return pwm_frequency


# def generate_s_curve_with_ramp_fraction(total_pulses, steps, ramp_fraction):
#     """
#     Generate an S-curve velocity profile with specified ramp fractions for acceleration and deceleration.
    
#     :param total_pulses: Total encoder pulses corresponding to the desired movement.
#     :param steps: Number of discrete steps to divide the total movement into.
#     :param ramp_fraction: Fraction of the total profile duration dedicated to each of the ramp phases (acceleration and deceleration).
#     :return: Arrays of encoder positions and the corresponding velocity.
#     """
#     positions = np.linspace(0, total_pulses, steps)
    
#     # Define the acceleration and deceleration points based on the ramp fraction
#     acc_end = total_pulses * ramp_fraction
#     dec_start = total_pulses * (1 - ramp_fraction)
    
#     # Generate the velocity profile
#     velocities = np.zeros_like(positions)
#     for i, pos in enumerate(positions):
#         if pos < acc_end:  # Acceleration phase
#             velocities[i] = (pos / acc_end)**2
#         elif pos > dec_start:  # Deceleration phase
#             velocities[i] = ((total_pulses - pos) / (total_pulses - dec_start))**2
#         else:  # Constant velocity phase
#             velocities[i] = 1
    
#     return positions, velocities


# def generate_five_phase_s_curve(total_steps, ramp_up_fraction, constant_fraction, ramp_down_fraction):
#     """
#     Generate a five-phase S-curve profile.
    
#     :param total_steps: Total steps for the movement.
#     :param ramp_up_fraction: Fraction of total steps for each ramp-up phase.
#     :param constant_fraction: Fraction of total steps for the constant velocity phase.
#     :param ramp_down_fraction: Fraction of total steps for each ramp-down phase.
#     :return: Arrays of steps and the corresponding velocities.
#     """
#     # Calculate phase lengths in steps
#     ramp_up_steps = int(total_steps * ramp_up_fraction)
#     constant_steps = int(total_steps * constant_fraction)
#     ramp_down_steps = int(total_steps * ramp_down_fraction)

#     # Ensure total is consistent
#     total_phase_steps = 2 * ramp_up_steps + constant_steps + 2 * ramp_down_steps
#     if total_phase_steps > total_steps:
#         # Adjust if total exceeds the planned steps (simple handling for rounding issues)
#         constant_steps -= (total_phase_steps - total_steps)

#     # Initialize arrays
#     velocities = np.zeros(total_steps)
#     steps = np.arange(total_steps)
    
#     # Phase 1 & 2: Ramp-up
#     for step in range(ramp_up_steps):
#         velocities[step] = (step / ramp_up_steps)**2  # Quadratic ramp-up
    
#     # Adjust phase 2 ramp-up to start from end of phase 1
#     start_velocity = velocities[ramp_up_steps-1]
#     for step in range(ramp_up_steps, 2*ramp_up_steps):
#         velocities[step] = start_velocity + ((step-ramp_up_steps) / ramp_up_steps)**2 * (1 - start_velocity)

#     # Phase 3: Constant velocity
#     velocities[2*ramp_up_steps:2*ramp_up_steps+constant_steps] = 1
    
#     # Phase 4 & 5: Ramp-down
#     for step in range(ramp_down_steps):
#         velocities[2*ramp_up_steps+constant_steps+step] = 1 - ((step / ramp_down_steps)**2)  # Quadratic ramp-down from full to intermediate
    
#     # Adjust phase 5 ramp-down to end at 0 velocity
#     end_velocity = velocities[2*ramp_up_steps+constant_steps+ramp_down_steps-1]
#     for step in range(ramp_down_steps, 2*ramp_down_steps):
#         velocities[2*ramp_up_steps+constant_steps+step] = end_velocity * (1 - (step / ramp_down_steps)**2)

#     return steps, velocities


def adjust_pwm_based_on_position(current_position, positions, velocities):
    """
    Adjust PWM frequency based on the current encoder position using the velocity profile,
    ensuring the PWM frequency never drops below a minimum value.
    
    :param current_position: Current encoder position.
    :param positions: Array of encoder positions for the velocity profile.
    :param velocities: Array of desired velocities at each position.
    :param max_pwm_frequency: Maximum PWM frequency for the motor.
    :param min_pwm_frequency: Minimum PWM frequency to ensure motor starts moving.
    :return: PWM frequency to set, with consideration for the minimum value.
    """
    # Find the closest position in the profile and get the corresponding velocity
    closest_idx = np.abs(positions - current_position).argmin()
    desired_pwm = velocities[closest_idx]
    
    # Convert the desired velocity to a PWM frequency
    # This is a placeholder for the conversion logic, which depends on specific hardware characteristics
    # pwm_frequency = max_pwm_frequency * desired_velocity / np.max(velocities)
    
    # Ensure the PWM frequency does not fall below the minimum value
    # pwm_frequency = max(pwm_frequency, min_pwm_frequency)
    
    return desired_pwm


def scale_velocity_profile(velocities, min_pwm_frequency, max_pwm_frequency):
    """
    Scale the entire S-curve velocity profile to fit between the minimum and maximum PWM frequencies.
    
    :param velocities: The array of desired velocities from the S-curve profile.
    :param min_pwm_frequency: The minimum PWM frequency for the motor.
    :param max_pwm_frequency: The maximum PWM frequency for the motor.
    :return: Scaled velocities corresponding to PWM frequencies.
    """
    # Normalize velocities to range from 0 to 1
    normalized_velocities = (velocities - np.min(velocities)) / (np.max(velocities) - np.min(velocities))
    
    # Scale normalized velocities to fit between min and max PWM frequencies
    scaled_pwm = min_pwm_frequency + (max_pwm_frequency - min_pwm_frequency) * normalized_velocities
    
    return scaled_pwm


def generate_s_curve(steps, jm: float = 0.1, v0: float = 0):
    """
    Generate an S-curve trajectory with specified acceleration, steady, and total times.

    :param accel_time: Time duration for the acceleration phase.
    :param steady_time: Time duration for the steady (constant velocity) phase.
    :param total_time: Total time duration of the motion.
    :param steps: Number of discrete steps for the trajectory generation.
    :return: Time and acceleration arrays for the S-curve.
    """
    all_steps = np.linspace(1, steps, steps)
    concave_steps = int(steps/2)
    convex_steps = int(steps - concave_steps)

    ass = (jm * steps) / 2
    
    concave_steps = np.linspace(1, concave_steps, concave_steps)
    concave_velocities = v0 + (jm * (concave_steps)**2)/2

    convex_steps = np.linspace(1, convex_steps, convex_steps)
    vh = concave_velocities[-1]
    convex_velocities = vh + (ass * convex_steps) - (jm * (convex_steps)**2)/2

    steps = np.append(concave_steps, convex_steps)
    velocities = np.append(concave_velocities, convex_velocities)

    vels_norm = (velocities-np.min(velocities))/(np.max(velocities)-np.min(velocities))

    return all_steps, vels_norm


def generate_s_curve_profile(
        total_steps: int, 
        accel_frac: float = 0.2, 
        jm: float = 0.1,
        v0: float = 0):
    """
    Generate an S-curve profile based on steps, jerk, and acceleration.
    
    :param steps: Number of steps for the profile.
    :param jm: Maximum jerk.
    :param as_: Maximum acceleration at the inflection point.
    :param total_distance: Total distance for the motion.
    :return: Velocity profile as a numpy array.
    """
    # total_steps = np.linspace(1, total_steps, total_steps)
    accel_steps = int(round(total_steps * accel_frac))
    constant_steps = total_steps - (2 * accel_steps) 
    total_steps = np.linspace(1, total_steps, total_steps)
    # constant_steps = total_steps - (2 * accel_steps) 

    s_curve_accel_steps, s_curve_accel_vels = generate_s_curve(steps=accel_steps, jm=jm, v0=v0)
    s_curve_decel_vels = s_curve_accel_vels[::-1]

    # constant_steps = total_steps - (2 * accel_steps) 
    constant_steps = np.linspace(1, constant_steps, constant_steps)
    constant_vels = np.full((constant_steps.size), s_curve_accel_vels.max())

    vels = np.append(s_curve_accel_vels, constant_vels)
    vels = np.append(vels, s_curve_decel_vels)

    return total_steps, vels


def generate_scaled_s_curve(
        total_steps: int,
        min_pwm_frequency: int = 0,
        max_pwm_frequency: int = 100, 
        accel_fraction: float = 0.2, 
        jm: float = 0.1,
        v0: float = 0):
    try:
        steps, vels = generate_s_curve_profile(
            total_steps=total_steps,
            accel_frac=accel_fraction,
            jm=jm,
            v0=v0)
        
        scaled_vels = scale_velocity_profile(
            velocities=vels, 
            min_pwm_frequency=min_pwm_frequency, 
            max_pwm_frequency=max_pwm_frequency)
    except:
        steps = np.linspace(1, total_steps, total_steps)
        scaled_vels = np.full((steps.size), min_pwm_frequency)

    return steps, scaled_vels

def test():
    steps, vels = generate_scaled_s_curve(total_steps=5, min_pwm_frequency=50)
    # vels = scale_velocity_profile(velocities=vels, min_pwm_frequency=50, max_pwm_frequency=400)

    plt.plot(steps, vels)
    plt.xlabel('Steps')
    plt.ylabel('Speed')
    plt.title('S-Curve Velocity Profile')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    test()
