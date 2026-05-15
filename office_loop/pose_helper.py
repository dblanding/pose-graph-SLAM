"""Courtesy of Google AI"""

import numpy as np
import math

def pose_to_hom_matrix(x, y, theta):
    """Converts a 2D pose (x, y, theta) to a 3x3 homogeneous transformation matrix."""
    c = math.cos(theta)
    s = math.sin(theta)
    # 2D homogeneous transformation matrix structure
    T = np.array([
        [c, -s, x],
        [s, c, y],
        [0, 0, 1]
    ])
    return T

def hom_matrix_to_pose(T):
    """Converts a 3x3 homogeneous transformation matrix back to a 2D pose (x, y, theta)."""
    x = T[0, 2]
    y = T[1, 2]
    # Extract angle using arctan2 for correct quadrant handling
    theta = math.atan2(T[1, 0], T[0, 0])
    return x, y, theta

def calculate_relative_pose(pose1, pose2):
    """
    Calculates the relative pose of pose2 with respect to pose1.
    
    Args:
        pose1 (tuple): The first pose (x1, y1, theta1) in world coordinates.
        pose2 (tuple): The second pose (x2, y2, theta2) in world coordinates.

    Returns:
        tuple: The relative pose (dx, dy, dtheta).
    """
    x1, y1, theta1 = pose1
    x2, y2, theta2 = pose2

    # 1. Convert poses to homogeneous transformation matrices
    T_w1 = pose_to_hom_matrix(x1, y1, theta1) # World to pose1 transform
    T_w2 = pose_to_hom_matrix(x2, y2, theta2) # World to pose2 transform

    # 2. Calculate the inverse of the first matrix (T_w1^-1)
    # The inverse is used to transform a point from world frame to pose1's frame
    T_1w = np.linalg.inv(T_w1)

    # 3. Calculate the relative transformation T_12 = T_1w * T_w2
    # This matrix T_12 represents the transformation from pose1's frame to pose2's frame
    T_12 = np.dot(T_1w, T_w2)

    # 4. Convert the resulting matrix back to pose parameters
    dx, dy, dtheta = hom_matrix_to_pose(T_12)

    return dx, dy, dtheta

if __name__ == "__main__":
    # Example usage:
    # Pose 1: (x=1.0, y=0.0, theta=0.0 radians)
    # Pose 2: (x=2.0, y=1.0, theta=pi/2 radians)
    pose1_world = (1.0, 0.0, 0.0)
    pose2_world = (2.0, 1.0, math.pi / 2.0)

    relative_pose = calculate_relative_pose(pose1_world, pose2_world)

    print(f"Pose 1 in world: {pose1_world}")
    print(f"Pose 2 in world: {pose2_world}")
    print(f"Relative pose (dx, dy, dtheta): {relative_pose}")

    # Another example: 
    # Pose 1: (x=0, y=0, theta=0)
    # Pose 2: (x=1, y=0, theta=0) should give (1, 0, 0)
    pose3_world = (0.0, 0.0, 0.0)
    pose4_world = (1.0, 0.0, 0.0)
    relative_pose_2 = calculate_relative_pose(pose3_world, pose4_world)
    print(f"Relative pose 2 (dx, dy, dtheta): {relative_pose_2}") # Expected: (1.0, 0.0, 0.0)

