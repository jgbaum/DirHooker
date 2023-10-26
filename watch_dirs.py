import logging
import threading
import time
import subprocess
import yaml

# catalog of dirs to watch & hook to call
watched_dirs = [
    {
    'cam': 'Cam90',
    'dir': '/home/jgbaum/camFTP/Cam90/FoscamCamera_E8ABFAA77089/snap/',
    'url': 'http://192.168.15.80:11080/endpoint/@scrypted/webhook/public/69/7afce62f2e7565b4/turnOn'
    },
    {
    'cam': 'Cam91',
    'dir': '/home/jgbaum/camFTP/Cam91/FI9831P_00626E6092D0/snap/',
    'url': 'http://192.168.15.80:11080/endpoint/@scrypted/webhook/public/74/4c9d2fe3bbd65e70/turnOn'
    },
    {
    'cam': 'Cam92',
    'dir': '/home/jgbaum/camFTP/Cam92/FI9831P_00626E6093FA/snap/',
    'url': 'http://192.168.15.80:11080/endpoint/@scrypted/webhook/public/75/48b9bb7aebfd8242/turnOn'
    },
    {
    'cam': 'Cam93',
    'dir': '/home/jgbaum/camFTP/Cam93/FI9831P_00626E6092B7/snap/',
    'url': 'http://192.168.15.80:11080/endpoint/@scrypted/webhook/public/76/30a48a53425a5240/turnOn'
    }
]

def watch_dir(dir_pair):
    
    watch_cmd = f'inotifywait -e create {dir_pair["dir"]};'
    webhook_url = dir_pair['url']
    curl_cmd = f"curl '{webhook_url}'"
    
    # loop infinitely until the process quits
    while True:
    
        logging.info("Thread %s: starting", dir_pair['cam'])
        watch_result = subprocess.run(watch_cmd, stdout=subprocess.PIPE, shell=True)
        print(f"{dir_pair['cam']} watch response: " + watch_result.stdout.decode())
        
        # If we pass ctrl-c, sometimes this block executes, so we need to first
        # check that CREATE exists in the watch result
        if 'CREATE' in watch_result.stdout.decode():
            curl_result = subprocess.run(curl_cmd, stdout=subprocess.PIPE, shell=True)
            print(f"{dir_pair['cam']} curl response: " + curl_result.stdout.decode())
        
        time.sleep(30)
        
        
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    for d in watched_dirs:
        x = threading.Thread(target=watch_dir, args=(d,))
        x.start()
    
    logging.info("Main    : wait for the threads to finish")
    logging.info("Main    : all done")
