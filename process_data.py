# process (sync pose to scan) and
# save data in format used by slam program

import numpy as np
import os
import pickle

# input filename
robot_data_file = "SLAM_Data/scan_data.pkl"

# output filenames
scan_data_file = "SLAM_Data/scan_data.npz"
pose_data_file = "SLAM_Data/pose_data.npz"
pose_data_csv_file = "SLAM_Data/pose_data.csv"

def load_data(filename):
    """
    data is a list of dictionaries {'pose': pose, 'scan': scan}
    collected periodicaly from robot, and stored in a .pkl file.
    pose is a dict: {"x": x, "y": y, "h": hdg, "t": time,
        "xr": x_rate, "yr": y_rate, "hr": hdg_rate} dict
    scan is a list of dicts: {'a': angle, 'd': dist, 't': time}
    """
    if os.path.exists(filename):
        # Open file in read-binary mode ('rb')
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        print(f"data loaded from {filename}")
        return data
    else:
        print(f"data File {filename} not found.")
        return None

def sync_pose(robot_scan, robot_pose):
    """
    Estimated value of pose synced to time of mid-scan
    robot_pose: {"x": , "y": , "h": , "t": , "xr": , "yr": , "hr": } dict
    robot_scan: list of {'a': , 'd': , 't': } dictionaries
    Return estimated pose.
    """
    # Find time difference between mid-scan and pose
    mid_scan_idx = len(robot_scan) // 2
    mid_scan_time = robot_scan[mid_scan_idx]['t']
    pose_time = robot_pose["t"]
    time_diff = mid_scan_time - pose_time

    # Estimate pose value at time of mid-scan
    rx = robot_pose["x"] + robot_pose["xr"] * time_diff
    ry = robot_pose["y"] + robot_pose["yr"] * time_diff
    rtheta = robot_pose["h"] + robot_pose["hr"] * time_diff
    return rx, ry, rtheta

def save_poses_csv(poses, filename):
    with open(filename, 'w') as file:
        for pose in poses:
            x, y, z = pose
            file.writelines(f"{x}, {y}, {z}\n")
    

if __name__ == "__main__":
    data = load_data(robot_data_file)
    prev_pose = (0, 0, 0)  # Initial value

    # Prepare for saving
    poses = []
    all_angles = []
    all_ranges = []
    scan_lengths = []

    # Step through each data point
    for n in range(0, len(data)):
        print(n)
        print(f"{prev_pose = }")
        robot_scan = (data[n]['scan'])  # in local polar coords
        print(f"{len(robot_scan) = }")
        robot_pose = data[n]['pose']
        print(f"{robot_pose = }")

        # estimate 'synced' pose at time of mid-scan
        synced_pose = sync_pose(robot_scan, robot_pose)
        print(f"{synced_pose = }")
        prev_pose = synced_pose
        print()
        
        # Separate angles and ranges into 2 parallel arrays
        scandict = {scan['a']: scan['d']
                    for scan in robot_scan}
        angles = np.array(list(scandict.keys()))
        ranges = np.array(list(scandict.values()))
        poses.append(synced_pose)
        all_angles.extend(angles)
        all_ranges.extend(ranges)
        scan_lengths.append(len(angles))

    # save scan data in numpy compressed format
    np.savez_compressed(
        scan_data_file,
        angles = np.array(all_angles),
        ranges = np.array(all_ranges),
        scan_lengths = np.array(scan_lengths),
        num_scans = len(data)
        )

    # save pose data in csv format
    save_poses_csv(poses, pose_data_csv_file)

    # Save poses in npz format
    # (Do this last because it re-defines 'poses' name)
    np.savez_compressed(
        pose_data_file,
        poses = np.array(poses),
        num_poses = len(poses)
        )
    
