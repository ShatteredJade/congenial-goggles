import csv, json
from pathlib import Path

# Before the implementation of PyInquirer


class UserInterface:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def user_input(self):
        request = input('\n>')
        if request.lower() == 'quit':
            quit()
        elif request.lower() == 'menu':
            self.directory()
        elif request.lower() == 'settings':
            self.settings_interface()
        else:
            return request

    def directory(self):
        while True:
            print('----\nMenu\n----\n\nMenu - Return to Menu\nQuit - Quit Program\nSettings - Access Settings Menu')
            self.user_input()
            print('Invalid response, returning...')

    def settings_interface(self):
        while True:
            counter, settings = self.settings_manager.settings_read()
            request = self.settings_prompt()
            key, line = self.settings_manager.settings_select(counter, settings, request)
            request = self.settings_prompt()
            self.settings_manager.settings_edit(key, line, request, settings)

    def settings_prompt(self):
        request = self.user_input()
        if request.lower() == 'default':
            request = input("\nAre you sure you want to return to default settings?\n\n>")
            if self.default_confirm(request):
                self.settings_manager.settings_create()
            self.settings_interface()
        else:
            return request

    def default_confirm(self, request):
        if request.lower() == 'y' or request.lower() == 'yes':
            print("\nReverting to default settings...")
            return True
        else:
            print("\nReturning to settings menu...")
            return False


class SettingsManager:
    def __init__(self):
        self.settings_check()

    def settings_read(self):
        print("--------\nSettings\n--------\n")
        with open('statements/settings.json', 'r') as settings_file:
            settings = json.load(settings_file)
            counter = 0
            for line in settings['test']:
                for key in line.keys():
                    counter += 1
                    print(f'{counter}. {key}: {line[key]}')
            return counter, settings

    def settings_select(self, counter, settings, request):
        if check_response(request, counter):
            counter_check = 0
            for line in settings['test']:
                for key in line.keys():
                    counter_check += 1
                    if counter_check == int(request):
                        print(f'\n{key}: {line[key]}\n\nPlease input a new value')
                        return key, line
        else:
            print('Invalid response, returning to settings menu...')

    def settings_edit(self, key, line, request, settings):
        answer, request = check_variable(line[key], request)
        with open('statements/settings.json', 'w') as settings_file:
            if answer:  # Check for if before opening folder
                line[key] = request
            else:
                print('Invalid response, returning to settings menu...')
            json.dump(settings, settings_file, indent=2)

    def settings_check(self):
        if not Path('statements/settings.json').is_file():
            self.settings_create()

    def settings_create(self):
        with open('statements/settings.json', 'w') as settings_file:
            json.dump({'test': [{'test_boolean': True, 'test_int': 84, 'test_string': 'jetstream sam'}]},
                      settings_file, indent=2)


def check_response(request, counter):
    try:
        request = int(request)
    except ValueError:
        return False
    if request <= 0 or request > counter:
        return False
    else:
        return True

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


def main():
    settings_manager = SettingsManager()
    ui = UserInterface(settings_manager)
    ui.directory()


if __name__ == '__main__':
    main()

# An example of PyInquirer
# -------------------------
# from PyInquirer import prompt, print_json
#
# questions = [
#     {
#         'type': 'list',
#         'name': 'beverage',
#         'message': 'What size drink would you like?',
#         'choices': ['small', 'medium', 'large', 'extra-large']
#     }
# ]
#
# answers = prompt(questions)
# print_json(answers)
