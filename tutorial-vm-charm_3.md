Now, lets add some code that interacts with snapd to get some information about the microsample.

For this, we are going to need the "requests_unixsocket" package that allows us to interact directly with snapd over a unix socket.

Add the following two packages to the "requirements.txt" file. They will be automatically picked up by charmcraft, added to our charm and installed/upgraded when we upgrade the charm.

The requirements.txt should look like this.
```
ops ~= 2.4
requests==2.28.1
requests-unixsocket==0.3.0
```
The charm.py should now look like this:
```
import os
import logging
import ops
import requests_unixsocket

logger = logging.getLogger(__name__)


class MicrosampleObservedCharm(ops.CharmBase):

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    def _on_start(self, event: ops.StartEvent):
        """Handle start event."""
        self.unit.status = ops.ActiveStatus()

    def _on_install(self, theevent):
        """Handle install event."""
        self.unit.status = ops.MaintenanceStatus("Installing microsample snap")
        channel = self.config.get('channel')
        if channel in ['beta', 'edge', 'candidate', 'stable']:
            os.system(f"snap install microsample --{channel}")
            self.unit.status = ops.ActiveStatus("Ready")
        else:
            self.unit.status = ops.BlockedStatus("Invalid channel configured.")

    def _on_config_changed(self,theevent):
        channel = self.config.get('channel')
        if channel in ['beta', 'edge', 'candidate', 'stable']:
            os.system(f"snap refresh microsample --{channel}")
            workload_version = self._getWorkloadVersion()
            self.unit.set_workload_version(workload_version)
            self.unit.status = ops.ActiveStatus("Ready at '%s'" % channel)
        else:
            self.unit.status = ops.BlockedStatus("Invalid channel configured.")


    def _getWorkloadVersion(self):
        """Get the microsample workload version from the snapd API via unix-socket"""
        snap_name = "microsample"
        snapd_url = f"http+unix://%2Frun%2Fsnapd.socket/v2/snaps/{snap_name}"
        session = requests_unixsocket.Session()
        # Use the requests library to send a GET request over the Unix domain socket
        response = session.get(snapd_url)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            workload_version = data["result"]["version"]
        else:
            workload_version = "unknown"
            print(f"Failed to retrieve Snap apps. Status code: {response.status_code}")

        # Return the workload version
        return workload_version


if __name__ == "__main__":  # pragma: nocover
    ops.main(MicrosampleObservedCharm)  # type: ignore
```

If the handling of snap versions is daunting, you can skip that part and call *set_workload_version('v1.0')* and continue with the tutorial.

NOTE! You might need to upgrade applications in an error state with:

```
juju upgrade-charm ./<charm> --force-units
juju resolved <unit>
```

Congratulations, you have made it so far! Lets continue to add a Juju integration!