"""
Connects to the server to receive and parse information about events.
"""

import json # for message parsing
import select # for handling sockets
import socket # for communicating with the server

from blob import Blob
from cv_event_data import CVEventData


class CVManager:
    """
    Sets up a non-blocking connection to the server via sockets. New events can
    be retrieved via the getNewEvents() method.
    """

    _client_socket = None
    _connectionSucceeded = False

    def __init__(self, host="localhost", port=5204):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._client_socket.connect((host, port))

            # Make the socket non-blocking
            # (see http://docs.python.org/library/socket.html#socket.socket.setblocking)
            self._client_socket.setblocking(0)

            self._connectionSucceeded = True

        # If we can't connect, report the error; we can't really recover from
        # not being able to establish a connection, but we don't want to crash.
        except socket.error, e:
            print ">>> Unable to establish a connection with the iHart server:"
            print e


    def getNewEvents(self):
        """
        @return a list of CVEventData objects containing information about faces and
            motion (aka shells) detected by the server. The list will be in order the
            events arrived. The list will be empty if there was nothing to detect.
            None will be returned if the server sent no data, or if an error occurred.
        """
        # We can't do anything if the connection wasn't established
        if not self._connectionSucceeded:
            return None

        # Try to grab a message from the server and parse it into an event data
        # object.
        message = self._tryToReceiveEvents()
        if message:
            return self._parseMessage(message)
        else:
            return None


    def destroy(self):
        """
        Close the connection to the server.
        @return None
        """
        self._client_socket.close()


    def _tryToReceiveEvents(self):
        """
        If there is anything available from the server, grab it and parse it.

        See http://stackoverflow.com/questions/8386679/why-am-i-receiving-a-string-from-the-socket-until-the-n-newline-escape-sequence
        for using select with non-blocking sockets.

        @return a message sent from the server containing detected faces and
            motion (shells), or None if there was nothing to detect (or an
            error ocurred)
        """
        # See if the client socket is ready to be read from.
        read_ready, _, _ = select.select([self._client_socket], [], [])

        if self._client_socket in read_ready:
            # The socket has data ready to be received
            message = ""
            continue_recv = True
            while continue_recv:
                try:
                    # Try to receive som data
                    message += self._client_socket.recv(1024)
                except socket.error, e:
                    if e.errno != socket.errno.EWOULDBLOCK:
                        # Error! Print it and tell main loop to stop
                        print 'Error: %r' % e
                    # If e.errno is errno.EWOULDBLOCK, then no more data
                    continue_recv = False

            if message:
                return message

        # If we get to this point and haven't returned anything, there's
        # nothing to return (either socket wasn't ready or there was an error).
        return None


    def _parseMessage(self, message):
        """
        Parse a JSON message from the server. See createInformationString in
        http://ihart-mhc.github.io/software/data.html for details on the format
        of the message.
        """
        # Remove characters that the json parser doesn't like
        message = message.translate(None, "\0\r")

        # We might have received multiple event objects, which are separated by
        # newline characters.
        messages = message.split("\n")

        # Process each message into an object containing all of the event
        # information.
        events = []
        for message in messages:
            if not message:
                continue

            # TODO: wrap this in a try-except block in case the parsing fails?
            data = json.loads(message)
            numRoi = len(data)

            facesByRegion = []
            shellsByRegion = []

            # Process the blobs in each region of interest and store them in the
            # corresponding list.
            for roi, blobs in enumerate(data):
                facesByRegion.append([ Blob(b[0], b[1], b[2], b[3], roi, Blob.FACE) for b in blobs["Faces"] ])
                shellsByRegion.append([ Blob(b[0], b[1], b[2], b[3], roi, Blob.SHELL) for b in blobs["Shells"] ])

            events.append(CVEventData(facesByRegion, shellsByRegion, numRoi))

        return events




# For testing/development
if __name__ == "__main__":
    cvm = CVManager()
    for i in range(10):
        print cvm.getNewEvents()
    cvm.destroy()
