import numpy as np
from scipy.spatial import KDTree

def estimate_normals(points, k=5):
    """
    Estimate 2D normals using local PCA and KDTree.
    Points shape: (N, 2) # efficient access to each point
    """
    tree = KDTree(points)
    normals = np.zeros_like(points)
    for i, p in enumerate(points):
        _, idx = tree.query(p, k=k)
        neighbors = points[idx]
        cov = np.cov(neighbors.T)
        evals, evecs = np.linalg.eigh(cov)
        normals[i] = evecs[:, 0]  # Eigenvector with smallest eigenvalue
    return normals

def point_to_plane_icp(source, target, init_pose=(0,0,0), max_iter=20):
    """
    Apply 2D Point-to-Plane ICP algorithm to source points.
    Args:
        source (np.ndarray): Array of points shape (N, 2)
        target (np.ndarray): Array of points shape (M, 2)
    Returns: SE(2) transformation [x, y, theta].
    """
    # 1. Estimate target normals
    target_normals = estimate_normals(target)
    target_tree = KDTree(target)
    
    curr_pose = np.array(init_pose, dtype=float)
    
    for _ in range(max_iter):
        # Transform source points by current pose
        c, s = np.cos(curr_pose[2]), np.sin(curr_pose[2])
        R = np.array([[c, -s], [s, c]])
        t = curr_pose[:2].reshape(2, 1)
        src_transformed = (R @ source.T + t).T
        
        # 2. Data Association (Nearest Neighbor)
        dist, indices = target_tree.query(src_transformed)
        matched_target = target[indices]
        matched_normals = target_normals[indices]
        
        # 3. Solve Point-to-Plane linear system: (p_i' - q_i)·n_i ≈ 0
        # where p_i' is source point moved by delta (dx, dy, dtheta)
        A = []
        b = []
        for i in range(len(src_transformed)):
            p = src_transformed[i]
            q = matched_target[i]
            n = matched_normals[i]
            
            # Jacobian for SE(2): [1, 0, -py], [0, 1, px]
            J = np.array([[1, 0, -p[1]], [0, 1, p[0]]])
            row = n.T @ J
            A.append(row)
            b.append(n.T @ (q - p))
            
        dx = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)[0]
        curr_pose += dx
        if np.linalg.norm(dx) < 1e-4: break
            
    return curr_pose
