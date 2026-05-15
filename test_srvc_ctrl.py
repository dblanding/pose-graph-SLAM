# test_srvc_ctrl.py
"""
Test starting and stopping of services on raspibot
"""

import service_ctrl as sc
import time

print("Starting the scan motor")
sc.start_scan_mtr()
print("Starting the odometer")
sc.start_odometer()
print("Giving the odometer time to initialize")
time.sleep(10)  # The odometer has to do some initialization
print("Stopping the odometer")
sc.stop_odometer()
print("Stopping the scan motor")
sc.stop_scan_mtr()
