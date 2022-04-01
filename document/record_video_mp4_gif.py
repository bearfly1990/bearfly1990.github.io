import os
import cv2
from PIL import ImageGrab, Image, ImageSequence
import numpy as np
import argparse
from datetime import datetime
import keyboard
from moviepy.editor import *
import argparse

global img
global point1, point2


# def compressGif(filename):
#     gif = Image.open(filename)
#     if not gif.is_animated:
#         return False
#     imageio.mimsave('compress-' + filename, [frame.convert('RGB') for frame in ImageSequence.Iterator(gif)],
#                     duration=gif.info['duration'] / 2000)


def time_flag():
    return datetime.strftime(datetime.now(), '%y%m%d.%H%M%S')


def on_mouse(event, x, y, flags, param):
    global img, point1, point2
    img2 = img.copy()
    if event == cv2.EVENT_LBUTTONDOWN:
        point1 = (x, y)
        cv2.circle(img2, point1, 10, (0, 255, 0), thickness=2)
        cv2.imshow('image', img2)
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):
        cv2.rectangle(img2, point1, (x, y), (255, 0, 0), thickness=2)
        cv2.imshow('image', img2)
    elif event == cv2.EVENT_LBUTTONUP:
        point2 = (x, y)
        cv2.rectangle(img2, point1, point2, (0, 0, 255), thickness=2)
        cv2.imshow('image', img2)


def select_roi(frame):
    global img, point1, point2
    img = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
    win_name = 'image'
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(win_name, on_mouse)
    cv2.imshow(win_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return point1, point2


def start_record(*args):
    args = args[0]
    print('press alt+F10 to stop the recording')
    print('#' * 80)
    savename = args.savename
    print(savename)
    cur_screen = ImageGrab.grab()
    if args.screen_type:
        height, width = cur_screen.size
        min_x, min_y, max_x, max_y = 0, 0, width, height
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(savename, fourcc, args.fps, (height, width))
    else:
        point1, point2 = select_roi(cur_screen)
        min_x = min(point1[0], point2[0])
        min_y = min(point1[1], point2[1])
        max_x = max(point1[0], point2[0])
        max_y = max(point1[1], point2[1])

        height, width = max_y - min_y, max_x - min_x

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(savename, fourcc, args.fps, (width, height))

    print(datetime.now(), '"Record Video Started..."')
    imageNum = 0
    while True:
        imageNum += 1
        captureImage = ImageGrab.grab()
        frame = cv2.cvtColor(np.array(captureImage), cv2.COLOR_RGB2BGR)
        if args.screen_type == 0:
            frame = frame[min_y:max_y, min_x:max_x, :]
        video.write(frame)
        if keyboard.is_pressed('alt+f10'):
            break

    video.release()
    cv2.destroyAllWindows()
    if args.gif:
        print('save to gif...')
        videoclip = VideoFileClip(savename)
        # videoclip = videoclip.resize(0.8)
        videoclip.write_gif(f"{savename}.gif", fuzz=1, fps=videoclip.fps, loop=0, program='ffmpeg')
    print(datetime.now(), '"Record Video Ended..."')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--savename', type=str, default=f'output.{time_flag()}.mp4', help='save file name')
    parser.add_argument('--fps', type=int, default=20, help='frame per second')
    parser.add_argument('--screen_type', default=1, type=int, choices=[0, 1],
                        help='1: generate gif, 0: not generate gif')
    parser.add_argument('--gif', default=1, type=int, choices=[0, 1],
                        help='1: generate gif, 0: not generate gif')
    args = parser.parse_args()
    print('#' * 80)
    print('press alt+F9 to start the recording')
    keyboard.add_hotkey('alt + f9', start_record, args=(args, None))
    keyboard.wait('esc')
