import glob
import logging

import cv2

from action import Action
import config

def main():

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)

    action = Action(debug=True)

    for image in sorted(glob.glob(r'C:\Users\HOME\Pictures\MEmu Photo\Screenshots\kick\*.png')):
        img_color = cv2.imread(image)
        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        action.kick(img_gray, img_color)
        action.frame_index += 1

if __name__ == '__main__':
    main()
