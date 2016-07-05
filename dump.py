# Old code from the good old multithreaded days
'''
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
'''

