from src.files_manager import read_evm_wallets_from_file
from src.config import get_stake_stg_config_from_dict
from src.stake_manager import StakeManager
from stake.stake_stg.main import mass_stake_stg

import PySimpleGUI as sg


class StargateStgStakeGui:
    def __init__(self):
        self.source_chain_options = ['BSC', 'Arbitrum', 'Polygon', 'Avalanche', 'Fantom']

        self.stake_data = None

    def check_info_layout(self, values):
        warning_text = sg.Text('Check all entered data!!!', text_color='red',
                               font=('Helvetica', 12))

        if values['test_mode']:
            test_mode_text = sg.Text(f'You are currently in test mode\n',
                                     font=('Helvetica', 12), text_color='yellow')
        else:
            test_mode_text = sg.Text(f'You are currently in real mode\n',
                                     font=('Helvetica', 12), text_color='red')

        source_chain_text = sg.Text(f'Source chain: {values["source_chain"]}',
                                    font=('Helvetica', 12))
        min_stake_amount_text = sg.Text(f'Min STG amount to stake: {values["min_amount_to_stake"]}',
                                        font=('Helvetica', 12))
        max_stake_amount_text = sg.Text(f'Max STG amount to stake: {values["max_amount_to_stake"]}',
                                        font=('Helvetica', 12))
        stake_all_balance_text = sg.Text(f'Stake all STG balance: {values["stake_all_balance"]}',
                                         font=('Helvetica', 12))
        lock_period_months_text = sg.Text(f'Lock period in months (5-36): {values["lock_period_months"]}',
                                          font=('Helvetica', 12))
        min_delay_seconds_text = sg.Text(f'Min delay in seconds: {values["min_delay_seconds"]}',
                                         font=('Helvetica', 12))
        max_delay_seconds_text = sg.Text(f'Max delay in seconds: {values["max_delay_seconds"]}',
                                         font=('Helvetica', 12))

        agree_checkbox = sg.Checkbox('All data correct', key='agree_checkbox')
        stake_button = sg.Button('Stake', size=(10, 1), key='stake_button')
        back_button = sg.Button('Back', size=(10, 1), key='back_button')
        watermark = sg.Text('https://github.com/frankmurrey (tg @shnubjack)', font=('Helvetica', 9), text_color='white')

        layout = [
            [warning_text],
            [test_mode_text],
            [source_chain_text],
            [min_stake_amount_text],
            [max_stake_amount_text],
            [stake_all_balance_text],
            [lock_period_months_text],
            [min_delay_seconds_text],
            [max_delay_seconds_text],
            [agree_checkbox],
            [back_button, stake_button],
            [watermark],
        ]

        return layout

    def stake_layout(self):
        field_size = (20, 1)

        evm_wallets_text = sg.Text(f'Wallets loaded: {len(read_evm_wallets_from_file())}',
                                   text_color='yellow',
                                   font=('Helvetica', 12),
                                   key='evm_wallets_text')

        source_chain_text = sg.Text('Source chain:')
        source_chain_combo = sg.Combo(self.source_chain_options,
                                      size=field_size,
                                      key='source_chain',
                                      enable_events=True)

        min_stake_amount_text = sg.Text('Min STG amount to stake:')
        min_stake_amount_input = sg.InputText(size=field_size,
                                              key='min_amount_to_stake')

        max_stake_amount_text = sg.Text('Max STG amount to stake:')
        max_stake_amount_input = sg.InputText(size=field_size,
                                              key='max_amount_to_stake',
                                              pad=((18, 0), (0, 0)))

        stake_all_balance_checkbox = sg.Checkbox('Stake all STG balance',
                                                 key='stake_all_balance',
                                                 enable_events=True)

        lock_period_months_text = sg.Text('Lock period in months (5-36):')
        lock_period_months_input = sg.InputText(size=field_size,
                                                key='lock_period_months',
                                                default_text=5)

        min_delay_seconds_text = sg.Text('Min delay in seconds:')
        min_delay_seconds_input = sg.InputText(size=field_size,
                                               key='min_delay_seconds',
                                               default_text=0)

        max_delay_seconds_text = sg.Text('Max delay in seconds:',
                                         pad=((31, 0), (0, 0)),)
        max_delay_seconds_input = sg.InputText(size=field_size,
                                               key='max_delay_seconds',
                                               pad=((18, 0), (0, 0)),
                                               default_text=0)

        max_gas_limit_text = sg.Text('Max gas limit:')
        max_gas_limit_input = sg.InputText(size=field_size,
                                           key='gas_limit',
                                           default_text=3000000)

        test_mode_checkbox = sg.Checkbox('Test mode',
                                         key='test_mode')

        next_button = sg.Button('Next',
                                size=(10, 1),
                                key='next_button')

        load_wallets_button = sg.Button('Load wallets',
                                        size=(10, 1),
                                        key='load_wallets_button')

        watermark = sg.Text('https://github.com/frankmurrey (tg @shnubjack)', font=('Helvetica', 9), text_color='white')

        layout = [
            [evm_wallets_text],
            [source_chain_text],
            [source_chain_combo],
            [sg.Text("")],
            [min_stake_amount_text, max_stake_amount_text],
            [min_stake_amount_input, max_stake_amount_input],
            [stake_all_balance_checkbox],
            [sg.Text("")],
            [lock_period_months_text],
            [lock_period_months_input],
            [sg.Text("")],
            [min_delay_seconds_text, max_delay_seconds_text],
            [min_delay_seconds_input, max_delay_seconds_input],
            [sg.Text("")],
            [max_gas_limit_text],
            [max_gas_limit_input],
            [test_mode_checkbox],
            [next_button, load_wallets_button],
            [watermark]

        ]

        return layout

    def stake_all_balance_option(self, values, window):
        include_option = values['stake_all_balance']
        min_stake_input = window['min_amount_to_stake']
        max_stake_input = window['max_amount_to_stake']

        if include_option:
            min_stake_input.update(disabled=True, value='', text_color='grey')
            max_stake_input.update(disabled=True, value='', text_color='grey')
        else:
            min_stake_input.update(disabled=False, value='', text_color='black')
            max_stake_input.update(disabled=False, value='', text_color='black')

    def load_wallets_option(self, window):
        evm_wallets = window['evm_wallets_text']

        evm_wallets.update(f"Wallets loaded: {len(read_evm_wallets_from_file())}")
        window.read()

    def run_stake_window(self):
        stake_layout = self.stake_layout()
        window = sg.Window('Stargate STG staker', stake_layout, size=(400, 530))

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == 'Cancel':
                break

            elif event == "stake_all_balance":
                self.stake_all_balance_option(values, window)

            elif event == "load_wallets_button":
                self.load_wallets_option(window)

            elif event == "next_button":
                config = get_stake_stg_config_from_dict(values)
                stake_manager = StakeManager(input_data=config)
                error_message = stake_manager.check_if_route_eligible()

                if error_message is not True:
                    sg.popup(error_message, title='Error', text_color='yellow')
                    continue

                self.stake_data = values

                window.close()
                window = sg.Window('Check data', self.check_info_layout(values), size=(400, 530))

            elif event == "back_button":
                window.close()
                window = sg.Window('Stargate STG staker', self.stake_layout(), size=(400, 530))

            elif event == "stake_button":
                if not values['agree_checkbox']:
                    sg.popup('Please check the checkbox to confirm all data is correct', title='Error',
                             text_color='red')
                    continue
                config = get_stake_stg_config_from_dict(self.stake_data)
                window.close()

                mass_stake_stg(config)



if __name__ == '__main__':
    StargateStgStakeGui().run_stake_window()