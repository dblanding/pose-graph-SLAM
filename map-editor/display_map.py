import cv2
import numpy as np

def display_ogm(filename="occupancy_map.npy"):
    """Load ogm and display. Use button on display window to save as .png"""
    try:
        # Load the map
        grid = np.load(filename)
        print(f"✓ Map loaded from {filename}")
        print(f"Grid shape: {grid.shape}")
        print(f"Grid dtype: {grid.dtype}")
        print(f"Value range: [{grid.min():.2f}, {grid.max():.2f}]")
        
        # Convert log-odds to occupancy probability
        # P(occupied) = 1 / (1 + exp(-log_odds))
        prob = 1.0 / (1.0 + np.exp(-grid))
        prob_scaled = (prob * 100).astype(np.float32)
        
        # Check map stats
        occupied = prob_scaled > 65
        free = prob_scaled < 35
        unknown = ~(occupied | free)
        print(f"Map stats: {np.sum(occupied)} occupied, {np.sum(free)} free, {np.sum(unknown)} unknown")
        
        # Create image
        height, width = grid.shape
        map_img = np.zeros((height, width, 3), dtype=np.uint8)
        map_img[unknown] = [128, 128, 128]  # Gray for unknown
        map_img[free] = [255, 255, 255]      # White for free
        map_img[occupied] = [0, 0, 0]        # Black for occupied
        
        # Scale up for better visibility (2x larger)
        map_img_scaled = cv2.resize(map_img, (width*2, height*2), interpolation=cv2.INTER_NEAREST)
        
        # Display in window
        cv2.imshow('Occupancy Grid Map', map_img_scaled)
        print("Displaying map... Press any key to close window")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print("✓ Window closed")
        
    except Exception as e:
        print(f"✗ Failed to display map: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    display_ogm()
