import sys
import socket
import thread
import time
import goban

if __name__ != '__main__':
   print 'Error: server.py should only be run as the main module'
   sys.exit(1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = ''   # Symbolic name, meaning all available interfaces
try:
   PORT = int(sys.argv[1])
except:
   PORT = 8888 # Arbitrary non-privileged port

try:
   s.bind( (HOST, PORT) )
except socket.error as err:
   print 'Bind failed:', str(err)
   sys.exit(1)

print 'Bound to port', PORT

# accept only 2 connections
s.listen(2)

# goban setup
gb = goban.Goban(9)
current_player = 1
prev_pass = False

def playerthread(conn, player_number):
   global current_player
   global prev_pass
   conn.send('Connected. You are player number ' + str(player_number) + '\n');

   data = conn.recv(1024)
   while data:
      # print data
      cmdlist = data.split()
      cmd = cmdlist[0]
      args = cmdlist[1:]

      if cmd == 'PLAY':
         if current_player != player_number:
            conn.sendall('ERROR: It\'s not your turn\n')
         elif len(args) != 2:
            conn.sendall('ERROR: Wrong number of arguments for PLAY\n')
         else:
            try:
               row = int(args[0])
               col = int(args[1])
               gb.play(player_number, row, col)
               current_player = 2 if (player_number == 1) else 1
               conn.sendall('SUCCESS: Play made at row '+str(row)+', column '+str(col)+'\n')
               gb.dbg_print()
            except goban.GobanError as e:
               conn.sendall('ERROR: Goban error: '+str(e)+'\n')
            except ValueError:
               conn.sendall('ERROR: row/column argument for PLAY was not an int\n')

      elif cmd == 'PASS':
         current_player = 2 if (player_number == 1) else 1
         
         conn.sendall('SUCCESS: You passed this turn')
      else:
         conn.sendall('ERROR: Unrecognized command '+cmd+'\n')

      # receive new data
      data = conn.recv(1024)

      # conn.sendall('fdsfds\n')
   print 'Connection 1 closed'


p1conn, p1addr = s.accept()
print 'Accepted connection from', p1addr

def parse_response(connection):
   data = connection.recv(1024)
   if not data:
      raise EOFError("Connection closed")

   rlist = data.split()
   if len(rlist) < 1:
      raise ValueError("No command")

   return rlist

# the first connector gets to set the terms of the game
boardsize = 0
while boardsize < 3:
   p1conn.send("QUERY boardsize\n")
   try:
      response = parse_response(p1conn)
      assert response[0] == 'RESPONSE'
      boardsize = int(response[1])
   except EOFError:
      print "Connection closed before board size could be set"
      sys.exit(1)
   except AssertionError:
      print "Expected RESPONSE, got", response[0]
      p1conn.send("ERROR QUERY command must be answered with RESPONSE\n")
      continue
   except ValueError as e:
      print "ValueError:", e
      p1conn.send("ERROR " + str(e) + ' \n')
      continue
   except IndexError as e:
      print 'Inadequate board size response parameters'
      p1conn.send('ERROR Must provide an integer board size\n')

   if boardsize < 3:
      print "Board", boardsize, "too small"
      p1conn.send("ERROR Boardsize " + boardsize + " too small\n")

print 'Board size successfully set to', boardsize

color = 0
while color != 1 and color != 2:
   p1conn.send("QUERY color\n")
   try:
      response = parse_response(p1conn)
      assert response[0] == 'RESPONSE'
      color_str = response[1]
   except EOFError:
      print "Connection closed before color could be set"
      sys.exit(1)
   except AssertionError:
      print "Expected RESPONSE, got", response[0]
      p1conn.send("ERROR QUERY command must be answered with RESPONSE\n")
      continue
   except ValueError as e:
      print "ValueError:", e
      p1conn.send("ERROR " + str(e) + ' \n')
      continue
   except IndexError as e:
      print 'Inadequate color response parameters'
      p1conn.send("ERROR Must provide a color string 'white' or 'black'\n")

   if color_str == 'black':
      color = 1
   elif color_str == 'white':
      color = 2
   else:
      print "Incorrect color type", color_str
      p1conn.send("ERROR Color string " + color_str + " is not 'white' or 'black'\n")

print "Player 1 color successfully set to", color_str

handicap = -1
while handicap < 0:
   p1conn.send("QUERY handicap\n")
   try:
      response = parse_response(p1conn)
      assert response[0] == 'RESPONSE'
      handicap = int(response[1])
   except EOFError:
      print "Connection closed before handicap could be set"
      sys.exit(1)
   except AssertionError:
      print "Expected RESPONSE, got", response[0]
      p1conn.send("ERROR QUERY command must be answered with RESPONSE\n")
      continue
   except ValueError as e:
      print "ValueError:", e
      p1conn.send("ERROR " + str(e) + ' \n')
      continue
   except IndexError as e:
      print 'Inadequate handicap response parameters'
      p1conn.send("ERROR Must provide an integer handicap\n")

   if handicap < 0:
      print "Improper handicap", handicap
      p1conn.send("ERROR handicap must be 0 or greater")

print 'Handicap successfully set to', handicap

komi = -1
while komi < 0:
   p1conn.send("QUERY komi\n")
   try:
      response = parse_response(p1conn)
      assert response[0] == 'RESPONSE'
      komi = float(response[1])
   except EOFError:
      print "Connection closed before komi could be set"
      sys.exit(1)
   except AssertionError:
      print "Expected RESPONSE, got", response[0]
      p1conn.send("ERROR QUERY command must be answered with RESPONSE\n")
      continue
   except ValueError as e:
      print "ValueError:", e
      p1conn.send("ERROR " + str(e) + ' \n')
      continue
   except IndexError as e:
      print 'Inadequate komi response parameters'
      p1conn.send("ERROR Must provide a decimal komi\n")

   if komi < 0:
      print "Improper komi", komi
      p1conn.send("ERROR komi must be 0 or greater")

print 'Komi successfully set to', komi

print 'Now waiting for second player'
p2conn, p2addr = s.accept()
print 'Accepted connection from', p2addr

playermap = {
   1: color,
   2: (2 if color == 1 else 1)
}

p1conn.send('TERMS %s %s %s %s\n' % (boardsize, playermap[1], handicap, komi))
p2conn.send('TERMS %s %s %s %s\n' % (boardsize, playermap[2], handicap, komi))

data = p1conn.recv(1024)
sys.exit(0)

#thread.start_new_thread(playerthread, (p1conn, 1))

#thread.start_new_thread(playerthread, (p2conn, 2))

print 'Now past creating threads'

while 1:
   time.sleep(1)
