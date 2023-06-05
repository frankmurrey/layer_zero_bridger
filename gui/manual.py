from src.files_manager import load_config, save_config
from src.files_manager import read_evm_wallets_from_file, read_aptos_wallets_from_file
from src.bridge_manager import BridgeManager
from src.config import get_config_from_dict

from bridge_swap.bridge_runner import run_bridge

import PySimpleGUI as sg


class LayerZeroManualGui:
    def __init__(self):
        self.bridge_options = ['Stargate', 'Aptos', 'CoreDao']

        self.source_chain_options_stargate = ['Arbitrum', 'Optimism', 'Polygon', 'Ethereum', 'BSC', 'Fantom', 'Avalanche']
        self.target_chain_options_stargate = ['Arbitrum', 'Optimism', 'Polygon', 'Ethereum', 'BSC', 'Fantom', 'Avalanche']
        self.coin_options_stargate = ['Ethereum', 'USDC', 'USDT']

        self.source_chain_options_aptos = ['Ethereum', 'Polygon', 'Avalanche', 'Optimism', 'Arbitrum']
        self.target_chain_options_aptos = ['Aptos']
        self.coin_options_aptos = ['Ethereum', 'USDC', 'USDT']

        self.source_chain_options_core_dao = ['BSC', 'CoreDao']
        self.target_chain_options_core_dao = ['CoreDao', 'BSC']
        self.coin_options_core_dao = ['USDC', 'USDT']

        self.bridge_data = None

    def load_data_from_config(self, window):
        config = load_config()
        if not config:
            sg.popup('No config found', title='Error', text_color='red')
            return

        window['source_chain'].update(value=config['source_chain'])
        window['target_chain'].update(value=config['target_chain'])
        window['bridge_option'].update(value=config['bridge_option'])
        window['slippage'].update(value=config['slippage'])
        window['gas_limit'].update(value=config['gas_limit'])
        window['source_coin_to_transfer'].update(value=config['source_coin_to_transfer'])
        window['target_coin_to_transfer'].update(value=config['target_coin_to_transfer'])
        window['min_bridge_amount'].update(value=config['min_bridge_amount'])
        window['max_bridge_amount'].update(value=config['max_bridge_amount'])
        window['min_delay_seconds'].update(value=config['min_delay_seconds'])
        window['max_delay_seconds'].update(value=config['max_delay_seconds'])
        window['test_mode'].update(value=config['test_mode'])
        window['send_to_one_address'].update(value=config['send_to_one_address'])
        window['address_to_send'].update(value=config['address_to_send'])
        window['send_all_balance'].update(value=config['send_all_balance'])
        if config['custom_gas_price']:
            window['custom_gas_price'].update(value=True)
            window['gas_price'].update(value=config['gas_price'])

    def check_info_layout(self, values):
        warning_text = sg.Text('Check all entered data!!!', text_color='red',
                               font=('Helvetica', 12))

        if values['test_mode']:
            test_mode_text = sg.Text(f'You are currently in test mode\n',
                                     font=('Helvetica', 12), text_color='yellow')
        else:
            test_mode_text = sg.Text(f'You are currently in real mode\n',
                                     font=('Helvetica', 12), text_color='red')

        addr_text = values['address_to_send'] if values['send_to_one_address'] else 'Wallet to bridge: auto or to the same wallet'
        address_to_send_text = sg.Text(addr_text,
                                       font=('Helvetica', 12))

        source_chain_text = sg.Text(f'Source chain: {values["source_chain"]}',
                                    font=('Helvetica', 12))
        target_chain_text = sg.Text(f'Target chain: {values["target_chain"]}',
                                    font=('Helvetica', 12),)
        bridge_option_text = sg.Text(f'Bridge option: {values["bridge_option"]}',
                                        font=('Helvetica', 12))
        slippage_text = sg.Text(f'Slippage: {values["slippage"]}%',
                                font=('Helvetica', 12))
        gas_limit_text = sg.Text(f'Gas limit: {values["gas_limit"]}',
                                 font=('Helvetica', 12))
        gas_price_text = sg.Text(f'Gas price: {values["gas_price"]}',
                                 font=('Helvetica', 12))
        src_coin_to_transfer_text = sg.Text(f'Coin to transfer: {values["source_coin_to_transfer"]}',
                                        font=('Helvetica', 12))
        target_coin_to_transfer_text = sg.Text(f'Coin to transfer: {values["target_coin_to_transfer"]}',
                                       font=('Helvetica', 12))
        send_all_balance_text = sg.Text(f'Send all balance: {values["send_all_balance"]}',
                                        font=('Helvetica', 12))
        min_delay_seconds_text = sg.Text(f'Min delay seconds: {values["min_delay_seconds"]}',
                                            font=('Helvetica', 12))
        max_delay_seconds_text = sg.Text(f'Max delay seconds: {values["max_delay_seconds"]}',
                                            font=('Helvetica', 12))
        min_bridge_amount_text = sg.Text(f'Amount to transfer min: {values["min_bridge_amount"]}',
                                         font=('Helvetica', 12))
        max_bridge_amount_text = sg.Text(f'Amount to transfer max: {values["max_bridge_amount"]}',
                                         font=('Helvetica', 12))

        agree_checkbox = sg.Checkbox('All data correct', key='agree_checkbox')
        bridge_button = sg.Button('Bridge', size=(10, 1), key='bridge_button')
        back_button = sg.Button('Back', size=(10, 1), key='back_button')
        watermark = sg.Text('https://github.com/frankmurrey (tg @shnubjack)', font=('Helvetica', 9), text_color='white')

        layout = [
            [warning_text],
            [test_mode_text],
            [address_to_send_text],
            [source_chain_text],
            [target_chain_text],
            [bridge_option_text],
            [slippage_text],
            [gas_limit_text],
            [gas_price_text],
            [src_coin_to_transfer_text],
            [target_coin_to_transfer_text],
            [min_bridge_amount_text],
            [max_bridge_amount_text],
            [send_all_balance_text],
            [min_delay_seconds_text],
            [max_delay_seconds_text],
            [agree_checkbox],
            [back_button, bridge_button],
            [watermark]

        ]

        return layout

    def bridge_layout(self):
        field_size = (20, 1)

        evm_wallets_text = sg.Text(f'Evm wallets loaded: {len(read_evm_wallets_from_file())}',
                                   text_color='yellow',
                                   font=('Helvetica', 12),
                                   key='evm_wallets_text')

        apt_addresses_text = sg.Text(f'Aptos addresses loaded: {len(read_aptos_wallets_from_file())}',
                                     text_color='orange',
                                     font=('Helvetica', 12),
                                     key='apt_addresses_text')

        source_chain_text = sg.Text('Source chain:')
        source_chain_combo = sg.Combo(self.source_chain_options_stargate,
                                      size=field_size,
                                      key='source_chain',
                                      enable_events=True)

        target_chain_text = sg.Text('Target chain:', pad=((106, 0), (0, 0)))
        target_chain_combo = sg.Combo(self.target_chain_options_stargate,
                                      size=field_size,
                                      key='target_chain',
                                      enable_events=True)

        slippage_text = sg.Text('Slippage (%):')
        slippage_input = sg.InputText(size=field_size,
                                      default_text=0.5,
                                      key='slippage')

        bridge_option_text = sg.Text('Bridge:')
        bridge_option_combo = sg.Combo(self.bridge_options,
                                       size=field_size,
                                       default_value='Stargate',
                                       key='bridge_option',
                                       enable_events=True)

        gas_limit_text = sg.Text('Gas limit:')
        gas_limit_input = sg.InputText(size=field_size,
                                       default_text=3000000,
                                       key='gas_limit')

        gas_price_text = sg.Text('Gas price (gwei):',
                                 pad=((88, 0), (0, 0)))
        gas_price_checkbox = sg.Checkbox('Use custom gas price',
                                         key='custom_gas_price',
                                         enable_events=True)

        gas_price_input = sg.InputText(size=field_size,
                                       disabled=True,
                                       default_text="Auto",
                                       text_color='grey',
                                       key='gas_price')

        source_coin_to_transfer_text = sg.Text('Coin to transfer:')
        source_coin_to_transfer_combo = sg.Combo(self.coin_options_stargate,
                                                 size=field_size,
                                                 default_value='USDC',
                                                 key='source_coin_to_transfer',
                                                 enable_events=True)

        target_coin_to_transfer_text = sg.Text('Coin to receive:',
                                               pad=((94, 0), (0, 0)))
        target_coin_to_transfer_combo = sg.Combo(self.coin_options_stargate,
                                                 size=field_size,
                                                 default_value='USDC',
                                                 key='target_coin_to_transfer',
                                                 enable_events=True)

        send_all_balance_checkbox = sg.Checkbox('Send all balance',
                                                key='send_all_balance',
                                                enable_events=True)

        min_bridge_amount_text = sg.Text('Min amount to bridge:')
        min_bridge_amount_input = sg.InputText(size=field_size,
                                               key='min_bridge_amount')

        max_bridge_amount_text = sg.Text('Max amount to bridge:',
                                         pad=((18, 0), (0, 0)))
        max_bridge_amount_input = sg.InputText(size=field_size,
                                               key='max_bridge_amount')

        address_to_send_checkbox = sg.Checkbox('Send to one address',
                                               key='send_to_one_address',
                                               enable_events=True,
                                               pad=((2, 0), (0, 0)))
        address_to_send_text = sg.Text('Address to send (evm or aptos):', pad=((4, 0), (0, 0)))
        address_to_send_input = sg.InputText(size=(65, 1),
                                             key='address_to_send',
                                             disabled=True)

        min_delay_text = sg.Text('Min delay (sec):')
        min_delay_input = sg.InputText(size=field_size,
                                       default_text=0,
                                       key='min_delay_seconds')

        max_delay_text = sg.Text('Max delay (sec):', pad=((51, 0), (0, 0)))
        max_delay_input = sg.InputText(size=field_size,
                                       default_text=0,
                                       key='max_delay_seconds',)

        test_mode_checkbox = sg.Checkbox('Test mode', key='test_mode')
        next_button = sg.Button('Next', size=(10, 1), key='next_button')
        load_wallets_button = sg.Button('Load wallets', size=(10, 1), key='load_wallets_button')
        save_cfg_button = sg.Button('Save config', size=(10, 1), key='save_cfg_button')
        load_cfg_button = sg.Button('Load config', size=(10, 1), key='load_cfg_button')
        watermark = sg.Text('https://github.com/frankmurrey (tg @shnubjack)', font=('Helvetica', 9), text_color='white')

        layout = [
            [evm_wallets_text, apt_addresses_text],
            [sg.Text('')],
            [source_chain_text, target_chain_text],
            [source_chain_combo, sg.Text("→"), target_chain_combo],
            [source_coin_to_transfer_text, target_coin_to_transfer_text],
            [source_coin_to_transfer_combo, sg.Text("→"), target_coin_to_transfer_combo],
            [bridge_option_text],
            [bridge_option_combo],
            [sg.Text('')],
            [address_to_send_text],
            [address_to_send_input],
            [address_to_send_checkbox],
            [sg.Text('')],
            [min_bridge_amount_text, max_bridge_amount_text],
            [min_bridge_amount_input, max_bridge_amount_input, send_all_balance_checkbox],
            [slippage_text],
            [slippage_input],
            [sg.Text('')],
            [gas_limit_text, gas_price_text],
            [gas_limit_input, gas_price_input, gas_price_checkbox],
            [min_delay_text, max_delay_text],
            [min_delay_input, max_delay_input],
            [sg.Text('')],
            [test_mode_checkbox],
            [next_button, load_wallets_button, save_cfg_button, load_cfg_button],
            [watermark]
        ]

        return layout

    def gas_price_option(self, values, window):
        include_option = values['custom_gas_price']
        gas_price_input = window['gas_price']

        if include_option:
            gas_price_input.update(disabled=False, value='', text_color='black')
        else:
            gas_price_input.update(disabled=True, value="Auto", text_color='grey')

    def send_all_balance_option(self, values, window):
        include_option = values['send_all_balance']
        min_bridge_input = window['min_bridge_amount']
        max_bridge_input = window['max_bridge_amount']

        if include_option:
            min_bridge_input.update(disabled=True, value='', text_color='grey')
            max_bridge_input.update(disabled=True, value='', text_color='grey')
        else:
            min_bridge_input.update(disabled=False, value='', text_color='black')
            max_bridge_input.update(disabled=False, value='', text_color='black')

    def send_to_one_address_option(self, values, window):
        include_option = values['send_to_one_address']
        address_input = window['address_to_send']

        if include_option:
            address_input.update(disabled=False, value='', text_color='black')
        else:
            address_input.update(disabled=True, value='', text_color='grey')

    def load_wallets_option(self, window):
        evm_wallets = window['evm_wallets_text']
        apt_wallets = window['apt_addresses_text']

        evm_wallets.update(f"Evm wallets loaded: {len(read_evm_wallets_from_file())}")
        apt_wallets.update(f"Aptos addresses loaded: {len(read_aptos_wallets_from_file())}")
        window.read()

    def update_chains_combo(self, values, window):
        source_chain_value = values['source_chain']
        target_chain_combo = window['target_chain']
        bridge_option = values['bridge_option']

        if bridge_option == 'Stargate':
            target_chains = self.target_chain_options_stargate
            target_chains.remove(source_chain_value)
            target_chain_combo.update(values=target_chains)
            window.read()

        elif bridge_option == 'CoreDao':
            target_chains = self.target_chain_options_core_dao
            target_chains.remove(source_chain_value)
            target_chain_combo.update(values=target_chains)
            window.read()

    def bridge_option(self, values, window):
        bridge_name = values['bridge_option']
        source_chain_combo = window['source_chain']
        target_chain_combo = window['target_chain']
        src_coin_to_transfer_combo = window['source_coin_to_transfer']
        target_coin_to_transfer_combo = window['target_coin_to_transfer']

        if bridge_name == 'Stargate':
            source_chain_combo.update(values=self.source_chain_options_stargate)
            target_chain_combo.update(values=self.target_chain_options_stargate)
            src_coin_to_transfer_combo.update(values=self.coin_options_stargate)
            target_coin_to_transfer_combo.update(values=self.coin_options_stargate)
            window.read()

        elif bridge_name == 'Aptos':
            source_chain_combo.update(values=self.source_chain_options_aptos)
            target_chain_combo.update(values=self.target_chain_options_aptos)
            src_coin_to_transfer_combo.update(values=self.coin_options_aptos)
            target_coin_to_transfer_combo.update(values=self.coin_options_aptos)
            window.read()

        elif bridge_name == 'CoreDao':
            source_chain_combo.update(values=self.source_chain_options_core_dao)
            target_chain_combo.update(values=self.target_chain_options_core_dao)
            src_coin_to_transfer_combo.update(values=self.coin_options_core_dao)
            target_coin_to_transfer_combo.update(values=self.coin_options_core_dao)
            window.read()

    def run_initial_window(self):
        bridge_layout = self.bridge_layout()
        window = sg.Window('Layer Zero Manual', bridge_layout, size=(600, 700))

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == 'Cancel':
                break

            elif event == 'source_chain':
                self.update_chains_combo(values, window)

            elif event == 'load_wallets_button':
                self.load_wallets_option(window)

            elif event == 'bridge_option':
                self.bridge_option(values, window)

            elif event == 'custom_gas_price':
                self.gas_price_option(values, window)

            elif event == 'send_to_one_address':
                self.send_to_one_address_option(values, window)

            elif event == 'send_all_balance':
                self.send_all_balance_option(values, window)

            elif event == 'save_cfg_button':
                bridge_manager = BridgeManager(get_config_from_dict(config_dict=values))
                error_message = bridge_manager.check_if_route_eligible()
                if error_message is not True:
                    sg.popup(error_message, title='Error', text_color='red')
                    continue

                save_config(values)
                sg.popup('Config saved', title='Success', text_color='blue')

            elif event == 'load_cfg_button':
                self.load_data_from_config(window)

            elif event == 'next_button':
                config_dict = get_config_from_dict(config_dict=values)
                bridge_manager = BridgeManager(config_dict)
                error_message = bridge_manager.check_if_route_eligible()

                if bridge_manager.check_if_route_eligible() is not True:
                    sg.popup(error_message, title='Error', text_color='yellow')
                    continue

                if len(read_evm_wallets_from_file()) == 0:
                    sg.popup('No wallets loaded', title='Error', text_color='red')
                    continue

                self.bridge_data = values
                window.close()
                window = sg.Window('Check data', self.check_info_layout(values), size=(600, 700))

            elif event == 'back_button':
                window.close()
                window = sg.Window('Layer0 bridger', self.bridge_layout(), size=(600, 700))

            elif event == 'bridge_button':
                if not values['agree_checkbox']:
                    sg.popup('Please check the checkbox to confirm all data is correct', title='Error', text_color='red')
                    continue
                config = get_config_from_dict(config_dict=self.bridge_data)
                window.close()

                run_bridge(config_data=config)
