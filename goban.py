# goban module
import hashlib
import collections # for deque

class PlacementError(Exception):
   def __init__(self, message, errors):
      super(PlacementError, self).__init__(message)
      self.errors = errors

class Goban:
   # actual board
   board = None
   size = 0
   history = collections.deque()

   def __init__(self, dimension):
      self.size = dimension
      self.board = [[0] * dimension for i in range(dimension)]

   def dbg_print(self):
      for row in self.board:
         for space in row:
            if space == 0:
               print '+',
            elif space == 1:
               print 'O',
            elif space == 2:
               print 'X',
         print

   def is_illegal(self, pnum, row, col):
      # TODO
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
         raise PlacementError("The row " + row + " is off the board")
      elif col < 0 or col >= self.size:
         raise PlacementError("The column " + col + " is off the board")

      # test if there is already something there
      elif self.board[row][col] != 0:
         raise PlacementError("There is already a stone on this space")

      # test if this is an illegal move
      elif self.is_illegal(pnum, row, col):
         raise PlacementError("This move is illegal")

      # test if this causes a repeat of a previous board state
      digest, is_repeat = self.putative_board_hash(pnum, row, col)
      if is_repeat:
         raise PlacementError("This move causes a repeat of a previous board state")

      else:
         # place the piece
         self.board[row][col] = pnum

         # capture any adjacent groups with no liberties
         # TODO

         # save the board state
         # a possible optimization is to limit the history queue's max size
         self.history.appendleft(digest)


gb = Goban(9)
gb.dbg_print()
gb.play(1, 3, 3)
gb.dbg_print()
