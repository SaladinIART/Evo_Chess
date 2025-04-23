#!/usr/bin/env python3
"""
Chess Game Implementation using Pygame
--------------------------------------
This module implements a playable chess game with a graphical interface.
Features:
- Visual chess board with alternating colors
- Chess pieces with proper graphics
- Implementation of basic chess movement rules
- Piece selection and movement according to chess rules
- Main menu with single player and multiplayer options
- Simple AI opponent for single player mode
"""

import pygame
import sys
import random
import json
import os
from typing import List, Tuple, Optional, Dict, Set, Any
from enum import Enum

# Initialize pygame
pygame.init()

# Game states
class GameState(Enum):
    MENU = 0
    PLAY = 1

# Game modes
class GameMode(Enum):
    SINGLE_PLAYER = 0
    MULTIPLAYER = 1

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
BOARD_WIDTH = BOARD_HEIGHT = BOARD_SIZE * SQUARE_SIZE
HISTORY_WIDTH = 200  # Width for move history panel
WINDOW_WIDTH = BOARD_WIDTH + HISTORY_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)  # Light brown
DARK_SQUARE = (181, 136, 99)    # Dark brown
HIGHLIGHT_COLOR = (124, 252, 0)  # Light green for highlighting selected pieces
MOVE_HIGHLIGHT = (173, 216, 230)  # Light blue for highlighting possible moves
MENU_BG = (50, 50, 80)          # Dark blue for menu background
BUTTON_COLOR = (100, 100, 150)  # Light blue for buttons
BUTTON_HOVER = (120, 120, 170)  # Lighter blue for button hover
BUTTON_TEXT = (230, 230, 230)   # Off-white for button text

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()

# Fonts
PIECE_FONT = pygame.font.SysFont('segoeuisymbol', 60)
MENU_TITLE_FONT = pygame.font.SysFont('arial', 48, bold=True)
MENU_BUTTON_FONT = pygame.font.SysFont('arial', 32)
HISTORY_FONT = pygame.font.SysFont('arial', 16)

# Piece types
PAWN = 'pawn'
ROOK = 'rook'
KNIGHT = 'knight'
BISHOP = 'bishop'
QUEEN = 'queen'
KING = 'king'

# Piece colors
WHITE_PIECE = 'white'
BLACK_PIECE = 'black'

# Unicode characters for chess pieces
PIECE_CHARS = {
    (WHITE_PIECE, PAWN): '♙',
    (WHITE_PIECE, ROOK): '♖',
    (WHITE_PIECE, KNIGHT): '♘',
    (WHITE_PIECE, BISHOP): '♗',
    (WHITE_PIECE, QUEEN): '♕',
    (WHITE_PIECE, KING): '♔',
    (BLACK_PIECE, PAWN): '♟',
    (BLACK_PIECE, ROOK): '♜',
    (BLACK_PIECE, KNIGHT): '♞',
    (BLACK_PIECE, BISHOP): '♝',
    (BLACK_PIECE, QUEEN): '♛',
    (BLACK_PIECE, KING): '♚',
}

