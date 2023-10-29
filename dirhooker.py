    # DirHooker - Send webhook request on directory change
    # Copyright (C) 2023 Jason Greenbaum (https://github.com/jgbaum)

    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU Affero General Public License as published
    # by the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU Affero General Public License for more details.

    # You should have received a copy of the GNU Affero General Public License
    # along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import threading
import time
import subprocess
import argparse
import yaml
import os
from copy import deepcopy

parser = argparse.ArgumentParser()

# add arguments to the parser
parser.add_argument('--generate-docker-command', 
    help='Generate the docker run command',
    action='store_true',
    default=False,
    required=False)
parser.add_argument('--config',
    help='Path to the config file',
    required=False)
parser.add_argument('--image-name',
    help='The name of the image to run',
    required=False,
    default='dirhooker:latest')


args = parser.parse_args()

def generate_docker_command(config_file):
    """Using the template config file, generate the docker run command"""

    # read in the yaml config file
    with open(config_file, 'r') as file:
         config = yaml.safe_load(file)
         
    # record the volumes to be mapped
    volume_maps = list()
    
    for d in config['directories']:
        volume_maps.append(f"{d['path']}:{d['path']}")
    
    # create the docker run command as a list
    # we'll join these together later
    docker_run_cmds = list()
    docker_run_cmds.append('docker run -d')
    
    # add the name and restart condition
    docker_run_cmds.append("--name dirhooker")
    docker_run_cmds.append("--restart on-failure")
    
    # now add the volume mounts
    for v in volume_maps:
        docker_run_cmds.append(f"-v {v}")
    
    # mount the config file
    runtime_config_full_path = os.path.abspath(config_file)
    
    docker_run_cmds.append(f"-v {runtime_config_full_path}:/config.yaml")
    
    # add the name of the image
    docker_run_cmds.append(f"{args.image_name}")
    
    # join into a string
    docker_cmd = " \\\n".join(docker_run_cmds)
    
    print(docker_cmd)  
  
    
def watch_dir(dir_info):
    
    # default to watching CREATE actions, but this can be overridden
    # by adding a list of 'watched_actions' item to the dir info
    watched_actions = ['CREATE']
    
    if 'watched_actions' in dir_info:
        watched_actions = dir_info['watched_actions']
    
    events_string = ','.join(watched_actions)
    watch_cmd = f'inotifywait -e {events_string} {dir_info["path"]};'
    webhook_url = dir_info['webhook_url']
    curl_cmd = f"curl '{webhook_url}'"
    
    logging.info(f"Thread {dir_info['name']}: watch command: {watch_cmd}")
    logging.info(f"Thread {dir_info['name']}: curl command: {curl_cmd}")
    
    # loop infinitely until the process quits
    while True:
    
        logging.info(f"Thread {dir_info['name']}: starting")
        watch_result = subprocess.run(watch_cmd, stdout=subprocess.PIPE, shell=True)
        logging.info(f"Thread {dir_info['name']}: watch response: " + watch_result.stdout.decode())
        
        # If we pass ctrl-c, sometimes this block executes, so we need to first
        # check that CREATE exists in the watch result
        if 'CREATE' in watch_result.stdout.decode():
            curl_result = subprocess.run(curl_cmd, stdout=subprocess.PIPE, shell=True)
            logging.info(f"Thread {dir_info['name']} curl response: " + curl_result.stdout.decode())
        
        time.sleep(30)
        
        
if __name__ == "__main__":
    
    config_file = args.config
    gen_config = args.generate_docker_command

    if gen_config:
        generate_docker_command(config_file)
    else:
    
        # read in the yaml config file
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
             
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO,
                            datefmt="%H:%M:%S")

        for d in config['directories']:
            x = threading.Thread(target=watch_dir, args=(d,))
            x.start()

