# Altocumulus

Integrate your Cumulus Linux switch with OpenStack Neutron

Manages VLAN bridges on the switch and L2 connectivity between (compute) hosts and the VLAN bridges. Uses LLDP to perform auto-discovery of hosts and the switchports they are connected to.

Uses the same conventions as the Linux Bridge agent so that DHCP/L3 agents can theoretically be hosted on the switch.

## Usage

There are two components involved in this project:

* ML2 mechanism driver (runs on hosts with Neutron server)
* HTTP API server (runs on switches)

## To-do

* Authentication
* Pluggable discovery strategies
* Integration with `oslo.rootwrap` for unprivileged operation
* Working upstart script
