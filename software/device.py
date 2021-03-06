import os

class Device:

    VENDORID  = 0x1fc9
    PRODUCTID = 0x1337
    INSIZE    = 64
    OUTSIZE   = 64

    def __init__(self):
        self.fake = os.getenv('EDUBRM') == 'fake'
        if not self.fake:
            import usb
            usbdev = usb.core.find(idVendor = self.VENDORID, idProduct = self.PRODUCTID)
            if usbdev == None:
                raise Exception('EduBRM device not found')
            try:
                usbdev.detach_kernel_driver(0)
            except:
                pass
            usbdev.set_configuration()
            cfg = usbdev.get_active_configuration()
            interface_number = cfg[(0,0)].bInterfaceNumber
            alternate_setting = usb.control.get_interface(usbdev, interface_number)
            intf = usb.util.find_descriptor(cfg, bInterfaceNumber = interface_number, bAlternateSetting = alternate_setting)
            self.epo = usb.util.find_descriptor(intf,
                           custom_match = lambda e: \
                               usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
            self.epi = usb.util.find_descriptor(intf,
                           custom_match = lambda e: \
                               usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        else:
            print 'device init'
        self.pwm(1, 1)
        self.pwm(2, 1)
        self.pwm(1, 0)
        self.pwm(2, 0)
#        self.ddswave(0) # not implemented
        self.ddsfreq(0)
        self.opamp(1, 0, 0)
        self.opamp(2, 0, 0)
        self.switches(0)
        self.setpins(0)
        self.setout(1, 0)
        self.setout(2, 0)
        self.setout(3, 0)

    # sets pwm (which=1,2), (duty=16bit)
    def pwm(self, which, duty):
        if duty < 0:
            duty = 0
        if duty > 65535:
            duty = 65535
        if self.fake:
            print 'pwm', which, duty
        else:
            if duty != 0:
                duty = 65536 - duty
            self.epo.write('p' + chr(which) + chr(duty & 0xff) + chr(duty >> 8))

    # sets ddswave (wave=square,sine,saw1,saw2)
    def ddswave(self, wavetype):
        if self.fake:
            print 'dds wave', wavetype
        else:
            self.epo.write('d' + chr(wavetype))

    # sets ddsfreq (freq=32bit)
    def ddsfreq(self, freq):
        if self.fake:
            print 'dds freq', freq
        else:
            self.epo.write('D' + chr(freq & 0xff) + chr((freq >> 8) & 0xff) + chr((freq >> 16) & 0xff) + chr(freq >> 24))

    # set opamp (which=1,2), (chan=0..5), (gain=0..7)
    def opamp(self, which, chan, gain):
        if self.fake:
            print 'opamp', which, chan, gain
        else:
            self.epo.write('m' + chr(which) + chr(chan) + chr(gain))

    # set all switches (states=6bit)
    def switches(self, states):
        if self.fake:
            print 'switches', states
        else:
            self.epo.write('s' + chr(states))

    # set pins state (states=3bit) (1 = input, 0 = output)
    def setpins(self, states):
        if self.fake:
            print 'setpins', states
        else:
            self.epo.write('P' + chr(states))

    # set output (which=1,2,3), (state=0,1)
    def setout(self, which, state):
        if self.fake:
            print 'setout', which, state
        else:
            self.epo.write('o' + chr((which<<1) + state))

    # 7x AD (16 bits) + 3 x I
    def read(self):
        if self.fake:
            from random import randint
            from time import time
            from math import sin
            return (randint(0,1023),                                                    # AD0
                    int(sin(6.2832*time())*511+512), randint(0,1023), randint(0,1023),  # AD1 .. AD3
                    randint(0,1023), randint(0,1023), int(sin(314.16*time())*511+512),  # AD4 .. AD6
                    randint(0,1), randint(0,1), randint(0,1))                           # IO1 .. IO3
        else:
            i = self.epi.read(self.INSIZE)
            return (i[0] + (i[1]<<8),                                          # AD0
                    i[2] + (i[3]<<8), i[4] + (i[5]<<8), i[6] + (i[7]<<8),      # AD1 .. AD3
                    i[9] + (i[9]<<8), i[10] + (i[11]<<8), i[12] + (i[13]<<8),  # AD4 .. AD6
                    i[14] & 0x01, (i[14] & 0x02) >> 1, (i[14] & 0x04) >> 2)    # IO1 .. IO3
