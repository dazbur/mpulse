#!/usr/bin/env python

import unittest
import os, sys

mpulse_path = os.path.abspath("../")
sys.path.append(mpulse_path)

from mpulse_agent import MPulseAgent, MPulseAgentError

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
        


if __name__ == "__main__":
    unittest.main()
