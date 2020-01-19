## a very basic event-driven IRC client

# helpful resources:
# https://tools.ietf.org/html/rfc1459 - the full IRC spec
# https://stackoverflow.com/a/822788/197772 - socket line buffering
#
# https://github.com/jaraco/irc - full IRC client in Python
# consider using the client or simple bot implementation

import re
import sys
import socket
import threading
import logging

# TODO need more error handling for events and daemon execution

################################################################################
# modified from https://stackoverflow.com/a/2022629/197772
class Event(list):

    #---------------------------------------------------------------------------
    def __iadd__(self, handler):
        self.append(handler)
        return self

    #---------------------------------------------------------------------------
    def __isub__(self, handler):
        self.remove(handler)
        return self

    #---------------------------------------------------------------------------
    def __call__(self, *args, **kwargs):
        for handler in self:
            handler(*args, **kwargs)

    #---------------------------------------------------------------------------
    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)

################################################################################
class LineBuffer():

    #---------------------------------------------------------------------------
    def __init__(self):
        self.logger = logging.getLogger('irc.LineBuffer')

        self._buffer = None
        self._lock = threading.Lock()

    #---------------------------------------------------------------------------
    def __iter__(self):
        return self

    #---------------------------------------------------------------------------
    def __len__(self):
        self._lock.acquire()

        if self._buffer is None:
            size = 0
        else:
            size = len(self._buffer)

        self._lock.release()
        return size

    #---------------------------------------------------------------------------
    def __next__(self):
        line = self.next()

        if line is None:
            raise StopIteration()

        return line

    #---------------------------------------------------------------------------
    def __iadd__(self, text):
        if text is None:
            return self

        self.append(text)

        return self

    #---------------------------------------------------------------------------
    def _unsafe_next_split(self):
        if self._buffer is None:
            self.logger.debug(': empty buffer')
            return None

        if not "\n" in self._buffer:
            return None

        # grab the current line and remaining buffer
        (line, newbuf) = self._buffer.split("\n", 1)

        # remove carriage returns if present
        line = line.rstrip("\r")

        # setup remaining buffer if there is any left
        self._buffer = newbuf if len(newbuf) > 0 else None

        return line

    #---------------------------------------------------------------------------
    def next(self):
        self._lock.acquire()
        line = self._unsafe_next_split()
        self._lock.release()

        # python2 requires us to raise here...
        if sys.version_info < (3, 0) and line is None:
            raise StopIteration()

        return line

    #---------------------------------------------------------------------------
    def append(self, text):
        self._lock.acquire()

        if self._buffer is None:
            self._buffer = text
        else:
            self._buffer += text

        self.logger.debug(': added %d bytes to socket buffer: total %d bytes',
                          len(text), len(self._buffer))

        self._lock.release()

################################################################################
# works much like a LineBuffer, but assumes incoming data is encoded
class SocketLineBuffer(LineBuffer):

    #---------------------------------------------------------------------------
    def __init__(self):
        LineBuffer.__init__(self)
        self.logger = logging.getLogger('irc.SocketLineBuffer')

    #---------------------------------------------------------------------------
    def __iadd__(self, data):
        if data is None:
            return self

        # TODO should we check for different encodings?
        text = data.decode()
        self.append(text)

        return self

