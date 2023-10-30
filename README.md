# DirHooker

This simple app will keep an eye on a set of directories and will fire off
GET requests to webhooks when changes occur.  By default, it will look for
newly created files, but can be extended to check for MODIFY or DELETE events
as well.  Directories are watched using the inotify framework.

## Background

The original intended purpose of this tool was to check a directory on an
FTP server for newly uploaded snapshots from a Foscam camera.  Once the snapshot
is found, this tool would hit a webhook in [Scrypted](https://github.com/koush/scrypted)
and/or [Home Assistant](https://github.com/home-assistant/home-assistant.io)
to indicate motion was detected and trigger recording through Homekit Secure
Video (HKSV).  This approach was found to be much more responsive than the
[SMTP approach described in the Scrypted documentation](https://docs.scrypted.app/dummy-detection.html)
, although it requires more setup if you are not already pushing Foscam snapshots
to your FTP server.

## Config file

An [example config file](config.example.yaml) is provided that should help get
you started.

## Docker usage (recommended)

To use the docker image published to ghrc.io:

1. Edit the [example config file](config.example.yaml) to your liking.
2. Use the ```--generate-docker-command``` flag to obtain the docker command to launch the app, e.g.:
```
% python dirhooker.py --generate-docker-command --config=config.example.yaml
docker run -d \
--name dirhooker \
--restart on-failure \
-v /Users/jgbaum/projects/dirhooker/testc/cam90:/Users/jgbaum/projects/dirhooker/testc/cam90 \
-v /Users/jgbaum/projects/dirhooker/testc/cam91:/Users/jgbaum/projects/dirhooker/testc/cam91 \
-v /Users/jgbaum/projects/dirhooker/testc/cam92:/Users/jgbaum/projects/dirhooker/testc/cam92 \
-v /Users/jgbaum/projects/dirhooker/testc/cam93:/Users/jgbaum/projects/dirhooker/testc/cam93 \
-v /Users/jgbaum/projects/dirhooker/config.example.yaml:/config.yaml \
ghcr.io/jgbaum/dirhooker:latest
```
3. Copy and paste the docker command into the terminal and hit 'enter'.

### Alternatively, build the image locally:

Instead of using the image published at ghrc.io, you may build the image from source locally with, e.g.:

```
docker build . -t dirhooker:latest
```

## Installation / Usage without Docker

A clean Python (3.8+) virtual environment is recommended.  Python requirements are listed
in [requirements.txt](requirements.txt).

System requirements include 'curl' and 'inotify-tools'.

1. Edit the [example config file](config.example.yaml) to your liking.
2. Launch the app and point it to your new config:
```
% python dirhooker.py --config=/path/to/new/config.yaml 
```
3. Keep the process running through, e.g., systemd or supervisord.