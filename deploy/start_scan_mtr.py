from pyinfra.operations import server

server.shell(
    name="Start Scan Motor",
    commands=["sudo systemctl start run_scan_mtr.service"],
    _retries=2,
    _retry_delay=10,  # 10 second delay between retries
)
