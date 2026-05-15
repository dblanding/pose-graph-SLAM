# load_data.py
"""
Demonstrates how to load scan & pose data from .npz file
"""

import numpy as np

pose_filename = "Scan_Pose_Data/pose_data.npz"
scan_filename = "Scan_Pose_Data/scan_data.npz"

with np.load(scan_filename) as scan_data:
    all_angles = scan_data['angles']
    all_ranges = scan_data['ranges']
    num_scans = scan_data['num_scans']
    scan_lengths = scan_data['scan_lengths']

# Reconstruct individual scans
scans = []
offset = 0

for i, length in enumerate(scan_lengths):
    scan = {
        'angles': all_angles[offset:offset+length],
        'ranges': all_ranges[offset:offset+length]
    }
    scans.append(scan)
    offset += length

print(f"Loaded {len(scans)} scans from {scan_filename}")
print(f"Loaded {num_scans} scans from {scan_filename}")
print(f"scans[0] length = {scan_lengths[0]}")
print(f"scans[0] angles = {scans[0]['angles']}")
print(f"scans[0] ranges = {scans[0]['ranges']}")
for n in range(num_scans):
    print(f"scans[{n}] length = {scan_lengths[n]}")

with np.load(pose_filename) as pose_data:
    num_poses = pose_data['num_poses']
    poses = pose_data['poses']
    # change from array to simple values
    poses = poses.tolist()

print(f"loaded {num_poses} poses from {pose_filename}")
print(poses)
