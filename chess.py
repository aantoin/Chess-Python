import sys
from gui import *

class Piece:
	def __init__(self, player, row, col, type="X"):
		self.player = player
		self.row = row
		self.col = col
		self.type = type
		self.moved = False
		self.passant = False
	def __str__(self):
		return "(P"+str(self.player)+","+str(self.type)+","+str(self.row)+","+str(self.col)+")"
	def getPossibleMoves(self,board):
		return []
	def getAttackMoves(self,board):
		return self.getPossibleMoves(board)
	def move(self,board,row,col):
		board.spaces[row][col]=self
		board.spaces[self.row][self.col]=None
		self.row=row
		self.col=col
		self.moved = True
	def blockedBy(self,position,kingPosition):
		if self.row==position[0] and self.col==position[1]:
			return True
		dist1 = round(((position[0] - kingPosition[0])**2 + (position[1] - kingPosition[1])**2)**0.5 + 
			((position[0] - self.row)**2 + (position[1] - self.col)**2)**0.5,5)
		dist2 = round(((self.row - kingPosition[0])**2 + (self.col - kingPosition[1])**2)**0.5,5)
		if dist1 == dist2:
		   return True
		return False
	def getPlayerDirection(self):
		return 1 if self.player==1 else -1
	"""Remove moves from moves list that don't protect the king if it is in check"""
	def movesProtectKing(self,board,moves):
		validMoves = []
		king = board.getKing(self.player)
		checks = king.getChecks()
		for m in moves:
			moveValid = True
			for p in checks:
				if not p.blockedBy(m,(king.row,king.col)):
					moveValid = False
			if moveValid:
				validMoves.append(m)
		return validMoves
	"""Remove moves from moves list that would put its own king in check"""
	def removeDangerMoves(self,board,moves):
		king = board.getKing(self.player)
		rd = king.row - self.row
		cd = king.col - self.col
		if abs(rd) == 0 and abs(cd) == 0:
			#return moves unchanged if king calls this function
			return moves
		if abs(rd) == 0 or abs(cd) == 0 or abs(rd) == abs(cd):
			#straight line to king
			rdn = 0 if rd == 0 else (1 if rd>0 else -1)
			cdn = 0 if cd == 0 else (1 if cd>0 else -1)
			rds = self.row+rdn
			cds = self.col+cdn
			while(board.contains(rds,cds) and board.spaces[rds][cds] != king):
				if board.spaces[rds][cds] is not None:
					#Piece other than king is found. Not pinning
					return moves
				rds = rds + rdn
				cds = cds + cdn			
			rds = self.row-rdn
			cds = self.col-cdn
			while(board.contains(rds,cds)):
				#search for opposing piece
				if board.spaces[rds][cds] is not None:
					#found piece
					p = board.spaces[rds][cds]
					if (p.player != self.player and
					   ( ( rdn*cdn==0 and (p.type=="R" or p.type=="Q")) or
						 ( rdn*cdn!=0 and (p.type=="B" or p.type=="Q")))):
						#piece in pin line
						ray = []
						for i in range(1,8):
							#build ray moves
							pr = king.row - i*rdn
							pc = king.col - i*cdn
							ray.append((pr,pc))
							if pr==rds and pc==cds:
								break
						validMoves=[]
						for move in moves:
							if move in ray:
								#valid moves only when in ray
								validMoves.append(move)
						return validMoves
					break
				rds = rds-rdn
				cds = cds-cdn
		return moves
	def removeOwnAttack(self,board,moves):
		rmoves = []
		for m in moves:
			if board.spaces[m[0]][m[1]] is None or board.spaces[m[0]][m[1]].player != self.player:
				rmoves.append(m)
		return rmoves
	def getValidMoves(self,board):
		moves = self.getPossibleMoves(board)
		moves = self.removeOwnAttack(board,moves)
		moves = self.movesProtectKing(board,moves)
		moves = self.removeDangerMoves(board,moves)
		return moves

