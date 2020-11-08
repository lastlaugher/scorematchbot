import time
import logging
import argparse

from action import Action
import emulator

def main(
    log: str = 'INFO',
    debug: bool = False,
    play_game: bool = False,
    play_duration: int = 60):

    log_level = getattr(logging, log.upper())
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    logFormatter = logging.Formatter(format)
    logging.basicConfig(format=format, level=log_level)

    fileHandler = logging.FileHandler('smbot.log')
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(log_level)
    logging.getLogger().addHandler(fileHandler)

    emulator.launch()
    action = Action(debug=debug)

    last_play_time = time.time() - play_duration * 60

    while True:
        action.open_rewards()
        action.open_package()
        action.open_box()
        action.unlock_box()

        elapsed_time = (time.time() - last_play_time) / 60
        logging.info(f'Elapsed time after last game: {int(elapsed_time)} minutes')
        if play_game and elapsed_time > play_duration:
            action.play_game()
            last_play_time = time.time()
        else:
            logging.info('Sleep 5 min in main loop')
            time.sleep(5 * 60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', default='info', help='Log level (CRITICAL, ERROR, WARNING, INFO, and DEBUG)')
    parser.add_argument('--debug', action='store_true', help='')
    parser.add_argument('--play-duration', default='60', type=int, help='Time duration how often play the game (default: 60 miniutes)')
    parser.add_argument('--play-game', action='store_true', help='If set, play the game every [play-duration] minutes')

    args = parser.parse_args()
    main(**vars(args))