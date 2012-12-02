#!/usr/bin/env python

import SocketServer
import logging
import ConfigParser
import io

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
        print "Recieved line %s from client %s" % (self.data,\
            format(self.client_address[0]))
        self.request.sendall("OK")


class MPulseAgent():
    """ Class for MPulse Agent. It's task is to poll MySQL status and respond
    to requests from MPulseMonitor
    """

    def __init__(self, config_file, configstream=None):
        self.parse_config(config_file, configstream)

    def parse_config(self,config_file, configstream):
        config = ConfigParser.RawConfigParser()
        # This is kinda ugly, but allow to send strings instead of real files
        # in unit tests
        if configstream:
            config.readfp(io.BytesIO(configstream))
        else:
            config.read(config_file)
        # Validate configuration file
        config_structure = {"agent":["host","port"],\
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
        self.agent_host = config.get("agent","host")
        try:
            self.agent_port = config.getint("agent","port")
        except ValueError:
            raise MPulseAgentError("Integer value expected for option 'port'")

    


if __name__ == "__main__":
    try:
        agent = MPulseAgent("agent.cnf")
    except MPulseAgentError, e:
        print e.message
        exit(1)

    # Sample code invoking TCP server
    #server = SocketServer.TCPServer((HOST, PORT), MonitorTCPHandler)
    # Activate the server; this will keep running until you                
    # interrupt the program with Ctrl-C
    #server.serve_forever()
