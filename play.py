import time
import logging

from action import Action

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)

    action = Action()

    while True:
        action.play_game()

if __name__ == '__main__':
    main()