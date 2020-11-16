import glob
import logging

import cv2

from action import Action
import config

def main():

    image_dir = r'C:\Users\HOME\Pictures\MEmu Photo\Screenshots\kick\*.png'
    show_image = False

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)

    action = Action(debug=True, save_mask=False)
    action.create_debug_dir()

    for index, image in enumerate(sorted(glob.glob(image_dir))):
        logging.info(f'Processing {index} {image}')
        img_color = cv2.imread(image)
        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        action.kick(img_gray, img_color)
        action.frame_index += 1

        if show_image:
            cv2.imshow('image', img_color)
            cv2.waitKey(0)

if __name__ == '__main__':
    main()
