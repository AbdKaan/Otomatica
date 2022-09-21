from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

class ModbusServer():
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.store = None
        self.context = None

        self.create_server()

    def create_server(self):
        # Server parameters
        self.store = ModbusSlaveContext(zero_mode=True)
        
        # If single=True => Every unit-id returns same context
        # If single=False => Will be interpreted as collection of slaves
        self.context = ModbusServerContext(slaves=self.store, single=True)

        # Start server
        StartTcpServer(self.context, address=(self.server_ip, self.port))