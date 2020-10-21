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

    def match_template(
        self,
        template_path:str,
        coordinate:list = None,
        threshold:float = 0.8,
        color:bool = True,
        mask:bool = False,
        image_path:str = None,
        diff_threshold:float = 0):

        template_image = cv2.imread(template_path)
        mask_image = cv2.imread(template_path) if mask else None

        if image_path:
            image = cv2.imread(image_path)
        else:
            image = self.adb.get_screen()

        if coordinate:
            x = coordinate[0]
            y = coordinate[1]
            width  = coordinate[2]
            height = coordinate[3]
            sub_image = image[y:y + height, x:x + width]
        else:
            sub_image = image

        score = image_processing.diff_image(template_image, sub_image, mask=mask_image, color=color, diff_threshold=diff_threshold)
        logging.debug(f'diff score: {score}')

        return (True, score) if score > threshold else (False, score)

    def find_template(self, template_path:str):
        template_image = cv2.imread(template_path)
        image = self.adb.get_screen()

        location = image_processing.find_template(image, template_image)
        logging.debug(f'Reward location {location}')

        return location

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
        template_path = 'templates/free_collect.png'
        coordinate = config.free_collect_loc
        logging.info('Trying to find free collect package')
        matched, score = self.match_template(template_path, coordinate, mask=True)
        if matched:
            logging.info(f'Free collect package is found ({score})')
            self.touch_box(coordinate)

            logging.info('Playing video')
            time.sleep(40)
            
            logging.info('Finished playing video')
            self.touch(config.free_collect_end_loc)
            self.touch(config.video_package_close_loc)
            time.sleep(3)

            logging.info('Opening cards')
            self.open_cards()

        for idx in range(2):
            if idx == 0:
                template_path = 'templates/free_package_open_now.png'
                coordinate = config.package_loc
                logging.info('Trying to find large package')
            else:
                template_path = 'templates/free_package_open_now_small.png'
                coordinate = config.package_small_loc
                logging.info('Trying to find small package')

            matched, score = self.match_template(template_path, coordinate)

            if matched:
                logging.info(f'Package is found ({score})')
                self.touch_box(coordinate)
                time.sleep(3)
                self.open_cards()
                return

    def open_box(self):
        template_path = 'templates/open_now.png'
        coordinates = config.open_now_locs

        for idx, coordinate in enumerate(coordinates, start=1):
            logging.info(f'Trying to find box {idx} to open')
            matched, score = self.match_template(template_path, coordinate)

            if matched:
                logging.info(f'Found box {idx} to open ({score})')
                self.touch_box(coordinate)
                time.sleep(3)
                self.open_cards()

    def unlock_box(self):
        template_path = 'templates/tap_to_unlock.png'
        coordinates = config.tap_to_unlock_locs

        for idx, coordinate in enumerate(coordinates, start=1):
            logging.info(f'Trying to find box {idx} to unlock')
            matched, score = self.match_template(template_path, coordinate, threshold=0.7)

            if matched:
                logging.info(f'Found box {idx} to unlock ({score})')
                self.touch_box(coordinate)
                time.sleep(3)
                for loc in config.start_unlock_locs:
                    self.touch(loc)
                time.sleep(3)
                break

    def open_cards(self):
        if self.sign_in():
            return

        idx = 0
        while True:
            template_path = 'templates/okay.png'
            coordinate = config.okay_loc

            matched, score = self.match_template(template_path, coordinate)
            if matched:
                logging.info(f'Found okay button to finish opening cards ({score})')
                self.touch_box(coordinate)
                break

            matched, score = self.match_template('templates/upgrade.png', config.upgrade_loc)
            if matched:
                logging.info(f'Player upgrade screen showed. Touch close location and going back ({score})')
                self.touch(config.close_loc)
                time.sleep(3)
                self.touch(config.go_back_loc)
                break

            matched, score = self.match_template('templates/formation.png', config.formation_loc)
            if matched:
                logging.info(f'Formation screen showed. Touch ok location and going back ({score})')
                self.touch(config.formation_ok_loc)
                time.sleep(3)
                self.touch(config.go_back_loc)
                break

            logging.info('Touch center since okay button is not found')
            self.touch_center()
            
            logging.info('Sleep 1 sec')
            time.sleep(1)

            idx += 1

            if idx > 30:
                logging.error('Can\'t find the okay button during 30 iterations')
                self.adb.restart_app()
                logging.info('App is restarted')
                break

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

        location_str = ['left', 'center', 'right']
        logging.info(f'Kicked {location_str[loc]}')

    def defend_penalty(self):
        locations = [
            config.penalty_defend_left_corner_loc,
            config.penalty_defend_center_top_loc,
            config.penalty_defend_right_corner_loc,
        ]

        loc = random.randint(0, 2)

        self.adb.touch(locations[loc][0], locations[loc][1])

        location_str = ['left', 'center', 'right']
        logging.info(f'Defend {location_str[loc]}')

    def open_rewards(self):
        template_path = 'templates/claim_rewards.png'
        coordinate = config.rewards_loc
        logging.info('Trying to find rewards')

        matched, score = self.match_template(template_path, coordinate, mask=True)

        if matched:
            logging.info(f'Reword box is found ({score})')
            self.touch_box(coordinate)
            time.sleep(3)

            logging.info('Trying to find reward locations')
            location = self.find_template('templates/found.png')

            if location:
                logging.info('Found reward location')
                self.touch_box(location)

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
            self.sign_in()

            matched, score = self.match_template('templates/support.png', config.support_loc)
            if matched:
                logging.info(f'Connection failed. Trying again ({score})')
                self.touch(config.support_ok_loc)
                time.sleep(3)

                logging.info('Playing match')
                self.touch(config.play_match_loc)

            matched, score = self.match_template('templates/bid.png', config.bid_loc)
            if matched:
                logging.info(f'Bid stage ({score})')
                time.sleep(5)
                break

        logging.info('Game starated')
        prev_image = self.adb.get_screen(color=False)
        photo_loc = [
            0, 
            0,
            prev_image.shape[1],
            config.my_photo_loc[1] + config.my_photo_loc[3]
            ]
            
        prev_image = prev_image[
            photo_loc[1]:photo_loc[1] + photo_loc[3],
            photo_loc[0]:photo_loc[0] + photo_loc[2]
        ]

        idx = 0
        while True:
            matched, score = self.match_template('templates/game_end.png', config.game_end_loc)
            if matched:
                logging.info(f'Game ended ({score})')
                break

            matched, score = self.match_template('templates/timeout.png', config.timeout_loc, mask=True, threshold=0.9)
            if matched:
                logging.info(f'Timeout ({score})')
                break

            image = self.adb.get_screen(color=False)

            cur_image = image[
                photo_loc[1]:photo_loc[1] + photo_loc[3],
                photo_loc[0]:photo_loc[0] + photo_loc[2]
            ]

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

        while True:
            logging.info('Trying to find shootout')
            matched, score = self.match_template('templates/shootout.png', config.shootout_loc, mask=True)
            if matched:
                logging.info(f'Shootout started ({score})')
                self.play_shootout()

            logging.info('Trying to find game end')
            matched, score = self.match_template('templates/game_end.png', config.game_end_loc)
            if matched:
                logging.info(f'Game ended ({score})')
                self.touch_box(config.game_end_loc)
                break

            time.sleep(1)

        relagation_matched = self.match_template('templates/okay.png', config.okay_loc)
        promotion_package_matched = self.match_template('templates/promotion_package.png', config.promotion_package_loc)

        if relagation_matched:
            logging.info('Relagation. Touch okay')
            self.touch_box(config.okay_loc)
        elif promotion_package_matched:
            logging.info('Promotion pakcage. Touch close')
            self.touch(config.promotion_package_close_loc)
        else:
            logging.info('Accepting video package')
            self.touch(config.video_package_play_loc)

            logging.info('Playing video')
            time.sleep(60)
            
            logging.info('Finished playing video')
            self.touch(config.video_package_close_loc)
            self.touch(config.free_collect_end_loc)
            time.sleep(3)

            logging.info('Opening cards')
            self.open_cards()

        time.sleep(3)

        logging.info('Going back to the main screen')
        self.touch(config.go_back_loc)
        time.sleep(3)

    def sign_in(self):
        logging.info('Trying to find signed-out screen')
        matched, score = self.match_template('templates/signed_out.png', config.signed_out_loc)
        if matched:
            logging.info('Found signed-out message. Trying to sign-in')
            self.touch(config.sign_in_loc)
            time.sleep(10)
            return True

        return False            

    def kick(self):
        logging.info('Implement how to kick')

    def play_shootout(self):
        logging.info('Starting shootout')

        not_found_count = 0
        while True:
            matched, score = self.match_template('templates/shootout_defence.png', mask=True)
            if (matched):
                logging.info('Found shootout defence')
                self.defend_penalty()

                time.sleep(1)
                continue

            matched, score = self.match_template('templates/shootout_offence.png', mask=True)
            if (matched):
                logging.info('Found shootout offence')
                self.kick_penalty()

                time.sleep(1)
                continue

            logging.info('None of defence and offence found')
            not_found_count += 1

            if not_found_count == 10:
                logging.info('Finished the shootout')
                break


    def test(self):
        import glob
        for path in sorted(glob.glob(r'C:\Users\HOME\Pictures\MEmu Photo\Screenshots\shootout\defence\*.png')):
            matched, score = self.match_template('templates/shootout_defence.png', mask=True)
            logging.info(f'{path} {matched} {score}')

        for path in sorted(glob.glob(r'C:\Users\HOME\Pictures\MEmu Photo\Screenshots\shootout\offence\*.png')):
            matched, score = self.match_template('templates/shootout_offence.png', mask=True)
            logging.info(f'{path} {matched} {score}')

    def estimate_uniform_colors(self, image_hsv, uniform_loc):
        uniform_eh = image_processing.hsv2eh(image_processing.crop(image_hsv, uniform_loc))
        uniform_mask = cv2.imread('templates/uniform_mask.png', cv2.IMREAD_GRAYSCALE)

        uniform_masked = np.ma.masked_array(uniform_eh, uniform_mask == 0)
        values, counts = np.unique(uniform_masked.astype('uint16'), return_counts=True)

        uniform_pixels = np.count_nonzero(uniform_mask)

        uniform_values = []
        for v, c in zip(values, counts):
            if type(v) == np.ma.core.MaskedConstant:
                continue

            if c / uniform_pixels > 0.2:
                uniform_values.append(v)

        return uniform_values

    def get_player_locations(self, image_eh, uniform_colors):
        mask = np.zeros(image_eh.shape, np.uint8)
        for color in uniform_colors:
            if color < 180:
                if color >= 178:
                    upper_margin = 179 - color 
                else:
                    upper_margin = 2

                if color <= 1:
                    lower_margin = color 
                else:
                    lower_margin = 2
            else:
                if color > 240:
                    upper_margin = 255 - color
                else:
                    upper_margin = 15

                if color < 195:
                    lower_margin = color - 180
                else:
                    lower_margin = 15

            cur_mask = cv2.inRange(image_eh, np.array(color - lower_margin, dtype=np.uint16), np.array(color + upper_margin, dtype=np.uint16))
            mask = cv2.bitwise_or(mask, cur_mask)

        return mask

    def test2(self):
        import glob
        #for file in sorted(glob.glob('C:/Users/HOME/Pictures/MEmu Photo/Screenshots/kick/*')):
        for file in sorted(glob.glob('C:/Users/HOME/Pictures/MEmu Photo/Screenshots/reverse/*')):
            image = cv2.imread(file)
            image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            image_eh = image_processing.hsv2eh(image_hsv)

            my_uniform_colors = self.estimate_uniform_colors(image_hsv, config.my_uniform_loc)
            opponent_uniform_colors = self.estimate_uniform_colors(image_hsv, config.opponent_uniform_loc)

            logging.info(f'my uniform color: {",".join(map(str, my_uniform_colors))}')
            logging.info(f'opponent uniform color: {",".join(map(str, opponent_uniform_colors))}')


            my_mask = self.get_player_locations(image_eh, my_uniform_colors)
            opponent_mask = self.get_player_locations(image_eh, opponent_uniform_colors)

            # Merge separated player's points, especially for striped uniform
            kernel = np.ones((3, 3), np.uint8) 
            my_mask = cv2.morphologyEx(my_mask, cv2.MORPH_CLOSE, kernel)
            opponent_mask = cv2.morphologyEx(opponent_mask, cv2.MORPH_CLOSE, kernel)

            # Remove noise
            kernel = np.ones((5, 5), np.uint8) 
            my_mask_open = cv2.morphologyEx(my_mask, cv2.MORPH_OPEN, kernel)
            opponent_mask_open = cv2.morphologyEx(opponent_mask, cv2.MORPH_OPEN, kernel)

            # Merge separated player's parts, i.e. body and leg
            kernel = np.ones((15, 15), np.uint8) 
            my_mask_close = cv2.morphologyEx(my_mask_open, cv2.MORPH_CLOSE, kernel)
            opponent_mask_close = cv2.morphologyEx(opponent_mask_open, cv2.MORPH_CLOSE, kernel)

            cv2.imshow('frame', image)
            cv2.imshow('my', my_mask)
            cv2.imshow('op', opponent_mask)
            cv2.imshow('my2', my_mask_open)
            cv2.imshow('op2', opponent_mask_open)
            cv2.imshow('my3', my_mask_close)
            cv2.imshow('op3', opponent_mask_close)
            cv2.waitKey(0)


