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

    def match_template(self, template_path:str, coordinate:list, threshold:float = 0.8, color:bool = True):
        template_image = cv2.imread(template_path)

        x = coordinate[0]
        y = coordinate[1]
        width  = coordinate[2]
        height = coordinate[3]

        image = self.adb.get_screen()
        sub_image = image[y:y + height, x:x + width]

        score = image_processing.diff_image(template_image, sub_image, color)

        logging.debug(f'diff score: {score}')

        return True if score > threshold else False

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
                time.sleep(3)
                self.open_cards()
                return

    def open_box(self):
        template_path = 'templates/open_now.png'
        coordinates = config.open_now_locs

        for idx, coordinate in enumerate(coordinates, start=1):
            logging.info(f'Trying to find box {idx} to open')
            matched = self.match_template(template_path, coordinate)

            if matched:
                logging.info(f'Found box {idx} to open')
                self.touch_box(coordinate)
                time.sleep(3)
                self.open_cards()
                break

    def unlock_box(self):
        template_path = 'templates/tap_to_unlock.png'
        coordinates = config.tap_to_unlock_locs

        for idx, coordinate in enumerate(coordinates, start=1):
            logging.info(f'Trying to find box {idx} to unlock')
            matched = self.match_template(template_path, coordinate)

            if matched:
                logging.info(f'Found box {idx} to unlock')
                self.touch_box(coordinate)
                time.sleep(3)
                for loc in config.start_unlock_locs:
                    self.touch(loc)
                time.sleep(3)
                break

    def open_cards(self):
        while True:
            template_path = 'templates/okay.png'
            coordinate = config.okay_loc

            matched = self.match_template(template_path, coordinate)

            if matched:
                logging.info('Found okay button to finish opening cards')
                self.touch_box(coordinate)
                break
            else:
                matched = self.match_template('templates/upgrade.png', config.upgrade_loc)

                if matched:
                    logging.info('Player upgrade screen showed. Touch close location and going back')
                    self.touch(config.close_loc)
                    time.sleep(3)
                    self.touch(config.go_back_loc)
                    break
                else:
                    logging.info('Touch center since okay button is not found')
                    self.touch_center()
            
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

        matched = self.match_template(template_path, coordinate, threshold=0.7)

        if matched:
            logging.info('Reword box is found')
            self.touch_box(coordinate)

            logging.info('Trying to find reward locations')
            locations = self.find_template('templates/found.png')
            logging.info(f'Found {len(locations)} locations')

            if len(locations) > 0:
                self.touch_box(locations[0])

                logging.info('Tapped rewards')
                time.sleep(5)

                self.open_cards()

    def play_game(self):
        logging.info('Starting game')

        logging.info('Entering arena')
        self.touch(config.arena_loc)
        time.sleep(3)

        logging.info('Playing match')
        self.touch(config.play_match_loc)
        time.sleep(3)

        logging.info('Finding an opponent')
        while True:
            matched = self.match_template('templates/support.png', config.support_loc)
            if matched:
                logging.info('Connection failed. Trying again')
                self.touch(config.support_ok_loc)
                time.sleep(3)

                logging.info('Playing match')
                self.touch(config.play_match_loc)

            matched = self.match_template('templates/bid.png', config.bid_loc)
            if matched:
                logging.info('Bid stage')
                time.sleep(5)
                break

        logging.info('Game starated')
        prev_image = self.adb.get_screen()

        idx = 0
        while True:
            matched = self.match_template('templates/game_end.png', config.game_end_loc)
            if matched:
                logging.info('Game ended')
                self.touch_box(config.game_end_loc)
                time.sleep(3)
                break

            cur_image = self.adb.get_screen()

            diff_image = cur_image - prev_image
            my_photo_diff = image_processing.crop(diff_image, config.my_photo_loc)
            opponent_photo_diff = image_processing.crop(diff_image, config.opponent_photo_loc)

            if np.sum(my_photo_diff) != 0:
                logging.info(f'{idx} My turn to kick') 
                self.kick()
            elif np.sum(opponent_photo_diff) != 0:
                logging.info(f'{idx} Opponent\'s turn to kick') 
            else:
                logging.info(f'{idx} In-progress')

            cv2.imwrite(f'frames/frame_{idx:05d}.png', diff_image)

            prev_image = cur_image
            idx += 1

        matched = self.match_template('templates/okay.png')
        if matched:
            logging.info('Relagation. Touch okay')
            self.touch_box(config.okay_loc)
        else:
            logging.info('Accepting video package')
            self.touch(config.video_package_play_loc)

            logging.info('Playing video')
            time.sleep(60)
            
            logging.info('Finished playing video')
            self.touch(config.video_package_close_loc)
            time.sleep(3)

            logging.info('Opening cards')
            self.open_cards()

        time.sleep(3)

        logging.info('Going back to the main screen')
        self.touch(config.go_back_loc)
        time.sleep(3)

    def kick(self):
        logging.info('Implement how to kick')