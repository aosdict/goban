# 
import sys
import socket
import thread
import time
import goban

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = ''   # Symbolic name, meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port

try:
   s.bind( (HOST, PORT) )
except socket.error as err:
   print 'Bind failed:', str(err)

print 'Bound to port', PORT

# accept only 2 connections
s.listen(2)

# goban setup
gb = goban.goban(9)

def playerthread(conn, player_number):
   conn.send('sdfsdf\n');

   data = conn.recv(1024)
   while True:
      data = conn.recv(1024)
      if not data:
         # connection closed
         break

      cmdlist = data.split()
      cmd = cmdlist[0]
      args = cmdlist[1:]

      if cmd == 'PLAY':
         if len(args) != 2:
            conn.sendall('ERROR: Wrong number of arguments for PLAY\n')
         else:
            try:
               row = int(args[0])
               col = int(args[1])
            except ValueError:
               conn.sendall('ERROR: row/column argument for PLAY was not an int\n')
            try:
               gb.play(player_number, row, col)
               conn.sendall('SUCCESS: Play made at row '+row+', column '+col+'\n')
            except Exception as e:
               conn.sendall('ERROR: Goban error: '+str(e)+'\n')
      else:
         conn.sendall('ERROR: Unrecognized command '+cmd+'\n')

      # conn.sendall('fdsfds\n')
   print 'Connection 1 closed'


p1conn, p1addr = s.accept()
print 'Accepted connection from', p1addr
thread.start_new_thread(playerthread, (p1conn, 1))

p2conn, p2addr = s.accept()
print 'Accepted connection from', p2addr
thread.start_new_thread(playerthread, (p2conn, 2))

print 'Now past creating threads'

while 1:
   time.sleep(1)
