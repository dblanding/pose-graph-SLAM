# Copy of scan_icp.py
# Explore using slam_front_end.py

import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos, atan2, pi
import os
import pickle
from pprint import pprint
import slam_front_end


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
    """
    Convert scan hits (polar coords) within dist=4 m
    to numpy array with shape (2, n) (2 rows, many columns)
    """
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

def sync_pose(robot_scan, robot_pose):
    """
    robot_scan: list of {'a': , 'd': , 't': } dictionaries
    robot_pose: {"x": , "y": , "h": , "t": , "xr": , "yr": , "hr": } dict
    Return estimated pose at time of mid-scan
    """
    # Find time difference between mid-scan and pose
    scan_len = len(robot_scan)
    mid_scan_time = scan_data[scan_len//2]['t']
    pose_time = robot_pose["t"]
    time_diff = mid_scan_time - pose_time

    # Estimate pose value at time of mid-scan
    rx = robot_pose["x"] + robot_pose["xr"] * time_diff
    ry = robot_pose["y"] + robot_pose["yr"] * time_diff
    ryaw = robot_pose["h"] + robot_pose["hr"] * time_diff
    return rx, ry, ryaw

def local_to_world(local_points, robot_pose):
    """
    Converts 2D points from a local robot frame to the world frame.

    :param local_points: Numpy array of shape (2, N) for N points.
    :param robot_pose: Tuple/array (x, y, theta) of the robot's pose in world frame.
    :return: Numpy array of shape (2, N) as world coordinates.
    """
    # Unpack robot pose
    robot_x, robot_y, robot_theta = robot_pose
    
    # 1. Create the 2x2 rotation matrix
    # The rotation matrix A [[cos(theta), -sin(theta)],
    #                        [sin(theta), cos(theta)]]
    # which transforms from local to world coordinates.
    c, s = np.cos(robot_theta), np.sin(robot_theta)
    rotation_matrix = np.array([[c, -s], 
                                [s, c]])
    
    # 2. Apply rotation: R @ local_points
    # The result is a (2, N) array of rotated points
    rotated_points = rotation_matrix @ local_points
    
    # 3. Apply translation: rotated_points + robot_position_vector
    # The robot's position vector needs to be a (2, 1) or (2, N) array for broadcasting
    robot_position = np.array([[robot_x], [robot_y]])
    world_points = rotated_points + robot_position
    
    return world_points

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
    odom_pose = (0, 0, 0)  # Initial value

    for n in range(0, len(data)-2, 2):
        print(f"scan number = {n+2}")
        prev_scan = scan_to_array(data[n]['scan'])
        prior_scan = local_to_world(prev_scan, odom_pose)  # in world coords
        curr_scan = scan_to_array(data[n+2]['scan'])
        odom_pose = (data[n+2]['pose']['x'], data[n+2]['pose']['y'], data[n+2]['pose']['h'])
        odom_time = data[n+2]['pose']['t']
        print(f"{odom_pose = }, {odom_time = }")
        scan_start_time = data[n+2]['scan'][0]['t']
        scan_end_time = data[n+2]['scan'][-1]['t']
        scan_duration = scan_end_time - scan_start_time
        scan_mid_time = scan_start_time + scan_duration / 2
        print(f"{scan_mid_time = }, {scan_duration = }")
        print(f"{odom_time - scan_mid_time = }")
        synced_pose = sync_pose(scan, odom_pose)
        icp_pose = slam_front_end.point_to_plane_icp(curr_scan.T, prev_scan.T, synced_pose)
        print(f"{icp_pose = }")
        print()
        latest_scan = local_to_world(curr_scan, synced_pose)
        plot_data(prior_scan, latest_scan, "prior scan", "current scan")
        plt.show()