class Button:
    """A button class for menu navigation."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        """
        Initialize a button.
        
        Args:
            x: The x-coordinate of the top-left corner
            y: The y-coordinate of the top-left corner
            width: The width of the button
            height: The height of the button
            text: The text to display on the button
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        
    def draw(self, surface: pygame.Surface):
        """
        Draw the button on the given surface.
        
        Args:
            surface: The surface to draw on
        """
        # Determine the button color based on hover state
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        
        # Draw the button
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BUTTON_TEXT, self.rect, 2)  # Border
        
        # Render the text
        text_surf = MENU_BUTTON_FONT.render(self.text, True, BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Check if the mouse is hovering over the button.
        
        Args:
            mouse_pos: The current mouse position (x, y)
            
        Returns:
            True if the mouse is hovering over the button, False otherwise
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Check if the button is clicked.
        
        Args:
            mouse_pos: The current mouse position (x, y)
            
        Returns:
            True if the button is clicked, False otherwise
        """
        return self.rect.collidepoint(mouse_pos)

class Piece:
    """Base class for all chess pieces."""
    
    def __init__(self, color: str, piece_type: str, row: int, col: int):
        """
        Initialize a chess piece.
        
        Args:
            color: The color of the piece (WHITE_PIECE or BLACK_PIECE)
            piece_type: The type of the piece (PAWN, ROOK, etc.)
            row: The row position on the board (0-7)
            col: The column position on the board (0-7)
        """
        self.color = color
        self.piece_type = piece_type
        self.row = row
        self.col = col
        self.has_moved = False  # Track if the piece has moved (useful for pawns, castling)
        
    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        """
        Get all legal moves for this piece on the current board.
        
        Args:
            board: The current chess board
            
        Returns:
            A list of (row, col) tuples representing legal destination squares
        """
        return []
    
    def render(self, surface: pygame.Surface, x: int, y: int):
        """
        Render the piece on the given surface at the specified position.
        
        Args:
            surface: The surface to render on
            x: The x-coordinate
            y: The y-coordinate
        """
        char = PIECE_CHARS.get((self.color, self.piece_type), '?')
        text_color = WHITE if self.color == WHITE_PIECE else BLACK
        text = PIECE_FONT.render(char, True, text_color)
        text_rect = text.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
        surface.blit(text, text_rect)
    
    def move_to(self, row: int, col: int):
        """
        Move the piece to a new position.
        
        Args:
            row: The new row position
            col: The new column position
        """
        self.row = row
        self.col = col
        self.has_moved = True
        
    def is_valid_position(self, row: int, col: int) -> bool:
        """
        Check if a position is valid on the board.
        
        Args:
            row: The row to check
            col: The column to check
            
        Returns:
            True if the position is on the board, False otherwise
        """
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


class Pawn(Piece):
    """Pawn chess piece."""
    
    def __init__(self, color: str, row: int, col: int):
        """Initialize a pawn."""
        super().__init__(color, PAWN, row, col)
    
    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        """Get all legal moves for this pawn."""
        moves = []
        direction = -1 if self.color == WHITE_PIECE else 1
        
        # Forward move (1 square)
        new_row = self.row + direction
        if self.is_valid_position(new_row, self.col) and board[new_row][self.col] is None:
            moves.append((new_row, self.col))
            
            # Initial two-square move
            if not self.has_moved:
                new_row = self.row + 2 * direction
                if self.is_valid_position(new_row, self.col) and board[new_row][self.col] is None:
                    moves.append((new_row, self.col))
        
        # Capture moves (diagonally)
        for col_offset in [-1, 1]:
            new_col = self.col + col_offset
            new_row = self.row + direction
            
            if self.is_valid_position(new_row, new_col):
                target = board[new_row][new_col]
                if target is not None and target.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves


class Rook(Piece):
    """Rook chess piece."""
    
    def __init__(self, color: str, row: int, col: int):
        """Initialize a rook."""
        super().__init__(color, ROOK, row, col)
    
    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        """Get all legal moves for this rook."""
        moves = []
        
        # Directions: horizontal and vertical
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                new_row, new_col = self.row + i * dr, self.col + i * dc
                
                if not self.is_valid_position(new_row, new_col):
                    break
                
                target = board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves


class Knight(Piece):
    """Knight chess piece."""
    
    def __init__(self, color: str, row: int, col: int):
        """Initialize a knight."""
        super().__init__(color, KNIGHT, row, col)
    
    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        """Get all legal moves for this knight."""
        moves = []
        
        # Knight's L-shaped moves
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dr, dc in offsets:
            new_row, new_col = self.row + dr, self.col + dc
            
            if not self.is_valid_position(new_row, new_col):
                continue
            
            target = board[new_row][new_col]
            if target is None or target.color != self.color:
                moves.append((new_row, new_col))
        
        return moves


class Bishop(Piece):
    """Bishop chess piece."""
    
    def __init__(self, color: str, row: int, col: int):
        """Initialize a bishop."""
        super().__init__(color, BISHOP, row, col)
    
    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        """Get all legal moves for this bishop."""
        moves = []
        
        # Directions: diagonals
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                new_row, new_col = self.row + i * dr, self.col + i * dc
                
                if not self.is_valid_position(new_row, new_col):
                    break
                
                target = board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves


class Queen(Piece):
    """Queen chess piece."""
    
    def __init__(self, color: str, row: int, col: int):
        """Initialize a queen."""
        super().__init__(color, QUEEN, row, col)
    
    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        """Get all legal moves for this queen."""
        moves = []
        
        # Directions: horizontal, vertical, and diagonals (combination of rook and bishop)
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # Rook-like moves
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Bishop-like moves
        ]
        
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                new_row, new_col = self.row + i * dr, self.col + i * dc
                
                if not self.is_valid_position(new_row, new_col):
                    break
                
                target = board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves


class King(Piece):
    """King chess piece."""
    
    def __init__(self, color: str, row: int, col: int):
        """Initialize a king."""
        super().__init__(color, KING, row, col)
    
    def get_legal_moves(self, board) -> List[Tuple[int, int]]:
        """Get all legal moves for this king."""
        moves = []
        
        # King can move one square in any direction
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # Horizontal and vertical
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonals
        ]
        
        for dr, dc in directions:
            new_row, new_col = self.row + dr, self.col + dc
            
            if not self.is_valid_position(new_row, new_col):
                continue
            
            target = board[new_row][new_col]
            if target is None or target.color != self.color:
                moves.append((new_row, new_col))
        
        # Note: Castling is not implemented yet (future expansion)
        
        return moves


class ChessBoard:
    """Represents the chess board and game state."""
    
    def __init__(self):
        """Initialize the chess board with pieces in starting positions."""
        # Create an empty 8x8 board
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Set up the initial piece positions
        self.setup_pieces()
        
        # Game state
        self.selected_piece = None
        self.current_player = WHITE_PIECE
        self.legal_moves = []
        self.move_history = []  # List to store move history
        self.game_mode = None   # Will be set when game starts
    
    def setup_pieces(self):
        """Set up the chess pieces in their initial positions."""
        # Set up pawns
        for col in range(BOARD_SIZE):
            self.board[1][col] = Pawn(BLACK_PIECE, 1, col)
            self.board[6][col] = Pawn(WHITE_PIECE, 6, col)
        
        # Set up rooks
        self.board[0][0] = Rook(BLACK_PIECE, 0, 0)
        self.board[0][7] = Rook(BLACK_PIECE, 0, 7)
        self.board[7][0] = Rook(WHITE_PIECE, 7, 0)
        self.board[7][7] = Rook(WHITE_PIECE, 7, 7)
        
        # Set up knights
        self.board[0][1] = Knight(BLACK_PIECE, 0, 1)
        self.board[0][6] = Knight(BLACK_PIECE, 0, 6)
        self.board[7][1] = Knight(WHITE_PIECE, 7, 1)
        self.board[7][6] = Knight(WHITE_PIECE, 7, 6)
        
        # Set up bishops
        self.board[0][2] = Bishop(BLACK_PIECE, 0, 2)
        self.board[0][5] = Bishop(BLACK_PIECE, 0, 5)
        self.board[7][2] = Bishop(WHITE_PIECE, 7, 2)
        self.board[7][5] = Bishop(WHITE_PIECE, 7, 5)
        
        # Set up queens
        self.board[0][3] = Queen(BLACK_PIECE, 0, 3)
        self.board[7][3] = Queen(WHITE_PIECE, 7, 3)
        
        # Set up kings
        self.board[0][4] = King(BLACK_PIECE, 0, 4)
        self.board[7][4] = King(WHITE_PIECE, 7, 4)
    
    def get_piece_at(self, row: int, col: int) -> Optional[Piece]:
        """
        Get the piece at the specified position.
        
        Args:
            row: The row position
            col: The column position
            
        Returns:
            The piece at the position, or None if no piece is there
        """
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.board[row][col]
        return None
    
    def select_piece(self, row: int, col: int) -> bool:
        """
        Select a piece at the specified position.
        
        Args:
            row: The row position
            col: The column position
            
        Returns:
            True if a piece was selected, False otherwise
        """
        piece = self.get_piece_at(row, col)
        
        if piece is not None and piece.color == self.current_player:
            self.selected_piece = piece
            self.legal_moves = piece.get_legal_moves(self.board)
            return True
        
        return False
    
    def move_selected_piece(self, row: int, col: int) -> bool:
        """
        Move the selected piece to the specified position.
        
        Args:
            row: The destination row
            col: The destination column
            
        Returns:
            True if the move was successful, False otherwise
        """
        if self.selected_piece is None:
            return False
        
        if (row, col) not in self.legal_moves:
            return False
        
        # Store the original position
        old_row, old_col = self.selected_piece.row, self.selected_piece.col
        
        # Check if this is a capture move
        is_capture = self.board[row][col] is not None
        
        # Update the board
        self.board[old_row][old_col] = None
        self.board[row][col] = self.selected_piece
        
        # Record the move in algebraic notation
        move_notation = get_move_notation(
            old_row, old_col, row, col, 
            self.selected_piece, is_capture
        )
        self.move_history.append(move_notation)
        
        # Update the piece's position
        self.selected_piece.move_to(row, col)
        
        # Switch players
        self.current_player = BLACK_PIECE if self.current_player == WHITE_PIECE else WHITE_PIECE
        
        # Reset selection
        self.selected_piece = None
        self.legal_moves = []
        
        return True
    
    def get_all_valid_moves(self, color: str) -> List[Tuple[Piece, Tuple[int, int]]]:
        """
        Get all valid moves for pieces of the specified color.
        
        Args:
            color: The color of the pieces to get moves for
            
        Returns:
            A list of (piece, (row, col)) tuples representing all valid moves
        """
        all_moves = []
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is not None and piece.color == color:
                    legal_moves = piece.get_legal_moves(self.board)
                    for move in legal_moves:
                        all_moves.append((piece, move))
        
        return all_moves
    
    def make_ai_move(self) -> bool:
        """
        Make a move for the AI (black pieces).
        
        Returns:
            True if a move was made, False otherwise
        """
        if self.current_player != BLACK_PIECE:
            return False
        
        # Get all valid moves for black pieces
        all_moves = self.get_all_valid_moves(BLACK_PIECE)
        
        if not all_moves:
            return False
        
        # Choose a random move
        piece, (row, col) = random.choice(all_moves)
        
        # Store the original position
        old_row, old_col = piece.row, piece.col
        
        # Check if this is a capture move
        is_capture = self.board[row][col] is not None
        
        # Update the board
        self.board[old_row][old_col] = None
        self.board[row][col] = piece
        
        # Record the move in algebraic notation
        move_notation = get_move_notation(
            old_row, old_col, row, col, 
            piece, is_capture
        )
        self.move_history.append(move_notation)
        
        # Update the piece's position
        piece.move_to(row, col)
        
        # Switch players
        self.current_player = WHITE_PIECE
        
        return True
    
    def render(self, surface: pygame.Surface):
        """
        Render the chess board and pieces.
        
        Args:
            surface: The surface to render on
        """
        # Draw the board
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Calculate the position
                x, y = col * SQUARE_SIZE, row * SQUARE_SIZE
                
                # Determine the square color
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                
                # Draw the square
                pygame.draw.rect(surface, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                # Highlight the selected piece
                if (self.selected_piece is not None and 
                    self.selected_piece.row == row and 
                    self.selected_piece.col == col):
                    pygame.draw.rect(surface, HIGHLIGHT_COLOR, 
                                    (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)
                
                # Highlight legal moves
                if (row, col) in self.legal_moves:
                    pygame.draw.rect(surface, MOVE_HIGHLIGHT, 
                                    (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)
        
        # Draw the pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is not None:
                    x, y = col * SQUARE_SIZE, row * SQUARE_SIZE
                    piece.render(surface, x, y)
        
        # Draw the move history panel
        history_x = BOARD_WIDTH
        
        # Draw the history panel background
        pygame.draw.rect(surface, (240, 240, 240), 
                        (history_x, 0, HISTORY_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(surface, (200, 200, 200), 
                        (history_x, 0), (history_x, WINDOW_HEIGHT), 2)
        
        # Draw the history title
        title_text = MENU_BUTTON_FONT.render("Move History", True, BLACK)
        title_rect = title_text.get_rect(center=(history_x + HISTORY_WIDTH // 2, 30))
        surface.blit(title_text, title_rect)
        
        # Draw the move history
        move_y = 70
        move_height = 25
        max_visible_moves = (WINDOW_HEIGHT - move_y) // move_height
        
        # Display moves in pairs (white and black)
        move_pairs = []
        for i in range(0, len(self.move_history), 2):
            white_move = self.move_history[i] if i < len(self.move_history) else ""
            black_move = self.move_history[i+1] if i+1 < len(self.move_history) else ""
            move_pairs.append((white_move, black_move))
        
        # Show the most recent moves if there are more than can fit
        start_idx = max(0, len(move_pairs) - max_visible_moves)
        
        for i, (white_move, black_move) in enumerate(move_pairs[start_idx:]):
            move_num = start_idx + i + 1
            move_text = f"{move_num}. {white_move} {black_move}"
            text = HISTORY_FONT.render(move_text, True, BLACK)
            surface.blit(text, (history_x + 10, move_y + i * move_height))


class Menu:
    """Represents the game menu."""
    
    def __init__(self):
        """Initialize the menu with buttons."""
        button_width = 300
        button_height = 60
        button_x = (WINDOW_WIDTH - button_width) // 2
        button_spacing = 75  # Increased spacing for more buttons
        
        # Create buttons
        self.single_player_button = Button(
            button_x, 200, button_width, button_height, "Single Player"
        )
        self.multiplayer_button = Button(
            button_x, 200 + button_spacing, button_width, button_height, "Multiplayer"
        )
        self.save_game_button = Button(
            button_x, 200 + 2 * button_spacing, button_width, button_height, "Save Game"
        )
        self.load_game_button = Button(
            button_x, 200 + 3 * button_spacing, button_width, button_height, "Load Game"
        )
        self.exit_button = Button(
            button_x, 200 + 4 * button_spacing, button_width, button_height, "Exit Game"
        )
        
        # List of all buttons for easy iteration
        self.buttons = [
            self.single_player_button,
            self.multiplayer_button,
            self.save_game_button,
            self.load_game_button,
            self.exit_button
        ]
        
        # Status message for save/load operations
        self.status_message = ""
        self.status_time = 0
    
    def handle_event(self, event, chess_board=None) -> Optional[str]:
        """
        Handle menu events.
        
        Args:
            event: The pygame event to handle
            chess_board: The current chess board (for save/load operations)
            
        Returns:
            The selected action ("mode:single_player", "mode:multiplayer", 
            "save", "load", or None)
        """
        if event.type == pygame.MOUSEMOTION:
            # Update button hover states
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                button.check_hover(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if a button was clicked
            mouse_pos = pygame.mouse.get_pos()
            
            if self.single_player_button.is_clicked(mouse_pos):
                return "mode:single_player"
            
            elif self.multiplayer_button.is_clicked(mouse_pos):
                return "mode:multiplayer"
            
            elif self.save_game_button.is_clicked(mouse_pos):
                if chess_board is not None:
                    success = save_game(chess_board)
                    if success:
                        self.status_message = "Game saved successfully!"
                    else:
                        self.status_message = "Failed to save game."
                    self.status_time = pygame.time.get_ticks()
                return "save"
            
            elif self.load_game_button.is_clicked(mouse_pos):
                if chess_board is not None:
                    success = load_game(chess_board)
                    if success:
                        self.status_message = "Game loaded successfully!"
                    else:
                        self.status_message = "Failed to load game."
                    self.status_time = pygame.time.get_ticks()
                return "load"
            
            elif self.exit_button.is_clicked(mouse_pos):
                pygame.quit()
                sys.exit()
        
        return None
    
    def render(self, surface: pygame.Surface):
        """
        Render the menu.
        
        Args:
            surface: The surface to render on
        """
        # Fill the background
        surface.fill(MENU_BG)
        
        # Draw the title
        title_text = MENU_TITLE_FONT.render("Chess Game", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
        surface.blit(title_text, title_rect)
        
        # Draw the buttons
        for button in self.buttons:
            button.draw(surface)
        
        # Draw status message if it exists and hasn't timed out
        if self.status_message and pygame.time.get_ticks() - self.status_time < 3000:  # Show for 3 seconds
            status_text = MENU_BUTTON_FONT.render(self.status_message, True, WHITE)
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
            surface.blit(status_text, status_rect)


def main():
    """Main function to run the chess game."""
    # Create the chess board and menu
    chess_board = ChessBoard()
    menu = Menu()
    
    # Game state and mode
    game_state = GameState.MENU
    game_mode = None
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Menu state
            if game_state == GameState.MENU:
                selected_action = menu.handle_event(event, chess_board)
                
                if selected_action == "mode:single_player":
                    game_mode = GameMode.SINGLE_PLAYER
                    chess_board.game_mode = game_mode
                    game_state = GameState.PLAY
                    # Reset the chess board for a new game
                    chess_board = ChessBoard()
                    chess_board.game_mode = game_mode
                    chess_board.move_history = []
                
                elif selected_action == "mode:multiplayer":
                    game_mode = GameMode.MULTIPLAYER
                    chess_board.game_mode = game_mode
                    game_state = GameState.PLAY
                    # Reset the chess board for a new game
                    chess_board = ChessBoard()
                    chess_board.game_mode = game_mode
                    chess_board.move_history = []
                
                elif selected_action == "load":
                    # If a game was successfully loaded, switch to play state
                    if chess_board.game_mode is not None:
                        game_mode = chess_board.game_mode
                        game_state = GameState.PLAY
            
            # Play state
            elif game_state == GameState.PLAY:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Return to menu when Escape is pressed
                    game_state = GameState.MENU
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Get the mouse position
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Only process clicks within the board area
                    if mouse_pos[0] < BOARD_WIDTH:
                        # Convert to board coordinates
                        col = mouse_pos[0] // SQUARE_SIZE
                        row = mouse_pos[1] // SQUARE_SIZE
                        
                        # If a piece is already selected, try to move it
                        if chess_board.selected_piece is not None:
                            # If the move is successful or if the same piece is clicked again, deselect
                            if chess_board.move_selected_piece(row, col) or (
                                chess_board.selected_piece.row == row and 
                                chess_board.selected_piece.col == col):
                                chess_board.selected_piece = None
                                chess_board.legal_moves = []
                                
                                # If in single player mode and it's the AI's turn, make an AI move
                                if (game_mode == GameMode.SINGLE_PLAYER and 
                                    chess_board.current_player == BLACK_PIECE):
                                    # Add a small delay to make the AI move more visible
                                    pygame.time.delay(500)
                                    chess_board.make_ai_move()
                            
                            # If another piece of the same color is clicked, select it instead
                            elif chess_board.select_piece(row, col):
                                pass  # The piece is now selected
                        else:
                            # Try to select a piece
                            chess_board.select_piece(row, col)
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Render the current state
        if game_state == GameState.MENU:
            menu.render(screen)
        else:  # GameState.PLAY
            chess_board.render(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Quit pygame
    pygame.quit()
    sys.exit()


# Helper functions for save/load functionality and chess notation

def get_algebraic_notation(row: int, col: int) -> str:
    """Convert board coordinates to algebraic notation."""
    file = chr(ord('a') + col)
    rank = str(8 - row)
    return file + rank

def get_board_coordinates(algebraic: str) -> Tuple[int, int]:
    """Convert algebraic notation to board coordinates."""
    file = algebraic[0]
    rank = algebraic[1]
    col = ord(file) - ord('a')
    row = 8 - int(rank)
    return row, col

def get_piece_notation(piece: Piece) -> str:
    """Get the notation letter for a piece."""
    if piece.piece_type == PAWN:
        return ""
    elif piece.piece_type == KNIGHT:
        return "N"
    elif piece.piece_type == BISHOP:
        return "B"
    elif piece.piece_type == ROOK:
        return "R"
    elif piece.piece_type == QUEEN:
        return "Q"
    elif piece.piece_type == KING:
        return "K"
    return ""

def get_move_notation(start_row: int, start_col: int, end_row: int, end_col: int, 
                      piece: Piece, is_capture: bool = False) -> str:
    """Generate standard algebraic notation for a move."""
    piece_letter = get_piece_notation(piece)
    start_square = get_algebraic_notation(start_row, start_col)
    end_square = get_algebraic_notation(end_row, end_col)
    
    # For pawns, we don't include the piece letter
    if piece.piece_type == PAWN:
        if is_capture:
            return f"{start_square[0]}x{end_square}"
        else:
            return end_square
    
    # For other pieces
    if is_capture:
        return f"{piece_letter}x{end_square}"
    else:
        return f"{piece_letter}{end_square}"

def game_to_dict(chess_board) -> Dict[str, Any]:
    """Convert game state to a dictionary for saving."""
    board_data = []
    for row in range(BOARD_SIZE):
        row_data = []
        for col in range(BOARD_SIZE):
            piece = chess_board.board[row][col]
            if piece is None:
                row_data.append(None)
            else:
                piece_data = {
                    "color": piece.color,
                    "type": piece.piece_type,
                    "has_moved": piece.has_moved
                }
                row_data.append(piece_data)
        board_data.append(row_data)
    
    return {
        "board": board_data,
        "current_player": chess_board.current_player,
        "game_mode": chess_board.game_mode.value if hasattr(chess_board, "game_mode") else None,
        "move_history": chess_board.move_history
    }

def dict_to_game(data: Dict[str, Any], chess_board) -> None:
    """Load game state from a dictionary."""
    # Clear the current board
    chess_board.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    # Load the board state
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece_data = data["board"][row][col]
            if piece_data is not None:
                # Create the appropriate piece
                piece_type = piece_data["type"]
                color = piece_data["color"]
                
                if piece_type == PAWN:
                    piece = Pawn(color, row, col)
                elif piece_type == ROOK:
                    piece = Rook(color, row, col)
                elif piece_type == KNIGHT:
                    piece = Knight(color, row, col)
                elif piece_type == BISHOP:
                    piece = Bishop(color, row, col)
                elif piece_type == QUEEN:
                    piece = Queen(color, row, col)
                elif piece_type == KING:
                    piece = King(color, row, col)
                
                piece.has_moved = piece_data["has_moved"]
                chess_board.board[row][col] = piece
    
    # Load other game state
    chess_board.current_player = data["current_player"]
    if hasattr(chess_board, "game_mode") and data["game_mode"] is not None:
        chess_board.game_mode = GameMode(data["game_mode"])
    
    # Load move history
    chess_board.move_history = data.get("move_history", [])

def save_game(chess_board, filename: str = "chess_save.json") -> bool:
    """Save the current game state to a file."""
    try:
        game_data = game_to_dict(chess_board)
        with open(filename, 'w') as f:
            json.dump(game_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False

def load_game(chess_board, filename: str = "chess_save.json") -> bool:
    """Load a game state from a file."""
    try:
        if not os.path.exists(filename):
            print(f"Save file {filename} does not exist")
            return False
        
        with open(filename, 'r') as f:
            game_data = json.load(f)
        
        dict_to_game(game_data, chess_board)
        return True
    except Exception as e:
        print(f"Error loading game: {e}")
        return False

if __name__ == "__main__":
    main()
