import sys
import sched, time
from datetime import datetime
from xmlrpc.client import ProtocolError
from pymodbus.client.sync import ModbusTcpClient
from pysnmp.hlapi import *

class ModbusClient():
    def __init__(self, server_ip, port, register_number, register_count, slave_number):
        self.server_ip = server_ip
        self.port = port
        self.register_number = register_number
        self.register_count = register_count
        self.slave_number = slave_number
        self.client = self.create_client()

    def create_client(self):
        # Create client server
        client = ModbusTcpClient(self.server_ip, self.port)

        # Check if client is connected
        print(f'\nConnection = {str(client.connect())}\n')

        return client

    def get_input(self, scheduler, register_number, count, slave_number, community_data,
                                                                        udp_transport_target_address,
                                                                        object_identity_address,
                                                                        mode):
        if(mode == "test"):
            # Get current time and write to registers
            now = datetime.now()
            self.client.write_register(register_number, now.hour)
            self.client.write_register(register_number+1, now.minute)
            self.client.write_register(register_number+2, now.second)

            # Reads 'count' amount of registers starting from the register number from the given slave unit
            result = self.client.read_holding_registers(address=register_number, count=count, unit=slave_number)

            #with open('data.txt', 'w') as f:
            #    f.write(str(result.registers))

            print(result.registers)

            # Start a scheduler for reading input every second
            scheduler.enter(1, 1, self.get_input, (scheduler, register_number, count,
                                                                        slave_number,
                                                                        community_data,
                                                                        udp_transport_target_address,
                                                                        object_identity_address,
                                                                        mode))

        elif(mode == "snmp"):
            # SNMP Configuration
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(community_data),
                UdpTransportTarget((udp_transport_target_address, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(object_identity_address))
            )
            # Check for errors and get data if no errors
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

            if errorIndication:
                print(errorIndication)

            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

            else:
                for varBind in varBinds:
                    data = varBind[1]
            
            with open('data.txt', 'w') as f:
                f.write(str(data))

            # Write data to given registers
            self.client.write_register(register_number, int(str(data)[:4]))
            self.client.write_register(register_number+1, int(str(data)[4:]))

            # Reads 'count' amount of registers starting from the register number from the given slave unit
            result = self.client.read_holding_registers(address=register_number, count=count, unit=slave_number)
            print(f'{result.registers}')
            # Start a scheduler for reading input every second
            
            scheduler.enter(1, 1, self.get_input, (scheduler, register_number, count,
                                                                        slave_number,
                                                                        community_data,
                                                                        udp_transport_target_address,
                                                                        object_identity_address,
                                                                        mode))
                                                                        
        scheduler.run()

        #self.client.close()