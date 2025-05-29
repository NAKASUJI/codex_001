import curses
import random
import time

# Game configuration
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
TETROMINOS = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'S': [
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'Z': [
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
}
TETROMINO_COLORS = {
    'I': 1,
    'J': 2,
    'L': 3,
    'O': 4,
    'S': 5,
    'T': 6,
    'Z': 7,
}

SPEED = 0.5

class Piece:
    def __init__(self, type_):
        self.type = type_
        self.rotation = 0
        self.x = BOARD_WIDTH // 2 - 2
        self.y = 0

    @property
    def blocks(self):
        shape = TETROMINOS[self.type][self.rotation]
        return [(self.x + x, self.y + y) for x, y in shape]

    def rotate(self, board):
        next_rotation = (self.rotation + 1) % len(TETROMINOS[self.type])
        shape = TETROMINOS[self.type][next_rotation]
        blocks = [(self.x + x, self.y + y) for x, y in shape]
        if all(0 <= bx < BOARD_WIDTH and 0 <= by < BOARD_HEIGHT and not board[by][bx] for bx, by in blocks):
            self.rotation = next_rotation

    def move(self, dx, dy, board):
        blocks = [(bx + dx, by + dy) for bx, by in self.blocks]
        if all(0 <= bx < BOARD_WIDTH and 0 <= by < BOARD_HEIGHT and not board[by][bx] for bx, by in blocks):
            self.x += dx
            self.y += dy
            return True
        return False


def draw_board(stdscr, board, piece, score):
    stdscr.clear()
    h, w = BOARD_HEIGHT, BOARD_WIDTH
    for y in range(h):
        for x in range(w):
            val = board[y][x]
            if val:
                stdscr.addstr(y, x * 2, '[]', curses.color_pair(val))
            else:
                stdscr.addstr(y, x * 2, ' .')

    for x, y in piece.blocks:
        if y >= 0:
            stdscr.addstr(y, x * 2, '[]', curses.color_pair(TETROMINO_COLORS[piece.type]))

    stdscr.addstr(h + 1, 0, f'Score: {score}')
    stdscr.refresh()


def remove_complete_lines(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    lines_cleared = BOARD_HEIGHT - len(new_board)
    while len(new_board) < BOARD_HEIGHT:
        new_board.insert(0, [0] * BOARD_WIDTH)
    return new_board, lines_cleared


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    for i in range(1, 8):
        curses.init_pair(i, i, 0)

    board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
    current = Piece(random.choice(list(TETROMINOS.keys())))
    next_piece = Piece(random.choice(list(TETROMINOS.keys())))
    score = 0
    last_time = time.time()

    while True:
        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            current.move(-1, 0, board)
        elif key == curses.KEY_RIGHT:
            current.move(1, 0, board)
        elif key == curses.KEY_DOWN:
            if not current.move(0, 1, board):
                for x, y in current.blocks:
                    board[y][x] = TETROMINO_COLORS[current.type]
                board, lines = remove_complete_lines(board)
                score += lines * 100
                current = next_piece
                next_piece = Piece(random.choice(list(TETROMINOS.keys())))
                if not current.move(0, 0, board):
                    break
        elif key == curses.KEY_UP:
            current.rotate(board)
        elif key == ord('q'):
            break

        if time.time() - last_time > SPEED:
            if not current.move(0, 1, board):
                for x, y in current.blocks:
                    board[y][x] = TETROMINO_COLORS[current.type]
                board, lines = remove_complete_lines(board)
                score += lines * 100
                current = next_piece
                next_piece = Piece(random.choice(list(TETROMINOS.keys())))
                if not current.move(0, 0, board):
                    break
            last_time = time.time()

        draw_board(stdscr, board, current, score)

    stdscr.nodelay(False)
    stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH, "Game Over! Press any key to exit.")
    stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)

