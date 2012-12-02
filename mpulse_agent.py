#!/usr/bin/env python

import SocketServer,socket
import logging
import ConfigParser
import io, os, sys

from common.daemonize import Daemon
from common.globals import DATE_FORMAT,LOG_FORMAT

class MPulseAgentError(Exception):
    """ Base class for MPulseAgent Exceptions """
    
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

# This is just a placeholder with sample TCP scoket server code
class MonitorTCPHandler(SocketServer.StreamRequestHandler):
    
    def handle(self):
        # self.rfile is a file-like object created by the handler;
        self.data = self.rfile.readline()
        logging.debug("Recieved line %s from client %s" % (self.data,\
            format(self.client_address[0])))
        self.request.sendall("OK")


class MPulseAgent(Daemon):
    """ Class for MPulse Agent. It's task is to poll MySQL status and respond
    to requests from MPulseMonitor
    """
    def __init__(self, config_file, configstream=None):
        self.parse_config(config_file, configstream)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Need to call constructor of the Daemon class as well
        super(MPulseAgent, self).__init__(script_dir+'/agent.pid')
        # Init log file
        logging.basicConfig(filename=self.agent_log, level=logging.DEBUG,\
            format=LOG_FORMAT, datefmt=DATE_FORMAT)


    def parse_config(self,config_file, configstream):
        config = ConfigParser.RawConfigParser()
        # This is kinda ugly, but allows to send strings instead of real files
        # in unit tests
        if configstream:
            config.readfp(io.BytesIO(configstream))
        else:
            config.read(config_file)
        # Validate configuration file
        config_structure = {"agent":["host","port","log"],\
            "mysql":["socket","user","password"]}
        # TODO: We may want to raise different exceptions for sections and
        # options not found
        for section in config_structure.keys():
            if not config.has_section(section):
                raise MPulseAgentError("No section %s found in config file"\
                    % section)
            for option in config_structure[section]:
                if not config.has_option(section, option):
                    raise MPulseAgentError("""No option '%s' 
                        found in section [%s]""" % (option, section))
        self.agent_host = config.get("agent", "host")
        self.agent_log = config.get("agent", "log")
        try:
            self.agent_port = config.getint("agent","port")
        except ValueError:
            raise MPulseAgentError("Integer value expected for option 'port'")

    def run(self):
        """ This method overrides run() of Daemon class and is called when
        Daemon.start() or Daemon.restart() is called
        """
        # Initialize TCP server and start serving!
        try:
            self.TCPServer = SocketServer.TCPServer((self.agent_host,\
                self.agent_port), MonitorTCPHandler)
        except socket.error:
            logging.error("Failed to start agent on port %d. Address already in use"\
                % self.agent_port)
            raise MPulseAgentError("Failed to start server")
        logging.info("Started agent on %s port %d" % (self.agent_host,\
            self.agent_port))
        self.TCPServer.serve_forever()
        
if __name__ == "__main__":
    try:
        agent = MPulseAgent("agent.cnf")
    except MPulseAgentError, e:
        print e.message
        sys.exit(2)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            agent.start()
        elif 'stop' == sys.argv[1]:
            agent.stop()
        else:
            print "Uknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print  "usage: %s start|stop" % sys.argv[0]
        sys.exit(2)
