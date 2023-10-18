This tutorial will introduce you writing a machine charm. A machine charm deploys on any cloud except kubernetes clouds and typically involves installing and configuring your software and its dependencies, and, acting on events related to integrations with other charms.

In this tutorial, we will explore all these aspects step by step.

What you will need:

- A laptop with amd64 architecture, installed Ubuntu 22.04+.
- Understanding of Linux fundamentals.
- Familiarity with Juju
- Familiarity with the Python programming language.
- Have a juju client installed and added credentials for a cloud of your choise. (LXD, AWS, GCE etc.)
- Installed charmcraft which is the build system for charms.

What you’ll do:

You will learn how to develop a charm that carries an API service called "microsample" and added some basic juju features to the charm.

These are the steps we will take:

  - Step 0: Plan what the charm should be able to do, like configuration, integrations with other charms etc.
  - Step 1:
    - Initialize a new charm with charmcraft.
    - Make your charm install the microsample snap.
    - Build (pack) the charm with charmcraft.
    - Deploy the charm and test the microsample service.
  - Step 2:
    - Add a configuration option to the charm.
    - Expose the version of the application behind your charm.
  - Step 3:
    - Handle an upgrade of the charm.
    - Integrate the charm with prometheus+grafana (via COSlite) to provide monitoring of the microsample service.

By the end of this tutorial you will have touch base with the ops framework, juju configuration, juju libraries and integrations. This is a great start for a beginner to juju development. Good luck!


## Step 0: Planning
A charm author plans for what functionality should be exposed to operational users (people using juju as a DevOps tool) and implements that functionality with the "ops" library. Unlike ansible, where all magic is decelared in yaml, juju typically uses Python code for installing, configuring, upgrade and interact with other softwares. Writing a charm is exactly the same process as developing any other application.

In this tutorial, will be making some decicions as what the charm should do:

1. We will be installing a service called microsample. This service is referenced as the *workload* of the charm and can have a different name than the charm itself.

2. We decide to use *snap* as the workload package format. This is since microsample is already published in the snapstore. https://snapcraft.io/microsample This makes installation easy and workload upgrades are taken care of by snapd.

    *Note* You can test microsample on your local machine:
        sudo snap install microsample --channel edge
        curl http://localhost:8080
        Online

3. We decide that we want to be able to let the juju users configure the snap "channel" which will control which channel is used for microsample when it is installed.

    snap has a concept of installation "channels", what tells us what quality the release of the snap is. Channels available are "edge", "beta", "candidate" and "stable".

This is a good start for a simple charm and we can add more features later, such as integrations and actions.

## Step 1: Initialization of a new charm with charmcraft

Lets initialize our new charm with charmcraft by creating a directory with its name and running snapcraft:

    mkdir microsample-observed
    cd microsample-observed
    charmcraft init --profile machine

Charmcraft has now produced the skeleton for a new charm. Lets edit metadata.yaml which contains information about the charm. It should look like this:

    name: microsample-observed
    display-name: microsample-observed
    summary: Microsample (charmed operator)
    description: |
    A charm that deploys the microsample snap and allows for a configuration of the snap channel via juju config.

### Edit charm.py and act on the installation event.

Now, lets make our charm code install the microsample snap when the *install* event is triggered by the "ops" framework.

*We're also adding an event handler for the start event. It has nothing to do with actually starting the microsample but could certainly be used for this if needed.*

Edit charm.py as:

```
    #!/usr/bin/env python3
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
            self.unit.status = ops.MaintenanceStatus("Installing microsample snap")
            os.system(f"snap install microsample --channel edge")
            self.unit.status = ops.ActiveStatus("Ready")  


    if __name__ == "__main__":  # pragma: nocover
        ops.main(MicrosampleObservedCharm)  # type: ignore
```


Build the charm (pack) to produce the charm file:

    charmcraft pack
    Created 'microsample-observed_ubuntu-22.04-amd64.charm'.
    Charms packed:
         microsample-observed_ubuntu-22.04-amd64.charm

To deploy the charm, create a model and deploy the charm into it.

    # Create a model
    juju add-model my-model
    # Deploy the charm
    juju deploy ./microsample-observed_ubuntu-22.04-amd64.charm
    # Watch as it comes to life.
    juju status

If your deploy enters "error" state, the process of upgrading the charm with a new (bug-free) version is:

1. Fix the code in charm.py
2. Rebuild the charm: `charmcraft pack`
3. Upgrade the charm: `juju upgrade-charm microsample-observed --path=./microsample-observed_ubuntu-22.04-amd64.charm --force-units`
4. Let the model know the issue is resolved (fixed) with `juju resolved microsample-observed/0`

Finally, test that the service works by calling it through the juju exec mechanism that executes a command on the unit:

    juju exec --unit microsample-observed/0 -- "curl -s http://localhost:8080"
    Online

We succeeded with our sourcery!

*Note: If you open up the firewall for your cloud, you can test the service directly with curl. On some clouds that supports manipulation of firewalls, juju can do this for us with "juju expose".*

## 