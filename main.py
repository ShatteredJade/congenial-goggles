import csv, json
from pathlib import Path
from PyInquirer import prompt


class UserInterface:
    def __init__(self, settings_manager, bucket_manager):
        self.settings_manager = settings_manager
        self.bucket_manager = bucket_manager

    def menu(self):
        menu_options = self.menu_maker('list', 'options', 'Main Menu',
                                       ['Edit Buckets', 'Edit Residences', 'Status', 'Exit'])
        select = prompt(menu_options).get('options')

        if select == 'Edit Buckets':
            self.bucket_interface()
        elif select == 'Edit Residences':
            self.residence_interface()
        elif select == 'Status':
            self.status_interface()
        self.prompt_check(select)

    def bucket_interface(self):
        menu_options = self.menu_maker('list', 'options', 'Bucket Menu',
                                       ['Create New Bucket', 'Edit Existing Buckets', 'Return to Main Menu'])
        select = prompt(menu_options).get('options')

        if select == 'Create New Bucket':
            pass
        elif select == 'Edit Existing Buckets':
            pass
        self.prompt_check(select)

    def residence_interface(self):
        menu_options = self.menu_maker('list', 'options', 'Residence Menu',
                                       ['Create Residence', 'Edit Existing Residences', 'Return to Main Menu'])
        select = prompt(menu_options).get('options')

        if select == 'Create Residence':
            pass
        elif select == 'Edit Existing Residences':
            pass
        self.prompt_check(select)

    # Considering directly displaying missing or unallocated money from menu
    def status_interface(self):
        print("Not done! w dV.Vb w")
        self.menu()

    def prompt_check(self, select):
        if select == 'Return to Main Menu':
            self.menu()
        elif select == 'Exit':
            quit()

    # Wrapper to reduce bloat from the creation of menus
    def menu_maker(self, menu_type, name, message, choices=None):
        menu_options = [
            {
                'type': menu_type,
                'name': name,
                'message': message
            }
        ]

        if choices is not None:
            menu_options[0]['choices'] = choices

        return menu_options


class BucketManager:
    def __init__(self):
        pass


class SettingsManager:
    def __init__(self):
        pass


def main():
    settings_manager = SettingsManager(); bucket_manager = BucketManager()
    ui = UserInterface(settings_manager, bucket_manager)
    ui.menu()


if __name__ == '__main__':
    main()
