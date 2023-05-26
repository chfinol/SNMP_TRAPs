from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pyasn1.codec.ber import decoder
from pysnmp.proto import api

from Polish import Polish


class Received:
    
    def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
        msgVer = int(api.decodeMessageVersion(wholeMsg))
        if msgVer in api.protoModules:
            pMod = api.protoModules[msgVer]
        else:
            print('Unsupported SNMP version %s' % msgVer)
            return
        reqMsg, wholeMsg = decoder.decode(
            wholeMsg, asn1Spec=pMod.Message(),
            )    
        device = transportAddress[0]
        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        if reqPDU.isSameTypeWith(pMod.TrapPDU()):
            if not (msgVer == api.protoVersion1):
                varBinds = pMod.apiPDU.getVarBinds(reqPDU)
                for oid, val in varBinds:
                    Polish.cleanUP(oid, val, device)
                
    def run():
        transportDispatcher = AsynsockDispatcher()
        transportDispatcher.registerRecvCbFun(Received.cbFun)
        transportDispatcher.registerTransport(
            udp.domainName, udp.UdpSocketTransport().openServerMode(('0.0.0.0', 162))
        )
        transportDispatcher.jobStarted(1)
        try:
            transportDispatcher.runDispatcher()
        except:
            transportDispatcher.closeDispatcher()
            raise

Received.run() 