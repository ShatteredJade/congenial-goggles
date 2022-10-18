import json
from pathlib import Path


def settings_check():
    if Path('statements/settings.json').is_file():
        directory()
    else:
        settings_create()


def settings_create():
    with open('statements/settings.json', 'w') as settings_file:
        json.dump(settings_default(), settings_file, indent=2)
    directory()


def settings_default():
    data = {'test': [{'test_boolean': True, 'test_int': 84, 'test_string': 'jetstream sam'}]}
    return data


def directory():
    print("--------\nSettings\n--------\n")
    settings_read()


def settings_read():
    with open('statements/settings.json', 'r') as settings_file:
        settings = json.load(settings_file)
        counter = 0
        for line in settings['test']:
            for key in line.keys():
                counter += 1
                print(f'{counter}. {key}: {line[key]}')
        settings_write(counter, settings)


def settings_write(counter, settings):
    request = user_input()
    if check_response(request, counter):
        counter_check = 0
        for line in settings['test']:
            for key in line.keys():
                counter_check += 1
                if counter_check == int(request):
                    print(f'\n{key}: {line[key]}\n\nPlease input a new value')
                    request = user_input()
                    answer, request = check_variable(line[key], request)
                    with open('statements/settings.json', 'w') as settings_file:
                        if answer:  # Check for if before opening folder
                            line[key] = request
                        else:
                            print('Invalid response,returning...')
                        json.dump(settings, settings_file, indent=2)
                    directory()
    else:
        print('Invalid response, returning...')
        directory()


def check_variable(value, request):
    if isinstance(value, bool):
        if request.lower() == 'false':
            request = False
        elif request.lower() == 'true':
            request = True
        else:
            return False, request
        return True, request
    else:
        try:
            request = type(value)(request)
            return True, request
        except ValueError:
            return False, request


def check_response(request, counter):
    try:
        request = int(request)
    except ValueError:
        return False
    if request <= 0 or request > counter:
        return False
    else:
        return True


def user_input():
    request = input('\n> ')
    if request.lower() == 'quit':
        quit()
    if request.lower() == 'default':
        request = input("\nAre you sure you want to return to default settings?\n\n>")
        if request.lower() == 'y' or request.lower() == 'yes':
            settings_create()
        else:
            print("\nReturning...")
            directory()
    else:
        return request


settings_check()
