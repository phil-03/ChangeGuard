#!/usr/bin/python3
import os
import argparse
import hashlib
import sys
import glob
from collections import OrderedDict
import time
import datetime


def Get_File_Hash(path, object_type, verbosity): #retrieve the hash for either file or directory

    if os.path.exists(path) != True:
        #TODO put in guard actions here just in case, endless loop right now
        print("Modification detected, file to guard has been deleted.  Initating guard actions...")
        return "GUARD"
        
    sha1 = hashlib.sha1()


    if object_type == "file": #if file is being guarded
        

        BUF_SIZE = 65536 #need to make sure we go through big files in chunks
        
        try:
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
        
        except:
            f.close()
            return "Cannot open file"

def Get_Dir_Hashes(path, object_type, verbosity):

    if os.path.exists(path) != True:
        #TODO put in guard actions here just in case
        print("Modification detected, directory to guard has been deleted.  Initating guard actions...")
        return "GUARD"
       
    dir_count = 0 #needed to give directory names a unique place in dict, otherwise could create or remove empty directories without being noticed

    
    sha1 = hashlib.sha1()

    if object_type == "dir": # if directory is being guarded
        

        dict_of_hashes = OrderedDict()
        try:
            for filename in glob.iglob(path + '**/**', recursive=True):
                if os.path.isfile(filename) == True: # not sure why, always starts with initial directory path, which is not a file
                    
                    hash_file = Get_File_Hash(filename, "file", verbosity)
                    dict_of_hashes.update({'{}'.format(hash_file): '{}'.format(filename)})

                else:
                   dict_of_hashes.update({'{}'.format(dir_count): '{}'.format(filename)})
                   dir_count =+ 1
                    

            return dict_of_hashes

        except:
            print("Error hashing files inside {0}.  Make sure there is a trailing slash on {0}!!".format(path))
            sys.exit()

def Guard_Check_File(path, object_type, previous_hash): # check the previous file hash, and see if the watched file has been modified
    new_hash = Get_File_Hash(path, object_type, False)
    
    if new_hash == previous_hash:
        return True, new_hash, path #no modification has occurred
    
    else:
        return False, new_hash, path #modification has occurred

def Guard_Check_Directory(path, object_type, previous_dict):# check the previous file hashes, and see if the watched directory has been modified
    
    modified_file_list = list() #we will put every file which has been modified into this list

    count_old = 0
    count_new = 0
    new_dict = Get_Dir_Hashes(path, object_type, False)


    value = True #True means no modification has happened
    modified_file = ""
    modified_hash = ""

    #make sure lengths of dicts are the same, or else modification must have occurred
    count_old = len(previous_dict)
    count_new = len(new_dict)

    if count_old != count_new:
        value = False
        if count_new > count_old:
            for key in new_dict:
                if key not in previous_dict:
                    modified_hash = key
                    modified_file = new_dict[key]
                    modified_file_list.append("File added: " + modified_file)
        else:
            for key in previous_dict:
                if key not in new_dict:
                    modified_hash = key
                    modified_file = previous_dict[key]
                    modified_file_list.append("File removed/changed: " + modified_file)

    elif count_old == count_new: #make sure count is the same, or this code section will error due to index issues
        
        
        for key in new_dict: #make sure to account for edge cases
            
            if key not in previous_dict:
                value = False
                modified_hash = key
                modified_file = new_dict[key]
                modified_file_list.append("File added: " + modified_file)

            elif new_dict[key] != previous_dict[key]:
                value = False
                modified_hash = key
                modified_file = new_dict[key]
                modified_file_list.append("Filename modified " + modified_file)


        for key in previous_dict:
            if key not in new_dict:
                value = False
                modified_hash = key
                modified_file = previous_dict[key]
                if modified_file not in modified_file_list:
                    modified_file_list.append("File removed/changed: " + modified_file)
     
    
    
    return value, modified_file_list, new_dict
    
       


def Guard_Log(path, output, modified_files):

    with open(output, 'a') as f: #open and write to log file
        print("{0} modification detected at approximately {1}.  See {2}.".format(path, datetime.datetime.now(), modified_files), file=f)

def Guard_Armed(guard_action, output, modified_files):
    pass

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

    if object_type == "dir":
        #make sure path exists
        if os.path.exists(path) != True:
            print("Path to the directory appears to be incorrect, does not exist.  Your path is: {} - is this correct?".format(path))
            sys.exit()

        #make sure path is a directory, not a file
        if os.path.isdir(path) != True:
            print("Your path does not point to a directory. Please change your object type.")
            sys.exit()

        orig_hash_dict = Get_Dir_Hashes(path, object_type, verbosity)
        if orig_hash_dict == "GUARD":
            if guard_action == "log":
                Guard_Log(path, output, "Main directory to guard deleted.")
        while True: # keep the script running indefinitely, runs once per 15 seconds
            mod_value, modified_file_list, new_dict = Guard_Check_Directory(path, object_type, orig_hash_dict)
            time.sleep(15)
            if mod_value == False:
                print("{0} directory modified at {1}. Taking {2} action...".format(path, modified_file_list, guard_action))
                if guard_action == "log":
                    Guard_Log(path, output, modified_file_list)

                
                orig_hash_dict = new_dict
    
    if object_type == "file":

         #make sure path is legit 
        if os.path.exists(path) != True:
            print("Path to the file appears to be incorrect, does not exist.  Your path is: {} - is this correct?".format(path))
            sys.exit()
        
        #check to make sure path is a file
        if os.path.isfile(path) != True:
            print("Your path does not point to a file. Please change your object type")
            sys.exit()

        orig_file_hash = Get_File_Hash(path, object_type, verbosity)
        if orig_file_hash == "GUARD":
            if guard_action == "log":
                Guard_Log(path, output, "Main file to guard deleted.")
        
        while True: # keep the script running indefinitely, runs once per 15 seconds
            mod_value, new_hash, modified_file = Guard_Check_File(path, object_type, orig_file_hash)
            time.sleep(15)
            if mod_value == False:
                print("{0} modification detected! Taking {1} action...".format(path, guard_action))
                if guard_action == "log":
                    Guard_Log(path, output, modified_file)
                orig_file_hash = new_hash

        
        


    




    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Guard a file or a directory from changes, and either log or take other actions if a change is recorded.")
    parser.add_argument('-path', action='store', dest="path", default="", help="Provide the path to either an indivial file or a directory which you want to monitor.")
    parser.add_argument('-type', action='store', dest="type", default="", help="Define what you are guarding.  Choices are a file or a dir.")
    parser.add_argument('-guard_action', action='store', dest="guard_action", default="log", help="Type of defensive action to take. Currently includes default of log the event, or system shutdown.")
    parser.add_argument('-o', action='store', dest="output", default="log.txt", help="Where to output log file.")
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
    