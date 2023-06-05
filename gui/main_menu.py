import PySimpleGUI as sg

from gui.autobridge import LayerZeroAutoBridgeGui
from gui.manual import LayerZeroManualGui
from gui.stg_stake import StargateStgStakeGui
from gui.liquidity import StargateLiquidityGui


def choose_menu_layout():
    main_text = sg.Text('Select mode', text_color='white', font=('Helvetica', 15), pad=(120, 0))

    manual_bridger_button = sg.Button('Manual Bridger', size=(20, 1), key='manual_button', font=('Helvetica', 12),
                                      pad=(90, 0))
    auto_bridger_button = sg.Button('Auto Bridger', size=(20, 1), key='auto_button', font=('Helvetica', 12),
                                    pad=(90, 0))
    stake_stg_button = sg.Button('STG staker', size=(20, 1), key='stake_stg_button', font=('Helvetica', 12),
                                 pad=(90, 0))
    add_liquidity_button = sg.Button('Liquidity adder', size=(20, 1), key='add_liquidity_button', font=('Helvetica', 12),
                                     pad=(90, 0))

    watermark_text = sg.Text('https://github.com/frankmurrey (tg @shnubjack)', text_color='white',
                             font=('Helvetica', 8), pad=(60, 0))
    layout = [
        [main_text],
        [watermark_text],
        [sg.Text('')],
        [manual_bridger_button],
        [sg.Text('')],
        [auto_bridger_button],
        [sg.Text('')],
        [stake_stg_button],
        [sg.Text('')],
        [add_liquidity_button],
    ]

    return layout


def run_main_menu():
    layout = choose_menu_layout()
    window = sg.Window('Layer Zero Auto', layout, size=(400, 300))

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

        if event == 'manual_button':
            window.close()
            LayerZeroManualGui().run_initial_window()

        elif event == 'auto_button':
            window.close()
            LayerZeroAutoBridgeGui().run_initial_window()

        elif event == 'stake_stg_button':
            window.close()
            StargateStgStakeGui().run_stake_window()

        elif event == 'add_liquidity_button':
            window.close()
            StargateLiquidityGui().run_liquidity_window()