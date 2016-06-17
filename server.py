# 
import sys
import socket
import thread
import time

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

def p1thread(conn):
   conn.send('sdfsdf\n');

   data = conn.recv(1024)
   while True:
      data = conn.recv(1024)
      if not data:
         break
      conn.sendall('fdsfds\n')
   print 'Connection 1 closed'

def p2thread(conn):
   conn.send('sdfsdf\n');

   data = conn.recv(1024)
   while True:
      data = conn.recv(1024)
      if not data:
         break
      conn.sendall('fdsfds\n')
   print 'Connection 2 closed'

p1conn, p1addr = s.accept()
print 'Accepted connection from', p1addr
thread.start_new_thread(p1thread, (p1conn,))

p2conn, p2addr = s.accept()
print 'Accepted connection from', p2addr
thread.start_new_thread(p2thread, (p2conn,))

print 'Now past creating threads'

while 1:
   time.sleep(1)
