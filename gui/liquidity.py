from src.files_manager import read_evm_wallets_from_file
from src.config import get_add_liquidity_config_from_dict
from src.stake_manager import LiquidityManager
from stake.add_liquidity.main import mass_add_liquidity

import PySimpleGUI as sg


class StargateLiquidityGui:
    def __init__(self):
        self.source_chain_options = ['BSC', 'Arbitrum', 'Optimism', 'Polygon', 'Avalanche', 'Fantom']
        self.coin_options = ['USDC', 'USDT']

        self.liq_data = None

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
        coin_to_add_liquidity_text = sg.Text(f'Coin to add liquidity: {values["coin_to_stake"]}',
                                             font=('Helvetica', 12))
        min_stake_amount_text = sg.Text(f'Min STG amount to stake: {values["min_amount_to_stake"]}',
                                        font=('Helvetica', 12))
        max_stake_amount_text = sg.Text(f'Max STG amount to stake: {values["max_amount_to_stake"]}',
                                        font=('Helvetica', 12))
        stake_all_balance_text = sg.Text(f'Stake all balance: {values["stake_all_balance"]}',
                                         font=('Helvetica', 12))
        min_delay_seconds_text = sg.Text(f'Min delay in seconds: {values["min_delay_seconds"]}',
                                            font=('Helvetica', 12))
        max_delay_seconds_text = sg.Text(f'Max delay in seconds: {values["max_delay_seconds"]}',
                                            font=('Helvetica', 12))
        max_gas_limit_text = sg.Text(f'Max gas limit: {values["gas_limit"]}',
                                            font=('Helvetica', 12))
        wait_for_confirmation_text = sg.Text(f'Wait for confirmation: {values["wait_for_confirmation"]}',
                                             font=('Helvetica', 12))
        confirmation_timeout_seconds_text = sg.Text(
            f'Confirmation timeout seconds: {values["confirmation_timeout_seconds"]}',
            font=('Helvetica', 12))
        agree_checkbox = sg.Checkbox('All data correct', key='agree_checkbox')
        start_button = sg.Button('Start', size=(10, 1), key='start_button')
        back_button = sg.Button('Back', size=(10, 1), key='back_button')
        watermark = sg.Text('https://github.com/frankmurrey (tg @shnubjack)', font=('Helvetica', 9), text_color='white')

        layout = [
            [warning_text],
            [test_mode_text],
            [source_chain_text],
            [coin_to_add_liquidity_text],
            [min_stake_amount_text],
            [max_stake_amount_text],
            [stake_all_balance_text],
            [min_delay_seconds_text],
            [max_delay_seconds_text],
            [max_gas_limit_text],
            [wait_for_confirmation_text],
            [confirmation_timeout_seconds_text],
            [agree_checkbox],
            [back_button, start_button],
            [watermark]
        ]

        return layout

    def add_liquidity_layout(self):
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

        coin_to_add_liquidity_text = sg.Text('Coin to add liquidity:')
        coin_to_add_liquidity_combo = sg.Combo(self.coin_options,
                                               size=field_size,
                                               key='coin_to_stake',
                                               enable_events=True)

        min_stake_amount_text = sg.Text('Min liquidity amount:')
        min_stake_amount_input = sg.InputText(size=field_size,
                                              key='min_amount_to_stake')

        max_stake_amount_text = sg.Text('Max liquidity amount:',
                                        pad=((36, 0), (0, 0)))
        max_stake_amount_input = sg.InputText(size=field_size,
                                              key='max_amount_to_stake',
                                              pad=((18, 0), (0, 0)))

        stake_all_balance_checkbox = sg.Checkbox('Stake all balance',
                                                 key='stake_all_balance',
                                                 enable_events=True)

        min_delay_seconds_text = sg.Text('Min delay in seconds:')
        min_delay_seconds_input = sg.InputText(size=field_size,
                                               key='min_delay_seconds',
                                               default_text=0)

        max_delay_seconds_text = sg.Text('Max delay in seconds:',
                                         pad=((31, 0), (0, 0)), )
        max_delay_seconds_input = sg.InputText(size=field_size,
                                               key='max_delay_seconds',
                                               pad=((18, 0), (0, 0)),
                                               default_text=0)

        max_gas_limit_text = sg.Text('Max gas limit:')
        max_gas_limit_input = sg.InputText(size=field_size,
                                           key='gas_limit',
                                           default_text=3000000)

        wait_for_receipt_checkbox = sg.Checkbox('Wait for txn receipt',
                                                key='wait_for_confirmation',
                                                enable_events=True)
        receipt_timeout_text = sg.Text('Receipt timeout (sec):')
        receipt_timeout_input = sg.InputText(size=field_size,
                                             disabled=True,
                                             default_text='',
                                             key='confirmation_timeout_seconds')

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
            [coin_to_add_liquidity_text],
            [coin_to_add_liquidity_combo],
            [sg.Text("")],
            [min_stake_amount_text, max_stake_amount_text],
            [min_stake_amount_input, max_stake_amount_input],
            [stake_all_balance_checkbox],
            [sg.Text("")],
            [min_delay_seconds_text, max_delay_seconds_text],
            [min_delay_seconds_input, max_delay_seconds_input],
            [max_gas_limit_text],
            [max_gas_limit_input],
            [sg.Text("")],
            [receipt_timeout_text],
            [receipt_timeout_input, wait_for_receipt_checkbox],
            [sg.Text("")],
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

    def wait_for_receipt_option(self, values, window):
        include_option = values['wait_for_confirmation']
        receipt_timeout_input = window['confirmation_timeout_seconds']

        if include_option:
            receipt_timeout_input.update(disabled=False, value='', text_color='black')
        else:
            receipt_timeout_input.update(disabled=True, value='', text_color='grey')

    def run_liquidity_window(self):
        layout = self.add_liquidity_layout()
        window = sg.Window('Stargate Liquidity adder', layout, size=(400, 580))

        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                break

            elif event == 'stake_all_balance':
                self.stake_all_balance_option(values, window)

            elif event == 'wait_for_confirmation':
                self.wait_for_receipt_option(values, window)

            elif event == 'load_wallets_button':
                evm_wallets = read_evm_wallets_from_file()
                window['evm_wallets_text'].update(f'Wallets loaded: {len(evm_wallets)}')

            elif event == 'next_button':
                config = get_add_liquidity_config_from_dict(values)
                liquidity_manager = LiquidityManager(input_data=config)
                error_message = liquidity_manager.check_if_route_eligible()

                if error_message is not True:
                    sg.popup(error_message, title='Error', text_color='yellow')
                    continue

                self.liq_data = values

                window.close()
                window = sg.Window('Check data', self.check_info_layout(values), size=(400, 580))

            elif event == "back_button":
                window.close()
                window = sg.Window('Stargate Liquidity adder', self.add_liquidity_layout(), size=(400, 580))

            elif event == 'start_button':
                if not values['agree_checkbox']:
                    sg.popup('Please check the checkbox to confirm all data is correct', title='Error',
                             text_color='red')
                    continue
                config = get_add_liquidity_config_from_dict(self.liq_data)
                window.close()

                mass_add_liquidity(config)

