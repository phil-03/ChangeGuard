# ChangeGuard

## Purpose
ChangeGuard is a tool which is designed to help guard against unauthorized filesystem changes.  It will record the datetime and path anytime a change is made to a protected file/files inside a protected directory.  If prompted, ChangeGuard will also initiate action to prevent further modification by shutting down the system.  Since it is written solely in python, it is platform independent, and has been tested on Windows and Linux systems (it has not yet been tested on Mac OS but should theoretically work there as well.)  This is one of my first publicly released projects, and is not supposed to be the best code in the world. I figure this could come in handy for Defenders, or at least help development efforts on similar tools along.  

## Installation
Clone the repo to a local directory.  Make sure you have Python3 installed.  If any python libraries are missing from your system, you should be prompted.  Use pip3 install to install these python libraries.

## Usage
Using ChangeGuard is extremely simple.  To see a ChangeGuard help menu, open a terminal or cmd prmpt and type: python3 change_guard.py -h.  You will see:

Guard a file or a directory from changes, and either log or take other actions if a change is recorded.

optional arguments:

  -h, --help            show this help message and exit

  -path PATH            Provide the path to either an indivial file or a
                        directory which you want to monitor.

  -type TYPE            Define what you are guarding. Choices are a file or a
                        dir.

  -guard_action GUARD_ACTION
                        Type of defensive action to take. Currently includes
                        default of log the event, or system shutdown.

  -o OUTPUT             Where to output log file.

  -v VERBOSE            Define if you want verbose output. Your options are
                        boolean True or False. The default is False.

Example commands:
To protect a single file called "test.txt" in directory C:\Users\User\Documents\text.txt and log all changes to output.txt:

```
python change_guard.py -path C:\Users\User\Documents\text.txt -type file -o output.txt
```

To protect a directory called "test" in path C:\Users\User and log all changes to output.txt:
```
python change_guard.py -path C:\Users\User\test\ -type dir -o output.txt
```

## Guard actions
The default guard_action option is just "log".  This means that ChangeGuard will log file modifications but take no further actions.  If "armed" is selected, ChangeGuard will log the modification, wait 5 seconds, and then initiate a system shutdown.  This is to prevent further unauthorized modification and encourage inspect of the potentially compromised machine.  


## Future Ideas
I have a few to-dos for this code, in no particular order.

#TODO maybe incorporate Windows Event Log or Linux Last command (or other Linux logs to pinpoint user)
#TODO this script does not currently address empty directories.  
#TODO input list of files, only guard those files.
#TODO add ability to lock users out of system rather than shut down
#TODO don't use os, only use subprocess
#TODO add more armed actions that are not just shutdown, see user lockout above