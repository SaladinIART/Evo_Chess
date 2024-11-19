from PIL import Image, ImageDraw

def create_pixel_chess_piece(piece_name, color, size=64):
    # Create a blank image with a transparent background
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Define pixel coordinates for simple shapes representing each piece
    if piece_name[1] == "P":  # Pawn
        pixels = [(28, 48), (36, 48), (36, 32), (28, 32), (24, 28), (40, 28), (32, 16)]
    elif piece_name[1] == "R":  # Rook
        pixels = [(24, 48), (40, 48), (40, 32), (24, 32), (24, 28), (40, 28), (28, 16), (36, 16)]
    elif piece_name[1] == "N":  # Knight
        pixels = [(24, 48), (36, 48), (36, 32), (28, 32), (24, 24), (36, 16)]
    elif piece_name[1] == "B":  # Bishop
        pixels = [(28, 48), (36, 48), (36, 32), (28, 32), (32, 16), (24, 24), (40, 24)]
    elif piece_name[1] == "Q":  # Queen
        pixels = [(24, 48), (40, 48), (40, 28), (24, 28), (28, 16), (32, 12), (36, 16)]
    elif piece_name[1] == "K":  # King
        pixels = [(24, 48), (40, 48), (40, 32), (32, 28), (24, 32), (28, 12), (36, 12)]

    # Draw the pixelated shape
    draw.polygon(pixels, fill=color)

    # Save the image
    image.save(f"images/{piece_name}.png")

def main():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
    colors = {'b': (0, 0, 0, 255), 'w': (255, 255, 255, 255)}

    for piece in pieces:
        color = colors[piece[0]]
        create_pixel_chess_piece(piece, color)

if __name__ == "__main__":
    import os
    # Create images directory if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")
    main()