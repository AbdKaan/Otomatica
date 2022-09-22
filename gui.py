import threading
import sched, time
import socket
from subprocess import Popen, PIPE

from kivy.config import Config
Config.set('graphics', 'width', '650')
Config.set('graphics', 'height', '620')
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from modbus_server import ModbusServer
from modbus_client import ModbusClient

class ConnectionScreen(GridLayout):

    def __init__(self, **kwargs):
        super(ConnectionScreen, self).__init__(**kwargs)

        self.modbus_server = None
        self.thread_modbus_clients = []

        # Create scheduler to keep showing current time with some intervals
        self.scheduler = sched.scheduler(time.time, time.sleep)

        self.rows = 12
        self.cols = 3

        self.add_widget(Label(text='Server', size_hint_y=None, height=70))
        self.add_widget(Label(text='Client', size_hint_y=None, height=70))
        self.add_widget(Label(text='SNMP', size_hint_y=None, height=70))

        self.add_widget(Label(text='Address', size_hint_y=None, height=50))
        self.add_widget(Label(text='Address', size_hint_y=None, height=50))
        self.add_widget(Label(text='Mode (test/snmp)', size_hint_y=None, height=50))

        self.server_address = TextInput(multiline=False, size_hint_y=None, height=50)        
        self.add_widget(self.server_address)
        self.client_address = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.client_address)
        self.mode = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.mode)

        ###########################

        self.add_widget(Label(text='Port', size_hint_y=None, height=50))
        self.add_widget(Label(text='Port', size_hint_y=None, height=50))
        self.add_widget(Label(text='Port', size_hint_y=None, height=50))

        self.server_port = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.server_port)
        self.client_port = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.client_port)
        self.snmp_port = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.snmp_port)

        ###########################

        self.add_widget(Label(text='Inputs', size_hint_y=None, height=50))
        self.add_widget(Label(text='Register Number', size_hint_y=None, height=50))
        self.add_widget(Label(text='Community Data', size_hint_y=None, height=50))

        self.read_input = Button(text='Read Input', size_hint_y=None, height=50)
        self.add_widget(self.read_input)
        #self.read_input.bind(on_release=self.read)
        self.register_number = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.register_number)
        self.community_data = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.community_data)

        ############################

        self.add_widget(Label(text='', size_hint_y=None, height=50))
        self.add_widget(Label(text='Register Count', size_hint_y=None, height=50))
        self.add_widget(Label(text='UDP Transport Target Address', size_hint_y=None, height=50))

        self.input = Label(size_hint_y=None, height=50)
        self.add_widget(self.input)
        self.register_count = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.register_count)
        self.udp_address = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.udp_address)

        #############################

        self.add_widget(Label(text='', size_hint_y=None, height=50))
        self.add_widget(Label(text='Slave Number', size_hint_y=None, height=50))
        self.add_widget(Label(text='Object Identity Address', size_hint_y=None, height=50))

        self.empty = Label(size_hint_y=None, height=50)
        self.add_widget(self.empty)
        self.slave_number = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.slave_number)
        self.object_identity_address = TextInput(multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.object_identity_address)

        #############################

        self.button_create_server = Button(text="Create Server", size_hint_y=None, height=50)
        self.add_widget(self.button_create_server)
        self.button_create_server.bind(on_press=self.create_server)
        self.button_connect = Button(text="Add Client", size_hint_y=None, height=50)
        self.button_connect.bind(on_press=self.add_client)
        self.add_widget(self.button_connect)
        self.button_exit = Button(text="Exit", size_hint_y=None, height=50)
        self.button_exit.bind(on_release=self.exit)
        self.add_widget(self.button_exit)

        ###### For test
        self.server_address.text = "127.0.0.1"
        self.client_address.text = "127.0.0.1"
        self.server_port.text = "505"
        self.client_port.text = "505"
        self.snmp_port.text = "161"
        self.register_number.text = "200"
        self.slave_number.text = "1"
        self.community_data.text = "public"
        #self.udp_address.text = "192.168.253.190"
        self.udp_address.text = "127.0.0.1"
        self.object_identity_address.text = ".1.3.6.1.2.1.1.3.0"

    def create_server(self, widget):
        #Create the modbus master/server for clients to connect to.
        self.modbus_server = threading.Thread(target=ModbusServer, daemon=True,
                                                            args=(self.server_address.text,
                                                            int(self.server_port.text)))
        self.modbus_server.start()
        widget.text = "Server Created"
        widget.disabled = True
        print('Server is running.')

    '''
    def stop_server(self, widget):
        self.modbus_server = threading.Thread(target=ModbusServer, daemon=True,
                                                            args=(self.server_address.text,
                                                            int(self.server_port.text)))
        self.modbus_server.start()
        print('Server is running.')
    '''

    def add_client(self, widget):
        thread = threading.Thread(target=self.create_instance, args=(), daemon=True)
        thread.start()

    def exit(self, widget):
        return MainApp().stop()
    '''
    def read(self, widget, scheduler):
        # Read first line of the data.txt file
        with open('data.txt') as f:
            try:
                lines = f.readlines()
                self.input.text = lines[0]
            except:
                pass

        # Read again every 2 seconds
        scheduler.enter(2, 1, self.read, ())
    '''
    def create_instance(self):
        modbus_client = ModbusClient(self.server_address.text,
                                            int(self.client_port.text),
                                            int(self.register_number.text),
                                            int(self.register_count.text),
                                            int(self.slave_number.text))

        modbus_client = threading.Thread(target=ModbusClient.get_input, daemon=True, 
                                                                                args=(modbus_client,
                                                                                self.scheduler, 
                                                                                int(self.register_number.text),
                                                                                int(self.register_count.text),
                                                                                1, 
                                                                                self.community_data.text, 
                                                                                self.udp_address.text, 
                                                                                self.object_identity_address.text, 
                                                                                self.mode.text))

        self.thread_modbus_clients.append(modbus_client)
        
        modbus_client.start()
        '''
        scheduler = sched.scheduler(time.time, time.sleep)
        thread_reader = threading.Thread(target=self.read, daemon=True, args=[self.read_input, scheduler])
        thread_reader.start()
        '''

class MainApp(App):
    def build(self):
        return ConnectionScreen()

if __name__ == '__main__':
    MainApp().run()