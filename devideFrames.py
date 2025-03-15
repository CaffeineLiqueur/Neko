from PIL import Image
import pygame
import sys
import os

def split_sprite_sheet(image_path, rows, cols, output_dir):
    """
    分割精灵表为单帧图片。
    :param image_path: 精灵表路径
    :param rows: 行数
    :param cols: 列数
    :param output_dir: 输出文件夹
    """
    img = Image.open(image_path)
    frame_width = img.width // cols
    frame_height = img.height // rows

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frames = []
    for row in range(rows):
        for col in range(cols):
            left = col * frame_width
            top = row * frame_height
            right = left + frame_width
            bottom = top + frame_height
            frame = img.crop((left, top, right, bottom))
            frame_path = os.path.join(output_dir, f"frame_{row}_{col}.png")
            frame.save(frame_path)
            frames.append(frame_path)
    return frames