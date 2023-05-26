import netaddr

from module.IPv6Formatter import IPv6
from module.logger_base import log
from module.snmp import SNMP
import time



class Polish: 
    cacheBGP = {}
    countBGP = 0 
    _ifindex = ''
    _ifNameChassis = ''
    _ifStatus = ''
    cacheBGPv6 = {}
    countBGPv6 = 0
    
    @classmethod
    def cleanUP(cls, oids, val, device):
        print(oids, val)
        oid = str(oids)
        val = str(val)
        try:
            if oid.find('1.3.6.1.2.1.2.2.1.1') != -1 :
                cls._ifindex = val
            elif oid.find('1.3.6.1.4.1.2636.3.1.8.1.6') != -1:
                cls._ifNameChassis = val
            elif oid.find('1.3.6.1.6.3.1.1.4.1') != -1:
                cls._ifStatus = val
            elif oid.find('1.3.6.1.2.1.2.2.1.8') != -1:
                log.debug(f'oids: [{oids}] \t value: {val} \t device: {device}')
                cls.operationalPort(val,device)
            elif oid.find('1.3.6.1.4.1.2011.5.25.177.1.1.2.1.5.') != -1:
                cls.huaBGPM2(oid,val,device)
            elif oid.find('1.3.6.1.2.1.14.10.1.6.') != -1:
                log.debug(f'oids: [{oids}] \t value: {val} \t device: {device}')
                cls.ospfFormat(oid,val,device)
            elif oid.find('1.3.6.1.2.1.15.3.1.2.') != -1:
                cls.bgp4Format(oid,val,device)
            elif oid.find('1.3.6.1.4.1.2636.3.1.13.1.6.') != -1:
                cls.chassis(device)    
            elif oid.find('1.3.6.1.4.1.2636.5.1.1.2.1.1.1.2.0.2') != -1 and len(oid) >= 110:
                cls.bgp6Format(oid,val,device)
            elif oid.find('1.3.6.1.2.1.191.1.9.1.8.') != -1:
                cls.ospf3Format(oid,val,device) 
        except Exception as e:
            log.error(e)



    @classmethod
    def operationalPort(cls, val, device):
        state = 'UP' if (val == '1') else 'DOWN'
        if device != '100.64.253.61':
            snmp1 = SNMP(device)
            hostname = snmp1.getValue()
            snmp2 = SNMP(device, True)
            descriptionPort = snmp2.getValue(f'.{cls._ifindex}')
            snmp3 = SNMP(device, True, True)
            namePort = snmp3.getValue(f'.{cls._ifindex}')
        else:
            snmp1 = SNMP(device, False, False, 'NOCMBOATKSOL')
            hostname = snmp1.getValue()
            snmp2 = SNMP(device, True, False, 'NOCMBOATKSOL')
            descriptionPort = snmp2.getValue(f'.{cls._ifindex}')
            snmp3 = SNMP(device, True, True, 'NOCMBOATKSOL')
            namePort = snmp3.getValue(f'.{cls._ifindex}')
        if not ('.' in namePort):
            if namePort.find('a') != -1:
                print(f'IP: {device}\nHostname: {hostname}\nPortChannel: {namePort}\nDescripcion: {descriptionPort}\nEstado: {state}')
            else:
                print(f'IP: {device}\nHostname: {hostname}\nPuerto: {namePort}\nDescripcion: {descriptionPort}\nEstado: {state}')
            
    @classmethod 
    def ospfFormat(cls, oid, val, device):
        snmp1 = SNMP(device)
        hostname = snmp1.getValue()
        state = ''
        if str(val) != '8':
            state = 'DOWN'
        else:
            state = 'UP'
        protocol = 'OSPF'
        vecino = str(oid).replace('1.3.6.1.2.1.14.10.1.6.', '')
        indice = str(vecino).rindex('.')
        vecino = vecino[:indice]
        print(f'IP: {device}\nHostname: {hostname}\nSesion OSPF {state}\nNeighbor: {vecino}')
        
    @classmethod
    def bgp4Format(cls,oid,val,device):
            neighbor = str(oid).replace('1.3.6.1.2.1.15.3.1.2.','')
            if str(val) != '6':
                status = 'DOWN'
            else:
                status = 'UP'
            snmp1 = SNMP(device)
            hostname = snmp1.getValue()
            if status != Polish.cacheBGP.get(f'{neighbor}'):
                print(f'Equipo: {device}\nHostname: {hostname}\nSesion BGP {status}\nNeighbor: {neighbor}')
                Polish.cacheBGP.update({neighbor: status})
            if status == 'UP':
                Polish.countBGP += 1
                if Polish.countBGP >= 3:
                    Polish.cacheBGP.pop(f'{neighbor}')
    
    @classmethod
    def chassis(cls, device):
        status = ''
        if(cls._ifStatus.find('1.3.6.1.4.1.2636.4.2.1') != -1):
            status = 'UP'
        else:
            status = 'DOWN'
        snmp1 = SNMP(device)
        hostname = snmp1.getValue()
        print(f'IP: {device}\nHostname: {hostname}\nFuente: {cls._ifNameChassis}\nStatus: {status}')        
        


    @classmethod
    def bgp6Format(cls,oid,val,device):
        status = ''
        host = str(device)
        snmp = SNMP(device)
        hostname = snmp.getValue()
        indice = str(oid).replace('1.3.6.1.4.1.2636.5.1.1.2.1.1.1.2.0.2.','')
        oidConsulta = f'1.3.6.1.4.1.2636.5.1.1.2.1.1.1.11.0.2.{indice}'
        neighborAddr = snmp.getOspf3Neighbor(oidConsulta)
        neighbor = str(neighborAddr).split('x')[-1]
        ipNeighbor = IPv6(neighbor)
        nbrAddr = ipNeighbor.format_ipv6_address()
        if type(int(val)) == type(0):
            if int(val) != 6:
                status = 'DOWN'
            else:
                status = 'UP'
        if Polish.cacheBGPv6.get(f'{indice}') != status:
            print(f'IP:{device}\nHostname: {hostname}\nSesion BGP {status}\nNeighbor: {nbrAddr}\n')
            Polish.cacheBGPv6.update({indice:status})
        if status == 'UP':
            Polish.cacheBGPv6.pop(f'{indice}')
            
    @classmethod
    def ospf3Format(cls,oid,val,device):
        state = ''
        if str(val) != '8':
            state = 'DOWN'
            time.sleep(11)
        else:
            state = 'UP'
        
        indice = str(oid).replace('1.3.6.1.2.1.191.1.9.1.8','')
        neighborOid = f'1.3.6.1.2.1.191.1.9.1.5{indice}'
        host = str(device)
        snmp = SNMP(device)
        hostname = snmp.getValue()
        asking_for_neighbor = snmp.getOspf3Neighbor(neighborOid)
        neighbor = str(asking_for_neighbor).split('x')[-1]
        ipNeighbor = IPv6(neighbor)
        ipmsj = ipNeighbor.format_ipv6_address()

        if type(neighbor) == str and neighbor != '':
            print(f'IP: {device}\nHostname: {hostname}\nSesion OSPF {state}\nNeighbor: {ipmsj}')
            
    @classmethod
    def huaBGPM2(cls,oid,val,device):
        status = ''
        host = str(device)
        snmp = SNMP(device)
        hostname =  snmp.getValue()
        indice = str(oid).replace('1.3.6.1.4.1.2011.5.25.177.1.1.2.1.5.', '')
        oidConsulta = f'1.3.6.1.4.1.2011.5.25.177.1.1.2.1.4.{indice}'
        neighborAddr = snmp.getOspf3Neighbor(oidConsulta)
        if str(val) != '6':
            status = 'DOWN'
        else:
            status = 'UP'
        if Polish.cacheBGPv6.get(f'{indice}') != status:
            print(f'IP:{device}\nHostname: {hostname}\nSesion BGP {status}\nNeighbor: {neighborAddr}\n')
            Polish.cacheBGPv6.update({indice:status})
        if status == 'UP':
            Polish.cacheBGPv6.pop(f'{indice}')
            