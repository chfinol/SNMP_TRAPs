class IPv6:
    def __init__(self, address):
        self._address = address
    @property
    def address(self):
        return self._address
    @address.setter
    def address(self, address):
        self._address = address

    def format_ipv6_address(self):
        index = -1
        formatted_address = ':'.join([self._address[i:i+4] for i in range(0, len(self._address), 4)])
        formatted_address = formatted_address.split(':')

        for hextect in formatted_address:
            index += 1
            if hextect == '0000':
                hextect = '0'
                formatted_address[index] = hextect
            if hextect == '0':
                hextect = ':'
                formatted_address[index] = hextect
            
        formatted_address = ':'.join(formatted_address).replace('::::::::','::').replace(':::::::','::').replace('::::::','::').replace(':::::','::').replace('::::','::').replace(':::','::')
        return formatted_address