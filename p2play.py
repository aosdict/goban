import sys
import socket
import goban
import curses
import traceback
import locale

locale.setlocale(locale.LC_ALL, '')

stdscr = curses.initscr()
curses.noecho() # don't display letters when input is received
curses.cbreak() # don't require Enter to react to keys
stdscr.keypad(1)
gobansize = 9
gb = goban.Goban(gobansize)
gb.play(2, 2, 2)
horiz_spacing = 1
vert_spacing = 0
# Board drawn with 3 spaces between points horizontally and 1 between points
# vertically, with the same margins on either side.
# Total width = (gobansize-1) * (1 + *_spacing) + 1 (extra column) + 2 (edges) + (*_spacing * 2) (margins)
tot_draw_w = (gobansize-1) * (horiz_spacing + 1) + (horiz_spacing * 2) + 3
tot_draw_h = (gobansize-1) * (vert_spacing + 1) + (vert_spacing * 2) + 3
gobanwin = curses.newwin(tot_draw_h, tot_draw_w, 0, 0)


def cleanup():
   stdscr.keypad(0)
   curses.nocbreak()
   curses.echo()
   curses.endwin()

def maindraw():
   gobanwin.move(0,0)
   gobanwin.box()
   # gobanwin.move(vert_spacing + 1, horiz_spacing + 1)

   board = gb.board
   for y in range(len(board)):
      gobanwin.move((y * (vert_spacing+1)) + 1 + vert_spacing, 1 + horiz_spacing)
      
      on_top = (y == 0)
      on_bot = (y == len(board) - 1)

      for x in range(len(board[y])):
         on_left = (x == 0)
         on_right = (x == len(board[y]) - 1)

         stone = None
         if board[y][x] == 1:
            stone = u'\u25cf'
         elif board[y][x] == 2:
            stone = u'\u25cb'
         
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

         if stone is not None:
            gobanwin.addstr(stone.encode('utf-8'))
         else:
            gobanwin.addch(draw)

         if not on_right:
            for i in range(horiz_spacing):
               gobanwin.addch(curses.ACS_HLINE)

      # draw lines that don't include horizontals
      if not on_bot:
         for i in range(vert_spacing):
            gobanwin.move((y * (vert_spacing+1)) + 3 + i, 1 + horiz_spacing)
            for x in range(len(board[y])):
               gobanwin.addch(curses.ACS_VLINE)
               cy, cx = gobanwin.getyx()
               gobanwin.move(cy, cx + horiz_spacing)


   stdscr.refresh()
   gobanwin.refresh()

try:
   maindraw()
   stdscr.move(4, 4)
   stdscr.getch()
except Exception as e:
   cleanup()
   traceback.print_exc()
   raise e

cleanup()
print 'chimol'
