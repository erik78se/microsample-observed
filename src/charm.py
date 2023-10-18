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

    def _on_start(self, event: ops.StartEvent):
        """Handle start event."""
        self.unit.status = ops.ActiveStatus()

    def _on_install(self, theevent):
        """Handle install event."""
        self.unit.status = ops.MaintenanceStatus("Installing microsample snap")
        os.system(f"snap install microsample --channel edge")
        self.unit.status = ops.ActiveStatus("Ready")  


if __name__ == "__main__":  # pragma: nocover
    ops.main(MicrosampleObservedCharm)  # type: ignore
