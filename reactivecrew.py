import os
import json
import keyboard
import math
import websockets
import asyncio
import math
from threading import Event, Thread

class ReactiveCrew:
    def __init__(self):
        self.initialize_events()
        self.initialize_vars(False)

    def initialize_events(self):
        self.hotkey_event = Event()
        self.thread_started = Event()
        self.restarting_event = Event()
        self.html_created_event = Event()
        # Set the refresh button hotkey

    def initialize_vars(self, resetting):
        self.max_row, self.max_column = 0, 0
        if resetting:
            self.last_main_icon = self.selected_icon
        else:
            self.started = False

        self.selected_icon = 0
        
        self.crew_names, self.crew_links, self.crew_indexes, self.crew_style_files, self.crew_hotkeys = [], [], [], [], []
        f = open("./HTML/reactivecrew.html", "w")
        f.write(self.write_main_html())
        f.close()
        self.html_created_event.set()

    # Sets the hotkeys
    def set_keyboard(self):

        # For some reason, another function is required for the lambda.
        # Would otherwise cause all the hotkeys to be set to the last function.
        print('setting keyboard')
        def set_hotkey(i):
            if len(self.crew_hotkeys) > i:
                hotkey = str(self.crew_hotkeys[i])
                position = int(self.crew_indexes[i])
                keyboard.add_hotkey(hotkey,  lambda : self.switch_view(hotkey, position))
    
        for i in range(len(self.crew_indexes)):
            set_hotkey(i)
            
        keyboard.add_hotkey(self.refresh_hotkey,  lambda : self.restart())

      
    # Sets the server thread to run forever
    async def server_loop(self):
        async with websockets.serve(self.handler, "", 8001):
            await asyncio.Future()  # run forever

    # Sets the class data and crew list data
    def write_main_html(self):
        crew_data_file = open(os.path.join(os.curdir, 'settings.json'))
        crew_data = json.load(crew_data_file)

        self.max_row = int(crew_data['max_row'])
        self.max_column = int(crew_data['max_column'])
        self.main_img_width = int(crew_data['main_img_width'])
        self.main_img_height = int(crew_data['main_img_height'])
        self.img_width = int(crew_data['img_width'])
        self.img_height = int(crew_data['img_height'])
        self.name_size = int(crew_data['name_size'])
        crew_index = -1
        self.scale = 0.5
        self.name_offset = self.img_height * (self.scale / 2)
        self.main_name_size = int(crew_data['main_text_size'])
        self.refresh_hotkey = crew_data['refresh_hotkey']

        for crew in crew_data['crew_list']:
            crew_index += 1
            if crew['active'] == 'true':
                self.crew_indexes.append(crew_index)
                self.crew_names.append(crew['name'])
                self.crew_links.append(crew['img_src'])
                self.crew_style_files.append(crew['css_file'])
                if crew['hotkey'] != '':
                    self.crew_hotkeys.append(crew['hotkey'])

        crew_data_file.close()

        # print('Crew initialized!')
        # print('!!!')
        # print('Current Crew: ' + ',\n'.join(self.crew_names))
        plate_height = int(crew_data['img_height']) + int(crew_data['name_size'])

        # Get height of the combined icons to see if the main image needs to be placed lower
        self.combined_icon_height = math.ceil((len(self.crew_indexes) - 1) / self.max_column) * plate_height

        self.main_img_top = 0
        if (self.main_img_height < self.combined_icon_height):
            self.main_img_top = self.combined_icon_height - self.main_img_height

        if self.main_img_top == 0:
            self.main_img_top += self.main_img_height * (self.scale / 2)

        print('img_top: ' + str(self.main_img_top))
        # First icon styling
        main_plate_height = str(int(crew_data['main_img_height']) + int(crew_data['main_name_size']))

        main_iframe_styling = 'max-height:'+ crew_data['main_img_height'] + 'px;max-width:' + crew_data['main_img_width'] + 'px;'

        main_plate_style = 'width:' + crew_data['main_img_width'] + 'px;height:' + main_plate_height + 'px;'
        main_plate_style += 'position:relative;top:' + str(self.main_img_top) +';text-align:bottom;font-size:' + crew_data['main_text_size'] + ';'
        # main_plate_style += 'position:relative;text-align:bottom;font-size:' + crew_data['main_text_size'] + ';'

        # Other icon styling
        plate_style = 'width:' + crew_data['img_width'] + 'px;height:' + str(plate_height) + 'px;'
        plate_style += 'position:fixed;text-align:center;font-size:' + crew_data['crew_text_size'] + ';'

        page_styling = '<style>.main-plate{' + main_plate_style + '} .main-plate .icon {' + main_iframe_styling + '}'
        page_styling += '.crew-plate .icon {max-height:'+ crew_data['img_height'] + 'px;max-width:' + crew_data['img_width'] + 'px;}'
        page_styling += '.crew-plate{' + plate_style + '} .row-end { clear:left; }</style>'

        link_HTML = '<script type="text/javascript" src="./js/reactivecrew.js"></script>'
        link_HTML += '<link rel="icon" type="image/x-icon" href="./images/favicon.ico">'
        link_HTML += '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.1/jquery.min.js"></script>'
        link_HTML += '<link rel="stylesheet" href="./css/reactivecrew.css">'

        # Add CSS Files collected from the ones associated with the crew here
        link_HTML += self.write_styling_html()

        html = '<HTML><head>' + link_HTML + page_styling + '</head>'
        html += '<body><div id="big-div" class="fade-div">' + self.write_crew_html() + '</div></body></HTML>'
        return html

    def write_styling_html(self):

        styling_links = ''

        for i in range(0, len(self.crew_indexes)):
            
            styling_link = ''
            # If the crew doesn't have a custom style sheet
            if self.crew_style_files[i] == "":

                # Check to see if they have a file named after them
                if os.path.exists('./HTML/CrewCSS/' + self.crew_names[i] + '.css'):
                    css_file = open('./HTML/CrewCSS/' + self.crew_names[i] + '.css', 'r')

                    # Link the file if it contains data
                    if css_file.read() != '':
                        styling_links += '<link rel="stylesheet" href="./CrewCSS/' + self.crew_names[i] + '.css">'

                # Otherwise, create a blank one for later
                else:
                    css_file = open('./HTML/CrewCSS/' + self.crew_names[i] + '.css', 'w')
                    css_file.write('')

            # Otherwise, link a custom style sheet if it exists
            if os.path.exists('./css/' + self.crew_style_files[i] + '.css'):
                styling_links += '<link rel="stylesheet" href="./css/' + self.crew_style_files[i] + '.css">'

        return styling_links

    def write_crew_html(self):

        row, column = 0, 0
        crew_html = self.generate_crew_plate(0, True, column, row)

        for i in range(1, len(self.crew_indexes)):
            if row < self.max_row:
                if not column < self.max_column:
                    column, row = 0, row + 1

                crew_html += self.generate_crew_plate(i, False, column, row)
                column += 1

        return crew_html

    # Generates HTML for each of the active crew
    def generate_crew_plate(self, i, is_main, column, row):
        crew_html = ''
        num_rows = math.floor((len(self.crew_indexes) - 2) / self.max_column)
        imagePosAmt = 0
        if num_rows > 0:

            imagePosAmt = int(self.img_height + self.name_size)

        else:
            imagePosAmt =  int(self.main_img_top) + (int(self.main_name_size) / 2) + int(self.name_size)
            num_rows = 1
        

        # Check to see if there is a file associated with the crew's name
        if os.path.exists('./HTML/CrewHTML/' + self.crew_names[i] + '.html'):
            crew_markup_file = open('./HTML/CrewHTML/' + self.crew_names[i] + '.html', 'r')
            crew_markup = crew_markup_file.read()
            crew_markup_file.close()

        # Otherwise, create a new file to potentially personalize later
        else:
            crew_markup_file = open('./HTML/CrewHTML/' + self.crew_names[i] + '.html', 'w')
            crew_markup = self.crew_names[i]
            crew_markup_file.write(crew_markup)

        # If generating the main crew image
        if is_main:
            crew_html += '<div id="crew-' + str(self.crew_indexes[i]) + '" class="main-plate">'
            crew_html += '<iframe class="icon" src="' + str(self.crew_links[i]) + '"></iframe>'
            crew_html += '<div class="name-div" style="position:relative;">'

        # Or generate a regular crew image in the grid
        else:
            crew_html += '<div id="crew-' + str(self.crew_indexes[i]) + '" class="crew-plate"'
            crew_html += 'style="left:' + str(int(self.main_img_width + (self.img_width * column)))
            crew_html += ';top:' + str(imagePosAmt * (num_rows - row)) + ';">'
            crew_html += '<iframe class="icon" src="' + str(self.crew_links[i]) + '"></iframe>'
            crew_html += '<div class="name-div">'

        crew_html += crew_markup + '</div></div>'
        return crew_html
        
    #
    def switch_view(self, hotkey, crew_position):
        print('last main in switchView: ' + str(self.last_main_icon))
        print('new main in switchView: ' + str(self.selected_icon))
        print('crew_position: ' + str(crew_position))
        # if the selection is on an active crew member, change the main image plate to the new crew member's
        if self.crew_indexes.count(crew_position) > 0:
            self.last_main_icon = self.selected_icon
            self.selected_icon = crew_position
            self.hotkey_event.set()

    def restart(self):
        print('restarting')
        self.initialize_vars(True)
        keyboard.unhook_all_hotkeys()
        self.set_keyboard()
        self.restarting_event.set()
        self.hotkey_event.set()

    async def send_restart_message(self, websocket):
        print('restarting...')
        event_params = {'type': 'refresh'}
        await websocket.send(json.dumps(event_params))
        # await self.send_message(websocket)

    async def send_message(self, websocket):

        event_params = {
            'type': 'switch',
            'indexes': str(self.crew_indexes),
            'oldMainIndex': str(self.last_main_icon),
            'newMainIndex': str(self.selected_icon),
            'mainIconWidth': str(self.main_img_width),
            'img_width': str(self.img_width),
            'img_height': str(self.img_height),
            'max_column': str(self.max_column),
            'mainIconTop': str(self.main_img_top),
            'mainNameSize': str(self.main_name_size),
            'nameSize': str(self.name_size),
            'name_offset': str(self.name_offset)
        }
        await websocket.send(json.dumps(event_params))

    def start_new_handler(self, websocket):
        asyncio.run(self.handler(websocket, ''))

    async def handler(self, websocket, path):

        while True:
            if not self.started:
                print('starting!!!')
                self.last_main_icon = len(self.crew_indexes) - 1
                self.selected_icon = self.crew_indexes[0]
                self.started = True
                await self.send_message(websocket)
            else:
                print('last main: ' + str(self.last_main_icon))
                print('new main: ' + str(self.selected_icon))
                print('---------')
                # print('waiting for hotkey')
                self.hotkey_event.clear()
                self.hotkey_event.wait()
                # print('hotkey pressed')
                if not self.restarting_event.is_set():
                    # print('switching')
                    await self.send_message(websocket)
                else:
                    self.restarting_event.clear()
                    self.html_created_event.wait()
                    self.html_created_event.clear()
                    # await self.send_message(websocket)
                    await self.send_restart_message(websocket)
                    print('restarted!')

            await websocket.recv()

    def start_server(self):
        asyncio.run(self.server_loop())

if __name__ == "__main__":
    server = ReactiveCrew()
    server_thread = Thread(target=server.start_server, args=())
    server_thread.start()
    server.set_keyboard() 
    keyboard.wait() # blocks forever



    