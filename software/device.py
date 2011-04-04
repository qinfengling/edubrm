import usb

class Device:

    VENDORID  = 0x1fc9
    PRODUCTID = 0x0003
    INSIZE    = 64
    OUTSIZE   = 2

    def __init__(self):
        usbdev = usb.core.find(idVendor = self.VENDORID, idProduct = self.PRODUCTID)
        if usbdev == None:
            raise Exception('EduBRM device not found')
        usbdev.set_configuration()
        self.epo = usb.util.find_descriptor(usbdev.get_interface_altsetting(),
                       custom_match = lambda e: \
                           usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        self.epi = usb.util.find_descriptor(usbdev.get_interface_altsetting(),
                       custom_match = lambda e: \
                           usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)

# TODO: VERSION ?
# TODO: PWM
# TODO: SPI
# TODO: SETPINS
# TODO: CLEARPINS

    def state(self):
        # TODO: format?
        return self.epi.read(self.INSIZE)
