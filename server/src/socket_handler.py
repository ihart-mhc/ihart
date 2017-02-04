"""
Handles connecting to client applications and sending information about events.
"""

import socket   # the only module needed for all our socket interactions
import sys      # so that we can exit()

class SocketHandler():

    """
    Manages a non-blocking server socket: searches for incoming connections (checkIncomingConnections)
    and sends messages to all found connections (sendInformation).
    """

    server_socket = None
    clients = []
    message = None
    host = None
    port = 0

    def __init__(self, host='', port=5204):
        """
        Creates a server socket with the specified host and port number.
        Sets the socket to non-blocking, and sets it to listen for connections.
        @param host: The host address. Default value: ''
                     (gives the socket local address)
        @param port: The port number. Default value: 5204
                     (the port number of the majority of python applications)
        @return: none
        """

        self.port = port
        self.host = host
        # Create the socket.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Attempt to bind the socket to the host and port
            # (Until this is done, one cannot do anything with the socket.)
            self.server_socket.bind((self.host, self.port))
        except socket.error, message:
            # If the binding failed, exit.
            # (If the binding fails,  don't panic--if you run the code and it fails,
            # it is quite possible that if you wait a few moments and run it again,
            # it will work. A failure does not necessarily mean that something is
            # wrong with the host and the port number.)
            sys.exit()

        # Sets the server to non blocking. The server needs to check for connections
        # frequently so that all incoming requests are found, but it is quite possible
        # that there will be no requests; in this instance, we want to continue executing
        # instead of waiting for a connection (this is the default setting).
        #
        # Set the socket to listen for up to 10 incoming connections.
        self.server_socket.setblocking(0)
        self.server_socket.listen(10)

    def checkIncomingConnections(self):
        """
        Accepts a waiting socket connection and add it to the list of clients
        to send information to. If there is no waiting connection, do nothing.
        (This is a non-blocking call.)
        @return: none
        """

        try:
            # Accept any waiting socket connections and add them to the client list.
            client, address = self.server_socket.accept()
            if client is not None:
                self.clients.append(client)
        except socket.error, error:
            # If there were no waiting connections, do nothing.
            return

    def sendInformation(self, message):
        """
        Sends the specified message to every socket connection (every item of self.clients).
        If a connection has exited, catch the error and remove it from the list.
        @param message: The message to send to each waiting client.
        @return: none
        """

        toRemove = []
        # Send the message to each client; add each exited client to toRemove.
        for client in self.clients:
            try:
                client.sendall(message)
            except socket.error:
                # A socket.error will be thrown when we try to send a message to
                # a socket connection that has exited. Add the connection to
                # our list to remove after we're done iterating through the
                # list of clients.
                toRemove.append(client)

        # Remove each item in toRemove from self.clients
        for remove in toRemove:
            self.clients.remove(remove)
