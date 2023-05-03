import time
from bridge_swap.eth_bridge import eth_mass_transfer
from bridge_swap.token_bridge import token_mass_transfer, token_mass_approve
from bridge_swap.bridge_to_aptos import eth_mass_transfer_to_aptos, token_mass_transfer_to_aptos
from bridge_swap.bridge_to_aptos import token_mass_approve_to_aptos

from src.files_manager import load_config, save_config
from src.files_manager import read_evm_wallets_from_file, read_aptos_wallets_from_file
from src.bridge_manager import BridgeManager
from src.config import get_config_from_dict

from loguru import logger

import PySimpleGUI as sg


class LayerZeroGui:
    def __init__(self):
        self.source_chain_options = ['Arbitrum', 'Optimism', 'Polygon', 'Ethereum', 'BSC', 'Fantom', 'Avalanche']
        self.target_chain_options = ['Arbitrum', 'Optimism', 'Polygon', 'Ethereum', 'BSC', 'Fantom', 'Avalanche', 'Aptos']
        self.coin_options = ['Ethereum', 'USDC', 'USDT']

        self.bridge_data = None

    def update_chain_options(self, window, values):
        chosen_chain = values['source_chain']
        update_target_chain_options = self.target_chain_options.copy()
        try:
            update_target_chain_options.remove(chosen_chain)
        except ValueError:
            pass
        window['target_chain'].update(values=update_target_chain_options)

    def load_data_from_config(self, window):
        config = load_config()
        if not config:
            sg.popup('No config found', title='Error', text_color='red')
            return

        window['source_chain'].update(value=config['source_chain'])
        window['target_chain'].update(value=config['target_chain'])
        window['slippage'].update(value=config['slippage'])
        window['gas_limit'].update(value=config['gas_limit'])
        window['coin_to_transfer'].update(value=config['coin_to_transfer'])
        window['min_bridge_amount'].update(value=config['min_bridge_amount'])
        window['max_bridge_amount'].update(value=config['max_bridge_amount'])
        window['test_mode'].update(value=config['test_mode'])
        window['send_to_one_address'].update(value=config['send_to_one_address'])
        window['address_to_send'].update(value=config['address_to_send'])
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
        slippage_text = sg.Text(f'Slippage: {values["slippage"]}%',
                                font=('Helvetica', 12))
        gas_limit_text = sg.Text(f'Gas limit: {values["gas_limit"]}',
                                 font=('Helvetica', 12))
        gas_price_text = sg.Text(f'Gas price: {values["gas_price"]}',
                                 font=('Helvetica', 12))
        coin_to_transfer_text = sg.Text(f'Coin to transfer: {values["coin_to_transfer"]}',
                                        font=('Helvetica', 12))
        min_bridge_amount_text = sg.Text(f'Amount to transfer min: {values["min_bridge_amount"]}',
                                         font=('Helvetica', 12))
        max_bridge_amount_text = sg.Text(f'Amount to transfer max: {values["max_bridge_amount"]}',
                                         font=('Helvetica', 12))

        agree_checkbox = sg.Checkbox('All data correct', key='agree_checkbox')
        bridge_button = sg.Button('Bridge', size=(10, 1), key='bridge_button')
        back_button = sg.Button('Back', size=(10, 1), key='back_button')

        layout = [
            [warning_text],
            [test_mode_text],
            [address_to_send_text],
            [source_chain_text],
            [target_chain_text],
            [slippage_text],
            [gas_limit_text],
            [gas_price_text],
            [coin_to_transfer_text],
            [min_bridge_amount_text],
            [max_bridge_amount_text],
            [agree_checkbox],
            [back_button, bridge_button]
        ]

        return layout

    def bridge_layout(self):
        field_size = (20, 1)

        evm_wallets_text = sg.Text(f'Evm wallets loaded: {len(read_evm_wallets_from_file())}',
                                   text_color='yellow',
                                   font=('Helvetica', 12))

        apt_wallets_text = sg.Text(f'Aptos wallets loaded: {len(read_aptos_wallets_from_file())}',
                                   text_color='orange',
                                   font=('Helvetica', 12))

        source_chain_text = sg.Text('Source chain:')
        source_chain_combo = sg.Combo(self.source_chain_options,
                                      size=field_size,
                                      key='source_chain',
                                      enable_events=True)

        arrow_text = sg.Text('->')

        target_chain_text = sg.Text('Target chain:', pad=((110, 0), (0, 0)))
        target_chain_combo = sg.Combo(self.target_chain_options,
                                      size=field_size,
                                      key='target_chain',
                                      enable_events=True)

        slippage_text = sg.Text('Slippage (%):')
        slippage_input = sg.InputText(size=field_size,
                                      default_text=0.5,
                                      key='slippage')

        gas_limit_text = sg.Text('Gas limit:')
        gas_limit_input = sg.InputText(size=field_size,
                                       default_text=3000000,
                                       key='gas_limit')

        gas_price_text = sg.Text('Gas price:',
                                 pad=((88, 0), (0, 0)))
        gas_price_checkbox = sg.Checkbox('Use custom gas price',
                                         key='custom_gas_price',
                                         enable_events=True)

        gas_price_input = sg.InputText(size=field_size,
                                       disabled=True,
                                       default_text="Auto",
                                       text_color='grey',
                                       key='gas_price')

        coin_to_transfer_text = sg.Text('Coin to transfer:')
        coin_to_transfer_combo = sg.Combo(self.coin_options,
                                          size=field_size,
                                          default_value='USDC',
                                          key='coin_to_transfer',
                                          enable_events=True)

        min_bridge_amount_text = sg.Text('Min amount to bridge:',
                                         pad=((65, 0), (0, 0)))
        min_bridge_amount_input = sg.InputText(size=field_size,
                                               key='min_bridge_amount')

        max_bridge_amount_text = sg.Text('Max amount to bridge:',
                                         pad=((29, 0), (0, 0)))
        max_bridge_amount_input = sg.InputText(size=field_size,
                                               key='max_bridge_amount',
                                               pad=((10, 0), (0, 0)))

        address_to_send_checkbox = sg.Checkbox('Send to one address',
                                               key='send_to_one_address',
                                               enable_events=True,
                                               pad=((2, 0), (0, 0)))
        address_to_send_text = sg.Text('Address to send (evm or aptos):', pad=((4, 0), (0, 0)))
        address_to_send_input = sg.InputText(size=(65, 1),
                                             key='address_to_send',
                                             disabled=True)

        test_mode_checkbox = sg.Checkbox('Test mode', key='test_mode')
        next_button = sg.Button('Next', size=(10, 1), key='next_button')
        cancel_button = sg.Button('Cancel', size=(10, 1), key='cancel_button')
        save_cfg_button = sg.Button('Save config', size=(10, 1), key='save_cfg_button')
        load_cfg_button = sg.Button('Load config', size=(10, 1), key='load_cfg_button')

        layout = [[evm_wallets_text, apt_wallets_text],
                  [sg.Text('')],
                  [source_chain_text, target_chain_text],
                  [source_chain_combo, arrow_text, target_chain_combo],
                  [sg.Text('')],
                  [address_to_send_text],
                  [address_to_send_input],
                  [address_to_send_checkbox],
                  [sg.Text('')],
                  [coin_to_transfer_text, min_bridge_amount_text, max_bridge_amount_text],
                  [coin_to_transfer_combo, min_bridge_amount_input, max_bridge_amount_input],
                  [slippage_text],
                  [slippage_input],
                  [sg.Text('')],
                  [gas_limit_text, gas_price_text],
                  [gas_limit_input, gas_price_input, gas_price_checkbox],
                  [sg.Text('')],
                  [test_mode_checkbox],
                  [next_button, cancel_button, save_cfg_button, load_cfg_button]]

        return layout

    def gas_price_option(self, values, window):
        include_option = values['custom_gas_price']
        gas_price_input = window['gas_price']

        if include_option:
            gas_price_input.update(disabled=False, value='', text_color='black')
        else:
            gas_price_input.update(disabled=True, value="Auto", text_color='grey')

    def send_to_one_address_option(self, values, window):
        include_option = values['send_to_one_address']
        address_input = window['address_to_send']

        if include_option:
            address_input.update(disabled=False, value='', text_color='black')
        else:
            address_input.update(disabled=True, value='', text_color='grey')

    def run(self):
        bridge_layout = self.bridge_layout()
        window = sg.Window('Layer0 bridger', bridge_layout, size=(600, 600))

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == 'Cancel':
                break

            elif event == 'custom_gas_price':
                self.gas_price_option(values, window)

            elif event == 'send_to_one_address':
                self.send_to_one_address_option(values, window)

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

            elif event == 'source_chain':
                self.update_chain_options(window, values)

            elif event == 'next_button':
                bridge_manager = BridgeManager(get_config_from_dict(config_dict=values))
                error_message = bridge_manager.check_if_route_eligible()

                if bridge_manager.check_if_route_eligible() is not True:
                    sg.popup(error_message, title='Error', text_color='yellow')
                    continue

                if len(read_evm_wallets_from_file()) == 0:
                    sg.popup('No wallets loaded', title='Error', text_color='red')
                    continue

                self.bridge_data = values
                window.close()
                window = sg.Window('Check data', self.check_info_layout(values), size=(600, 600))

            elif event == 'back_button':
                window.close()
                window = sg.Window('Layer0 bridger', self.bridge_layout(), size=(600, 600))

            elif event == 'bridge_button':
                if not values['agree_checkbox']:
                    sg.popup('Please check the checkbox to confirm all data is correct', title='Error', text_color='red')
                    continue
                config = get_config_from_dict(config_dict=self.bridge_data)
                window.close()

                if config.target_chain == "Aptos":
                    if config.coin_to_transfer == "Ethereum":
                        eth_mass_transfer_to_aptos(config_data=config)
                    else:
                        token_mass_approve_to_aptos(config_data=config)
                        time.sleep(2)
                        token_mass_transfer_to_aptos(config_data=config)

                if config.target_chain != "Aptos":
                    if config.coin_to_transfer == "Ethereum":
                        eth_mass_transfer(config_data=config)
                    else:
                        token_mass_approve(config_data=config)
                        time.sleep(2)
                        token_mass_transfer(config_data=config)