class Pawn(Piece):
	def __init__(self, player, row, col):
		super().__init__(player, row, col, "P")
	def getPossibleMoves(self,board):
		moves = []
		direction = self.getPlayerDirection()
		if board.contains(self.row+direction,self.col) and board.spaces[self.row+direction][self.col] is None:
			#Normal move
			moves.append((self.row+direction,self.col))
			if board.contains(self.row+2*direction,self.col) and board.spaces[self.row+2*direction][self.col] is None and self.moved == False:
				#Double move
				moves.append((self.row+2*direction,self.col))
		if (board.contains(self.row+direction,self.col-1) and 
		    isinstance(board.spaces[self.row+direction][self.col-1],Piece)):
			#Take left
			moves.append((self.row+direction,self.col-1))
		if (board.contains(self.row+direction,self.col+1) and 
		    isinstance(board.spaces[self.row+direction][self.col+1],Piece)):
			#Take Right
			moves.append((self.row+direction,self.col+1))
		if (board.contains(self.row+direction,self.col-1) and 
		    board.contains(self.row,self.col-1) and 
		    board.spaces[self.row+direction][self.col-1] is None and
		    isinstance(board.spaces[self.row][self.col-1],Piece) and
			board.spaces[self.row][self.col-1].passant):
			#Take passant left
			moves.append((self.row+direction,self.col-1))
		if (board.contains(self.row+direction,self.col+1) and 
		    board.contains(self.row,self.col+1) and 
		    board.spaces[self.row+direction][self.col+1] is None and
		    isinstance(board.spaces[self.row][self.col+1],Piece) and
			board.spaces[self.row][self.col+1].passant):
			#Take passant right
			moves.append((self.row+direction,self.col+1))
		return moves
	def getAttackMoves(self, board):
		moves = []
		r = self.row+self.getPlayerDirection()
		c = self.col+1
		if board.contains(r,c):
			moves.append((r,c))
		c = self.col-1
		if board.contains(r,c):
			moves.append((r,c))
		return moves
	def move(self,board,row,col):
		self.passant = abs(row-self.row)>1
		killpassant = False
		if board.spaces[row-self.getPlayerDirection()][col] is not None and board.spaces[row-self.getPlayerDirection()][col].passant == True:
			killpassant = True
		super().move(board,row,col)
		if killpassant:
			board.spaces[self.row-self.getPlayerDirection()][self.col]=None
		if self.row == 0 or self.row == 7:
			q = Queen(self.player,self.row,self.col)
			q.moved = True
			board.spaces[self.row][self.col] = q
		return

class Rook(Piece):
	def __init__(self, player, row, col):
		super().__init__(player, row, col, "R")
	def getPossibleMoves(self,board):
		moves = []
		direction = self.getPlayerDirection()
		for r in range(self.row+1,self.row+8,1):
			c = self.col
			if board.contains(r,c):
				moves.append((r,c))
				if board.spaces[r][c] is not None:
					break
		for r in range(self.row-1,self.row-8,-1):
			c = self.col
			if board.contains(r,c):
				moves.append((r,c))
				if board.spaces[r][c] is not None:
					break
		for c in range(self.col+1,self.col+8,1):
			r = self.row
			if board.contains(r,c):
				moves.append((r,c))
				if board.spaces[r][c] is not None:
					break
		for c in range(self.col-1,self.col-8,-1):
			r = self.row
			if board.contains(r,c):
				moves.append((r,c))
				if board.spaces[r][c] is not None:
					break
		return moves

class Bishop(Piece):
	def __init__(self, player, row, col):
		super().__init__(player, row, col, "B")
	def getPossibleMoves(self,board):
		moves = []
		for r in range(1,8,1):
			c = r
			if board.contains(self.row+r,self.col+c):
				moves.append((self.row+r,self.col+c))
				if board.spaces[self.row+r][self.col+c] is not None:
					break
		for r in range(1,8,1):
			c = -r
			if board.contains(self.row+r,self.col+c):
				moves.append((self.row+r,self.col+c))
				if board.spaces[self.row+r][self.col+c] is not None:
					break
		for r in range(-1,-8,-1):
			c = r
			if board.contains(self.row+r,self.col+c):
				moves.append((self.row+r,self.col+c))
				if board.spaces[self.row+r][self.col+c] is not None:
					break
		for r in range(-1,-8,-1):
			c = -r
			if board.contains(self.row+r,self.col+c):
				moves.append((self.row+r,self.col+c))
				if board.spaces[self.row+r][self.col+c] is not None:
					break
		return moves

