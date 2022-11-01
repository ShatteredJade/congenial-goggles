import csv, json, keyboard
from pathlib import Path
from PyInquirer import prompt
from uuid import uuid1
from datetime import datetime

# Will optimize fetching, editing, and creating data in settings later.
# Functions to appraise: bucket_interface_create, bucket_interface_edit, edit_select, residence_create, bucket_create,
#                        settings_fetch, settings_fetch_check


class UserInterface:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

        if self.settings_manager.check() is False:
            if self.prompt_confirm('Would you like a tutorial:'):
                self.tutorial_interface()

    def menu(self):
        answer = self.menu_prompt('list', 'Main Menu',
                                  ['Status', 'Edit Buckets', 'Edit Residences', 'Exit', 'Tutorial'])

        if answer == 'Status':
            self.status_interface()
        elif answer == 'Edit Buckets':
            self.bucket_interface()
        elif answer == 'Edit Residences':
            self.residence_interface()
        elif answer == 'Tutorial':
            self.tutorial_interface()

    def bucket_interface(self):
        answer = self.menu_prompt('list', 'Bucket Menu', ['Create New Bucket', 'Edit Existing Buckets',
                                                          'Remove a Bucket', 'Return to Main Menu'])

        if answer == 'Create New Bucket':
            if self.settings_manager.residence_check():  # checking for at least one residence for the new bucket
                self.data_gather('buckets', ['name', 'type', 'residence_id'])
            else:
                if self.prompt_confirm('You have not created any residences yet. Would you like to:'):
                    self.data_gather('residences', ['name'])
                    self.data_gather('buckets', ['name', 'type', 'residence_id'])
                else:
                    print("\nCannot create a bucket while no residences exist. Returning to Main Menu.\n")

            self.menu()

        elif answer == 'Edit Existing Buckets':
            bucket_id = self.menu_prompt('list', 'Choose a Bucket to Edit',
                                         self.settings_manager.fetch('buckets', 'name', main_menu=True))

            self.edit_interface('buckets', bucket_id)
            self.menu()

        elif answer == 'Remove a Bucket':
            bucket_id = self.menu_prompt('list', 'Choose a Bucket to Remove',
                                         self.settings_manager.fetch('buckets', 'name', main_menu=True))

            if self.prompt_confirm(f"Are you sure you wish to remove this bucket?"):
                self.settings_manager.remove('buckets', bucket_id)
            self.menu()

    def edit_interface(self, category, data_id):
        data_list = self.settings_manager.grab(category, data_id)
        del data_list['id']
        tags = self.settings_manager.tags(titles=True)
        choices = []

        for data in data_list:
            if data == 'config':
                choices = self.config_choices(data, data_list, choices)
            elif data == 'residence_id':
                name = self.settings_manager.fetch('residences', 'name', data_id=data_list.get(data))[0]
                choices.append({'name': f"{tags.get(data)}: {name.get('name')}", 'value': data})
            else:
                choices.append({'name': f'{tags.get(data)}: {self.label_currency(data_list.get(data))}', 'value': data})

        choices.append('Return to Main Menu')

        answer = self.menu_prompt('list', 'Select a Setting to Edit', choices)

        self.data_gather(category, [answer], data_id)

        # data_list = self.settings_manager.grab('buckets', bucket_id)
        # del data_list['id']
        # titles = []
        #
        # for data in data_list:  # creates titles for edit menu
        #     if data == 'config':
        #         for config in data_list.get(data):
        #             titles.append(f"{config.replace('_', ' ').title()}: "
        #                           f"{self.label_currency(data_list.get(data).get(config))}")
        #     elif data == 'residence_id':
        #         res = self.settings_manager.fetch('residences', 'name', data_id=data_list.get(data))
        #         titles.append(f"Residence - {res[0].get('name')}")
        #         continue
        #     else:
        #         titles.append(f"{data.replace('_', ' ').title()}: {self.label_currency(data_list.get(data))}")
        #
        # titles.append('Return to Main Menu')
        #
        # menu_options = self.menu_maker('list', 'options', f"Edit Bucket {data_list.get('name')}", titles)
        # select = prompt(menu_options).get('options')
        # self.prompt_check(select)
        #
        # self.edit_select(select, bucket_id, data_list)

        # --------------------------------------------------------------------------------------------------------------

        # data_list = self.settings_manager.settings_fetch('buckets', 'name', 'type', 'residence_id', 'balance',
        #                                                  'config', data_id=bucket_id)
        # residence = self.settings_manager.settings_fetch('residences', 'name', data_id=data_list[2])[0]
        #
        # title_list = [
        #     f"Name: {data_list[0].get('name')}",
        #     f"Type: {data_list[1]}",
        #     f"Residence: {residence.get('name')}",
        #     f"Balance: ${data_list[3]}"
        # ]
        #
        # if data_list[1] == 'Static':
        #     title_list.insert(2, 'Target Goal: $' + data_list[4].get('target'))
        # else:
        #     title_list.insert(2, 'Monthly Target Goal: $' + data_list[4].get('monthly_target'))
        #     title_list.insert(3, 'Last Contribution: ' + data_list[4].get('last_contribution'))
        #
        # title_list.append(data_list[-1])  # adding return to main menu
        #
        # menu_options2 = self.menu_maker('list', 'options', f'Edit Bucket {data_list[0]}', title_list)
        # select = prompt(menu_options2).get('options')
        # self.prompt_check(select)
        #
        # self.edit_select(select, bucket_id)

    def residence_interface(self):
        answer = self.menu_prompt('list', 'Residence Menu', ['Create Residence', 'Edit Existing Residences',
                                                             'Remove a Residence', 'Return to Main Menu'])

        if answer == 'Create Residence':
            self.data_gather('residences', ['name'])
            self.menu()
        elif answer == 'Edit Existing Residences':
            res_id = self.menu_prompt('list', 'Choose a Residence to Edit',
                                      self.settings_manager.fetch('residences', 'name', main_menu=True))

            self.edit_interface('residences', res_id)
            self.menu()

        elif answer == 'Remove a Residence':
            res_id = self.menu_prompt('list', 'Choose a Residence to Remove',
                                      self.settings_manager.fetch('residences', 'name', main_menu=True))

            if self.settings_manager.res_dependents(res_id) is False:
                if self.prompt_confirm(f"Are you sure you wish to remove this residence?"):
                    self.settings_manager.remove('residences', res_id)
            else:
                print('\nDetected buckets that rely upon this residence, please remove all dependent buckets first.\n')

            self.menu()

    # gathers input data according to data_list, sends it all off to data_dump
    def data_gather(self, category, data_list, data_id=None):
        data_dict = {}

        for data in data_list:
            while True:
                answer = self.ask_input(category, data)

                if self.input_check(data, answer):
                    data_dict[data] = answer
                    if data == 'type':
                        data_dict['config'] = self.config_type(answer)
                    break
                else:
                    print("\nPlease enter a valid input.\n")

        self.settings_manager.data_dump(category, data_dict, data_id)

    # Considering directly displaying missing or unallocated money from menu
    def status_interface(self):
        bucket_id = self.menu_prompt('list', 'Status Menu', self.settings_manager.status_display())
        data_list = self.settings_manager.fetch('buckets', 'name', 'type', 'config', 'balance', data_id=bucket_id)
        message = f"\nBucket {data_list[0].get('name')} has a balance of ${data_list[3]} "
        data_dict = {}

        if data_list[1] == 'Static':
            message = message+f"and a target balance of ${data_list[2].get('target')}.\n"
        else:
            message = message+f"and a monthly goal of ${data_list[2].get('monthly_target')}." \
                              f" The last time you contributed was {data_list[2].get('last_contribution')}.\n"
        print(message)

        if self.prompt_confirm(f"Would you like to add to {data_list[0].get('name')}'s balance?"):
            if data_list[1] == 'Static':
                while True:
                    answer = self.menu_prompt('input', 'How much would you like to add:')

                    if self.input_check('balance', answer):
                        data_list[3] = f"{float(data_list[3]) + float(answer):.2f}"
                        data_dict = {'balance': data_list[3]}
                        break
                    else:
                        print('\nPlease enter a valid input.\n')
            else:
                if self.prompt_confirm(f"Contribute {data_list[2].get('monthly_target')}?"):
                    data_list[3] = float(data_list[3])+float(data_list[2].get('monthly_target'))
                    data_list[2]['last_contribution'] = str(datetime.now().strftime('%Y-%m-%d'))
                    data_dict = {'config': data_list[2], 'balance': data_list[3]}

            self.settings_manager.data_dump('buckets', data_dict, data_id=bucket_id)
            print(f"\nSuccessfully Added to {data_list[0].get('name')}'s Balance.\n")
        self.menu()

    def prompt_check(self, select):
        if select.lower()[:6] == 'return':
            self.menu()
        elif select.lower() == 'exit':
            quit()

    def prompt_confirm(self, question):
        answer = self.menu_prompt('list', question, ['Yes', 'No', 'Return to Main Menu'])

        if answer == 'Yes':
            return True
        else:
            return False

    # Wrapper to reduce bloat from the creation of menus. Prompts user and returns answer
    def menu_prompt(self, menu_type, message, choices=None):
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
        self.prompt_check(answer)
        return answer

    # Asks user for data input, returns answer
    def ask_input(self, category, data):
        tags = self.settings_manager.tags()
        message_end = ':'
        choices = None

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
            choices.append('Return to Main Menu')

        message = f"New {category[:-1].title()} {tags[menu_type].get(data)}" + message_end

        return self.menu_prompt(menu_type, message, choices)

    def float_check(self, data):
        try:
            f"{float(data):.2f}"
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
                print('\nPlease input a correct value\n')

        return config

    def config_choices(self, data, data_list, choices):
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

    def tutorial_interface(self):
        request = "\n\nPress Space to Continue\n"
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
            keyboard.wait('space')

        self.menu()


