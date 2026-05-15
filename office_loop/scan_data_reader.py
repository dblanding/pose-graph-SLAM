# read scans and poses from file 

import os
import pickle
from pprint import pprint


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

data = load_data()
print(f"{len(data)=}")
print()
for n, d in enumerate(data):
    pose = d['pose']
    scan = d['scan']
    print(f"Scan {n} Len = {len(scan)}")
    print('Pose:')
    pprint(pose)
    print()


# notice that pose data renews only on odd records.
# e.g. pose[0] and pose[1] are the same
# A new scan with every record (every half second).
# 46 data records cover 23 seconds of operation

pprint(scan)  # the last scan
