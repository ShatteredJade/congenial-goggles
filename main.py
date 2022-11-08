import csv, json
from pathlib import Path
from PyInquirer import prompt
from uuid import uuid1
from datetime import datetime

# menu constants
status_menu = 'Status Menu'
bucket_menu = 'Bucket Menu'
residence_menu = 'Residence Menu'
tutorial = 'Tutorial'
exit_program = 'Exit'
return_to_menu = 'Return to Main Menu'

create_bucket = 'Create Bucket'
edit_bucket = 'Edit Buckets'
remove_bucket = 'Remove a Bucket'

create_residence = 'Create Residence'
edit_residence = 'Edit Residences'
remove_residence = 'Remove a Residence'

yes = 'Yes'
no = 'No'

# sys msg constants
invalid_input = "\nPlease enter a valid input.\n"


class UserInterface:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

        if self.settings_manager.check() is False:
            if self.prompt_confirm('Would you like a tutorial:'):
                self.tutorial_interface()

    def menu(self):
        while True:
            answer = self.menu_prompt('list', 'Main Menu',
                                      [status_menu, bucket_menu, residence_menu, exit_program, tutorial])
            if answer == status_menu:
                self.status_interface()
            elif answer == bucket_menu:
                self.bucket_interface()
            elif answer == residence_menu:
                self.residence_interface()
            elif answer == tutorial:
                self.tutorial_interface()

    def bucket_interface(self):
        bucket_id = self.menu_prompt('list', 'Bucket Menu', [create_bucket, edit_bucket, remove_bucket, return_to_menu])

        if bucket_id == create_bucket:
            # check for residences
            if self.settings_manager.residence_check():
                self.data_gather('buckets', ['name', 'type', 'residence_id'])
            else:
                if self.prompt_confirm('You have not created any residences yet. Would you like to:'):
                    self.data_gather('residences', ['name'])
                    self.data_gather('buckets', ['name', 'type', 'residence_id'])
                else:
                    print("\nCannot create a bucket while no residences exist. Returning to Main Menu.\n")

        elif bucket_id == edit_bucket:
            bucket_id = self.menu_prompt('list', 'Choose a Bucket to Edit',
                                         self.settings_manager.fetch('buckets', 'name', add_return=True))
            if self.return_check(bucket_id):
                self.edit_interface('buckets', bucket_id)

        elif bucket_id == remove_bucket:
            bucket_id = self.menu_prompt('list', 'Choose a Bucket to Remove',
                                         self.settings_manager.fetch('buckets', 'name', add_return=True))
            if self.return_check(bucket_id):
                if self.prompt_confirm('Are you sure you wish to remove this bucket?'):
                    self.settings_manager.remove('buckets', bucket_id)

    def edit_interface(self, category, data_id):
        data_list = self.settings_manager.grab(category, data_id)
        del data_list['id']
        tags = self.settings_manager.tags(titles=True)
        choices = []

        # get edit options
        for data in data_list:
            if data == 'config':
                choices = self.config_choices(data, data_list, choices)
            elif data == 'residence_id':
                name = self.settings_manager.fetch('residences', 'name', data_id=data_list.get(data))[0]
                choices.append({'name': f"{tags.get(data)}: {name.get('name')}", 'value': data})
            else:
                choices.append({'name': f'{tags.get(data)}: {self.label_currency(data_list.get(data))}', 'value': data})

        choices.append(return_to_menu)

        answer = self.menu_prompt('list', 'Choose a Setting to Edit', choices)

        if self.return_check(answer):
            self.data_gather(category, [answer], data_id)

    def residence_interface(self):
        answer = self.menu_prompt('list', 'Residence Menu', [create_residence, edit_residence, remove_residence,
                                                             return_to_menu])

        if answer == create_residence:
            self.data_gather('residences', ['name'])

        elif answer == edit_residence:
            res_id = self.menu_prompt('list', 'Choose a Residence to Edit',
                                      self.settings_manager.fetch('residences', 'name', add_return=True))
            if self.return_check(res_id):
                self.edit_interface('residences', res_id)

        elif answer == remove_residence:
            res_id = self.menu_prompt('list', 'Choose a Residence to Remove',
                                      self.settings_manager.fetch('residences', 'name', add_return=True))

            if self.return_check(res_id):
                # check for dependents
                if self.settings_manager.res_dependents(res_id) is False:
                    if self.prompt_confirm('Are you sure you wish to remove this residence?'):
                        self.settings_manager.remove('residences', res_id)
                else:
                    print('\nDetected buckets that rely on this residence, please remove dependent buckets first.\n')

    def status_interface(self):
        bucket_id = self.menu_prompt('list', 'Status Menu', self.settings_manager.status_display())

        if self.return_check(bucket_id) is False:
            return

        data_list = self.settings_manager.fetch('buckets', 'name', 'type', 'config', 'balance', data_id=bucket_id)
        data_dict = {}

        print(self.status_sys_msg(data_list))

        # prompt user to contribute to bucket balance
        if self.prompt_confirm(f"Would you like to add to {data_list[0].get('name')}'s balance?"):
            if data_list[1] == 'Static':
                while True:
                    answer = self.menu_prompt('input', 'How much would you like to add:')

                    if self.input_check('balance', answer):
                        data_list[3] = f"{float(data_list[3]) + float(answer):.2f}"
                        data_dict = {'balance': data_list[3]}
                        break
                    else:
                        print(invalid_input)
            else:
                # contributes entire monthly goal
                if self.prompt_confirm(f"Contribute {data_list[2].get('monthly_target')}?"):
                    data_list[3] = float(data_list[3])+float(data_list[2].get('monthly_target'))
                    data_list[2]['last_contribution'] = str(datetime.now().strftime('%Y-%m-%d'))
                    data_dict = {'config': data_list[2], 'balance': data_list[3]}

            self.settings_manager.data_dump('buckets', data_dict, data_id=bucket_id)
            print(f"\nSuccessfully Added to {data_list[0].get('name')}'s Balance.\n")

    # assembles sys msg for a bucket's status, returns it
    def status_sys_msg(self, data_list):
        msg = f"\nBucket {data_list[0].get('name')} has a balance of ${data_list[3]} "

        if data_list[1] == 'Static':
            msg = msg+f"and a target balance of ${data_list[2].get('target')}.\n"
        else:
            msg = msg+f"and a monthly goal of ${data_list[2].get('monthly_target')}." \
                              f" The last time you contributed was {data_list[2].get('last_contribution')}.\n"

        return msg

    # gathers input data according to data_list, sends it all off to data_dump
    def data_gather(self, category, data_list, data_id=None):
        data_dict = {}

        for data in data_list:
            while True:
                answer = self.ask_input(category, data)

                if self.return_check(answer) is False:
                    return

                # check input matches necessary value type
                if self.input_check(data, answer):
                    data_dict[data] = answer
                    if data == 'type':
                        data_dict['config'] = self.config_type(answer)
                    break
                else:
                    print(invalid_input)

        self.settings_manager.data_dump(category, data_dict, data_id)

    def prompt_confirm(self, question):
        answer = self.menu_prompt('list', question, [yes, no, return_to_menu])

        if answer == yes:
            return True
        else:
            return False

    def return_check(self, answer):
        if answer == return_to_menu:
            return False
        else:
            return True

    # Wrapper to reduce bloat from the creation of menus. Prompts user, checks prompt, and returns answer
    def menu_prompt(self, menu_type, message, choices=None):
        # PyInquirer format
        menu_options = [
            {
                'type': menu_type,
                'name': 'answer',
                'message': message
            }
        ]

        if choices is not None:
            menu_options[0]['choices'] = choices

        answer = prompt(menu_options).get('answer')

        if answer == exit_program:
            quit()

        return answer

    # Asks user for data input, returns answer
    def ask_input(self, category, data):
        tags = self.settings_manager.tags()
        message_end = ':'
        choices = None

        # assign PyInquirer menu data
        if data in tags['input']:
            menu_type = 'input'
            if data == 'last_contribution':
                message_end = ' (Must be YEAR-MM-DD):'
        else:
            menu_type = 'list'
            if data == 'residence_id':
                choices = self.settings_manager.fetch('residences', 'name')
            else:
                choices = ['Static', 'Growing']

        if choices is not None:
            choices.append(return_to_menu)

        message = f"New {category[:-1].title()} {tags[menu_type].get(data)}" + message_end

        return self.menu_prompt(menu_type, message, choices)

    def float_check(self, data):
        try:
            float(data)
            return True
        except ValueError:
            return False

    def label_currency(self, data):
        if self.float_check(data):
            return f'${float(data):.2f}'
        else:
            return data

    # returns true if input matches required value type, false otherwise
    def input_check(self, data, user_input):
        tags = self.settings_manager.tags()

        if data in list(tags['input'])[:3]:  # if data requires float value
            if self.float_check(user_input):
                return True
            else:
                return False
        elif data == list(tags['input'])[3]:  # if data is a date
            try:
                datetime.strptime(user_input, '%Y-%m-%d')
                return True
            except ValueError:
                return False
        else:
            return True

    # asks for input and returns config dict
    def config_type(self, bucket_type):
        while True:
            # format according to bucket type
            if bucket_type == 'Static':
                target = 'target'
                config = {'target': self.ask_input('buckets', 'target')}
            else:
                target = 'monthly_target'
                config = {'monthly_target': self.ask_input('buckets', 'monthly_target'),
                          'last_contribution': datetime.now().strftime('%Y-%m-%d')}

            try:
                config[target] = f'{float(config.get(target)):.2f}'
                break
            except ValueError:
                print(invalid_input)

        return config

    # returns PyInquirer compatible choices for bucket config
    def config_choices(self, data, data_list, choices):
        # format according to bucket type
        if data_list.get('type') == 'Static':
            value = data_list.get(data).get('target')
            choices.append({'name': f"Target Goal: ${value}", 'value': 'target'})
        else:
            value = data_list.get(data).get('monthly_target')
            value2 = data_list.get(data).get('last_contribution')
            choices.append({'name': f"Monthly Goal: ${value}",
                            'value': 'monthly_target'})
            choices.append({'name': f"Last Contribution: {value2}",
                            'value': 'last_contribution'})
        return choices

    # uses keyboard module, replace later
    def tutorial_interface(self):
        request = "\n\nPress Enter to Continue"
        tutorial_text = ['''
\nCongenial Goggles consists of buckets and residences.''',
                         '''
Buckets represent your financial goals. How much you're trying to save and what you're saving it for.
How much you're saving can be either 'static' or 'growing'.''',
                         '''
Static is a flat dollar amount to be saved. 
Once the bucket is 'filled,' you no longer have to worry until you take some out.''',
                         '''
Growing is a regular contribution to be made once per month. 
The bucket 'grows' as you fill it.''',
                         '''
Residences are where those buckets reside.
Whether that be a corresponding banking account (I.E. Chequeings Account),
or just a category (I.E. Children's College Fund)''']

        for text in tutorial_text:
            print(text, request)
            input()


