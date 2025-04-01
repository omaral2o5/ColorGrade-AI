import cv2
import numpy as np
import subprocess
import os
import uuid

def apply_color_transfer(ref_path, video_path, output_path):
    # Load reference image and convert to LAB color space
    ref_img = cv2.imread(ref_path)
    ref_lab = cv2.cvtColor(ref_img, cv2.COLOR_BGR2LAB)
    ref_mean, ref_std = cv2.meanStdDev(ref_lab)

    # Create temp directory for frames
    frame_dir = 'temp_frames_' + str(uuid.uuid4())
    os.makedirs(frame_dir, exist_ok=True)

    # Extract frames from the video
    vidcap = cv2.VideoCapture(video_path)
    frame_paths = []
    index = 0
    success, frame = vidcap.read()
    while success:
        frame_lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        tgt_mean, tgt_std = cv2.meanStdDev(frame_lab)

        # Apply color transfer
        lab_result = (frame_lab - tgt_mean) * (ref_std / (tgt_std + 1e-6)) + ref_mean
        lab_result = np.clip(lab_result, 0, 255).astype('uint8')
        result = cv2.cvtColor(lab_result, cv2.COLOR_LAB2BGR)

        # Save the processed frame
        frame_filename = os.path.join(frame_dir, f'frame_{index:04d}.jpg')
        cv2.imwrite(frame_filename, result)
        frame_paths.append(frame_filename)
        index += 1
        success, frame = vidcap.read()

    vidcap.release()

    # Rebuild video using ffmpeg
    temp_output = os.path.join(frame_dir, 'out.mp4')
    subprocess.call([
        'ffmpeg', '-y', '-framerate', '24',
        '-i', os.path.join(frame_dir, 'frame_%04d.jpg'),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        temp_output
    ])

    # Move the final video to output path
    os.rename(temp_output, output_path)

    # Clean up frames
    for file in os.listdir(frame_dir):
        os.remove(os.path.join(frame_dir, file))
    os.rmdir(frame_dir)