class Knight(Piece):
	def __init__(self, player, row, col):
		super().__init__(player, row, col, "N")
	def getPossibleMoves(self,board):
		moves = []
		for r in range(-2,3,1):
			for c in range(-2,3,1):
				if abs(r*c) == 2 and board.contains(self.row+r,self.col+c):
					moves.append((self.row+r,self.col+c))
		return moves

class Queen(Piece):
	def __init__(self, player, row, col):
		super().__init__(player, row, col, "Q")
	def getPossibleMoves(self,board):
		moves = []
		direction = self.getPlayerDirection()
		for r in range(self.row+1,self.row+8,1):
			c = self.col
			if board.contains(r,c):
				moves.append((r,c))
				if board.spaces[r][c] is not None:
					break
		for r in range(self.row-1,self.row-8,-1):
			c = self.col
			if board.contains(r,c):
				moves.append((r,c))
				if board.spaces[r][c] is not None:
					break
		for c in range(self.col+1,self.col+8,1):
			r = self.row
			if board.contains(r,c):
				moves.append((r,c))
				if board.spaces[r][c] is not None:
					break
		for c in range(self.col-1,self.col-8,-1):
			r = self.row
			if board.contains(r,c):
				moves.append((r,c))
				if board.spaces[r][c] is not None:
					break
		for r in range(1,8,1):
			c = r
			if board.contains(self.row+r,self.col+c):
				moves.append((self.row+r,self.col+c))
				if board.spaces[self.row+r][self.col+c] is not None:
					break
		for r in range(1,8,1):
			c = -r
			if board.contains(self.row+r,self.col+c):
				moves.append((self.row+r,self.col+c))
				if board.spaces[self.row+r][self.col+c] is not None:
					break
		for r in range(-1,-8,-1):
			c = r
			if board.contains(self.row+r,self.col+c):
				moves.append((self.row+r,self.col+c))
				if board.spaces[self.row+r][self.col+c] is not None:
					break
		for r in range(-1,-8,-1):
			c = -r
			if board.contains(self.row+r,self.col+c):
				moves.append((self.row+r,self.col+c))
				if board.spaces[self.row+r][self.col+c] is not None:
					break
		return moves

class King(Piece):
	def __init__(self, player, row, col):
		super().__init__(player, row, col, "K")
		self.checks = []
	def getChecks(self):
		return self.checks
	def getPossibleMoves(self,board):
		moves = []
		for r in range(-1,2):
			for c in range(-1,2):
				if board.contains(self.row+r,self.col+c):
					moves.append((self.row+r,self.col+c))
		if not self.moved and len(self.checks)==0:
			r = self.row
			c = self.col
			if (board.spaces[r][c+1] is None and
				board.spaces[r][c+2] is None and
				board.spaces[r][c+3] is None and
				isinstance(board.spaces[r][c+4],Rook) and
				not board.spaces[r][c+4].moved and
				not isinstance(board.spaces[r+self.getPlayerDirection()][c+2],King) and
				not isinstance(board.spaces[r+self.getPlayerDirection()][c+3],King)):
				valid = True
				for row in board.spaces:
					for p in row:
						if p is not None and not isinstance(p,King) and p.player!=self.player:
							amoves = p.getAttackMoves(board)
							if (r,c+1) in amoves or (r,c+2) in amoves:
								valid = False
							if not valid:
								break
					if not valid:
						break
				if valid:
					moves.append((r,c+2))
			if (board.spaces[r][c-1] is None and
				board.spaces[r][c-2] is None and
				isinstance(board.spaces[r][c-3],Rook) and
				not board.spaces[r][c-3].moved and
				not isinstance(board.spaces[r+self.getPlayerDirection()][c-2],King) and
				not isinstance(board.spaces[r+self.getPlayerDirection()][c-3],King)):
				valid = True
				for row in board.spaces:
					for p in row:
						if p is not None and not isinstance(p,King) and p.player!=self.player:
							amoves = p.getAttackMoves(board)
							if (r,c-1) in amoves or (r,c-2) in amoves:
								valid = False
							if not valid:
								break
					if not valid:
						break
				if valid:
					moves.append((r,c-2))


		return moves
	"""Override: Remove moves from moves list that don't protect the king if it is in check"""
	def movesProtectKing(self,board,moves):
		return moves
	"""Remove moves from moves list that would put the king in check"""
	def removeDangerMoves(self,board,moves):
		board.spaces[self.row][self.col] = None
		for r in range(8):
			for c in range(8):
				p = board.spaces[r][c]
				if p is not None and p.player != self.player:
					pmoves = p.getAttackMoves(board)
					vmoves = []
					for m in moves:
						if m not in pmoves:
							vmoves.append(m)
					moves = vmoves
		board.spaces[self.row][self.col] = self
		return moves
	def move(self,board,row,col):
		
		castle = abs(col-self.col)>1
		super().move(board,row,col)
		if castle:
			if col == 1:
				board.spaces[self.row][0].move(board,self.row,2)
			if col == 5:
				board.spaces[self.row][7].move(board,self.row,4)
		return

