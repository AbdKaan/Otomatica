from pysnmp.hlapi import *

iterator = getCmd(
    SnmpEngine(),
    CommunityData('public'),
    UdpTransportTarget(('192.168.253.190', 161)),
    ContextData(),
    ObjectType(ObjectIdentity('1.3.6.1.4.1.674.10892.5.2.5.0'))
)

errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

if errorIndication:
    print(errorIndication)

elif errorStatus:
    print('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

else:
    for varBind in varBinds:
        print(' = '.join([x.prettyPrint() for x in varBind]))