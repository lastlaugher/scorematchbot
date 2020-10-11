import time
import logging

from action import Action

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)

    action = Action()
    action.play_game()
#    action.test2()

if __name__ == '__main__':
    main()