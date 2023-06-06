from src.files_manager import read_evm_wallets_from_file
from src.bridge_manager import WarmUpRouteValidator
from src.config import get_warmup_config_from_dict

from bridge_swap.warm_up.main import initialize_all_wallets, warm_up, save_summary_log_file

import PySimpleGUI as sg


class LayerZeroAutoBridgeGui:
    def __init__(self):
        self.available_chain_names = ['Arbitrum', 'Avalanche', 'BSC', 'Ethereum', 'Fantom', 'Optimism', 'Polygon']
        self.available_coin_names = ['Stablecoins', 'Ethereum']
        self.bridge_data = None

    def bridge_menu_layout(self):
        evm_wallets_loaded_text = sg.Text(f'Evm wallets loaded: {len(read_evm_wallets_from_file())}',
                                          text_color='yellow',
                                          font=('Helvetica', 12))
        chain_options_text = sg.Text('Select chains (Stargate bridge):', text_color='white', font=('Helvetica', 12))
        chain_name_layouts = []
        for chain_name in self.available_chain_names:
            chain_name_checkbox = sg.Checkbox(chain_name, default=False, key=f'{chain_name}_checkbox_chain_option', size=(10, 1),
                                              font=('Helvetica', 11))
            chain_name_layout = [chain_name_checkbox]
            chain_name_layouts.extend(chain_name_layout)

        checkbox_layouts = [chain_name_layouts[i:i + 4] for i in range(0, len(chain_name_layouts), 4)]

        coin_to_transfer_text = sg.Text('Coin to transfer:', text_color='white', font=('Helvetica', 12))
        coin_to_transfer_combo = sg.Combo(self.available_coin_names, default_value='Stablecoins',
                                          key='coin_to_transfer')

        min_delay_text = sg.Text('Min delay (seconds):', text_color='white', font=('Helvetica', 12))
        min_delay_input = sg.InputText('0', key='min_delay', size=(20, 1))

        max_delay_text = sg.Text('Max delay (seconds):', text_color='white', font=('Helvetica', 12), pad=(20, 0))
        max_delay_input = sg.InputText('0', key='max_delay', size=(20, 1), pad=(23, 0))

        min_amount_to_transfer_text = sg.Text('Min amount to transfer:', text_color='white', font=('Helvetica', 12))
        min_amount_to_transfer_input = sg.InputText('0', key='min_amount_to_transfer', size=(20, 1))

        max_amount_to_transfer_text = sg.Text('Max amount to transfer:', text_color='white', font=('Helvetica', 12),
                                              pad=(6, 0))
        max_amount_to_transfer_input = sg.InputText('0', key='max_amount_to_transfer', size=(20, 1), pad=(23, 0))

        send_all_balance_checkbox = sg.Checkbox('Send all balance', default=False, key='send_all_balance',
                                                enable_events=True)

        max_gas_limit_text = sg.Text('Max gas limit:', text_color='white', font=('Helvetica', 12))
        max_gas_limit_input = sg.InputText(default_text=4000000, key='max_gas_limit', size=(20, 1))

        slippage_text = sg.Text('Slippage %:', text_color='white', font=('Helvetica', 12))
        slippage_input = sg.InputText(default_text=0.5, key='slippage', size=(20, 1))

        shuffle_wallets_checkbox = sg.Checkbox('Shuffle wallets', default=False, key='shuffle_wallets')

        test_mode_checkbox = sg.Checkbox('Test mode', default=True, key='test_mode')

        next_button = sg.Button('Next', size=(10, 1), key='next_button')
        exit_button = sg.Button('Exit', size=(10, 1), key='exit_button')

        watermark_text = sg.Text('https://github.com/frankmurrey (tg @shnubjack)', text_color='white',
                                 font=('Helvetica', 9))
        layout = [
            [evm_wallets_loaded_text],
            [sg.Text('')],
            [chain_options_text],
            [checkbox_layouts],
            [coin_to_transfer_text],
            [coin_to_transfer_combo],
            [min_delay_text, max_delay_text],
            [min_delay_input, max_delay_input],
            [min_amount_to_transfer_text, max_amount_to_transfer_text],
            [min_amount_to_transfer_input, max_amount_to_transfer_input],
            [send_all_balance_checkbox],
            [max_gas_limit_text],
            [max_gas_limit_input],
            [slippage_text],
            [slippage_input],
            [shuffle_wallets_checkbox],
            [test_mode_checkbox],
            [next_button, exit_button],
            [watermark_text]
        ]

        return layout

    def check_info_layout(self, values, chain_options):
        warning_text = sg.Text('Check all entered data!!!', text_color='red',
                               font=('Helvetica', 12))

        if values['test_mode']:
            test_mode_text = sg.Text(f'You are currently in test mode\n',
                                     font=('Helvetica', 12), text_color='yellow')
        else:
            test_mode_text = sg.Text(f'You are currently in real mode\n',
                                     font=('Helvetica', 12), text_color='red')

        chain_options_text = sg.Text(f'Chains: {chain_options}\n',
                                     font=('Helvetica', 12), text_color='white')

        coin_to_transfer_text = sg.Text(f'Coin to transfer: {values["coin_to_transfer"]}\n',
                                        font=('Helvetica', 12), text_color='white')

        min_delay_text = sg.Text(f'Min delay: {values["min_delay"]} seconds\n',
                                    font=('Helvetica', 12), text_color='white')

        max_delay_text = sg.Text(f'Max delay: {values["max_delay"]} seconds\n',
                                    font=('Helvetica', 12), text_color='white')

        min_amount_to_transfer_text = sg.Text(f'Min amount to transfer: {values["min_amount_to_transfer"]}\n',
                                                font=('Helvetica', 12), text_color='white')

        max_amount_to_transfer_text = sg.Text(f'Max amount to transfer: {values["max_amount_to_transfer"]}\n',
                                                font=('Helvetica', 12), text_color='white')

        max_gas_limit_text = sg.Text(f'Max gas limit: {values["max_gas_limit"]}\n',
                                        font=('Helvetica', 12), text_color='white')

        slippage_text = sg.Text(f'Slippage: {values["slippage"]}\n',
                                    font=('Helvetica', 12), text_color='white')

        shuffle_wallets_text = sg.Text(f'Shuffle wallets: {values["shuffle_wallets"]}\n',
                                        font=('Helvetica', 12), text_color='white')

        agreement_checkbox = sg.Checkbox('I agree to use this software at my own risk', default=False, key='agreement')
        back_button = sg.Button('Back', size=(10, 1), key='back_button')
        start_button = sg.Button('Start', size=(10, 1), key='start_button')

        layout = [
            [warning_text],
            [test_mode_text],
            [chain_options_text],
            [coin_to_transfer_text],
            [min_delay_text],
            [max_delay_text],
            [min_amount_to_transfer_text],
            [max_amount_to_transfer_text],
            [max_gas_limit_text],
            [slippage_text],
            [shuffle_wallets_text],
            [agreement_checkbox],
            [back_button, start_button]
        ]

        return layout

    def build_config_dict(self, values: dict):
        chain_options = []
        for value in values:
            if value.endswith('_checkbox_chain_option'):
                if values[value] is True:
                    chain_options.append(value.replace('_checkbox_chain_option', ''))

        if values['coin_to_transfer'] == 'Stablecoins':
            coin_to_transfer = 'stable_coins'
        else:
            coin_to_transfer = 'ethereum'

        config = {
            'chain_options': chain_options,
            'coin_to_transfer': coin_to_transfer,
            'min_delay_seconds': values['min_delay'],
            'max_delay_seconds': values['max_delay'],
            'min_amount_to_transfer': values['min_amount_to_transfer'],
            'max_amount_to_transfer': values['max_amount_to_transfer'],
            'max_gas_limit': values['max_gas_limit'],
            'slippage': values['slippage'],
            'shuffle_wallets_order': values['shuffle_wallets'],
            'test_mode': values['test_mode'],
            'send_all_balance': values['send_all_balance']
        }

        return config

    def send_all_balance_option(self, values, window):
        include_option = values['send_all_balance']
        min_bridge_input = window['min_amount_to_transfer']
        max_bridge_input = window['max_amount_to_transfer']

        if include_option:
            max_bridge_input.update(disabled=True, value='', text_color='grey')
        else:
            min_bridge_input.update(disabled=False, value='', text_color='black')
            max_bridge_input.update(disabled=False, value='', text_color='black')

    def run_initial_window(self):
        bridge_menu_layout = self.bridge_menu_layout()
        window = sg.Window('Layer Zero Auto', bridge_menu_layout, size=(600, 600))

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == 'Cancel':
                break

            elif event == 'exit_button':
                break

            elif event == 'send_all_balance':
                self.send_all_balance_option(values, window)

            elif event == 'next_button':
                config_data = self.build_config_dict(values)
                config = get_warmup_config_from_dict(config_data)
                self.bridge_data = config

                warmup_route_validator = WarmUpRouteValidator(input_data=config)
                route_status = warmup_route_validator.check_route()
                if route_status is not True:
                    sg.popup(route_status, title='Error', text_color='yellow')
                    continue
                check_info_layout = self.check_info_layout(values=values, chain_options=config.chain_options)
                window.close()
                window = sg.Window('Layer Zero Auto', check_info_layout, size=(600, 600))

            elif event == 'back_button':
                bridge_menu_layout = self.bridge_menu_layout()
                window.close()
                window = sg.Window('Layer Zero Auto', bridge_menu_layout, size=(600, 600))

            elif event == 'start_button':
                if values['agreement'] is False:
                    sg.popup('Please agree to the terms of use', title='Error', text_color='yellow')
                    continue

                window.close()
                initialize_all_wallets()
                warm_up(config=self.bridge_data)
                save_summary_log_file()

