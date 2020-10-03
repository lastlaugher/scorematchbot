import os
import subprocess
import logging
import time

import psutil
import adb

emulator_paths = {
    'Memu': "C:\\Program Files (x86)\\Microvirt\\MEmu\\MEmu.exe",
}

def get_process_list():
    return [p.name() for p in psutil.process_iter()]

def launch():

    for name, path in emulator_paths.items():
        if os.path.exists(path):
            logging.info(f'{name} is installed')

            base_name = os.path.basename(path)
            process_found = False
            if base_name in get_process_list():
                logging.info(f'{name} process is running')
                process_found = True
            else:
                logging.info(f'{name} process is not found. Trying to execute {name}')
                subprocess.Popen([path])
                time.sleep(20)

                for sec in range(10):
                    if base_name in get_process_list():
                        logging.info(f'{name} is successfully executed')
                        process_found = True
                        break
                    
                    time.sleep(1)
                    logging.info('Sleep 1 sec')

            if not process_found:
                logging.warning(f'Please run the {name} manually')
                continue
            
            client = adb.Adb()
            client.run_app()

        else:
            logging.warning(f'{name} is not installed')