class SettingsManager:
    def __init__(self):
        pass

    # boolean return is for newcomer tutorial
    def check(self):
        if not Path('settings.json').is_file():
            self.dump({'buckets': [], 'residences': []})
            return False
        else:
            return True

    def residence_check(self):
        settings = self.load()

        for line in settings['residences']:
            try:
                line['id']
                return True
            except KeyError:
                return False

    # creates config, formatted for bucket type
    def config_create(self, bucket_type, bucket_goal):
        if bucket_type == 'Static':
            return {'target': bucket_goal}
        else:
            return {'monthly_target': bucket_goal, 'last_contribution': str(datetime.now().strftime('%Y-%m-%d'))}

    # creates and returns a list of all buckets, tagging them if unallocated/missing funds detected
    def status_display(self):
        bucket_list = []

        settings = self.load()

        for bucket in settings['buckets']:
            bucket_dict = {'name': bucket.get('name'), 'value': bucket.get('id')}

            # format according to bucket type
            if bucket.get('type') == 'Static':
                # if bucket hasn't reached goal
                if float(bucket.get('config').get('target')) > float(bucket.get('balance')):
                    bucket_dict['name'] = f"{bucket.get('name')} (Missing Funds)"  # tag
            else:
                # split recorded and current date into year, month, day
                last_contribution = bucket.get('config').get('last_contribution').split('-')
                current_date = str(datetime.now().strftime('%Y-%m-%d')).split('-')
                # if at least a month has elapsed
                if self.month_check(last_contribution, current_date):
                    bucket_dict['name'] = f"{bucket.get('name')} (Missing Funds)"  # tag

            bucket_list.append(bucket_dict)
        bucket_list.append(return_to_menu)

        return bucket_list

    # finds specified data, returns as a list
    def fetch(self, category, *args, data_id=None, add_return=False):
        data_list = []
        settings = self.load()

        for data in settings[category]:
            if data_id is not None:  # Only ID's data
                if data.get('id') == data_id:
                    data_list = self.fetch_append(data, data_list, args)
            else:  # All data regardless of ID
                data_list = self.fetch_append(data, data_list, args)

        if add_return:
            data_list.append(return_to_menu)

        return data_list

    # iterates through *args, fetching data
    def fetch_append(self, data, data_list, args):
        for arg in args:
            if arg == 'name':  # pair name with an ID value
                data_list.append({'name': data.get('name'), 'value': data.get('id')})
            else:
                data_list.append(data.get(arg))

        return data_list

    # returns entire bucket/residence dict
    def grab(self, category, data_id):
        settings = self.load()

        for setting in settings[category]:
            if setting.get('id') == data_id:
                return setting

    def load(self):
        with open('settings.json', 'r') as f:
            return json.load(f)

    def dump(self, settings):
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=2)

    def data_dump(self, category, data_dict, data_id=None):  # category = bucket/residence
        settings = self.load()

        # default new data format
        if data_id is None:  # if no id then it's a new bucket/residence
            settings[category].append({'id': str(uuid1()), 'name': data_dict.get('name')})
            if category == 'buckets':
                settings[category][-1]['type'] = data_dict.get('type')
                settings[category][-1]['config'] = data_dict.get('config')
                settings[category][-1]['residence_id'] = data_dict.get('residence_id')
                settings[category][-1]['balance'] = '0.00'
            print(f"\nNew {category.title()[:-1]} {data_dict.get('name')} has been created.\n")

        else:
            for setting in settings[category]:
                if setting['id'] == data_id:
                    # overwrites data according to data_dict
                    for data in data_dict:
                        if data == 'balance':
                            setting[data] = f"{float(data_dict.get(data)):.2f}"
                        elif data == 'target' or data == 'monthly_target':
                            setting.get('config')[data] = f"{float(data_dict.get(data)):.2f}"
                        elif data == 'last_contribution':
                            setting.get('config')[data] = data_dict.get(data)
                        else:
                            setting[data] = data_dict.get(data)

                    print(f"\n{category[:-1].title()} {setting.get('name')} has been edited.\n")

        self.dump(settings)

    def remove(self, category, data_id):
        settings = self.load()

        for setting in settings[category]:
            if setting['id'] == data_id:
                settings[category].remove(setting)

        self.dump(settings)

    # possible cringe alert
    def tags(self, titles=False):
        if titles:
            return {
                'target': 'Target Balance',
                'monthly_target': 'Monthly Goal',
                'balance': 'Balance',
                'last_contribution': 'Last Contribution',
                'name': 'Name',
                'type': 'Type',
                'residence_id': 'Residence'
            }
        else:
            return {
                'input': {
                    'target': 'Target Goal',
                    'monthly_target': 'Monthly Goal',
                    'balance': 'Balance',
                    'last_contribution': 'Last Contribution',
                    'name': 'Name'
                },
                'list': {
                    'type': 'Type',
                    'residence_id': 'Residence'
                }
            }

    # checks if a month has elapsed, returns corresponding boolean
    def month_check(self, last_contribution, current_date):
        if current_date[1] > last_contribution[1] and current_date[2] >= last_contribution[2]:
            return True
        elif current_date[0] > last_contribution[0] and current_date[2] >= last_contribution[2]:
            return True
        elif int(current_date[1]) - int(last_contribution[1]) > 1:
            return True
        else:
            return False

    # checks if a residence has dependent buckets, returns corresponding boolean
    def res_dependents(self, data_id):
        settings = self.load()

        for setting in settings['buckets']:
            if setting['residence_id'] == data_id:
                return True
        else:
            return False


def main():
    settings_manager = SettingsManager()
    ui = UserInterface(settings_manager)
    ui.menu()


if __name__ == '__main__':
    main()
