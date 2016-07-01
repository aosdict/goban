import sys
import socket
import goban
import curses
import traceback
import locale


def init_curses():
   stdscr = curses.initscr()
   curses.start_color()
   curses.use_default_colors()
   curses.init_pair(1, curses.COLOR_CYAN, -1)
   curses.init_pair(2, curses.COLOR_GREEN, -1)
   curses.init_pair(3, curses.COLOR_WHITE, -1)
   curses.init_pair(4, curses.COLOR_RED, -1)
   default_curses_settings = curses.color_pair(3)
   curses.curs_set(2)
   curses.noecho() # don't display letters when input is received
   curses.cbreak() # don't require Enter to react to keys
   stdscr.keypad(1)

def init():
   locale.setlocale(locale.LC_ALL, '')
   mode = raw_input("Start in server or client mode? ")
   if mode == 'SERVER':
      # Server gets to control the parameters of the game.
      gobansize_str = raw_input("Enter size of goban: ")
      try:
         gobansize = int(gobansize_str)
      except ValueError:
         print "goban size must be a number"
         sys.exit(1)

      if gobansize < 3:
         print "goban smaller than 3 does not make much sense"
         sys.exit(1)

      # TODO: this should accept empty strings
      p1handicap_str = raw_input("Enter your handicap: ")
      try:
         p1handicap = int(p1handicap_str)
      except ValueError:
         print "your handicap must be a number"
         sys.exit(1)

      p2handicap = 0
      if p1handicap == 0:
         # TODO: this should accept empty strings
         p2handicap_str = raw_input("Enter opponent's handicap: ")
         try: 
            p2handicap = int(p2handicap_str)
         except ValueError:
            print "opponent's handicap must be a number"
            sys.exit(1)

         if p2handicap == 0:
            choice = raw_input("Play as (b)lack, (w)hite, or (r)andom? ")

   elif mode == 'CLIENT':
      # Client only gets to confirm the parameters.
      pass

   else:
      print "Mode must be SERVER or CLIENT"
      sys.exit(1)

gobansize = 19
gb = goban.Goban(gobansize)
gb.play(2, 2, 2)
gb.play(1, 4, 4)
gb.play(1, 0, 0)
gb.play(2, 0, 1)
gb.play(1, 1, 0)
horiz_spacing = 3
vert_spacing = 1
# Board drawn with 3 spaces between points horizontally and 1 between points
# vertically, with the same margins on either side.
# Total width = (gobansize-1) * (1 + *_spacing) + 1 (extra column) + 2 (edges) + (*_spacing * 2) (margins)
tot_draw_w = (gobansize-1) * (horiz_spacing + 1) + (horiz_spacing * 2) + 3
tot_draw_h = (gobansize-1) * (vert_spacing + 1) + (vert_spacing * 2) + 3
gobanwin = curses.newwin(tot_draw_h, tot_draw_w, 0, 0)
statuswin = curses.newwin(3, tot_draw_w, tot_draw_h, 0)

def cleanup():
   stdscr.keypad(0)
   curses.nocbreak()
   curses.echo()
   curses.endwin()

def maindraw():
   gobanwin.move(0,0)

   board = gb.board
   for y in range(len(board)):
      gobanwin.move((y * (vert_spacing+1)) + 1 + vert_spacing, 1 + horiz_spacing)

      on_top = (y == 0)
      on_bot = (y == len(board) - 1)

      for x in range(len(board[y])):
         on_left = (x == 0)
         on_right = (x == len(board[y]) - 1)


         # stone = None
         # if board[y][x] == 1:
         #    stone = u'\u25cf'
         # elif board[y][x] == 2:
         #    stone = u'\u25cb'

         if on_top:
            if on_left:
               draw = curses.ACS_ULCORNER
            elif on_right:
               draw = curses.ACS_URCORNER
            else:
               draw = curses.ACS_TTEE
         elif on_bot:
            if on_left:
               draw = curses.ACS_LLCORNER
            elif on_right:
               draw = curses.ACS_LRCORNER
            else:
               draw = curses.ACS_BTEE
         else:
            if on_left:
               draw = curses.ACS_LTEE
            elif on_right:
               draw = curses.ACS_RTEE
            else:
               draw = curses.ACS_PLUS


         a = default_curses_settings
         if board[y][x] == 1:
            draw = ' '
            a = curses.color_pair(1) | curses.A_REVERSE
         elif board[y][x] == 2:
            draw = ' '
            a = curses.color_pair(2) | curses.A_REVERSE

         # if stone is not None:
         #    gobanwin.addstr(stone.encode('utf-8'))
         # else:
            # gobanwin.addch(draw)
         gobanwin.addch(draw, a)

         if not on_right:
            for i in range(horiz_spacing):
               gobanwin.addch(curses.ACS_HLINE, default_curses_settings)

      # draw lines that don't include horizontals
      if not on_bot:
         for i in range(vert_spacing):
            gobanwin.move((y * (vert_spacing+1)) + 3 + i, 1 + horiz_spacing)
            for x in range(len(board[y])):
               gobanwin.addch(curses.ACS_VLINE, default_curses_settings)
               cy, cx = gobanwin.getyx()
               gobanwin.move(cy, cx + horiz_spacing)
   
   gobanwin.box()

   stdscr.refresh()
   gobanwin.refresh()
   statuswin.refresh()

def cursorx_to_real(cursor_coord):
   return (1 + horiz_spacing) * (cursor_coord + 1)

def cursory_to_real(cursor_coord):
   return (1 + vert_spacing) * (cursor_coord + 1)

try:
   maindraw()
   cursorx = 0
   cursory = 0
   # Movement loop
   while True:
      stdscr.move(cursory_to_real(cursory), cursorx_to_real(cursorx))
      inpt = stdscr.getch()
      if inpt == ord('p'):
         # Pass (in goban)
         pass

      elif inpt == ord('\n'):
         try:
            gb.play(1, cursory, cursorx)
         except goban.GobanError as e:
            errmsg = 'Error: ' + e.message
            statuswin.addstr(0, 0, errmsg, curses.color_pair(4))

      elif (inpt == ord('l') or inpt == curses.KEY_RIGHT):
         if cursorx < gobansize - 1:
            cursorx += 1

      elif (inpt == ord('h') or inpt == curses.KEY_LEFT):
         if cursorx > 0:
            cursorx -= 1

      elif (inpt == ord('j') or inpt == curses.KEY_DOWN):
         if cursory < gobansize - 1:
            cursory += 1

      elif (inpt == ord('k') or inpt == curses.KEY_UP):
         if cursory > 0:
            cursory -= 1

      else:
         break

      maindraw()

except Exception as e:
   cleanup()
   traceback.print_exc()
   raise e

cleanup()
print 'chimol'
