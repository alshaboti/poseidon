#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2016-2017 In-Q-Tel, Inc, All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
Created on 19 November 2017
@author: cglewis
"""
import yaml

from poseidon.baseClasses.Logger_Base import Logger

module_logger = Logger.logger


class HexInt(int): pass


def representer(dumper, data):
    return dumper.represent_int(hex(data))


class Parser:

    def __init__(self, mirror_ports=None):
        self.logger = module_logger
        self.mirror_ports = mirror_ports

    def config(self, config_file, action, port, switch):
        switch_found = None
        if config_file:
            # TODO check for other files
            stream = open(config_file, 'r')
            obj_doc = yaml.safe_load(stream)
            stream.close()
        else:
            return False

        if action == 'mirror':
            ok = True
            if not self.mirror_ports:
                self.logger.error("Unable to mirror, no mirror ports defined")
                return False
            if not 'dps' in obj_doc:
                self.logger.warning("Unable to find switch configs in "
                                    "'/etc/ryu/faucet/faucet.yaml'")
                ok = False
            else:
                for s in obj_doc['dps']:
                    try:
                        if hex(int(switch, 16)) == hex(obj_doc['dps'][s]['dp_id']):
                            switch_found = s
                    except Exception as e:  # pragma: no cover
                        self.logger.debug("switch is not a hex value: %s" % switch)
                        self.logger.debug("error: %s" % e)
            if not switch_found:
                self.logger.warning("No switch match found to mirror "
                                    "from in the configs. switch: %s" % switch)
                ok = False
            else:
                if not switch_found in self.mirror_ports:
                    self.logger.warning("Unable to mirror " + str(port) +
                                        " on " + str(switch_found) +
                                        ", mirror port not defined on that switch")
                    ok = False
                else:
                    if not port in obj_doc['dps'][switch_found]['interfaces']:
                        self.logger.warning("No port match found to "
                                            "mirror from in the configs")
                        ok = False
                    if not self.mirror_ports[switch_found] in obj_doc['dps'][switch_found]['interfaces']:
                        self.logger.warning("No port match found to "
                                            "mirror to in the configs")
                        ok = False
                    else:
                        if 'mirror' in obj_doc['dps'][switch_found]['interfaces'][port]:
                            self.logger.info("Mirror port already set to "
                                             "mirror something, removing "
                                             "old mirror setting")
                            del obj_doc['dps'][switch_found]['interfaces'][port]['mirror']
            if ok:
                obj_doc['dps'][switch_found]['interfaces'][port]['mirror'] = self.mirror_ports[switch_found]
            else:
                self.logger.error("Unable to mirror due to warnings")
                return False
        elif action == 'unmirror':
            # TODO
            pass
        elif action == 'shutdown':
            # TODO
            pass
        else:
            self.logger.warning("Unknown action: " + action)

        # ensure that dp_id gets written as a hex string
        for sw in obj_doc['dps']:
            try:
                obj_doc['dps'][sw]['dp_id'] = HexInt(obj_doc['dps'][sw]['dp_id'])
            except Exception as e:
                pass

        stream = open(config_file, 'w')
        yaml.add_representer(HexInt, representer)
        yaml.dump(obj_doc, stream, default_flow_style=False)

        return True

    def events(self, event):
        # TODO
        pass

    def log(self, log_file):
        mac_table = {}
        # NOTE very fragile, prone to errors
        if log_file:
            with open(log_file, 'r') as f:
                for line in f:
                    if 'L2 learned' in line:
                        learned_mac = line.split()
                        data = {'ip-address': learned_mac[16][0:-1],
                                'ip-state': 'L2 learned',
                                'mac': learned_mac[10],
                                'segment': learned_mac[7][1:-1],
                                'port': learned_mac[19],
                                'tenant': learned_mac[21] + learned_mac[22]}
                        if learned_mac[10] in mac_table:
                            dup = False
                            for d in mac_table[learned_mac[10]]:
                                if data == d:
                                    dup = True
                            if dup:
                                mac_table[learned_mac[10]].remove(data)
                            mac_table[learned_mac[10]].insert(0, data)
                        else:
                            mac_table[learned_mac[10]] = [data]
        return mac_table

