# Altocumulus

Integrate your Cumulus Linux switch with OpenStack Neutron

Manages VLAN bridges on the switch and L2 connectivity between (compute) hosts and the VLAN bridges. Uses LLDP to perform auto-discovery of hosts and the switchports they are connected to.

Uses the same conventions as the Linux Bridge agent so that DHCP/L3 agents can theoretically be hosted on the switch.

## Usage

There are two components involved in this project:

* ML2 mechanism driver (runs on hosts with Neutron server)
* HTTP API server (runs on switches)

## Installation

### ML2 mechanism driver

1. Install the driver and its dependencies with the following

    ```bash
    pip install git+git://github.com/ianunruh/altocumulus.git
    pip install requests
    ```

2. Add `cumulus` to the `mechanism_drivers` field in `/etc/neutron/neutron.conf`
3. Configure `/etc/neutron/plugins/ml2/ml2_cumulus.ini`

### HTTP API server

1. Install the API server

    ```bash
    pip install git+git://github.com/ianunruh/altocumulus.git
    ```

2. Place the included Upstart script in `/etc/init` and run `start altocumulus-api`

## To-do

* Authentication
* Pluggable discovery strategies
* Integration with `oslo.rootwrap` for unprivileged operation
* Working upstart script
