# load scans from file
# Plot 2 consecutive scans and display them in red & blue
# TODO: Use odometer pose to see how well they are brought into alignment
# TODO: Use ICP (improved pose) to see if registration is improved

import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos, atan2, pi
import os
import pickle
from pprint import pprint


def load_data(filename="scan_data.pkl"):
    """Loads and deserializes an OGM instance from a binary file."""
    if os.path.exists(filename):
        # Open file in read-binary mode ('rb')
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        print(f"data loaded from {filename}")
        return data
    else:
        print(f"data File {filename} not found.")
        return None

def plot_data(data_1, data_2, label_1, label_2, markersize_1=8, markersize_2=8):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.axis('equal')
    if data_1 is not None:
        x_p, y_p = data_1
        ax.plot(x_p, y_p, color='#336699', markersize=markersize_1, marker='o', linestyle=":", label=label_1)
    if data_2 is not None:
        x_q, y_q = data_2
        ax.plot(x_q, y_q, color='orangered', markersize=markersize_2, marker='o', linestyle=":", label=label_2)
    ax.legend()
    return ax

def p2r(angle, dist):
    """Convert polar (angle in radians) to rectangular coords"""
    x = dist * cos(angle)
    y = dist * sin(angle)
    return x, y

def scan_to_array(scan):
    """Convert scan hits (polar) to xy (numpy array)"""
    hits = [(hit['a'], hit['d'])
              for hit in scan
              if hit['d'] < 4]
    x_list = []
    y_list = []
    for a, d in hits:
        x, y = p2r(-a, d)
        x_list.append(x)
        y_list.append(y)
    xy_points = np.zeros((2, len(hits)))
    xy_points[0, :] = x_list
    xy_points[1, :] = y_list
    return xy_points
    
def explore_data(data):
    for n, d in enumerate(data):
        pose = d['pose']
        scan = d['scan']
        print(f"Scan {n} Len = {len(scan)}")
        print('Pose:')
        pprint(pose)
        print()

if __name__ == "__main__":
    data = load_data()


    # Assign to variables we use in formulas.
    Q = scan_to_array(data[2]['scan'])
    P = scan_to_array(data[0]['scan'])

    plot_data(Q, P, "Q: next scan", "P: prior scan")
    plt.show()