class Board:
	def __init__(self):
		self.app = Application(self)
		self.selected = None
		self.player = 1
		self.mate = False
		self.spaces = [[None for x in range(8)] for y in range(8)]
		for x in range(8):
			self.spaces[1][x] = Pawn(1,1,x)
			self.spaces[6][x] = Pawn(2,6,x)
		for p in range(2):
			self.spaces[p*7][0] = Rook(p+1,p*7,0) 
			self.spaces[p*7][1] = Knight(p+1,p*7,1)
			self.spaces[p*7][2] = Bishop(p+1,p*7,2)
			self.spaces[p*7][3] = King(p+1,p*7,3)
			self.spaces[p*7][4] = Queen(p+1,p*7,4)
			self.spaces[p*7][5] = Bishop(p+1,p*7,5)
			self.spaces[p*7][6] = Knight(p+1,p*7,6)
			self.spaces[p*7][7] = Rook(p+1,p*7,7)
		"""
		self.spaces[0][0] = Rook(2,0,0)
		self.spaces[0][4] = Queen(2,0,4)
		self.spaces[1][4] = King(1,1,4)
		self.spaces[1][4].moved=True
		self.spaces[6][4] = King(2,6,4)
		self.spaces[6][4].moved=True
		"""
		self.app.update_cells()
	def __str__(self):
		s = ""
		for r in self.spaces:
			for p in r:
				if p is None:
					s = s+"."
				else:
					s = s+(p.type if p.player == 1 else p.type.lower())
			s = s+"\n"
		return s
	def start(self):
		self.app.mainloop()
	def contains(self,row,col):
		return row>=0 and col>=0 and row<=7 and col<=7
	def getKing(self,player):
		for y in self.spaces:
			for x in y:
				if isinstance(x,Piece) and x.type=="K" and x.player==player:
					return x
		sys.exit("King is dead")
	def updateChecks(self):
		k1 = self.getKing(1)
		k2 = self.getKing(2)
		k1.checks = []
		k2.checks = []
		mate = [True,True]
		for r in range(8):
			for c in range(8):
				p = self.spaces[r][c]
				if p is not None:
					moves = p.getValidMoves(self)
					if p.player==1 and (k2.row,k2.col) in moves:
						k2.checks.append(p)
					if p.player==2 and (k1.row,k1.col) in moves:
						k1.checks.append(p)
		for r in range(8):
			for c in range(8):
				p = self.spaces[r][c]
				if p is not None:
					moves = p.getValidMoves(self)
					if len(moves)>0:
						mate[p.player-1]=False
		if mate[0] or mate[1]:
			self.mate = True
		return
	def resetPassant(self):
		for r in range(8):
			for c in range(8):
				p = self.spaces[r][c]
				if p is not None and p.player == self.player:
					p.passant = False
		return
	def getMove(self,row,col):
		moves = []
		s = self.selected
		p = self.spaces[row][col]
		if s is None:
			if p is None:
				pass
			elif p.player == self.player:
				self.selected = p
				moves = p.getValidMoves(self)
		else:
			if p is None or p.player != self.player:
				moves = s.getValidMoves(self)
				if (row,col) in moves:
					s.move(self,row,col)
					moves=[]
					self.player = 1 if self.player == 2 else 2
					self.selected = None
					self.updateChecks()
					self.resetPassant()
			else:
				self.selected = p
				moves = p.getValidMoves(self)
		self.app.update_label("White" if self.player == 1 else "Black")
		if self.mate:
			self.app.update_label("Checkmate")
		return moves

b = Board()
b.start()
