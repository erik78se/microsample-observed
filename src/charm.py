#!/usr/bin/env python3
# Author: erik.lonroth@gmail.com
# License: Apache2

import os
import logging
import ops

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
            self.unit.status = ops.ActiveStatus("Ready at '%s'" % channel)
        else:
            self.unit.status = ops.BlockedStatus("Invalid channel configured.")


if __name__ == "__main__":  # pragma: nocover
    ops.main(MicrosampleObservedCharm)  # type: ignore
