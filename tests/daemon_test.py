# Very simple test program which starts/stop a deamon
# Used in TestDaemonize unit test class

import os, sys, time

test_path = os.path.abspath("../")
sys.path.append(test_path)

from common.daemonize import Daemon

class TestDaemon (Daemon):

	def run(self):
		while True:
			time.sleep(1)

daemon =\
	TestDaemon(test_path+"/tests/files/test_daemon.pid")
if sys.argv[1] == "start":
	daemon.start()
if sys.argv[1] == "stop":
	daemon.stop()