import sys
import socket
import goban
import curses
import traceback

stdscr = curses.initscr()
curses.noecho() # don't display letters when input is received
curses.cbreak() # don't require Enter to react to keys
stdscr.keypad(1)
gobansize = 9
gb = goban.Goban(gobansize)
horiz_spacing = 3
vert_spacing = 1
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
   gobanwin.move(vert_spacing + 1, horiz_spacing + 1)

   board = gb.board
   for y in range(len(board)):
      for x in range(len(board[y])):
         on_right = (x == len(board[y]) - 1)
         on_bot = (y == len(board) - 1)
         draw = curses.ACS_PLUS
         if y == 0:
            if x == 0:
               draw = curses.ACS_ULCORNER
            elif on_right:
               draw = curses.ACS_URCORNER
            else:
               draw = curses.ACS_TTEE
         # if space:

   stdscr.refresh()
   gobanwin.refresh()

try:
   maindraw()
   stdscr.getch()
except Exception as e:
   cleanup()
   traceback.print_exc()
   raise e

cleanup()
print 'chimol'
