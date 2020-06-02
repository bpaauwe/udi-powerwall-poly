#!/usr/bin/env python3
"""
Polyglot v2 node server Tesla Powerwall data
Copyright (C) 2020 Robert Paauwe
"""

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import datetime
import requests
import socket
import math
import re
import json
import node_funcs
from datetime import timedelta
from nodes import meter

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(polyinterface.Controller):
    id = 'powerwall'
    hint = [0,0,0,0]
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'PowerWall'
        self.address = 'pw'
        self.primary = self.address
        self.configured = False
        self.token = ''
        self.force = True

        self.params = node_funcs.NSParameters([{
                'name': 'IP Address',
                'default': 'set me',
                'isRequired': True,
                'notice': 'Tesla gateway IP address must be set',
            },
            {
                'name': 'Serial Number',
                'default': 'set me',
                'isRequired': True,
                'notice': 'Tesla gateway serial number must be set',
            },
            {
                'name': 'Password',
                'default': 'set me',
                'isRequired': True,
                'notice': 'Tesla gateway password must be set',
            },
            ])


        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        (valid, changed) = self.params.update_from_polyglot(config)
        if changed and not valid:
            LOGGER.debug('-- configuration not yet valid')
            self.removeNoticesAll()
            self.params.send_notices(self)
        elif changed and valid:
            LOGGER.debug('-- configuration is valid')
            self.removeNoticesAll()
            self.configured = True
        elif valid:
            LOGGER.debug('-- configuration not changed, but is valid')

    def start(self):
        LOGGER.info('Starting node server')
        self.check_params()
        self.discover()
        self.authenticate()
        LOGGER.info('Node server started')

        # Do an initial query to get filled in as soon as possible
        self.query_meters()
        self.force = False

    def longPoll(self):
        LOGGER.debug('longpoll')

    def shortPoll(self):
        self.query_meters()

    # Log into the gateway and get a token
    def authenticate(self):
        if not self.configured:
            LOGGER.info('Skipping authentication because we aren\'t configured yet.')
            return

        request = 'https://' + self.params.get('IP Address')
        request += '/api/login/Basic'

        c = requests.post(request, verify=False, json={'username':'', 'password':self.params.get('Password'), 'force_sm_off':false})

        jdata = c.json()
        c.close()
        LOGGER.debug(jdata)

        if 'token' in jdata:
            self.token = jdata['token']
            LOGGER.info('Authenticated')
        

    def query_meters(self):
        # Query for the meters aggregates.  I.E. grid, battery, load, solar
        # busway, frequency, generator

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return


        try:
            request = 'https://' + self.params.get('IP Address')
            request += '/api/meters/aggregates'

            c = requests.get(request, verify=False)
            jdata = c.json()
            c.close()
            LOGGER.debug(jdata)

            if jdata == None:
                LOGGER.error('Meter query returned no data')
                return

            # FIXME: call update_node in the actual of each type
            if 'site' in jdata:
                self.nodes['pw_grid'].update_node(jdata['site'])
            if 'battery' in jdata:
                self.nodes['pw_battery'].update_node(jdata['battery'])
            if 'load' in jdata:
                self.nodes['pw_load'].update_node(jdata['load'])
            if 'solar' in jdata:
                self.nodes['pw_solar'].update_node(jdata['solar'])
            if 'busway' in jdata:
                self.nodes['pw_busway'].update_node(jdata['busway'])
            if 'frequency' in jdata:
                self.nodes['pw_frequency'].update_node(jdata['frequency'])
            if 'generator' in jdata:
                self.nodes['pw_generator'].update_node(jdata['generator'])

        except Exception as e:
            LOGGER.error('gateway update failure')
            LOGGER.error(e)

        # needs to be authenticated
        try: 
            request = 'https://' + self.params.get('IP Address')
            request += '/api/operation'

            c = requests.get(request, headers={'Authorization':self.token}, verify=False)
            jdata = c.json()
            c.close()
            LOGGER.debug(jdata)

            if jdata == None:
                LOGGER.error('Operation query returned no data')
                return

            if 'mode' in jdata:
                if jdata['mode'] == 'self_consumption':
                    self.set_driver('GV8', 0)
                elif jdata['mode'] == 'backup':
                    self.set_driver('GV8', 1)
                elif jdata['mode'] == 'autonomous':
                    self.set_driver('GV8', 2)
                elif jdata['mode'] == 'scheduler':
                    self.set_driver('GV8', 3)


        except Exception as e:
            LOGGER.error('Operation query failure')
            LOGGER.error(e)

        # TODO: /api/system_status/soe (state of charge)
        # TODO: /api/system_status/grid_status 


    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        # Create any additional nodes here
        LOGGER.info("In Discovery...")

        node = meter.MeterNode(self, self.address, 'pw_grid', 'Grid')
        self.addNode(node)
        node = meter.MeterNode(self, self.address, 'pw_battery', 'Battery')
        self.addNode(node)
        node = meter.MeterNode(self, self.address, 'pw_load', 'Home')
        self.addNode(node)
        node = meter.MeterNode(self, self.address, 'pw_solar', 'Solar')
        self.addNode(node)
        node = meter.MeterNode(self, self.address, 'pw_busway', 'Busway')
        self.addNode(node)
        node = meter.MeterNode(self, self.address, 'pw_frequency', 'Frequency')
        self.addNode(node)
        node = meter.MeterNode(self, self.address, 'pw_generator', 'Generator')
        self.addNode(node)

    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    def check_params(self):
        self.removeNoticesAll()

        if self.params.get_from_polyglot(self):
            LOGGER.debug('All required parameters are set!')
            self.configured = True
        else:
            LOGGER.debug('Configuration required.')
            self.params.send_notices(self)


    def remove_notices_all(self, command):
        self.removeNoticesAll()

    def set_logging_level(self, level=None):
        if level is None:
            try:
                # level = self.getDriver('GVP')
                level = self.get_saved_log_level()
            except:
                LOGGER.error('set_logging_level: get saved log level failed.')

            if level is None:
                level = 30

            level = int(level)
        else:
            level = int(level['value'])

        # self.setDriver('GVP', level, True, True)
        self.save_log_level(level)
        LOGGER.info('set_logging_level: Setting log level to %d' % level)
        LOGGER.setLevel(level)

    def set_operation_mode(self, mode=None):
        LOGGER.info('set operation mode to ' + str(mode))

    commands = {
            'UPDATE_PROFILE': update_profile,
            'REMOVE_NOTICES_ALL': remove_notices_all,
            'OPERATION': set_operation_mode,
            'DEBUG': set_logging_level,
            }

    # For this node server, all of the info is available in the single
    # controller node.
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'GV8', 'value': 0, 'uom': 25}, # Operation
            ]


