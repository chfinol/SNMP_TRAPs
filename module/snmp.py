from pysnmp.entity.rfc3413.oneliner import cmdgen

class SNMP:
    
    def __init__(self, host, ifindex = False, namePort = False, community = None) -> None:
        self._host = host
        self._ifindex = ifindex
        self._namePort = namePort
        self._SYSNAME = '1.3.6.1.2.1.1.5.0'
        self._PORTDESCRIPTION = '1.3.6.1.2.1.31.1.1.1.18'
        self._NAME = '1.3.6.1.2.1.31.1.1.1.1'
        self._COMMUNITY = community
        
    def getValue(self, ifIndex = ''):
        response = ''
        if self._ifindex == True and self._namePort == False:
            oid = f'{self._PORTDESCRIPTION}{ifIndex}'
        elif self._ifindex == False and self._namePort == False:
            oid = self._SYSNAME
        if self._ifindex == True and self._namePort == True:
            oid = f'{self._NAME}{ifIndex}'
        auth = cmdgen.CommunityData(self._COMMUNITY)
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            auth,
            cmdgen.UdpTransportTarget((self._host, 161)),
            cmdgen.MibVariable(oid),
            lookupMib=False,
        )
        for oid, val in varBinds:
            response = val.prettyPrint()
        return response
    def getOspf3Neighbor(self,oid):
        response = ''
        auth = cmdgen.CommunityData(self._COMMUNITY)
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            auth,
            cmdgen.UdpTransportTarget((self._host, 161)),
            cmdgen.MibVariable(str(oid)),
            lookupMib=False,
        )
        for oid, val in varBinds:
            response = val.prettyPrint()
        return response
