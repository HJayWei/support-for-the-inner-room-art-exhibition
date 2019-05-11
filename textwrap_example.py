# textwrap_example.py
# $Rev$
# Copyright (c) 2016 Able Systems Limited. All rights reserved.
'''This simple code example is provided as-is, and is for demonstration
purposes only. Able Systems takes no responsibility for any system
implementations based on this code.

The BasicPrint.py example prints simple text to the Pipsta's paper roll.
By default, Pipsta prints 32 characters per line. The Pipsta printer does 
not attempt to intelligently split text sent to it: it simply continues 
to print characters on the next line.

A standard Python module called 'textwrap' *can* however intelligently 
process simple text to wrap at a specified number of characters whilst
also ensuring that only whole words will be printed on a line. This
improves the readability of simple text print jobs with no coding
overhead for the user.


Copyright (c) 2016, Able Systems Ltd. All rights reserved.
'''

import argparse
import platform
import struct
import sys
import time
import os
import inspect
import textwrap
import usb.core
import usb.util


example_strings = [ 
'00000000011111111112222222222333',
'12345678901234567890123456789012',
'--------------------------------',
'                                ',
'A line shorter that 32 chars.',
'A line slightly longer than 32 chars.',
'A line that is even longer than two lines of 32 chars is also split well by textwrap.',
'The 512 character string below is also handled:',
'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam dictum leo a mauris viverra auctor. In iaculis iaculis ligula, eget imperdiet nisi vehicula vel. Sed in sodales risus. Nullam luctus nisl tempus eros feugiat, eget ornare dolor posuere. Duis interdum lorem sed lorem iaculis, sit amet convallis libero rutrum. Donec imperdiet iaculis ultricies. Curabitur hendrerit aliquam ultrices. Integer ac dui et lacus sollicitudin dapibus. Integer at nisl ut nibh suscipit eleifend. Phasellus porttitor posuere.'
                  ]

# USB specific constant definitions
PIPSTA_USB_VENDOR_ID = 0x0483
PIPSTA_USB_PRODUCT_ID = 0xA19D
AP1400_USB_PRODUCT_ID = 0xA053
AP1400V_USB_PRODUCT_ID = 0xA19C

valid_usb_ids = {PIPSTA_USB_PRODUCT_ID, AP1400_USB_PRODUCT_ID, AP1400V_USB_PRODUCT_ID}

class printer_finder(object):
    def __call__(self, device):
        if device.idVendor != PIPSTA_USB_VENDOR_ID:
            return False

        return True if device.idProduct in valid_usb_ids else False


CR = b'\x0D'
PIPSTA_LINE_CHAR_WIDTH = 32
FEED_PAST_TEAR_BAR = b'\n' * 5

def setup_usb():
    '''Connects to the 1st Pipsta found on the USB bus'''
    # Find the Pipsta's specific Vendor ID and Product ID (also known as vid
    # and pid)
    dev = usb.core.find(custom_match=printer_finder())
    if dev is None:                 # if no such device is connected...
        raise IOError('Printer not found')  # ...report error

    try:
        dev.reset()

        # Initialisation. Passing no arguments sets the configuration to the
        # currently active configuration.
        dev.set_configuration()
    except usb.core.USBError as err:
        raise IOError('Failed to configure the printer', err)

    # Get a handle to the active interface
    cfg = dev.get_active_configuration()

    interface_number = cfg[(0, 0)].bInterfaceNumber
    usb.util.claim_interface(dev, interface_number)
    alternate_setting = usb.control.get_interface(dev, interface_number)
    intf = usb.util.find_descriptor(
        cfg, bInterfaceNumber=interface_number,
        bAlternateSetting=alternate_setting)

    ep_out = usb.util.find_descriptor(
        intf,
        custom_match=lambda e:
        usb.util.endpoint_direction(e.bEndpointAddress) ==
        usb.util.ENDPOINT_OUT
    )

    if ep_out is None:  # check we have a real endpoint handle
        raise IOError('Could not find an endpoint to print to')
    
    return ep_out


def main():

	pipsta = setup_usb()
        for line in example_strings:
            print (textwrap.fill(line, PIPSTA_LINE_CHAR_WIDTH))
            pipsta.write(textwrap.fill(line, PIPSTA_LINE_CHAR_WIDTH))
            pipsta.write(CR)
        pipsta.write(FEED_PAST_TEAR_BAR)
                
if __name__ == '__main__':
    main()
