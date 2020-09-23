import time
import logging

from adb import Adb

import action 

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
    adb = Adb()

    action.kick_penalty(adb)

if __name__ == '__main__':
    main()