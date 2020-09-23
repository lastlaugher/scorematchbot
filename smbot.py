import time
import logging

from adb import Adb

import action 

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.INFO)
    adb = Adb()

    while True:
#        action.match_kick(adb)
        action.open_package(adb)
        action.open_box(adb)
        logging.info('Sleep 5 min in main loop')
        time.sleep(5 * 60)

if __name__ == '__main__':
    main()