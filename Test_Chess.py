import unittest
from Chess import Board, King, Rook, Pawn, Queen, Knight, Bishop

class TestChess(unittest.TestCase):
    def test_king_movement(self):
        king = King('w')
        board = [[None]*8 for _ in range(8)]
        board[4][4] = king
        moves = king.valid_moves(board, 4, 4)
        self.assertIn((5, 4), moves)
        self.assertIn((4, 5), moves)
        self.assertEqual(len(moves), 8)  # King can move to 8 adjacent squares

    def test_check_detection(self):
        b = Board()
        b.board = [[None]*8 for _ in range(8)]
        b.board[0][0] = King('w')
        b.board[0][7] = Rook('b')
        self.assertTrue(b.is_check('w'))

    def test_no_check(self):
        b = Board()
        b.board = [[None]*8 for _ in range(8)]
        b.board[0][0] = King('w')
        b.board[7][7] = Rook('b')
        self.assertFalse(b.is_check('w'))

    def test_pawn_promotion(self):
        b = Board()
        b.board = [[None]*8 for _ in range(8)]
        b.board[1][0] = Pawn('w')
        b.move_piece((0, 1), (0, 0))
        self.assertIsInstance(b.board[0][0], Queen)

    def test_castling_kingside(self):
        b = Board()
        b.board = [[None]*8 for _ in range(8)]
        b.board[7][4] = King('w')
        b.board[7][7] = Rook('w')
        king = b.board[7][4]
        rook = b.board[7][7]
        king.has_moved = False
        rook.has_moved = False
        b.move_piece((4, 7), (6, 7))
        self.assertIsInstance(b.board[7][6], King)
        self.assertIsInstance(b.board[7][5], Rook)

    def test_en_passant(self):
        b = Board()
        b.board = [[None]*8 for _ in range(8)]
        white_pawn = Pawn('w')
        black_pawn = Pawn('b')
        b.board[3][4] = white_pawn
        b.board[1][5] = black_pawn
        b.move_piece((5, 1), (5, 3))  # black pawn moves 2 squares
        b.move_piece((4, 3), (5, 2))  # white performs en passant
        self.assertIsNone(b.board[3][5])
        self.assertIsInstance(b.board[2][5], Pawn)

if __name__ == '__main__':
    unittest.main()
