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
parser.add_argument('--template-config',
    help='Path to the config file to be used to generate the runtime config',
    required=False)
parser.add_argument('--runtime-config',
    help='Path to the runtime config file',
    required=False,
    default='config.runtime.yaml')
parser.add_argument('--container-name',
    help='A name for the container',
    required=False,
    default='dirwatcher')
parser.add_argument('--image-name',
    help='The name of the image to run',
    required=False,
    default='dirwatcher:latest')


args = parser.parse_args()

def generate_docker_command(template_config_file, runtime_config_file):
    """Using the template config file, generate the runtime config file
    and docker run command"""

    # read in the yaml config file
    with open(template_config_file, 'r') as file:
         config = yaml.safe_load(file)
         
    # for each directory, we map it to /ftp/{name}
    run_config = deepcopy(config)
    
    # record the volumes to be mapped
    volume_maps = list()
    
    for d in run_config['directories']:
        container_path = f"/ftp/{d['name']}"
        volume_maps.append(f"{d['path']}:{container_path}")
        d['path'] = container_path
        
    # output the run config file
    with open(runtime_config_file, 'w') as file:
        yaml.dump(run_config, file)
    
    # create the docker run command as a list
    # we'll join these together later
    docker_run_cmds = list()
    docker_run_cmds.append('docker run -d')
    
    # if we were given a name, add it here
    docker_run_cmds.append(f"--name {args.container_name}")
    
    docker_run_cmds.append("--restart on-failure")
    
    # now add the volume mounts
    for v in volume_maps:
        docker_run_cmds.append(f"-v {v}")
    
    # mount the config file
    runtime_config_full_path = os.path.abspath(runtime_config_file)
    
    docker_run_cmds.append(f"-v {runtime_config_full_path}:/config.yaml")
    
    # add the name of the image
    docker_run_cmds.append(f"{args.image_name}")
    
    # join into a string
    docker_cmd = " \\\n".join(docker_run_cmds)
    
    print(docker_cmd)
    
    # now create the output config file
  
  
    
def watch_dir(dir_info):
    
    watch_cmd = f'inotifywait -e create {dir_info["path"]};'
    webhook_url = dir_info['webhook_url']
    curl_cmd = f"curl '{webhook_url}'"
    
    # loop infinitely until the process quits
    while True:
    
        logging.info("Thread %s: starting", dir_info['name'])
        watch_result = subprocess.run(watch_cmd, stdout=subprocess.PIPE, shell=True)
        print(f"{dir_info['name']} watch response: " + watch_result.stdout.decode())
        
        # If we pass ctrl-c, sometimes this block executes, so we need to first
        # check that CREATE exists in the watch result
        if 'CREATE' in watch_result.stdout.decode():
            curl_result = subprocess.run(curl_cmd, stdout=subprocess.PIPE, shell=True)
            print(f"{dir_info['name']} curl response: " + curl_result.stdout.decode())
        
        time.sleep(30)
        
        
if __name__ == "__main__":
    
    template_config = args.template_config
    runtime_config = args.runtime_config
    gen_config = args.generate_docker_command

    if gen_config:
        generate_docker_command(template_config, runtime_config)
    else:
    
        # read in the yaml config file
        with open(runtime_config, 'r') as file:
            config = yaml.safe_load(file)
             
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO,
                            datefmt="%H:%M:%S")

        logging.info("Main    : before creating thread")
        for d in config['directories']:
            x = threading.Thread(target=watch_dir, args=(d,))
            x.start()
        
        logging.info("Main    : wait for the threads to finish")
        logging.info("Main    : all done")
