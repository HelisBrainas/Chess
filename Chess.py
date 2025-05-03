import pygame
import sys
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE = (245, 245, 220)
BLACK = (139, 69, 19)
SELECTED_COLOR = (255, 255, 0)

# Load piece images
PIECE_IMAGES = {}
PIECES = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
COLORS = ['w', 'b']
for color in COLORS:
    for piece in PIECES:
        img = pygame.image.load(f'images/{color}_{piece}.png')
        PIECE_IMAGES[f'{color}_{piece}'] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess')

font = pygame.font.SysFont('arial', 36)

class Piece:
    def __init__(self, color, name):
        self.color = color
        self.name = name
        self.image = PIECE_IMAGES[f'{color}_{name}']
        self.has_moved = False

    def valid_moves(self, board, x, y):
        return []

class King(Piece):
    def __init__(self, color):
        super().__init__(color, 'king')

    def valid_moves(self, board, x, y):
        moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < COLS and 0 <= ny < ROWS:
                    target = board[ny][nx]
                    if target is None or target.color != self.color:
                        moves.append((nx, ny))

        if not self.has_moved:
            row = 7 if self.color == 'w' else 0
            if isinstance(board[row][7], Rook) and not board[row][7].has_moved:
                if all(board[row][i] is None for i in [5, 6]):
                    moves.append((6, row))
            if isinstance(board[row][0], Rook) and not board[row][0].has_moved:
                if all(board[row][i] is None for i in [1, 2, 3]):
                    moves.append((2, row))
        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, 'queen')

    def valid_moves(self, board, x, y):
        return Rook(self.color).valid_moves(board, x, y) + Bishop(self.color).valid_moves(board, x, y)

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, 'rook')

    def valid_moves(self, board, x, y):
        moves = []
        directions = [(0,1), (1,0), (0,-1), (-1,0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < COLS and 0 <= ny < ROWS:
                if board[ny][nx] is None:
                    moves.append((nx, ny))
                elif board[ny][nx].color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, 'bishop')

    def valid_moves(self, board, x, y):
        moves = []
        directions = [(1,1), (-1,1), (-1,-1), (1,-1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < COLS and 0 <= ny < ROWS:
                if board[ny][nx] is None:
                    moves.append((nx, ny))
                elif board[ny][nx].color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, 'knight')

    def valid_moves(self, board, x, y):
        moves = []
        offsets = [(2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)]
        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if board[ny][nx] is None or board[ny][nx].color != self.color:
                    moves.append((nx, ny))
        return moves

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, 'pawn')
        self.__just_moved_two = False

    def set_just_moved_two(self, value: bool):
        self.__just_moved_two = value

    def get_just_moved_two(self):
        return self.__just_moved_two

    def valid_moves(self, board, x, y):
        direction = -1 if self.color == 'w' else 1
        start_row = 6 if self.color == 'w' else 1
        moves = []
        if 0 <= y + direction < ROWS and board[y + direction][x] is None:
            moves.append((x, y + direction))
            if y == start_row and board[y + 2 * direction][x] is None:
                moves.append((x, y + 2 * direction))
        for dx in [-1, 1]:
            nx, ny = x + dx, y + direction
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                target = board[ny][nx]
                if target and target.color != self.color:
                    moves.append((nx, ny))
                # En passant
                ep_row = 3 if self.color == 'w' else 4
                if y == ep_row and isinstance(board[y][nx], Pawn) and board[y][nx].color != self.color:
                    if board[y][nx].get_just_moved_two():
                        moves.append((nx, ny))
        return moves

class Board:
    def __init__(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.setup_board()

    def setup_board(self):
        for i in range(COLS):
            self.board[1][i] = Pawn('b')
            self.board[6][i] = Pawn('w')
        placements = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, piece_class in enumerate(placements):
            self.board[0][i] = piece_class('b')
            self.board[7][i] = piece_class('w')

    def draw(self, screen, selected_square=None, valid_moves=[], winner=None):
        for row in range(ROWS):
            for col in range(COLS):
                color = WHITE if (row + col) % 2 == 0 else BLACK
                pygame.draw.rect(screen, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                if (col, row) in valid_moves:
                    pygame.draw.rect(screen, SELECTED_COLOR, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)
                piece = self.board[row][col]
                if piece:
                    screen.blit(piece.image, (col*SQUARE_SIZE, row*SQUARE_SIZE))

        if winner:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            text = font.render(f'{winner} wins!', True, (255, 255, 255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))

    def move_piece(self, start_pos, end_pos):
        x1, y1 = start_pos
        x2, y2 = end_pos
        piece = self.board[y1][x1]

        for row in self.board:
            for p in row:
                if isinstance(p, Pawn):
                    p.set_just_moved_two(False)

        if isinstance(piece, King) and abs(x2 - x1) == 2:
            row = y1
            if x2 == 6:
                self.board[row][5] = self.board[row][7]
                self.board[row][7] = None
            else:
                self.board[row][3] = self.board[row][0]
                self.board[row][0] = None

        if isinstance(piece, Pawn) and abs(y2 - y1) == 2:
            piece.set_just_moved_two( True)

        if isinstance(piece, Pawn) and x2 != x1 and self.board[y2][x2] is None:
            self.board[y1][x2] = None

        if isinstance(piece, Pawn) and (y2 == 0 or y2 == 7):
            piece = Queen(piece.color)

        self.board[y2][x2] = piece
        self.board[y1][x1] = None
        piece.has_moved = True

    def get_piece(self, x, y):
        return self.board[y][x]

    def is_check(self, color):
        king_pos = None
        for y in range(ROWS):
            for x in range(COLS):
                piece = self.board[y][x]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (x, y)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        for y in range(ROWS):
            for x in range(COLS):
                piece = self.board[y][x]
                if piece and piece.color != color:
                    if king_pos in piece.valid_moves(self.board, x, y):
                        return True
        return False

    def has_legal_moves(self, color):
        for y in range(ROWS):
            for x in range(COLS):
                piece = self.board[y][x]
                if piece and piece.color == color:
                    moves = piece.valid_moves(self.board, x, y)
                    for move in moves:
                        original = self.board[move[1]][move[0]]
                        self.board[move[1]][move[0]] = piece
                        self.board[y][x] = None
                        if not self.is_check(color):
                            self.board[y][x] = piece
                            self.board[move[1]][move[0]] = original
                            return True
                        self.board[y][x] = piece
                        self.board[move[1]][move[0]] = original
        return False
    def copy(self):
        new_board = Board()
        for y in range(ROWS):
            for x in range(COLS):
                piece = self.board[y][x]
                if piece:
                    # Manually create a new piece object with the same properties
                    new_piece = type(piece)(piece.color)
                    new_piece.has_moved = piece.has_moved
                    new_board.board[y][x] = new_piece
        return new_board


class Game:
    def __init__(self):
        self.board = Board()
        self.selected = None
        self.valid_moves = []
        self.turn = 'w'
        self.move_number = 1
        self.last_move = ""
        self.history = []
        self.winner = None
        self.log_file = open("chess_log.txt", "w")
        self.log_file.write(f"Game started at {datetime.now()}\n")
    
    def to_chess_notation(self, pos):
        x, y = pos
        file = chr(x + ord('a'))
        rank = str(ROWS - y)
        return f"{file}{rank}"

    def handle_click(self, pos):
        if self.winner:
            return

        x, y = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
        if self.selected:
            if (x, y) in self.valid_moves:
                self.history.append(self.board)
                start_piece = self.board.get_piece(*self.selected)
                self.board.move_piece(self.selected, (x, y))
                if self.board.is_check(self.turn):
                    self.board = self.history.pop()
                else:
                    move_notation = self.to_chess_notation(self.selected) + self.to_chess_notation((x, y))
                    if self.turn == 'w':
                        self.last_move = move_notation
                    else:
                        self.log_file.write(f"{self.move_number}. {self.last_move} {move_notation}\n")
                        self.move_number += 1
                    opponent = 'b' if self.turn == 'w' else 'w'
                    if self.board.is_check(opponent) and not self.board.has_legal_moves(opponent):
                        self.winner = 'White' if self.turn == 'w' else 'Black'
                        self.log_file.write(f"Checkmate. {self.winner} wins.\n")
                    elif not self.board.has_legal_moves(opponent):
                        self.winner = 'Draw'
                        self.log_file.write("Stalemate. Game drawn.\n")
                    self.turn = opponent
            self.selected = None
            self.valid_moves = []
        else:
            piece = self.board.get_piece(x, y)
            if piece and piece.color == self.turn:
                self.selected = (x, y)
                self.valid_moves = [move for move in piece.valid_moves(self.board.board, x, y) if not self.would_cause_check(x, y, move)]


    def would_cause_check(self, x, y, move):
        original = self.board.board[move[1]][move[0]]
        piece = self.board.board[y][x]
        self.board.board[move[1]][move[0]] = piece
        self.board.board[y][x] = None
        result = self.board.is_check(piece.color)
        self.board.board[y][x] = piece
        self.board.board[move[1]][move[0]] = original
        return result

    def undo(self):
        if self.history:
            self.board = self.history.pop()
            self.turn = 'b' if self.turn == 'w' else 'w'
            self.selected = None
            self.valid_moves = []
            self.winner = None
            self.log_file.write("Undo move.\n")

    def mainloop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.log_file.write("Game ended by user.\n")
                    self.log_file.close()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
            self.board.draw(screen, self.selected, self.valid_moves, self.winner)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    Game().mainloop()