class SettingsManager:
    def __init__(self):
        pass

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

    # Formats settings file based on bucket type
    def config_create(self, bucket_type, bucket_goal):
        if bucket_type == 'Static':
            return {'target': bucket_goal}
        else:
            return {'monthly_target': bucket_goal, 'last_contribution': str(datetime.now().strftime('%Y-%m-%d'))}

    def status_display(self):
        bucket_list = []

        settings = self.load()

        for bucket in settings['buckets']:
            bucket_dict = {'name': bucket.get('name'), 'value': bucket.get('id')}

            if bucket.get('type') == 'Static':
                # if bucket hasn't reached goal
                if float(bucket.get('config').get('target')) > float(bucket.get('balance')):
                    bucket_dict['name'] = f"{bucket.get('name')} (Missing Funds)"

            else:  # if type is growing
                last_contribution = bucket.get('config').get('last_contribution').split('-')
                current_date = str(datetime.now().strftime('%Y-%m-%d')).split('-')
                # if at least a month has elapsed
                if self.month_check(last_contribution, current_date):
                    bucket_dict['name'] = f"{bucket.get('name')} (Missing Funds)"

            bucket_list.append(bucket_dict)
        bucket_list.append('Return to Main Menu')

        return bucket_list

    # finds specified data, returns as a list
    def fetch(self, category, *args, data_id=None, main_menu=False):
        data_list = []
        settings = self.load()

        for data in settings[category]:
            if data_id is not None:  # Only ID's data
                if data.get('id') == data_id:
                    data_list = self.fetch_check(data, data_list, args)
            else:  # All data regardless of ID
                data_list = self.fetch_check(data, data_list, args)

        if main_menu:
            data_list.append('Return to Main Menu')

        return data_list

    # iterates through *args, fetching data
    def fetch_check(self, data, data_list, args):
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

    # if no id, dump new bucket/residence
    def data_dump(self, category, data_dict, data_id=None):  # kwarg = setting: data
        settings = self.load()

        if data_id is None:  # if no id then new bucket/residence
            settings[category].append({'id': str(uuid1()), 'name': data_dict.get('name')})
            if category == 'buckets':
                settings[category][-1]['type'] = data_dict.get('type')
                settings[category][-1]['config'] = data_dict.get('config')
                settings[category][-1]['residence_id'] = data_dict.get('residence_id')
                settings[category][-1]['balance'] = '0.00'
            print(f"\nNew {category.title()[:-1]} {data_dict.get('name')} has been created.\n")

        for setting in settings[category]:
            if setting['id'] == data_id:
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

    def month_check(self, last_contribution, current_date):
        if current_date[1] > last_contribution[1] and current_date[2] >= last_contribution[2]:
            return True
        elif current_date[0] > last_contribution[0] and current_date[2] >= last_contribution[2]:
            return True
        elif int(current_date[1]) - int(last_contribution[1]) > 1:
            return True
        else:
            return False

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
