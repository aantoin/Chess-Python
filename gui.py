import tkinter as tk

class Cell(tk.Canvas):
	def __init__(self, app, boardFrame,row,col):
		self.app = app
		self.color = '#CCCCCC' if ((row+col)%2==0) else '#888888'
		super().__init__(boardFrame,bd=1,bg=self.color,width=21,height=21)
		self.row = row
		self.col = col
		self.grid(row=row,column=col)
		self.bind('<Button-1>', self.click)
		self.rect_id = self.create_rectangle(0,0,24,24,fill=self.color,width=0)
		self.text_id = self.create_text(11,11,text=" ",font=('Helvetica', '12'))
	
	def updatePiece(self,piece,moves=[]):
		
		if (self.row,self.col) in moves:
			if self.color == '#CCCCCC':
				self.itemconfigure(self.rect_id,fill='#CCCCEE')
			else:
				self.itemconfigure(self.rect_id,fill='#8888AA')
		else:
			self.itemconfigure(self.rect_id,fill=self.color)
		if piece is not None:
			self.itemconfigure(self.text_id,text=piece.type,fill=('white' if piece.player==1 else 'black'))
		else:
			self.itemconfigure(self.text_id,text=' ')
	def click(self,event):
		print("Clicked",event.widget.row,event.widget.col)
		self.app.cellClicked(self)

class Application(tk.Frame):
	def __init__(self, board, master=tk.Tk()):
		super().__init__(master)
		self.board = board
		self.master = master
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		
		self.boardFrame = tk.Frame(self,bd=1,bg='#FFFFFF')
		self.cells = []
		for r in range(8):
			row = []
			for c in range(8):
				row.append(Cell(self,self.boardFrame,r,c))
			self.cells.append(row)
		self.boardFrame.pack(side="top")
		
		self.labelText = tk.StringVar(None,"White")
		self.message = tk.Label(self,textvariable=self.labelText)
		self.message.pack(side="bottom")
		
	def update_cells(self,moves=[]):
		for r in range(8):
			for c in range(8):
				self.cells[r][c].updatePiece(self.board.spaces[r][c],moves)
	def cellClicked(self,cell):
			self.update_cells(self.board.getMove(cell.row,cell.col))
	def update_label(self,text=""):
		self.labelText.set(text)