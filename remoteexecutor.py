#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 09:50:55 2016

@author: chrisbetters
"""

from subprocess import Popen, PIPE
import subprocess
from threading import Thread
try:
    from Queue import Queue, Empty 
except:
    from queue import Queue, Empty 
import time
import atexit

class remoteexecutor:
    
    def __init__(self,cmd):
        self.io_q = Queue()
        self.proc = Popen( cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        atexit.register(self.proc.kill)
    
#        Thread(target=self.stream_watcher, name='stdout-watcher',
#               args=('STDOUT', self.proc.stdout)).start()
#        Thread(target=self.stream_watcher, name='stderr-watcher',
#               args=('STDERR', self.proc.stderr)).start()
#        Thread(target=self.printer, name='printer').start()
        
        
    def stream_watcher(self,identifier, stream):
        for line in stream:
            self.io_q.put((identifier, line))
    
        if not stream.closed:
            stream.close()
            
      
    def printer(self):
        while True:
            try:
                # Block for 1 second.
                item = self.io_q.get(True, 1)
            except Empty:
                # No output in either streams for a second. Are we done?
                if self.proc.poll() is not None:
                    break
            else:
                identifier, line = item
                print(identifier + ':', line)
                
#    def __del__(self):
#        print('Proc Ending')
#        self.proc.kill()
        
    def close(self):
        #self.proc.kill()
        self.proc.terminate()
        #self.proc.send_signal()
        #print('Proc Ended ' + str(self.proc.returncode))
        
if __name__ == '__main__':
    exec=remoteexecutor(["ssh","-t","-t","root@10.66.101.121", "~/RpRbDAQ/UDPStreamer"])
    time.sleep(10)
    exec.close()
        
        