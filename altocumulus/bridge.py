# Copyright 2012 Cisco Systems, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
#
# Performs per host Linux Bridge configuration for Neutron.
# Based on the structure of the OpenVSwitch agent in the
# Neutron OpenVSwitch Plugin.
# @author: Sumit Naiksatam, Cisco Systems, Inc.
import os
from subprocess import CalledProcessError

BRIDGE_NAME_PREFIX = 'brq'

BRIDGE_INTERFACES_FS = '/sys/devices/virtual/net/{}/brif/'
SUBINTERFACE_NAME = '{}.{}'

class LinuxBridgeManager(object):
    """
    Much of this code is from the Linux Bridge agent for Neutron
    """
    def __init__(self, shell):
        self.shell = shell

    def device_exists(self, device):
        try:
            self.shell.call(['ip', 'link', 'show', 'dev', device])
        except CalledProcessError:
            return False
        return True

    def interface_exists_on_bridge(self, bridge, interface):
        directory = BRIDGE_INTERFACES_FS.format(bridge)
        for filename in os.listdir(directory):
            if filename == interface:
                return True
        return False
    
    def get_bridge_name(self, network_id):
        bridge_name = BRIDGE_NAME_PREFIX + network_id[0:11]
        return bridge_name

    def get_subinterface_name(self, physical_interface, vlan_id):
        return SUBINTERFACE_NAME.format(physical_interface, vlan_id)

    def ensure_vlan(self, physical_interface, vlan_id):
        interface = self.get_subinterface_name(physical_interface, vlan_id)

        if not self.device_exists(interface):
            self.shell.call(['ip', 'link', 'add', 'link', physical_interface, 'name', interface, 'type', 'vlan', 'id', vlan_id])
            self.shell.call(['ip', 'link', 'set', interface, 'up'])

        return interface

    def delete_vlan(self, physical_interface, vlan_id):
        interface = self.get_subinterface_name(physical_interface, vlan_id)
        if not self.device_exists(interface):
            return

        self.shell.call(['ip', 'link', 'set', interface, 'down'])
        self.shell.call(['ip', 'link', 'delete', interface])

    def add_interface(self, bridge_name, interface_name):
        if self.interface_exists_on_bridge(bridge_name, interface_name):
            return

        self.shell.call(['brctl', 'addif', bridge_name, interface_name])

    def ensure_bridge(self, bridge_name):
        if self.device_exists(bridge_name):
            return

        self.shell.call(['brctl', 'addbr', bridge_name])
        self.shell.call(['brctl', 'stp', bridge_name, 'off'])
        self.shell.call(['ip', 'link', 'set', bridge_name, 'up'])

    def remove_bridge(self, bridge_name):
        if not self.device_exists(bridge_name):
            return

        self.shell.call(['ip', 'link', 'set', bridge_name, 'down'])
        self.shell.call(['brctl', 'delbr', bridge_name])
