import time
import logging
import random

import cv2
import numpy as np
from adb import Adb

import config
import image_processing

class Action():
    def __init__(self):
        self.adb = Adb()

    def match_template(self, template_path:str, coordinate:list):
        template_image = cv2.imread(template_path)

        x = coordinate[0]
        y = coordinate[1]
        width  = coordinate[2]
        height = coordinate[3]

        image = self.adb.get_screen()
        sub_image = image[y:y + height, x:x + width]

        score = image_processing.diff_image(template_image, sub_image)

        logging.debug(f'diff score: {score}')

        return True if score > 0.7 else False

    def find_template(self, template_path:str):
        template_image = cv2.imread(template_path)
        image = self.adb.get_screen()

        locations = image_processing.find_template(image, template_image)

        logging.debug(f'Found locations: {locations}')

        return locations

    def touch_box(self, coordinate:list):
        x = coordinate[0]
        y = coordinate[1]
        width  = coordinate[2]
        height = coordinate[3]

        self.adb.touch(x + width / 2, y + height / 2)

    def touch_center(self):
        self.adb.touch(config.screen_size[0] / 2, config.screen_size[1] / 2)

    def touch(self, coordinate:list):
        self.adb.touch(coordinate[0], coordinate[1])

    def open_package(self):
        for idx in range(2):
            if idx == 0:
                template_path = 'templates/free_package_open_now.png'
                coordinate = config.package_loc
                logging.info('Trying to find large package')
            else:
                template_path = 'templates/free_package_open_now_small.png'
                coordinate = config.package_small_loc
                logging.info('Trying to find small package')

            matched = self.match_template(template_path, coordinate)

            if matched:
                logging.info('Package is found')
                self.touch_box(coordinate)
                self.open_cards(adb)
                return

    def open_box(self):
        open_template_path = 'templates/open_now.png'
        unlock_template_path = 'templates/tap_to_unlock.png'
        coordinates = config.box_locs

        for idx, coordinate in enumerate(coordinates, start=1):
            logging.info(f'Trying to find box {idx} to open')
            matched = self.match_template(open_template_path, coordinate)

            if matched:
                logging.info(f'Found box {idx} to open')
                self.touch_box(coordinate)
                self.open_cards(adb)
                return

            logging.info(f'Trying to find box {idx} to unlock')
            matched = self.match_template(unlock_template_path, coordinate)

            if matched:
                logging.info(f'Found box {idx} to unlock')
                self.touch_box(coordinate)
                time.sleep(5)
                self.touch(config.start_unlock_loc)
                return

    def open_cards(self):
        while True:
            template_path = 'templates/okay.png'
            coordinate = config.open_cards_finish_loc

            matched = self.match_template(template_path, coordinate)

            if matched:
                logging.info('Found okay button to finish opening cards')
                self.touch_box(coordinate)
                break
            else:
                logging.info('Touch center since okay button is not found')
                self.touch_center(adb)

                # In case of player upgrade screen
                logging.info('Touch close location and going back location for player upgrade screen')
                self.touch(config.close_loc)
                time.sleep(3)
                self.touch(config.go_back_loc)

            logging.info('Sleep 1 sec')
            time.sleep(1)

    def match_kick(self):
        template_image = cv2.imread('templates/kick.png')

        image = self.adb.get_screen()
        sub_image = image[y:y + height, x:x + width]

        score = image_processing.diff_image(template_image, sub_image)

        return True if score > 0.8 else False

    def kick_penalty(self):
        locations = [
            config.penalty_left_corner_loc,
            config.penalty_center_top_loc,
            config.penalty_right_corner_loc,
        ]

        loc = random.randint(0, 2)
        start_x = config.penalty_start_loc[0]
        start_y = config.penalty_start_loc[1]
        end_x = locations[loc][0]
        end_y = locations[loc][1]

        self.adb.swipe(start_x, start_y, end_x, end_y, 500)

    def open_rewards(self):
        template_path = 'templates/claim_rewards.png'
        coordinate = config.rewards_loc
        logging.info('Trying to find rewards')

        matched = self.match_template(template_path, coordinate)

        if matched:
            logging.info('Reword box is found')
            self.touch_box(coordinate)

            logging.info('Trying to find rewards location')
            locations = self.find_template('templates/found.png')
            logging.info(f'Found {len(locations)} locations')

            for loc in locations:
                self.touch_box(loc)

                logging.info('Tapped rewards')
                time.sleep(5)

                self.open_cards()
