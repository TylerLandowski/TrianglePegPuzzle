# TODO Support larger puzzles

from collections import deque 

INIT_BOARD = [
	[    1    ],
	[   0,1   ],
	[  1,1,1  ],
	[ 1,1,1,1 ],
	[1,1,1,1,1],
]

# Modes of operation
STATS    = 0 # Shows all possible stats for the board
SOLUTION = 1 # Shows the very first solution found for given board

# Indexes for history stack
BOARD_IDX   = 0
MOVES_IDX   = 1
MOVEIDX_IDX = 2

# Stack [board, moves, moveidx]
#     board   = Current board
#     moves   = List of all possible moves (start, middle, end)
#     moveidx = Next move to try
history = None
mode = None
board = None

# Initializes variables (to allow program to run more than once)
def init(new_mode, new_board=INIT_BOARD):
	global board, mode, history
	
	board   = deepcopy(new_board)
	mode    = new_mode
	history = deque()

# Does a 2nd-level deep copy of a list of lists
def deepcopy(l):
	ret = list()
	for y in l: ret.append(y.copy())
	return ret
	
# Prints the board
def show_board(b):
	print(
		"    {}\n   {} {}\n  {} {} {}\n {} {} {} {}\n{} {} {} {} {}\n".format(
			b[0][0], b[1][0], b[1][1], b[2][0], b[2][1], \
			b[2][2], b[3][0], b[3][1], b[3][2], b[3][3], \
			b[4][0], b[4][1], b[4][2], b[4][3], b[4][4]
		)
	)

# Shows the moves taken to get to current state
def show_moves(sol):
	for state in sol:
		b = state[BOARD_IDX]
		show_board(b)

# Returns the score for the current board
def get_score():
	return sum([sum(peg) for peg in board])
	
# Returns a list of moves playable by a peg. Move = (Start, Middle, End)
def get_moves(pos):
	moves = list()
	y = pos[0]
	x = pos[1]
	
	def exists(pos):
		y = pos[0]
		x = pos[1]		
		if y < 0: return False
		if y > 4: return False
		if x < 0: return False
		if x > y: return False
		return True
	
	def move_possible(mid, end):
		if exists(end) and board[end[0]][end[1]] == 0 and board[mid[0]][mid[1]] == 1: return True
		return False
	
	def handle(mid, end):
		if move_possible(mid, end): moves.append([pos, mid, end])
	
	handle((y  , x-1), (y  , x-2)) # Left
	handle((y  , x+1), (y  , x+2)) # Right
	handle((y-1, x-1), (y-2, x-2)) # Up-Left
	handle((y-1, x  ), (y-2, x  )) # Up-Right
	handle((y+1, x  ), (y+2, x  )) # Dn-Left
	handle((y+1, x+1), (y+2, x+2)) # Dn-Right
	
	return moves
	
# Updates the board to reflect the given move
def play_move(move):
	s = move[0]
	m = move[1]
	e = move[2]
	board[s[0]][s[1]] = 0
	board[m[0]][m[1]] = 0
	board[e[0]][e[1]] = 1

def run():
	global board, history, mode
	
	# Iterate over each possible board state
	solution  = None
	solutions = 0
	num_games = 0
	while True:
		# Look for available moves
		moves = list()
		for y in range(0, 5):
			for x in range(0, y+1):
				pos = (y, x)
				if board[y][x] == 1: moves += get_moves(pos)
		
		# Terminal state?
		if len(moves) == 0:
			num_games += 1
		
			# Win?
			if get_score() == 1:
				if mode == STATS:
					# Keep looking for statistics
					solution = deepcopy(history)
					solutions += 1
				elif mode == SOLUTION:
					# Show solution and end
					show_moves(history)
					return solution
				
			# Undo moves until we have a move
			while True:
				# All moves checked?
				if len(history) == 0:
					if solutions == 0:
						print("No winning strategy for this initial board state")
					else:
						#show_moves(solution)
						print("{} solutions found out of {} possible games ({:.2f}%)".format(
							solutions, num_games, solutions / num_games * 100
							)
						)
						return (solution, solutions, num_games)
			
				top = history[-1]
				# No more moves with previous board state?
				if top[MOVEIDX_IDX] >= len(top[MOVES_IDX]):
					# Move back another step
					#print("POP PREV")
					#for test2 in test:
					#	print("{} {}".format(test2[BOARD_IDX], sum(sum(a) for a in test2[BOARD_IDX])))
					#print()
					history.pop()
					#print("POP AFTER")
					#for test2 in test:
					#	print("{} {}".format(test2[BOARD_IDX], sum(sum(a) for a in test2[BOARD_IDX])))
					#print()
					
				else:
					# Reset board
					board = deepcopy(top[BOARD_IDX]) # global
					# Apply move
					prev_moves = top[MOVES_IDX]
					prev_idx   = top[MOVEIDX_IDX]
					play_move(prev_moves[prev_idx])
					# Mark this move as played
					history[-1][MOVEIDX_IDX] += 1
					break
		else:
			# Save state onto stack and play first move
			history.append([deepcopy(board), deepcopy(moves), 1])
			play_move(moves[0])
			test = history
			#print("PUSH")
			#for test2 in test:
			#	print("{} {}".format(test2[BOARD_IDX], sum(sum(a) for a in test2[BOARD_IDX])))
			#print()
	
# Gets global statistic	
def global_stats():
	tot_solutions = 0
	tot_games     = 0
	for hole_pos in range(0, 15):
		cur_pos = 0
		board   = list()
		for y in range(0, 5):
			row = list()
			for x in range(0, y+1):
				if cur_pos == hole_pos: row.append(0)
				else                  : row.append(1)
				cur_pos += 1
			board.append(row)
	
		init(new_mode=STATS, new_board=board)
		show_board(board)
		ret = run()
		tot_solutions += ret[1]
		tot_games     += ret[2]
		print()
	print("=================")
	print("GLOBAL STATISTICS")
	print("=================")
	print()
	print("Number of possible games    : {}"     .format(tot_games))
	print("Number of possible solutions: {}"     .format(tot_solutions))
	print("Percentage                  : {:.2f}%".format(tot_solutions / tot_games * 100))
	
# Finds the first given solution for the board
def find_solution():
	init(new_mode=SOLUTION, new_board=INIT_BOARD)
	run()
	
# ----------------------------------------------------------------------------------------------------------------------

def main():
	#global_stats()
	find_solution()

if __name__ == "__main__":
	main()