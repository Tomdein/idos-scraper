import PySimpleGUI as sg

import station_hint

search_text_size = (4, 1)
layout = [[sg.Text("From:", size=search_text_size), sg.In(size=(25, 1), enable_events=True, key="-FROM-")], [sg.Text("To:", search_text_size), sg.In(size=(25, 1), enable_events=True, key="-TO-")], [sg.Multiline(size=(50,10), key='-HINT-', autoscroll=False)], [sg.Button("OK")]]

# Create the window
window = sg.Window("Timetable", layout)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

    elif event == "-FROM-":
        hints = station_hint.GetHints(values["-FROM-"])
        
        window['-HINT-'].update("")
        for hint in hints:
            window['-HINT-'].print(hint)

    elif event == "-TO-":
        hints = station_hint.GetHints(values["-TO-"])

        window['-HINT-'].update("")
        for hint in hints:
            window['-HINT-'].print(hint)
            # or window['-HINT-'].update(hint + '\n', append=True)

window.close()