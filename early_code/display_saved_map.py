import numpy as np
import matplotlib.pyplot as plt
import math
import parameters

# map parameters
RES = parameters.resolution
WIDTH = parameters.width
HEIGHT = parameters.height
LFT = int(0 - parameters.orig_x_pos)
RGT = int(parameters.width - parameters.orig_x_pos)
BOT = int(0 - parameters.orig_y_pos)
TOP = int(parameters.height - parameters.orig_y_pos)

def p_from_log_odds(l):
    return 1.0 - (1.0 / (1.0 + np.exp(l)))

def plot_map(np_map):
    # Convert log-odds back to probability for visualization
    prob_map = p_from_log_odds(saved_map)
    plt.imshow(prob_map.T, cmap="Greys", origin="lower",
               extent=[LFT, RGT, BOT, TOP])

    # Draw 1 meter grid pattern
    h_lines = [line for line in range(BOT, TOP + 1)]
    v_lines = [line for line in range(LFT, RGT + 1)]
    for val in h_lines:
        plt.axhline(val, color='gray', linewidth=0.5)
    for val in v_lines:
        plt.axvline(val, color='gray', linewidth=0.5)

    plt.colorbar(label="Occupancy Probability")
    plt.xlabel("X [m]")
    plt.ylabel("Y [m]")
    plt.pause(0.01)
    plt.show()


# Load map from file and display it
saved_map = np.load('my_map.npy')
plot_map(saved_map)
