# system modules
import sys
import socket
import thread
import time
import goban
import select

# server modules
from get_message import get_message
from get_terms import get_terms

if __name__ != '__main__':
   print 'Error: server.py should only be run as the main module'
   sys.exit(1)

serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = ''   # Symbolic name, meaning all available interfaces
try:
   PORT = int(sys.argv[1])
except:
   PORT = 8888 # Arbitrary non-privileged port

try:
   serversock.bind( (HOST, PORT) )
except socket.error as err:
   print 'Bind failed:', str(err)
   sys.exit(1)

print 'Bound to port', PORT

# accept only 2 connections
serversock.listen(2)
print "Waiting for first player"

p1conn, p1addr = serversock.accept()
print 'Player 1 connected'

# the first connector gets to set the terms of the game
try:
   gobansize, p1_plays_black, handicap, komi = get_terms(p1conn)
except EOFError:
   print 'Connection closed before first player sent terms'
   sys.exit(1)

print 'Now waiting for second player'
p2conn, p2addr = serversock.accept()
print 'Accepted connection from', p2addr

terms_str = 'TERMS %s %s %s %s\n' % (gobansize, p1_plays_black, handicap, komi)
p1conn.send(terms_str)
p2conn.send(terms_str)

# tuple of whether a TERMSCONFIRM has been received, and its result if so
p1response = (False, None)
p2response = (False, None)
while p1response[0] == False or p2response[0] == False:
   read_socks, write_socks, err_socks = select.select([p1conn, p2conn], [], [])

   for sock in read_socks:
      response = get_message(sock)
      if response[0] != 'TERMSCONFIRM':
         print 'Expected TERMSCONFIRM, got', response[0]
         sock.send('ERROR TERMS must be answered with TERMSCONFIRM\n')
         continue
      if len(response) < 2:
         print 'Too few arguments to TERMSCONFIRM'
         sock.send('ERROR TERMSCONFIRM requires a second argument "no" or "yes"\n')
         continue
      if response[1] != 'no' and response[1] != 'yes':
         print 'Bad argument to TERMSCONFIRM', response[1]
         sock.send('ERROR argument of TERMSCONFIRM must be either "no" or "yes"')
         continue

      if sock == p1conn:
         p1response = (True, (response[1] == 'yes'))
         print 'Player 1 said', response[1], 'to the terms'
      elif sock == p2conn:
         p2response = (True, (response[1] == 'yes'))
         print 'Player 2 said', response[1], 'to the terms'
            
if not (p1response[1] and p2response[1]):
   # players did not agree
   print 'Players did not agree to the terms.'
   p1conn.send('TERMSDENY')
   p2conn.send('TERMSDENY')
   p1conn.close()
   p2conn.close()
   sys.exit(0)

# initiate goban
gb = goban.Goban(gobansize)
if handicap > 0:
   if p1_plays_black:
      handicap_sock = p1conn
      not_handicap_sock = p2conn
   else:
      handicap_sock = p2conn
      not_handicap_sock = p1conn
   for x in range(handicap):
      try:
         response = get_message(handicap_sock)
      except EOFError:
         print 'Connection closed while setting handicaps'
         not_handicap_sock.send('Connection closed by the other player\n')
         not_handicap_sock.close()
         sys.exit(1)

      if response[0] == 'PLAY':
         if len(response) < 3:
            print 'Handicap PLAY: wrong number of arguments'
            handicap_sock.send('ERROR PLAY requires two coordinates\n')
            continue
         try:
            py = int(response[1])
            px = int(response[2])
         except ValueError:
            print 'Bad PLAY coordinates:', response[1], response[2]
            handicap_sock.send('ERROR PLAY must provide two integer coordinates\n')
            continue

         try: 
            gb.play(goban.BLACK, py, px)
         except goban.GobanError as e:
            print 'GobanError encountered:', e.message
            handicap_sock.send('ERROR Logical error with this play: ' + e.message + '\n')

         
      

data = p1conn.recv(1024)
sys.exit(0)

# goban setup
gb = goban.Goban(9)
current_player = 1
prev_pass = False
