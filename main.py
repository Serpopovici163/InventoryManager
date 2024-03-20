import os
import sys
from datetime import datetime

import db_manager

# Argument structure

# [operation] [arguments]
# add_order -> add digikey/mouser order
# add_board -> add board type
# del_board -> delete board type
# list_boards -> list board types
# construct_board -> remove board BOM from inventory
# lookup -> look up item in inventory

### FUNCTION DEFINITIONS

#displays generic help message
def helpPage():
    print("\n\tUSAGE: main.py [operation] [arguments]\n")
    print("Possible operations:")
    print("\tadd_order -> add digikey/mouser order")
    print("\tadd_board -> add board type")
    print("\tdel_board -> delete board type")
    print("\tlist_boards -> list board types")
    print("\tconstruct_board -> remove board BOM from inventory")
    print("\tlookup -> look up item in inventory\n")
    print("Use --help after operation for operation-specific help")
    print("For any additive operations (adding orders or boards), place a CSV of the relevant BOM in the same directory as this python file. The BOM file's name is not important.")
    print("This tool works with DigiKey and Mouser order invoices as well as Altium BOMs. Compatibility with other BOM files is not guaranteed.")
    print("")

#function to add digikey/mouser order BOM to database
def add_order():
    #this function requires no arguments, check if used specified --help and mention this if so
    try:
        if (sys.argv[2] == "--help"):
            print("\nNo arguments required for this option :)\n")
            exit()
    except IndexError:

        # Initialize a variable to store the BOM file object
        BOM_file = None

        # Get the list of files in the current directory
        files = os.listdir()

        # Count the number of CSV files in the directory
        csv_count = sum(1 for file in files if file.endswith('.csv'))

        # Check if there's only one CSV file
        if csv_count == 1:
            # Loop through the files to find the CSV file
            for file in files:
                if file.endswith('.csv'):
                    # Assign the file object of the CSV file to BOM_file
                    BOM_file = file
                    break
        elif csv_count >= 1:
            print("\nMore than one BOM file found!")
            print("Please place ONLY ONE .csv file in the directory of this python file.\n")
            exit()
        else:
            print("\nNo BOM file found!")
            print("Please place a .csv file in the same directory as this python file.\n")
            exit()

        # If a CSV file is found, BOM_file will contain its file object
        print("\n BOM file found:", BOM_file)
        print("")


        #if we made it here, then a singular BOM file exists so we can add it to the database

        #handle operations requiring os/sys libraries in this file
        now = datetime.now()
        backup_path = os.getcwd() + "/BOM_HISTORY/" + now.strftime("%d_%m_%Y_%H_%M_%S")

        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
            with open(backup_path + "/log.txt", "w", encoding="utf-8-sig") as log_file:
                log_file.write("Adding order BOM to database...\n")

        print("Directory created: " + backup_path)

        #modify DB
        db_manager.db_add_order(backup_path, BOM_file)

        #now move BOM file to new folder
        os.rename(BOM_file, os.path.join(backup_path + "/BOM.csv"))

        with open(backup_path + "/log.txt", "w", encoding="utf-8-sig") as log_file:
                log_file.write("Success!\n")

