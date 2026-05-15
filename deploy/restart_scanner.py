from pyinfra.operations import systemd

systemd.service(
    name="Restart and enable the service",
    service="scanner.service",
    running=True,
    restarted=True,
    enabled=True,
    _sudo=True
)
