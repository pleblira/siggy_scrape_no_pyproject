from moviepy.editor import VideoFileClip
from PIL import Image, ImageSequence
import numpy as np

def mp4_to_gif(input_file, output_file):
    clip = VideoFileClip(input_file)

    frame_duration = 1 / clip.fps

    duration = clip.duration
    num_frames = int(duration / frame_duration)
    frames = [clip.get_frame(t) for t in np.linspace(0, duration, num=num_frames)]

    # Save frames as GIF using PIL
    frames_pil = [Image.fromarray(frame) for frame in frames]
    frames_pil[0].save(output_file, save_all=True, append_images=frames_pil[1:], optimize=False, duration=frame_duration * 1000, loop=0)

if __name__ == "__main__":
    mp4_to_gif("mp4.mp4","gif.gif")