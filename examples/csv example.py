import csv
from pathlib import Path


def ask_user():
    request = input('> ')
    if request.lower() == 'quit':
        quit()
    elif request.lower() == 'exit':
        file_directory()
    elif request.lower() == 'help':
        print("\nQuit - exit program\nExit - exit and choose new file")
        ask_user()
    else:
        return request


# Lists fieldnames, asks user to choose from them, then calls to dump the data belonging to that fieldname
def read_fieldnames(file_path):
    with open_file(file_path, 'r', csv.DictReader) as (file_handle, csv_reader):
        counter = 1
        print('\n----------------\nChoose category:\n----------------\n1. All')
        for key in csv_reader.fieldnames:
            counter += 1
            print(f'{counter}. {key}')
        # Making sure the user chose a viable option, then calling to dump the corresponding data
        else:
            user_input = ask_user()
            while True:
                try:
                    int(user_input)
                    break
                except ValueError:
                    print("Please enter a valid number")
        if int(user_input) <= counter:
            dump_csv(int(user_input), file_path)


def dump_csv(choice, file_path):
    with open_file(file_path, 'r', csv.reader) as (file_handle, csv_reader):
        if choice == 1:
            for line in csv_reader:
                print(', '.join(line))
        else:
            for line in csv_reader:
                print(line[choice - 2])


def file_directory():
    print("--------------------\nInput file directory\n--------------------")
    file_path = f'statements/{ask_user()}'
    if file_verification(file_path):
        read_fieldnames(file_path)


def file_verification(file_path):
    if Path(file_path).is_file() and file_path.endswith('.csv'):
        return True
    else:
        print("File does not exist or is not a valid CSV. Returning...\n")
        file_directory()


def open_file(file_path, mode, reader_type):
    file_handle = open(file_path, mode)
    file_manager = reader_type(file_handle)
    return file_handle, file_manager


file_directory()


# def test(file_path, mode, reader_type):
#     a = open(file_path, mode)
#     b = reader_type(a)
#     return a, b
