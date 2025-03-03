import argparse
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

def process_image(input_image, output_image, text, transformation):
    # Load the image
    img = Image.open(input_image).convert("RGB")
    
    # Prepare to overlay text
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()  # Default font
    
    # Calculate text size and position it at the bottom center
    text_width, text_height = draw.textsize(text, font=font)
    width, height = img.size
    x = (width - text_width) / 2
    y = height - text_height - 10
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    # Apply the chosen transformation
    if transformation.lower() == "grayscale":
        img = img.convert("L").convert("RGB")
    elif transformation.lower() == "rotate":
        # Rotate 45 degrees with expansion
        img = img.rotate(45, expand=True)
    elif transformation.lower() == "resize":
        # Resize the image to half its original dimensions
        img = img.resize((width // 2, height // 2))
    
    # Save the processed image
    img.save(output_image)
    return output_image

def create_video(image_file, music_file, output_video, duration):
    # Build the FFmpeg command
    command = [
        "ffmpeg",
        "-y",                  # Overwrite output file if it exists
        "-loop", "1",          # Loop the single image
        "-i", image_file,      # Input image
        "-i", music_file,      # Background music
        "-c:v", "libx264",     # Use H.264 codec
        "-t", str(duration),   # Duration of the video
        "-pix_fmt", "yuv420p", # Ensure compatibility with most players
        "-vf", "scale=1280:720", # Scale to 1280x720 resolution
        "-shortest",           # End the video when the shortest input ends
        output_video
    ]
    
    subprocess.run(command, check=True)

def main():
    parser = argparse.ArgumentParser(
        description="Generate a short video from an image using FFmpeg and Pillow."
    )
    parser.add_argument("--image", required=True, help="Path to the input image file.")
    parser.add_argument("--text", required=True, help="Text to overlay on the image.")
    parser.add_argument("--transformation", choices=["grayscale", "rotate", "resize"], default="grayscale", help="Transformation to apply (default: grayscale).")
    parser.add_argument("--music", required=True, help="Path to the background music MP3 file.")
    parser.add_argument("--duration", type=int, default=5, help="Duration of the video in seconds (default: 5).")
    parser.add_argument("--output", default="output_video.mp4", help="Path for the output video file (default: output_video.mp4).")
    parser.add_argument("--temp_image", default="processed_image.png", help="Temporary processed image file.")
    
    args = parser.parse_args()
    
    try:
        print("Processing image...")
        processed_image = process_image(args.image, args.temp_image, args.text, args.transformation)
        print("Creating video...")
        create_video(processed_image, args.music, args.output, args.duration)
        print(f"Video created successfully: {args.output}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Clean up temporary image file
    if os.path.exists(args.temp_image):
        os.remove(args.temp_image)

if __name__ == "__main__":
    main()
