"""
map_editor.py  --  Interactive wall-chain editor for SLAM maps

Controls:
  Left-click              Add corner point (or delete nearest in delete mode)
  Shift+Left-click        Force exact H or V from previous point
  D                       Toggle delete mode (click to remove nearest corner)
  Backspace               Remove last point in current chain
  Enter                   Finish current chain, start new one
  W                       Save raw chain data to JSON (no snapping, just backup)
  S                       Snap to H/V and save (npy + png)
  Esc                     Quit without saving

JSON backup:
  Press W anytime to write <input>_chains.json -- this is your raw click
  data, unsnapped, so you never lose work if the window closes early.
  On startup, if that JSON file already exists, it's loaded automatically
  so you can resume exactly where you left off.
"""

import os, sys, json
os.environ["GTK_PATH"] = ""

import numpy as np
import cv2

SCALE      = 4
LINE_WIDTH = 2
SNAP_DEG   = 10
FREE, UNKNOWN, OCCUPIED = 0, 127, 255

# ── Load & convert ────────────────────────────────────────────────────────────
path = sys.argv[1] if len(sys.argv) > 1 else "occupancy_map.npy"
raw  = np.load(path)
grid = np.full(raw.shape, UNKNOWN, dtype=np.uint8)
if raw.dtype.kind == 'f':
    p = 100.0 / (1.0 + np.exp(-raw))
    grid[p < 35] = FREE
    grid[p > 65] = OCCUPIED
else:
    grid[:] = raw.astype(np.uint8)
H, W = grid.shape

JSON_PATH = path.replace(".npy", "") + "_chains.json"

def make_bgr(g):
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    rgb[g == FREE]     = (255, 255, 255)
    rgb[g == UNKNOWN]  = (180, 180, 180)
    rgb[g == OCCUPIED] = (  0,   0,   0)
    return cv2.resize(rgb, (W*SCALE, H*SCALE), interpolation=cv2.INTER_NEAREST)

BASE = make_bgr(grid)

def draw_chain(img, chain, col):
    for i in range(len(chain)-1):
        cv2.line(img, (chain[i][0]*SCALE, chain[i][1]*SCALE),
                      (chain[i+1][0]*SCALE, chain[i+1][1]*SCALE), col, max(1, LINE_WIDTH*SCALE))
    for pt in chain:
        cv2.circle(img, (pt[0]*SCALE, pt[1]*SCALE), 4, col, -1)

