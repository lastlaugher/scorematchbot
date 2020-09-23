import time
import logging

import cv2
import numpy as np
from adb import Adb

import config
import image_processing

def match_template(adb:Adb, template_path:str, coordinate:list):
    template_image = cv2.imread(template_path)
    
    x = coordinate[0]
    y = coordinate[1]
    width  = coordinate[2]
    height = coordinate[3]

    image = adb.get_screen()
    sub_image = image[y:y + height, x:x + width]

    score = image_processing.diff_image(template_image, sub_image)

    logging.debug(f'diff score: {score}')

    return True if score > 0.8 else False

def touch_template(adb:Adb, coordinate:list):
    x = coordinate[0]
    y = coordinate[1]
    width  = coordinate[2]
    height = coordinate[3]

    adb.touch(x + width / 2, y + height / 2)

def touch_center(adb:Adb):
    adb.touch(config.screen_size[0] / 2, config.screen_size[1] / 2)

def touch(adb:Adb, coordinate:list):
    adb.touch(coordinate[0], coordinate[1])

def open_package(adb: Adb):
    for idx in range(2):
        if idx == 0:
            template_path = 'templates/free_package_open_now.png'
            coordinate = config.package_loc
            logging.info('Trying to find large package')
        else:
            template_path = 'templates/free_package_open_now_small.png'
            coordinate = config.package_small_loc
            logging.info('Trying to find small package')

        matched = match_template(adb, template_path, coordinate)

        if matched:
            logging.info('Package is found')
            touch_template(adb, coordinate)
            open_cards(adb)
            return

def open_box(adb: Adb):
    open_template_path = 'templates/open_now.png'
    unlock_template_path = 'templates/tap_to_unlock.png'
    coordinates = config.box_locs

    for coordinate in coordinates:
        logging.info('Trying to find box to open')
        matched = match_template(adb, open_template_path, coordinate)

        if matched:
            logging.info('Found box to open')
            touch_template(adb, coordinate)
            open_cards(adb)
            return

        logging.info('Trying to find box to unlock')
        matched = match_template(adb, unlock_template_path, coordinate)

        if matched:
            logging.info('Found box to unlock')
            touch_template(adb, coordinate)
            touch(adb, config.start_unlock_loc)
            return

def open_cards(adb: Adb):
    while True:
        template_path = 'templates/okay.png'
        coordinate = config.open_cards_finish_loc

        matched = match_template(adb, template_path, coordinate)

        if matched:
            logging.info('Found okay button to finish opening cards')
            touch_template(adb, coordinate)
            break
        else:
            logging.info('Touch center since okay button is not found')
            touch_center(adb)

        logging.info('Sleep 1 sec')
        time.sleep(1)

def match_kick(adb:Adb):
    template_image = cv2.imread('templates/kick.png')
    
    image = adb.get_screen()
    sub_image = image[y:y + height, x:x + width]

    score = image_processing.diff_image(template_image, sub_image)

    return True if score > 0.8 else False
