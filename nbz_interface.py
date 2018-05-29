#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: <Zurdi>


import sys
import os
import argparse
import pickle
from pprint import pprint

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(BASE_DIR, 'lib'))
sys.path.append(os.path.join(BASE_DIR, 'data'))
sys.path.append(os.path.join(BASE_DIR, 'parser'))

from nbz_core import NBZCore
from lib_log_nbz import Logging
logger = Logging()
from parser_nbz import NBZParser
from natives import NATIVES


class NBZInterface:


    def __init__(self, script, mode, debug=True):

        # Attributes
        self.core_attributes = {
            'instruction_set'   : '',
            'variables'         : {},
            'NATIVES'           : NATIVES,

            'script'            : script,
            'script_name'       : os.path.basename(script)[0:-4], # Avoiding file extension
            'mode'              : mode,
            'debug'             : debug,

            'proxy_path'        : '{base_dir}/proxy/bin/browsermob-proxy'.format(base_dir=BASE_DIR),  # Proxy binaries to execute the sniffer
            'set_browser'       : False, # Flag to instance browser once (even if z_code has more than one instance)
            'server'            : None,
            'proxy'             : None,
            'browser'           : None,

            'set_net_report'    : False,
            'net_reports_path'  : '',
            'complete_csv_path' : '',
            'complete_csv'      : None,
        }

        # Execute selected mode
        if self.core_attributes['mode'] == 'cx':
            self.compile_z_code()
            self.get_z_code()
        elif self.core_attributes['mode'] == 'c':
            self.compile_z_code()
            logger.log('NOTE', 'Successful compilation of {script}'.format(script=self.core_attributes['script']))
            sys.exit(0)
        elif self.core_attributes['mode'] == 'x':
            self.get_z_code()
        else:
            logger.log('ERROR', 'Not defined compile/execution mode {mode}'.format(mode=self.core_attributes['mode']))
            sys.exit(-1)

        # Instance core class and execute instructions
        nbz_core = NBZCore(self.core_attributes)

        # Return all core attributes to close needed
        self.core_attributes = NBZCore.get_attributes(nbz_core)

        # Close browser/proxy/server
        if self.core_attributes['set_browser']:
            self.close_all()


    def compile_z_code(self):
        """
        Compile z_code into object file ready to be executed
        """

        NBZParser(self.core_attributes['script'])


    def get_z_code(self):
        """
        Get the compiled z_code object file
        """

        try:
            with open('{script}code'.format(script=self.core_attributes['script'])) as zcode:
                self.core_attributes['instruction_set'] = pickle.load(zcode)
            with open('{script}vars'.format(script=self.core_attributes['script'])) as zcode_vars:
                self.core_attributes['variables'] = pickle.load(zcode_vars)
            if self.core_attributes['debug']:
                logger.log('NOTE', 'Instructions: {instructions}'.format(instructions=self.core_attributes['instruction_set']))
                logger.log('NOTE', 'Variables: {variables}'.format(variables=self.core_attributes['variables']))
        except Exception as e:
            logger.log('ERROR', 'Script not compiled ({script}): {exception}'.format(script=self.core_attributes['script'], exception=e))
            sys.exit(-1)


    def close_all(self):
        """
        Close all connections and export har log
        """

        if self.core_attributes['set_net_report']:
            self.core_attributes['complete_csv'].write('URL: {url}\n\n'.format(url=self.core_attributes['browser'].current_url))
            pprint(self.core_attributes['proxy'].har['log']['entries'], self.core_attributes['complete_csv'])
            self.core_attributes['complete_csv'].close()
            logger.log('NOTE', 'Complete_net csv file exported to: {net_report_csv}'.format(net_report_csv=self.core_attributes['complete_csv'].name))
        self.core_attributes['browser'].close()
        self.core_attributes['proxy'].close()
        self.core_attributes['server'].stop()
        logger.log('NOTE', 'Connections closed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-script", help="script file", required=True)
    parser.add_argument("-mode", help="compile/execution mode: -c (compile only) -x (execution only) -cx (compile & execution)", required=True)
    parser.add_argument("-debug", help="debug mode", required=False)
    args = parser.parse_args()
    script = args.script
    mode = args.mode
    debug = args.debug
    if debug == 'false':
        debug = False
    else:
        debug = True
    NBZInterface(script, mode, debug)


if __name__ == "__main__":
    sys.exit(main())