def make_display(chains, current, mouse, delete_mode):
    d = BASE.copy()
    for c in chains:
        draw_chain(d, c, (0, 200, 0))
    draw_chain(d, current, (255, 120, 0))
    if current and mouse and not delete_mode:
        cv2.line(d, (current[-1][0]*SCALE, current[-1][1]*SCALE), mouse, (180, 180, 0), 1)
    # Highlight nearest point in delete mode
    if delete_mode and mouse:
        gx, gy = mouse[0]//SCALE, mouse[1]//SCALE
        hit = nearest_point(gx, gy, chains, current)
        if hit:
            ci, pi = hit
            all_chains = chains + [current]
            pt = all_chains[ci][pi]
            cv2.circle(d, (pt[0]*SCALE, pt[1]*SCALE), 8, (0, 0, 255), 2)
    mode_str = "  [DELETE MODE -- click point to remove]" if delete_mode else ""
    cv2.putText(d,
        f"L=add  Shift+L=H/V  D=delete mode  Backspace=undo  Enter=finish  W=backup  S=save  Esc=quit{mode_str}",
        (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (50, 50, 255) if not delete_mode else (0, 0, 220),
        1, cv2.LINE_AA)
    return d

def forced_hv(prev, pt):
    dx, dy = pt[0]-prev[0], pt[1]-prev[1]
    return (pt[0], prev[1]) if abs(dx) >= abs(dy) else (prev[0], pt[1])

def nearest_point(gx, gy, chains, current):
    best_d, best = 10**2, None
    for ci, chain in enumerate(chains + [current]):
        for pi, pt in enumerate(chain):
            d = (pt[0]-gx)**2 + (pt[1]-gy)**2
            if d < best_d:
                best_d, best = d, (ci, pi)
    return best

def delete_point(chains, current, ci, pi):
    all_chains = chains + [current]
    chain = list(all_chains[ci])
    chain.pop(pi)
    if ci < len(chains):
        if len(chain) >= 2:
            chains[ci] = chain
        else:
            chains.pop(ci)
    else:
        current = chain
    return chains, current

def snap_chain(chain):
    if len(chain) < 2:
        return chain
    pairs = []
    for i in range(len(chain)-1):
        x0, y0 = chain[i]; x1, y1 = chain[i+1]
        dx, dy = x1-x0, y1-y0
        if dx == 0 or dy == 0:          # already exact -- never touch
            pairs.append(((x0,y0),(x1,y1)))
            continue
        angle = abs(np.degrees(np.arctan2(dy, dx))) % 90
        if angle <= SNAP_DEG:
            my = int(round((y0+y1)/2))
            pairs.append(((x0, my),(x1, my)))
        elif angle >= (90-SNAP_DEG):
            mx = int(round((x0+x1)/2))
            pairs.append(((mx, y0),(mx, y1)))
        else:
            pairs.append(((x0,y0),(x1,y1)))
    result = [pairs[0][0]]
    for i in range(len(pairs)-1):
        a, b = pairs[i][1], pairs[i+1][0]
        result.append((int(round((a[0]+b[0])/2)), int(round((a[1]+b[1])/2))))
    result.append(pairs[-1][1])
    return result

def rasterize(chains, shape):
    out = np.full(shape, UNKNOWN, dtype=np.uint8)
    for c in chains:
        for i in range(len(c)-1):
            cv2.line(out, c[i], c[i+1], OCCUPIED, LINE_WIDTH)
    return out

def save_chains_json(chains, current, json_path):
    """Save raw (unsnapped) chain data so work is never lost."""
    all_chains = chains + ([current] if len(current) >= 1 else [])
    data = {"chains": [[list(pt) for pt in c] for c in all_chains]}
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

def load_chains_json(json_path):
    """Load previously-saved raw chain data, if it exists."""
    if not os.path.exists(json_path):
        return []
    with open(json_path) as f:
        data = json.load(f)
    return [[tuple(pt) for pt in c] for c in data.get("chains", [])]

# ── State ─────────────────────────────────────────────────────────────────────
chains  = load_chains_json(JSON_PATH)
current = []
mouse, delete_mode = None, False
if chains:
    print(f"Resumed {len(chains)} chain(s) from {JSON_PATH}.")

def mouse_cb(event, x, y, flags, _):
    global mouse, current, chains, delete_mode
    gx = max(0, min(W-1, x//SCALE))
    gy = max(0, min(H-1, y//SCALE))
    if event == cv2.EVENT_MOUSEMOVE:
        mouse = (x, y)
    elif event == cv2.EVENT_LBUTTONDOWN:
        if delete_mode:
            hit = nearest_point(gx, gy, chains, current)
            if hit:
                chains, current = delete_point(chains, current, hit[0], hit[1])
                print(f"Deleted point {hit[1]} from chain {hit[0]}.")
        else:
            pt = forced_hv(current[-1], (gx,gy)) if (flags & cv2.EVENT_FLAG_SHIFTKEY) and current else (gx,gy)
            current.append(pt)

cv2.namedWindow("Map Editor", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Map Editor", W*SCALE, H*SCALE)
cv2.setMouseCallback("Map Editor", mouse_cb)
print("Map editor ready.")
print("L=add  Shift+L=H/V  D=toggle delete mode  Backspace=undo  Enter=finish chain  "
      "W=backup JSON  S=save  Esc=quit")

while True:
    cv2.imshow("Map Editor", make_display(chains, current, mouse, delete_mode))
    key = cv2.waitKey(20) & 0xFF

    if key == 27:
        print("Quit without saving."); break

    elif key == 13:          # Enter
        if len(current) >= 2:
            chains.append(current)
            print(f"Chain {len(chains)} finished ({len(current)} pts).")
        current = []

    elif key == 8:           # Backspace
        if current:
            current.pop()
        elif chains:
            current = chains.pop()
            print("Reopened last chain.")

    elif key == ord('d'):
        delete_mode = not delete_mode
        print(f"Delete mode {'ON' if delete_mode else 'OFF'}.")

    elif key == ord('w'):    # Backup raw chains to JSON
        save_chains_json(chains, current, JSON_PATH)
        print(f"Backup saved -> {JSON_PATH}")

    elif key == ord('s'):
        if len(current) >= 2:
            chains.append(current); current = []
        if not chains:
            print("Nothing to save."); continue
        snapped  = [snap_chain(c) for c in chains]
        out_grid = rasterize(snapped, (H, W))
        stem     = path.replace(".npy", "")
        npy_path = stem + "_editor_output.npy"
        png_path = stem + "_editor_output.png"
        np.save(npy_path, out_grid)

        # Render preview at NATIVE grid resolution (no SCALE), so saved
        # files are zoom-independent and match the original map's size.
        native_bg = np.zeros((H, W, 3), dtype=np.uint8)
        native_bg[grid == FREE]     = (255, 255, 255)
        native_bg[grid == UNKNOWN]  = (180, 180, 180)
        native_bg[grid == OCCUPIED] = (  0,   0,   0)
        preview = native_bg.copy()
        for c in snapped:
            for i in range(len(c)-1):
                cv2.line(preview, c[i], c[i+1], (0, 0, 200), LINE_WIDTH)

        cv2.imwrite(png_path, preview)
        print(f"Saved {npy_path}  |  {png_path}  ({W}x{H}, native resolution)")
        chains = snapped

cv2.destroyAllWindows()
