# Given a socket that is expected to receive a message formatted with the protocol for this program,
# get the message and parse it into a list. If the connection closes, it will raise an EOFError.
# If the data received from the socket contains only whitespace, it will ignore the sent data and wait for
# another message; thus the returned list will always contain at least 1 element.

import sys
sys.dont_write_bytecode=True

if __name__ == '__main__':
   print 'Error: this is an import and should not be run standalone'
   sys.exit(1)

import socket

def get_message(connection):
   rlist = []
   while len(rlist) < 1:
      data = connection.recv(1024)
      if not data:
         raise EOFError("Connection closed")

      rlist = data.split()

   return rlist

