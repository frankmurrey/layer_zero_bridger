import PySimpleGUI as sg

from gui.gui_autobridge import LayerZeroAutoBridgeGui
from gui.gui_manual import LayerZeroManualGui


def choose_menu_layout():
    main_text = sg.Text('Select bridger mode', text_color='white', font=('Helvetica', 15), pad=(100, 0))

    manual_bridger_button = sg.Button('Manual Bridger', size=(20, 1), key='manual_button', font=('Helvetica', 12),
                                      pad=(90, 0))
    auto_bridger_button = sg.Button('Auto Bridger', size=(20, 1), key='auto_button', font=('Helvetica', 12),
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
    ]

    return layout


def run_main_menu():
    layout = choose_menu_layout()
    window = sg.Window('Layer Zero Auto', layout, size=(400, 200))

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break

        if event == 'manual_button':
            window.close()
            LayerZeroManualGui().run_initial_window()

        if event == 'auto_button':
            window.close()
            LayerZeroAutoBridgeGui().run_initial_window()
