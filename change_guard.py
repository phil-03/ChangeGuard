#!/usr/bin/python3
import os
import argparse
import hashlib
import sys


def Get_Object_Hash(path, object_type, verbosity): #retrieve the hash for either file or directory


    #make sure path is legit 
    if os.path.exists(path) != True:
        print("Path to the file/directory appears to be incorrect, does not exist.  Your path is: {} - is this correct?".format(path))
        sys.exit()
    
    sha1 = hashlib.sha1()


    if object_type == "file": #if file is being guarded
        if os.path.isfile(path) != True:
            print("Your path does not point to a file. Please change your object type")
            sys.exit()

        BUF_SIZE = 65536 #need to make sure we go through big files in chunks
        

        with open(path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)

        hash_file = sha1.hexdigest()
        if verbosity == True:
            print("{0} hash is: {1}".format(path, hash_file))

        return hash_file

    elif object_type == "dir": # if directory is being guarded
        try:
            for root, dirs, files in os.walk(directory):
                for names in files:
                    if verbosity == True:
                        print('Hashing', names)
                        filepath = os.path.join(root,names)
                    try:
                        f1 = open(filepath, 'rb')
                    except:
                    # You can't open the file for some reason
                        f1.close()
                        continue

                    while 1:
                        # Read file in as little chunks
                        buf = f1.read(4096)
                        if not buf : break
                        sha1.update(hashlib.sha1(buf).hexdigest())
                    f1.close()

        except:
            print("Error hashing files inside {}".format(path))
            sys.exit()

        hash_dir = sha1.hexdigest()

        if verbosity == True:
            print("{0} hash is {1}".format(path, hash_dir))
        return hash_dir

def main(path, object_type, guard_action, output, verbosity):
    #determine OS
    operating_system = os.name
    if operating_system == "nt":
        if "\\\\" not in path:
            path = path.replace("\\", "\\\\")

        if verbosity == True:
            print("Operating System detected as Windows.")

    elif operating_system == "posix":
        if verbosity == True:
            print("Operating System detected as Linux or Mac.")

    else:
        print("No valid OS detected - exiting.")
        sys.exit()

    hash_object = Get_Object_Hash(path, object_type, verbosity)

    



    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Guard a file or a directory from changes, and either log or take other actions if a change is recorded.")
    parser.add_argument('-path', action='store', dest="path", default="", help="Provide the path to either an indivial file or a directory which you want to monitor.")
    parser.add_argument('-type', action='store', dest="type", default="", help="Define what you are guarding.  Choices are a file or a dir.")
    parser.add_argument('-guard_action', action='store', dest="guard_action", default="log", help="Type of defensive action to take. Currently includes default of log the event, or system shutdown.")
    parser.add_argument('-o', action='store', dest="output", default="pwd", help="Where to output log file.")
    parser.add_argument('-v', action='store', dest="verbose", default="False", help="Define if you want verbose output.  Your options are boolean True or False.  The default is False.")

    args = parser.parse_args()

    if str(args.verbose) == "False":
        args.verbose = False

    elif str(args.verbose) == "True":
        args.verbose = True

    if str(args.path) == "":
        print("Please provide a path to the file/directory you want to guard.")
        parser.print_help()
        sys.exit()

    if str(args.type) == "":
        print("Please provide a type of object to guard: your options are file or dir.")

    if str(args.type) != "file" and str(args.type) != "dir":
        print("Please provide a type of object to guard: your options are file or dir.")

    if args.verbose != True and args.verbose != False:
        print("Unrecognized verbosity option, please define -v as either True or False.")
        sys.exit()

    main(str(args.path), str(args.type), str(args.guard_action), str(args.output), args.verbose)
