import numpy as np
# import matplotlib.pyplot as plt


def generate_s_curve_velocity_profile(total_pulses, steps):
    """
    Generate an S-curve velocity profile based on encoder position.
    
    :param total_pulses: Total encoder pulses corresponding to the desired movement.
    :param steps: Number of discrete steps to divide the total movement into.
    :return: Arrays of encoder positions and the corresponding velocity.
    """
    positions = np.linspace(0, total_pulses, steps)
    # S-curve formula adjusted for position-based profile
    velocity = np.gradient(10 * (positions/total_pulses)**3 - 15 * (positions/total_pulses)**4 + 6 * (positions/total_pulses)**5)
    
    return positions, velocity


def adjust_pwm_based_on_position(current_position, positions, velocities, max_pwm_frequency):
    """
    Adjust PWM frequency based on the current encoder position using the velocity profile.
    
    :param current_position: Current encoder position.
    :param positions: Array of encoder positions for the velocity profile.
    :param velocities: Array of desired velocities at each position.
    :param max_pwm_frequency: Maximum PWM frequency for the motor.
    :return: PWM frequency to set.
    """
    # Find the closest position in the profile and get the corresponding velocity
    closest_idx = np.abs(positions - current_position).argmin()
    desired_velocity = velocities[closest_idx]
    
    # Placeholder for conversion from velocity to PWM frequency
    # This needs to be calibrated for your specific hardware
    pwm_frequency = max_pwm_frequency * desired_velocity / np.max(velocities)
    
    return pwm_frequency


def adjust_pwm_based_on_position(current_position, positions, velocities, max_pwm_frequency, min_pwm_frequency):
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
    desired_velocity = velocities[closest_idx]
    
    # Convert the desired velocity to a PWM frequency
    # This is a placeholder for the conversion logic, which depends on specific hardware characteristics
    pwm_frequency = max_pwm_frequency * desired_velocity / np.max(velocities)
    
    # Ensure the PWM frequency does not fall below the minimum value
    pwm_frequency = max(pwm_frequency, min_pwm_frequency)
    
    return pwm_frequency


def test():
    pos, vel = generate_s_curve_velocity_profile(total_pulses=1000, steps=100)
    pwms = np.array([])

    for val in pos:
        new_pwm = adjust_pwm_based_on_position(
            current_position=val,
            positions=pos,
            velocities=vel,
            max_pwm_frequency=500
        )
        pwms = np.append([pwms], [new_pwm])
    print(f"new pwm freq: {new_pwm}")

    # plt.plot(pos, pwms)
    # plt.xlabel('Steps')
    # plt.ylabel('Speed')
    # plt.title('S-Curve Velocity Profile')
    # plt.grid(True)
    # plt.show()


if __name__ == '__main__':
    test()
