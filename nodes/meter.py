# Node definition for a meter

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import json
import node_funcs

LOGGER = polyinterface.LOGGER

# UOM's
#  kW 30
#  kWH 33
#  amps 1   CC
# power factor 53
# volts 72
# watt 73
# watt-hour 119
# hertz 90

# CPW current power used
# CV current voltage
# PF power factor
# PPW Polarized power used
# TPW total power used


@node_funcs.add_functions_as_methods(node_funcs.functions)
class MeterNode(polyinterface.Node):
    id = 'meter'
    drivers = [
            {'driver': 'CPW', 'value': 0, 'uom': 73},   # instant power
            {'driver': 'GV0', 'value': 0, 'uom': 73},   # reactive power
            {'driver': 'GV1', 'value': 0, 'uom': 73},   # apparent power
            {'driver': 'GV2', 'value': 0, 'uom': 119},  # exported
            {'driver': 'GV3', 'value': 0, 'uom': 119},  # imported
            {'driver': 'GV4', 'value': 0, 'uom': 90},   # frequency
            {'driver': 'CV', 'value': 0, 'uom': 72},    # average volts
            {'driver': 'CC', 'value': 0, 'uom': 1},     # total current
            {'driver': 'GV5', 'value': 0, 'uom': 1},    # i_a current
            {'driver': 'GV6', 'value': 0, 'uom': 1},    # i_b current
            {'driver': 'GV7', 'value': 0, 'uom': 1},    # i_c current
            ]

    def update_node(self, data, force):

        if 'instant_power' in data:
            self.update_driver('CPW', data['instant_power'], force, prec=3)
        if 'instant_reactive_power' in data:
            self.update_driver('GV0', data['instant_reactive_power'], force, prec=3)
        if 'instant_apparent_power' in data:
            self.update_driver('GV1', data['instant_apparent_power'], force, prec=3)
        if 'frequency' in data:
            self.update_driver('GV2', data['frequency'], force, prec=3)
        if 'energy_exported' in data:
            self.update_driver('GV3', data['energy_exported'], force, prec=3)
        if 'energy_imported' in data:
            self.update_driver('GV4', data['energy_imported'], force, prec=3)
        if 'instant_average_voltage' in data:
            self.update_driver('CV', data['instant_average_voltage'], force, prec=3)
        if 'instant_total_current' in data:
            self.update_driver('CC', data['instant_total_current'], force, prec=3)
        if 'i_a_current' in data:
            self.update_driver('GV5', data['i_a_current'], force, prec=3)
        if 'i_b_current' in data:
            self.update_driver('GV6', data['i_b_current'], force, prec=3)
        if 'i_c_current' in data:
            self.update_driver('GV7', data['i_c_current'], force, prec=3)

