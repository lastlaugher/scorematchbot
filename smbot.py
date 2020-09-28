import time
import logging
import argparse

from action import Action

def main(**kwargs):
    log_level = getattr(logging, kwargs['log'].upper())
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    logFormatter = logging.Formatter(format)
    logging.basicConfig(format=format, level=log_level)

    fileHandler = logging.FileHandler('smbot.log')
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(log_level)
    logging.getLogger().addHandler(fileHandler)

    action = Action()

    while True:
        action.open_rewards()
        action.open_package()
        action.open_box()
        action.unlock_box()
        logging.info('Sleep 5 min in main loop')
        time.sleep(5 * 60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', default='info', help='Log level (CRITICAL, ERROR, WARNING, INFO, and DEBUG)')
    args = parser.parse_args()
    main(**vars(args))