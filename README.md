# Dirwatcher

This simple app will keep an eye on a set of directories and will fire off
GET requests to webhooks when changes occur.  By default, it will look for
newly created files, but can be extended to check for MODIFY or DELETE events
as well.  Directories are watched using the inotify framework.

The original intended purpose of this tool was to check a directory on an
FTP server for newly uploaded snapshots from a Foscam camera.  Once the snapshot
is found, this tool would hit a webhook in Scrypted and/or Home Assistant
to indicate motion was detected and trigger recording through Homekit Secure
Video (HKSV).  This approach was found to be much more responsive than the
SMTP approach described in the Scrypted documentation, although it requires
more setup if you are not already pushing Foscam snapshots to your FTP server.

## Config files

## Docker usage (recommended)




## Installation / Usage without Docker

A clean Python (3.8+) virtual environment is recommended.  Python requirements are listed
in [requirements.txt](requirements.txt).

System requirements include 'curl' and 'inotify-tools'.

