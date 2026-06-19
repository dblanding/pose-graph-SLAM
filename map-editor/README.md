# Map Editor

This is polygon editing tool that allows a user to build a clean version of a rough SLAM map with connected vertical and horizontal line segments. The line segments are 2 pixels wide (0.1 m), which is very close to the thickness of a typical wall. 

## Usage

`python3 map_editor.py occupancy_map.npy`

This loads the file created by SLAM and displays at an enlarged scale, facilitating the process of accurately selecting corner points. As the user clicks on corner points

## Controls:
* **Left-click** to place a corner, mouse shows a live preview line to the next click.
    * **Left-click** again to draw a segment from the previous click.
    * **Shift+Left-click** forces the new point to be exactly horizontal or vertical from the previous point.
* **Backspace** Remove last point in current chain
* **Enter** Finish current chain and start a new one
* **D** Toggle *Delete* mode
    * While in *Delete* mode, shows nearest corner in **Red**, click to delete owning segment.
    * **D** again to exit *Delete* mode
* **W** Save raw chain data to json (current editing session saved and can be resumed later)
    * JSON backup:
  Press W anytime to write occupancy_map_chains.json -- this is your raw click
  data so you never lose work if the window closes early.
  On startup, if that JSON file already exists, it's loaded automatically
  so you can resume exactly where you left off.
* **S** Save map in both .npy and .png formats 
* **Esc** Quit session