def add_board():
    #this function requires one argument, also check if used specified --help and mention this if so
    try:
        if (sys.argv[2] == "--help"):
            print("\n\tUSAGE: main.py add_board [arguments]\n")
            print("Possible arguments:")
            print("\t--help --> shows this help")
            print("\t[name] --> provide a *unique* name for the board you are adding (I will yell at you if it's not unique)")
            exit()
    except IndexError:
        #we need an argument here, so show help if none is provided
        print("\n\tUSAGE: main.py add_board [arguments]\n")
        print("Possible arguments:")
        print("\t--help --> shows this help")
        print("\t[name] --> provide a *unique* name for the board you are adding (I will yell at you if it's not unique)")
        exit()

    # Initialize a variable to store the BOM file object
    BOM_file = None

    # Get the list of files in the current directory
    files = os.listdir()

    # Count the number of CSV files in the directory
    csv_count = sum(1 for file in files if file.endswith('.csv'))

    # Check if there's only one CSV file
    if csv_count == 1:
        # Loop through the files to find the CSV file
        for file in files:
            if file.endswith('.csv'):
                # Assign the file object of the CSV file to BOM_file
                BOM_file = file
                break
    elif csv_count >= 1:
        print("\nMore than one BOM file found!")
        print("Please place ONLY ONE .csv file in the directory of this python file.\n")
        exit()
    else:
        print("\nNo BOM file found!")
        print("Please place a .csv file in the same directory as this python file.\n")
        exit()

    # If a CSV file is found, BOM_file will contain its file object
    print("\n BOM file found:", BOM_file)
    print("")


    #if we made it here, then a singular BOM file exists so we can add it to the database

    #handle operations requiring os/sys libraries in this file
    now = datetime.now()
    board_path = os.getcwd() + "/PCBs/" + sys.argv[2]

    if not os.path.exists(board_path):
        os.makedirs(board_path)
        with open(board_path + "/log.txt", "w", encoding="utf-8-sig") as log_file:
            log_file.write("Adding PCB BOM to database...\n")

    print("Directory created: " + board_path)

    #modify DB
    db_manager.db_add_board(board_path, BOM_file)

    #now move BOM file to new folder
    os.rename(BOM_file, os.path.join(board_path + "/BOM.csv"))

    with open(board_path + "/log.txt", "w", encoding="utf-8-sig") as log_file:
            log_file.write("Success!\n")

def del_board():
    #this function requires one argument, also check if used specified --help and mention this if so
    try:
        if (sys.argv[2] == "--help"):
            print("\n\tUSAGE: main.py del_board [arguments]\n")
            print("Possible arguments:")
            print("\t--help --> shows this help")
            print("\t[name] --> provide the name for the board you are deleting")
            exit()
    except IndexError:
        #we need an argument here, so show help if none is provided
        print("\n\tUSAGE: main.py del_board [arguments]\n")
        print("Possible arguments:")
        print("\t--help --> shows this help")
        print("\t[name] --> provide the name for the board you are deleting")
        exit()
    
    board_path = os.getcwd() + "/PCBs/" + sys.argv[2]

    if os.path.exists(board_path):
        confirmation = input(f"The PCB '{sys.argv[2]}' exists. Do you want to delete it? (yes/no): ")
        if confirmation.lower() == 'yes':
            try:
                for root, dirs, files in os.walk(board_path, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(board_path)
                print(f"The PCB '{sys.argv[2]}' has been successfully deleted.")
            except OSError as e:
                print(f"Error: {e}")
        else:
            print("Deletion canceled by user.")
    else:
        print(f"The PCB '{sys.argv[2]}' does not exist.")

def list_boards():
    # Join the folder path with "PCBs" folder
    folder_path = os.getcwd() + "/PCBs/"
    
    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # List all subdirectories
        subdirectories = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]
        
        # Print out the subdirectories
        if subdirectories:
            print("\nPCBs:")
            for subdir in subdirectories:
                print("\t" + subdir)
        else:
            print("No PCBs found.")
    else:
        print("'PCBs' folder does not exist or is not a directory.")

### ACTUAL CODE

#kind of a shit way to handle this, but this checks for a valid argument
arg_list = {"add_order", "add_board", "del_board", "list_boards", "construct_board", "lookup"}
index = 0

try:
    #for every invalid argument, increment index
    for argument in arg_list:
        if (argument == sys.argv[1]):
            break
        else:
            index += 1

    #if index == length of arg_list, no valid argument was provided so show help screen
    if (index == len(arg_list)):
        helpPage()
        exit()
except IndexError:
    helpPage()
    exit()

#valid argument has been provided

if (sys.argv[1] == "add_order"):
    add_order()
elif (sys.argv[1] == "add_board"):
    add_board()
elif (sys.argv[1] == 'del_board'):
    del_board()
elif (sys.argv[1] == 'list_boards'):
    list_boards()