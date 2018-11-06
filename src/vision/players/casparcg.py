import socket
import logging
import xml.etree.ElementTree as ET

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

    def _read_reply(self):
        response = self.socket.recv(3)

        try:
            return_code = int(response)
        except ValueError:
            raise ValueError('Did not receive numeric return code from CasparCG')

        while response[-2:] != '\r\n':
            response += self.socket.recv(1)

        logging.debug('CasparCG replied %s' % (response,))

        response = ''
        
        # From the AMCP spec:
        #
        # 200 [command] OK - The command has been executed and several lines of
        # data (seperated by \r\n) are being returned (terminated with an
        # additional \r\n) 
        #
        # 201 [command] OK - The command has been executed and
        # data (terminated by \r\n) is being returned.
        # 
        # 202 [command] OK - The command has been executed.        
        
        if return_code == 200: # multiline returned_data
            returned_data_buffer = ''

            while returned_data_buffer[-4:] != '\r\n\r\n':
                returned_data_buffer += self.socket.recv(512)

            returned_data = returned_data_buffer.splitlines()[:-1]

        elif return_code == 201: # single-line returned_data
            returned_data = ''
            while returned_data[-2:] != '\r\n':
                returned_data += self.socket.recv(512)

        elif return_code == 202: # no data returned
            returned_data = None

        else:
            raise ValueError('CasparCG command failed: ' + response)

        return returned_data

    def _send_command(self, command, xmlreply=False):
        self.socket.send("%s\r\n" % command)
        logging.debug("sending command %s" % (command,))
        return self._read_reply()

    def _get_info(self):
        raise NotImplementedError("I'm not done with this function yet")
        channels = {}
        for line in self._send_command('INFO'):
            (channel_id, video_standard, status) = line.split(' ', 3)
            channels[int(channel_id)] = {'standard': video_standard, 'status': status}

        for channel_id in channels.keys():
            xml_string = self._send_command('INFO %d' % (channel_id,))
            for i, num in enumerate(xml_string.splitlines()):
                print i, num
            # This hack needs doing because CasparCG emits malformed 
            # XML: (<|</)(?P<number>[0-9]?)>
            #root = ET.fromstring(xml_string)

    @property
    def layers(self):
        pass

if __name__ == '__main__':
    c = CasparCG()
    c.connect('localhost')
    #print(c._send_command('INFO 1-50'))
    c._get_info()
