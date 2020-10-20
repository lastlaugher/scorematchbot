import time
import logging

from action import Action

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)

    action = Action()
    action.play_shootout()

if __name__ == '__main__':
    main()