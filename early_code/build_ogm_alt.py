import numpy as np
import math


class Build_OGM:
    def __init__(self, width, height, resolution,
                 orig_x_pos=0.5, orig_y_pos=0.5,
                 p_occ=0.7, p_free=0.3, p_prior=0.5):
        self.resolution = resolution
        self.width = width
        self.height = height
        self.orig_x_pos = orig_x_pos  # origin position as a fraction of width
        self.orig_y_pos = orig_y_pos  # origin position as a fraction of height
        
        # Initialize grid dimensions
        self.nx = int(round(width / resolution))
        self.ny = int(round(height / resolution))
        
        # Log-odds values for updates
        self.l_occ = self._log_odds(p_occ)
        self.l_free = self._log_odds(p_free)
        self.l_prior = self._log_odds(p_prior)
        
        # Initialize map with prior log-odds
        self.data = np.full((self.nx, self.ny), self.l_prior)

    def _log_odds(self, p):
        return math.log(p / (1 - p))

    def _p_from_log_odds(self, l):
        return 1.0 - (1.0 / (1.0 + np.exp(l)))

    def pos_to_index(self, x, y):
        ix = int(round((x + self.width * self.orig_x_pos) / self.resolution))
        iy = int(round((y + self.height * self.orig_y_pos) / self.resolution))
        return ix, iy

    def update_map(self, robot_pose, scan_data):
        """
        pose is estimated fro each individual scan measurement.
        Updates the map using an inverse sensor model.
        robot_pose: {"x": , "y": , "h": , "t": , "xr": , "yr": , "hr": } dict
        scan_data: list of {'a': , 'd': , 't': } dictionaries
        """
        pose_time = robot_pose["t"]
        for meas in scan_data:
            angle = meas['a']
            dist = meas['d']
            scan_time = meas['t']

            # Find time difference between scan and pose
            time_diff = scan_time - pose_time

            # Estimate pose value at scan_time
            rx = robot_pose["x"] + robot_pose["xr"] * time_diff
            ry = robot_pose["y"] + robot_pose["yr"] * time_diff
            ryaw = robot_pose["h"] + robot_pose["hr"] * time_diff
            ix_src, iy_src = self.pos_to_index(rx, ry)

            # Calculate absolute position of the detection
            tx = rx + dist * math.cos(ryaw - angle)
            ty = ry + dist * math.sin(ryaw - angle)
            ix_tar, iy_tar = self.pos_to_index(tx, ty)

            # Bresenham's line algorithm to find all cells between robot and target
            line = self._get_line(ix_src, iy_src, ix_tar, iy_tar)
            
            # Update cells along the ray as 'free'
            for (x, y) in line[:-1]:
                if 0 <= x < self.nx and 0 <= y < self.ny:
                    self.data[x, y] += self.l_free - self.l_prior
            
            # Update the endpoint cell as 'occupied'
            if 0 <= ix_tar < self.nx and 0 <= iy_tar < self.ny:
                self.data[ix_tar, iy_tar] += self.l_occ - self.l_prior

    def _get_line(self, x1, y1, x2, y2):
        """Standard Bresenham's line algorithm."""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = -1 if x1 > x2 else 1
        sy = -1 if y1 > y2 else 1

        if dx > dy:
            err = dx / 2.0
            while x != x2:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        points.append((x, y))
        return points


# --- Example Usage ---
if __name__ == '__main__':
    # Initialize OGM (10m x 10m, 0.1m resolution)
    ogm = BuildOGM(width=3, height=3, resolution=0.04)

    # Simulated Robot Poses: [x, y, yaw]
    pose = [0, 0, 0]
    
    for i in range(1, 11, 1):  # 1 through 10, inclusive
        filename = f"../arena_scan_data/scan{i}.csv"
        scn = file_read(filename)
        ogm.update_map(pose, scn)

    # Save ogm
    np.save('my_map.npy', ogm.data)
    print("Map saved to my_map.npy")
