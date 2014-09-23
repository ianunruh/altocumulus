from argparse import ArgumentParser

from flask import Flask, Response, request

from altocumulus import utils
from altocumulus.bridge import LinuxBridgeManager
from altocumulus.discovery import DiscoveryManager
from altocumulus.utils import Shell

DEFAULT_API_BIND = '0.0.0.0'
DEFAULT_API_PORT = 8140
DEFAULT_ROOT_HELPER = 'sudo'

# TODO These should be persistent
networks = {
}
physical_interfaces = {
}

shell = Shell(DEFAULT_ROOT_HELPER)

lbm = LinuxBridgeManager(shell)
dm = DiscoveryManager(shell)

app = Flask(__name__)

def empty_response(status=200):
    return Response(None, status=200, mimetype='text/plain')

@app.route('/networks/<network_id>', methods=['PUT'])
def update_network(network_id):
    params = request.get_json(force=True)

    networks[network_id] = str(params['vlan'])

    bridge_name = lbm.get_bridge_name(network_id)
    lbm.ensure_bridge(bridge_name) 

    return empty_response()

@app.route('/networks/<network_id>', methods=['DELETE'])
def delete_network(network_id):
    if network_id in networks:
        bridge_name = lbm.get_bridge_name(network_id)
        lbm.remove_bridge(bridge_name)

        del networks[network_id]

    return empty_repsonse()

@app.route('/networks/<network_id>/hosts/<host>', methods=['PUT'])
def plug_host_into_network(network_id, host):
    physical_interfaces[host] = physical_interface = dm.find_interface(host)
    vlan_id = networks[network_id]

    bridge_name = lbm.get_bridge_name(network_id)
    subinterface_name = lbm.ensure_vlan(physical_interface, vlan_id)

    lbm.add_interface(bridge_name, subinterface_name)

    return empty_response()

@app.route('/networks/<network_id>/hosts/<host>', methods=['DELETE'])
def unplug_host_from_network(network_id, host):
    physical_interface = physical_interfaces[host]
    vlan_id = networks[network_id]

    lbm.delete_vlan(physical_interface, vlan_id)

    return empty_response()

def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config-file', default='config.yml')
    parser.add_argument('-d', '--debug', action='store_true')
    
    args = parser.parse_args()

    config = utils.load_config(args.config_file)

    bind = config.get('bind', DEFAULT_API_BIND) 
    port = config.get('port', DEFAULT_API_PORT)

    app.debug = config.get('debug', False)
    app.run(host=bind, port=port)
