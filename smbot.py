import time
import logging

from action import Action

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
    action = Action()

    while True:
        action.open_rewards()
        action.open_package()
        action.open_box()
        logging.info('Sleep 5 min in main loop')
        time.sleep(5 * 60)

if __name__ == '__main__':
    main()