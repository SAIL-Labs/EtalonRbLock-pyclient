#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 09:50:55 2016

@author: chrisbetters
"""

import os
from os.path import expanduser
import paramiko
from app import erlBase


class remoteexecutor(erlBase):
    stdout = []
    stderr = []
    stdin = []

    def __init__(self, rpserver):
        erlBase.__init__(self)
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(rpserver, username='root', key_filename=os.path.join(expanduser("~"), '.ssh', 'id_rsa.pub'))

    def startserver(self, clientip, pidmode=1, aquisitionsize=20000):
        options = " ".join(map(str, ['-i', clientip, '-m', pidmode, '-a', aquisitionsize]))

        self.stdin, self.stdout, self.stderr = self.client.exec_command('killall EtalonRbLock-server')

        self.logger.debug('EtalonRbLock-server was running. Process started/restarted with new options: ' + options)

        cmd = "bash ~/EtalonRbLock-server/start-server.sh  '~/EtalonRbLock-server/EtalonRbLock-server " + options + "'"
        self.stdin, self.stdout, self.stderr = self.client.exec_command(cmd)

        print(self.stdout.readlines())

        ## ps aux | grep EtalonRbLock-server | grep -v grep

    def __del__(self):
        self.client.close()


if __name__ == '__main__':
    exec = remoteexecutor('redpitaya1.sail-laboratories.com')

    exec.startserver('10.66.101.131', 1, 20000)
