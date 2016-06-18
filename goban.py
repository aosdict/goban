# goban module
import hashlib
import collections # for deque
import sys

# superclass for all exceptions thrown by this module
class GobanError(Exception):
   def __init__(self, message, errors=None):
      super(GobanError, self).__init__(message)
      self.errors = errors

class InvalidSpaceError(GobanError):
   def __init__(self, message, errors=None):
      super(InvalidSpaceError, self).__init__(message, errors)
      self.errors = errors

class Goban:
   # actual board
   board = None
   size = 0
   history = collections.deque()
   captures = { 1: 0, 2: 0 }

   def __init__(self, dimension):
      self.size = dimension
      self.board = [[0] * dimension for i in range(dimension)]

   def dbg_print(self):
      for row in self.board:
         for space in row:
            if space == 0:
               sys.stdout.write(u'\u00b7 ')
            elif space == 1:
               sys.stdout.write(u'\u25cf ')
            elif space == 2:
               sys.stdout.write(u'\u25cb ')
            # sys.stdout.write(u'\u2500')
         print

   # Given a board position, iterate over the group of stones it is part of 
   # and return the number of liberties the group has.
   # Also return the set of coordinates representing the group.
   # assumes this is a valid board location
   def count_liberties(self, init_row, init_col):
      player = self.board[init_row][init_col]
      if player == 0:
         raise InvalidSpaceError("This is an open space (not part of a group)")

      liberties = 0
      s_open = set()
      # maintain 2 closed sets so that it's easy to return only the set representing this contiguous group
      s_closed_same = set()
      s_closed_different = set()
      s_open.add((init_row,init_col))

      while len(s_open) > 0:
         row, col = s_open.pop()

         if self.board[row][col] == 0:
            # is a liberty, add to closed set but don't check neighbors
            s_closed_different.add((row, col))
            liberties += 1

         elif self.board[row][col] == player:
            s_closed_same.add((row,col))
            # add neighbors to open set if they are valid spaces
            if row > 0 and (row-1, col) not in s_closed_same and (row-1, col) not in s_closed_different:
               s_open.add((row-1, col))
            if row < self.size-1 and (row+1, col) not in s_closed_same and (row+1, col) not in s_closed_different:
               s_open.add((row+1, col))
            if col > 0 and (row, col-1) not in s_closed_same and (row, col-1) not in s_closed_different:
               s_open.add((row, col-1))
            if col < self.size-1 and (row, col+1) not in s_closed_same and (row, col+1) not in s_closed_different:
               s_open.add((row, col+1))

         else:
            # other player's stones don't have anything important happening to them
            s_closed_different.add((row, col))

      return (liberties, s_closed_same)

   # for optimization, this will return a tuple containing the following:
   # 1. truth value denoting whether it is illegal
   # 2. list of sets of coordinates (opposing groups that would get captured by this move)
   def is_illegal(self, pnum, row, col):
      # it is illegal if:
      # 1. no opposing groups are captured by this move AND
      # 2. making this move would cause the player's own group to be captured

      # simulate adding the stone to the board
      # (assumes this is a valid location and there is nothing there already)
      self.board[row][col] = pnum

      # return a 2-tuple of:
      # 1. boolean denoting whether the main group doesn't need to be checked anymore
      # 2. a set of coordinates that gets captured, or None
      def check_adjacency(row, col):
         # print 'Checking adjacency', row, col, self.board[row][col], pnum
         if self.board[row][col] == 0:
            return (True, None)
         elif self.board[row][col] != pnum:
            libs, group = self.count_liberties(row, col)
            if libs == 0:
               opposing_captured_groups.append(group)
               return (True, group)
         return (False, None)

      opposing_captured_groups=[]
      dont_need_to_check = False
      # check 4 adjacent spaces
      # if any are open, set dont_need_to_check so this group won't be checked
      # if any are opposing, see if they now have no liberties; if they do,
      #   add them to opposing_captured_groups and set dont_need_to_check
      if row > 0:
         flag, group = check_adjacency(row-1, col)
         dont_need_to_check = dont_need_to_check or flag
         if not group is None:
            opposing_captured_groups.append(group)
      if row < self.size-1:
         flag, group = check_adjacency(row+1, col)
         dont_need_to_check = dont_need_to_check or flag
         if not group is None:
            opposing_captured_groups.append(group)
      if col > 0:
         flag, group = check_adjacency(row, col-1)
         dont_need_to_check = dont_need_to_check or flag
         if not group is None:
            opposing_captured_groups.append(group)
      if col < self.size-1:
         flag, group = check_adjacency(row, col+1)
         dont_need_to_check = dont_need_to_check or flag
         if not group is None:
            opposing_captured_groups.append(group)

      # no direct liberties or captured opposing groups
      if dont_need_to_check:
         # there are liberties to this space, or groups have been captured
         self.board[row][col] = 0
         return (False, opposing_captured_groups)
      else:
         if self.count_liberties(row, col)[0] == 0:
            self.board[row][col] = 0
            return (True, [])
         else:
            self.board[row][col] = 0
            return (False, [])

      return False

   def putative_board_hash(self, pnum, row, col):
      # simulate adding the stone to the board
      # (assumes this is a valid location and there is nothing there already)
      self.board[row][col] = pnum

      # get the hash of the board state
      digest = hashlib.md5(str(self.board).encode()).hexdigest()

      # undo the addition
      self.board[row][col] = 0

      # if the hash exists already, the board position is (almost certainly) a repeat of a previous position
      if digest in self.history:
         return ('', True)
      else:
         return (digest, False)

   def play(self, pnum, row, col):
      # test if row or col are invalid
      if row < 0 or row >= self.size:
         raise InvalidSpaceError("The row " + row + " is off the board")
      elif col < 0 or col >= self.size:
         raise InvalidSpaceError("The column " + col + " is off the board")

      # test if there is already something there
      elif self.board[row][col] != 0:
         raise InvalidSpaceError("There is already a stone on this space")

      # test if this is an illegal move
      illegal, captured_groups = self.is_illegal(pnum, row, col)
      if illegal:
         raise InvalidSpaceError("This move is illegal")

      # test if this causes a repeat of a previous board state
      digest, is_repeat = self.putative_board_hash(pnum, row, col)
      if is_repeat:
         raise InvalidSpaceError("KO: This move causes a repeat of a previous board state")

      else:
         # place the piece
         self.board[row][col] = pnum

         # capture any adjacent groups with no liberties
         for group in captured_groups:
            for coord in group:
               self.board[coord[0]][coord[1]] = 0
               self.captures[pnum] = self.captures[pnum] + 1

         # save the board state
         # a possible optimization is to limit the history queue's max size
         self.history.appendleft(digest)

   # Play multiple turns alternating colors. Takes a list of coordinate tuples.
   def multiplay(self, coordlist):
      pnum = 1
      for coord in coordlist:
         self.play(pnum, coord[0], coord[1])
         if pnum == 1:
            pnum = 2
         else:
            pnum = 1

'''
gb = Goban(9)
# gb.play(1, 0, 2)
gb.play(1,1,1)
gb.play(1,2,0)
gb.play(1,3,1)
gb.play(1,4,2)
gb.play(1,3,3)
gb.play(1,2,4)
gb.play(1,1,3)
gb.play(2,1,2)
gb.play(2,2,1)
gb.play(2,3,2)
gb.play(2,2,3)
gb.play(1,2,2)
gb.dbg_print()
'''
