# Given a socket, sends a WAITING TERMS message to it and will wait for it to send
# back a TERMS proposing terms. If there is a problem parsing the message it will ask
# again, and will not return until a completely parseable TERMS is sent back. Then it
# will return a 4-tuple containing the terms.

import sys
sys.dont_write_bytecode=True

import socket
from get_message import get_message

if __name__ == '__main__':
   print 'Error: this is an import and should not be run standalone'
   sys.exit(1)

def get_terms(sock): 
   tmp_gobansize = 0
   tmp_p1_plays_black = None
   tmp_handicap = -1
   tmp_komi = -1
   while tmp_gobansize < 3 or tmp_p1_plays_black is None or tmp_handicap < 0 or tmp_komi < 0:
      tmp_gobansize = 0
      tmp_p1_plays_black = None
      tmp_handicap = -1
      tmp_komi = -1
      sock.send('WAITING TERMS\n')
         
      # may raise an EOFError, this function does not handle it
      response = get_message(sock)

      if len(response) < 5:
         print 'Not enough arguments to TERMS:', ' '.join(response)
         sock.send('ERROR TERMS must have exactly 4 parameters\n')
         continue

      # parse board size
      try:
         tmp_gobansize = int(response[1])
         if tmp_gobansize < 3:
            print "Board", tmp_gobansize, "too small"
            sock.send("ERROR board size " + str(tmp_gobansize) + " too small\n")
            continue
      except ValueError:
         print 'Could not convert board size', response[1], 'to int'
         sock.send('ERROR Board size ' + response[1] + ' is not an integer\n')
         continue

      # parse color preference
      if response[2] != 'True' and response[2] != 'False':
         print "Incorrect color type", response[2]
         sock.send("ERROR Color string " + response[2] + " is not 'white' or 'black'\n")
         continue
      else:
         tmp_p1_plays_black = (response[2] == 'True')

      # parse tmp_handicap
      try:
         tmp_handicap = int(response[3])
         if tmp_handicap < 0:
            print "Improper tmp_handicap", tmp_handicap
            sock.send("ERROR handicap must be 0 or greater\n")
            continue
      except ValueError:
         print 'Could not convert handicap', response[3], 'to int'
         sock.send('ERROR Handicap ' + response[3] + ' is not an integer\n')
         continue

      # parse tmp_komi
      try:
         tmp_komi = float(response[4])
         if tmp_komi < 0:
            print "Improper komi", tmp_komi
            sock.send("ERROR komi must be 0 or greater\n")
            continue
      except ValueError:
         print 'Could not convert komi', response[4], 'to float'
         sock.send('ERROR Komi ' + response[4] + ' is not a decimal number\n')
         continue

   return (tmp_gobansize, tmp_p1_plays_black, tmp_handicap, tmp_komi)

