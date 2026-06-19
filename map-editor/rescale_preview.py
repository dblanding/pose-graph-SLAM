"""
rescale_preview.py  --  Re-render the editor's saved .npy at native resolution

Your saved occupancy_map_editor_output.npy is already correct (chain
coordinates were always stored in native grid space, regardless of zoom).
Only the PREVIEW PNG was rendered at the display SCALE. This script just
re-draws that PNG at native resolution from the existing .npy -- no
retracing needed.

Usage:
  python3 rescale_preview.py occupancy_map_editor_output.npy
"""

import sys
import numpy as np
import cv2

FREE, UNKNOWN, OCCUPIED = 0, 127, 255

path = sys.argv[1] if len(sys.argv) > 1 else "occupancy_map_editor_output.npy"
grid = np.load(path)

H, W = grid.shape
preview = np.zeros((H, W, 3), dtype=np.uint8)
preview[grid == FREE]     = (255, 255, 255)
preview[grid == UNKNOWN]  = (180, 180, 180)
preview[grid == OCCUPIED] = (0, 0, 200)   # red-ish, matches editor's wall color

out_path = path.replace(".npy", "_native.png")
cv2.imwrite(out_path, preview)
print(f"Saved {out_path}  ({W}x{H}, native resolution)")
