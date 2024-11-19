from PIL import Image, ImageDraw, ImageFont

def create_chess_piece_image(piece_name, color, size=100):
    # Create a blank image with white background
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)

    # Choose font and size (you can customize this)
    font = ImageFont.load_default()

    # Draw a simple shape or text representing the piece
    text = piece_name[1]  # R, N, B, Q, K, or P
    draw.text((size // 3, size // 3), text, fill=color, font=font)

    # Save the image
    image.save(f"images/{piece_name}.png")

def main():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
    colors = {'b': "black", 'w': "white"}

    for piece in pieces:
        color = colors[piece[0]]
        create_chess_piece_image(piece, color)

if __name__ == "__main__":
    import os
    # Create images directory if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")
    main()