################################################################################
# a simple event-based IRC client
#
# the client will, by default, start a thread when calling connect() to handle
# server messages and PING responses.  if the caller disables the daemon, it
# must invoke the communicate() method directly in order to generate events and
# respond to PING requests.
#
# Events => Handler Function
#   on_welcome => func(client, msg)
#   on_connect => func(client)
#   on_quit => func(client, msg)
#   on_error => func(client, msg)
#   on_ping => func(client, txt)
#   on_privmsg => func(client, sender, recip, msg)
#   on_notice => func(client, sender, recip, msg)
#   on_join => func(client, channel)
#   on_part => func(client, channel, msg)
class Client():

    #---------------------------------------------------------------------------
    # Client initialization
    #   nick: the nickname used by this client
    #   name: the full name used by this client
    #   daemon: start a daemon to manage server messages
    def __init__(self, nick, name, daemon=True):
        self.logger = logging.getLogger('irc.Client')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = nick
        self.fullname = name

        self.recvbuf = SocketLineBuffer()
        self.connected = False

        if (daemon is True):
            self.daemon = threading.Thread(name='IRC.Client.Daemon',
                                           target=self.communicate)
            self.daemon.setDaemon(True)
        else:
            self.daemon = None

        # initialize event handlers
        self.on_welcome = Event()
        self.on_connect = Event()
        self.on_quit = Event()
        self.on_error = Event()
        self.on_ping = Event()
        self.on_privmsg = Event()
        self.on_notice = Event()
        self.on_join = Event()
        self.on_part = Event()

        # self-register for events we care about
        self.on_ping += self._on_ping
        self.on_error += self._on_error

    #---------------------------------------------------------------------------
    # send a message to the connected server followed by a newline
    #   msg: the message to send to the server
    def _xmit(self, msg):
        if not self.connected:
            raise BrokenPipeError('not connected')

        try:
            data = msg.encode()
            self.sock.sendall(data)
        except socket.error:
            self._hangup()

    #---------------------------------------------------------------------------
    # receive the next block of data from the server
    def _recv(self):
        if not self.connected:
            raise BrokenPipeError('not connected')

        data = None

        # receive a block of data at a time
        try:
            data = self.sock.recv(4096)
        except socket.error:
            data = None

        if data is None or len(data) == 0:
            self._hangup()
            data = None

        return data

    #---------------------------------------------------------------------------
    # send a message to the connected server followed by a newline
    #   msg: the message to send to the server, supports string formatting
    #   args: variables for formatting placeholders in msg
    def _send(self, msg, *args):
        if not self.connected:
            return False

        fmsg = msg.format(*args)
        self.logger.debug(u'> %s', fmsg)

        self._xmit(fmsg + "\n")

    #---------------------------------------------------------------------------
    # close the connection; usually unexpectedly
    def _hangup(self):
        self.logger.warn(u'Connection reset by peer.')
        self.connected = False

    #---------------------------------------------------------------------------
    # generate events from the given server message
    #   msg: the full text of the server message
    def _dispatcher(self, msg):
        if msg is None: return

        if (msg.startswith(':')):
            txt = parse_user_message(msg)
            self._handle_message(txt)

        elif (msg.startswith('PING')):
            txt = parse_user_message(msg)
            self.on_ping(self, txt)

        elif (msg.startswith('ERROR')):
            txt = parse_user_message(msg)
            self.on_error(self, txt)

        else:
            self.logger.warn(u'Unknown message -- %s', msg)

    #---------------------------------------------------------------------------
    # handle general server messages
    #   msg: the message from the server
    def _handle_message(self, msg):
        (origin, name, content) = parse_server_message(msg)

        if (name == '001'):
            txt = parse_user_message(content)
            self.on_welcome(self, txt)

        elif (name == 'PRIVMSG'):
            recip = parse_first_word(content)
            txt = parse_user_message(content)
            self.on_privmsg(self, origin, recip, txt)

        elif (name == 'NOTICE'):
            recip = parse_first_word(content)
            txt = parse_user_message(content)
            self.on_notice(self, origin, recip, txt)

        elif (name == 'JOIN'):
            channel = parse_user_message(content)
            self.on_join(self, channel)

        elif (name == 'PART'):
            channel = parse_first_word(content)
            if (':' in content):
                txt = parse_user_message(content)
            else:
                txt = None
            self.on_part(self, channel, txt)

    #---------------------------------------------------------------------------
    # handle PING commands
    #   client: the client generating the event (should be self)
    #   txt: the server challenge text in the PING
    def _on_ping(self, client, txt):
        self._send('PONG :{0}', txt)

    #---------------------------------------------------------------------------
    # handle ERROR commands from the server - NOTE servers send ERROR on QUIT
    #   client: the client generating the event (should be self)
    #   msg: error message supplied by the server
    def _on_error(self, client, msg):
        self.logger.warn(msg)

    #---------------------------------------------------------------------------
    # connect this client to the given IRC server
    #   server: the address or hostname of the server
    #   port: the IRC port to connect to (default=6667)
    #   passwd: a password if required to access the server (default=None)
    def connect(self, server, port=6667, passwd=None):
        self.logger.debug(u'connecting to IRC server: %s:%d', server, port)
        self.sock.connect((server, port))

        self.connected = True

        # startup the daemon if configured...
        if (self.daemon): self.daemon.start()

        if (passwd is not None):
            self._send('PASS {0}', passwd)

        self._send('NICK {0}', self.nickname)
        self._send('USER {0} - {1}', self.nickname, self.fullname)

        # notify on_connect event handlers
        self.on_connect(self)

    #---------------------------------------------------------------------------
    # join this client to the given channel
    #   channel: the channel to join
    def join(self, channel):
        self._send('JOIN {0}', channel)

    #---------------------------------------------------------------------------
    # leave the given channel with a parting message
    #   channel: the channel to leave
    #   msg: a parting message
    def part(self, channel, msg):
        self._send('PART {0} :{1}', channel, msg)

    #---------------------------------------------------------------------------
    # send a private message to the intended recipient
    #   recip: the user or channel to receive the message
    #   msg: the text of the message
    def msg(self, recip, msg):
        self._send('PRIVMSG {0} :{1}', recip, msg)

    #---------------------------------------------------------------------------
    # set the mode of the given user or channel
    #   nick: the user nickname or channel name
    #   flags: the flags to set on the target
    def mode(self, nick, flags):
        self._send('MODE {0} {1}', nick, flags)

    #---------------------------------------------------------------------------
    # close the connection to the server and process all remaining server messages
    #   msg: an optional message to provide when quitting (default=None)
    def quit(self, msg=None):
        if (msg is None):
            self._send('QUIT')
        else:
            self._send('QUIT :{0}', msg)

        # wait for the deamon to exit...
        if (self.daemon is not None):
            self.daemon.join()

        # notify on_quit event handlers
        self.on_quit(self, msg)
        self.connected = False

        self.sock.close()
        self.logger.debug(u': connection closed')

    #---------------------------------------------------------------------------
    # this method is blocking and should usually be called on a separate thread.
    # process server messages and generate events as needed until interrupted
    def communicate(self):
        more = self._recv()

        # keep reading data from the server...
        while (more is not None):
            self.recvbuf += more

            # process all lines we just received...
            for line in self.recvbuf:
                self.logger.debug(u'< %s', line)
                self._dispatcher(line)

            more = self._recv()

################################################################################
# utility methods for parsing IRC messages

#---------------------------------------------------------------------------
# parse regular server messages into: origin, name, payload
def parse_server_message(content):
    # TODO add error checking
    return content.split(' ', 2)

#---------------------------------------------------------------------------
# return the user message portion of the supplied content -- this is all
# text after the first colon (:) in the data
def parse_user_message(content):
    # TODO add error checking
    return content.split(':', 1)[1]

#---------------------------------------------------------------------------
# return the first word in the given content, breaking at whitespace
def parse_first_word(content):
    # TODO add error checking
    return content.split(' ', 1)[0]

