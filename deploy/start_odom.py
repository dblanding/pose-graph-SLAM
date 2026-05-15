from pyinfra.operations import server

server.shell(
    name="Start odometer",
    commands=["sudo systemctl start odometer.service"],
    _retries=2,
    _retry_delay=10,  # 10 second delay between retries
)
