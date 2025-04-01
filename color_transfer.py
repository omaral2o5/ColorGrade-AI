import cv2
import numpy as np
import subprocess

def apply_color_transfer(ref_path, video_path, output_path):
    print("Opening video:", video_path)
    vidcap = cv2.VideoCapture(video_path)
    success, frame = vidcap.read()
    if not success:
        raise Exception("Could not read video")

    ref_img = cv2.imread(ref_path)
    matched = transfer_color(ref_img, frame)

    temp_frame = 'frame_temp.jpg'
    cv2.imwrite(temp_frame, matched)

    subprocess.call([
        'ffmpeg', '-y', '-i', video_path, '-i', temp_frame,
        '-filter_complex', '[1:v]format=rgba,colorchannelmixer=aa=0.5[overlay];[0:v][overlay]overlay',
        output_path
    ])

def transfer_color(source, target):
    source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB)
    target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB)
    mean_src, std_src = cv2.meanStdDev(source_lab)
    mean_tar, std_tar = cv2.meanStdDev(target_lab)

    result = (target_lab - mean_tar) * (std_src / std_tar) + mean_src
    result = np.clip(result, 0, 255).astype('uint8')

    return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
