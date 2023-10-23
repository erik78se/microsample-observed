## Step 2 - Adding a config option.

Now that the charm deploys and install, lets add the configuration option which will controll the channel from which the snap is installed.

At the time of writing, Juju supports three types of options: "int", "string" and "bool".

Create a config.yaml file which looks like this:

    options:
    channel:
        type: string
        default: "edge"
        description: "Channel for microsample snap."

Update the _on_install funtion in charm.py to make use of the new config option:

```
    def _on_install(self, theevent):
        """Handle install event."""
        self.unit.status = ops.MaintenanceStatus("Installing microsample snap")
        channel = self.config.get('channel')
        if channel in ['beta', 'edge', 'candidate', 'stable']:
            os.system(f"snap install microsample --{channel}")
            self.unit.status = ops.ActiveStatus("Ready")
        else:
            self.unit.status = ops.BlockedStatus("Invalid channel configured.")
```