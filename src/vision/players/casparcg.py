import socket
import logging

class CasparCG:
    def __init__(self):
        self.socket = None

    def disconnect(self):
        self.socket.close()
        self.socket = None

    def connect(self, hostname, amcp_port = 5250):
        self.hostname = hostname
        self.amcp_port = amcp_port
        if self.socket is not None:
            self.disconnect()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.hostname, self.amcp_port))

    def _send_command(self, command, xmlreply=False):
        self.socket.send("%s\r\n" % command)
        logging.debug("sending command %s" % (command,))
        bufsize = 4096
        response = self.socket.recv(bufsize)
        # FIXME add code to split response in first line and the rest
        return (response, None)

if __name__ == '__main__':
    c = CasparCG()
    c.connect('localhost')
    print(c._send_command('CLS'))
