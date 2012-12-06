#!/usr/bin/env python

import unittest
import os, sys, subprocess, time

mpulse_path = os.path.abspath("../")
sys.path.append(mpulse_path)

from mpulse_agent import MPulseAgent, MPulseAgentError
from common.daemonize import Daemon

class TestAgentConfiParser(unittest.TestCase):
    """ Testing configuration file parsing """

    missing_opt_conf = """
[agent]
host = localhost

[mysql]
socket=/var/lib/mysql/mysql.sock
user=my_user
password=my_pass
"""
    missing_section_conf = """
[mysql]
socket=/var/lib/mysql/mysql.sock
user=my_user
password=1234
"""

    wrong_option_type = """
[agent]
host = localhost
port = 31415www
[mysql]
socket = /var/lib/mysql/mysql.sock
user = my_user
password = my_password
"""
    def testValidConfigFile(self):
        # Test if valid confi is parse fine
        # Also this test read from real file
        agent = MPulseAgent("files/valid.cnf")
        self.assertEqual(agent.agent_host, "localhost")
        self.assertEqual(agent.agent_port, 31415)
    
    def testMissingOpt(self):
        # Test if missin option raised correct exception
        with self.assertRaises(MPulseAgentError):
            agent = MPulseAgent("blah", self.missing_opt_conf)

    def testMissingSection(self):
        # Test if missing section raised correct exception
        with self.assertRaises(MPulseAgentError):
            agent = MPulseAgent("blah", self.missing_section_conf)
   
    def testWrongOptionType(self):
        # Test that wrong value for 'port' option raises proper exception
        with self.assertRaises(MPulseAgentError):
            agent = MPulseAgent("blah", self.wrong_option_type)

class TestDaemonize(unittest.TestCase):
    # This is even not a real unit test :) It's more like a functional
    # test where we call an external program and make sure it produces expected
    # results and effects. Not very nice, but I had to test Deamonize class
    # at leat in this way.

    pid_path = mpulse_path+"/tests/files/test_daemon.pid"

    def startDaemon(self):
        out = subprocess.call(["python",mpulse_path+\
            "/tests/daemon_test.py","start"])
        # Need to make sure process is completely daemonized
        time.sleep(0.05)
        return out

    def stopDaemon(self):
        out = subprocess.call(["python",mpulse_path+\
            "/tests/daemon_test.py","stop"])
        return out

    def getPID(self):
        pid = int(file(self.pid_path,'r').read().strip())
        return pid

    def testDaemonStartStopNormal(self):
        # Start daemon and make sure pid file is there
        out = self.startDaemon()    
        self.assertEqual(os.path.exists(self.pid_path), True)
        self.assertEqual(out, 0)
        pid = self.getPID()
        # This tests if process exisst. Will raise OSError if not
        os.kill(pid, 0)
        # Stop daemon and make sure pid and process are both gone
        out = self.stopDaemon()
        self.assertEqual(os.path.exists(self.pid_path), False)
        self.assertEqual(out, 0)
        with self.assertRaises(OSError):
            os.kill(pid, 0)

    def testStartWhenAlreadyRunning(self):
        # Start daemon twice and make sure nothing bad happens
        out = self.startDaemon()
        out = self.startDaemon()
        self.assertEqual(os.path.exists(self.pid_path), True)
        self.assertEqual(out, 1)
        # This will fail if process is not there
        os.kill(self.getPID(),0)
        self.stopDaemon()

    def testStopWhenNotRunning(self):
        # Stop daemon which is not running. In current implementation this
        # return error -- sys.exit(0). This makes Daemon.restart() 
        # work properly
        out = self.stopDaemon()
        self.assertEqual(out, 0)


if __name__ == "__main__":
    unittest.main()
