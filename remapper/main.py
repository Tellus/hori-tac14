import usb.core
import usb.util
import usb.control

from lib.constants import VENDOR_ID, PRODUCT_ID
from lib.util import str_to_hex_command, build_read_key_command, pad

hori: usb.core.Device = usb.core.find(idVendor = VENDOR_ID, idProduct = PRODUCT_ID)

print('Getting page 1 of profile 3 should be: %s' % build_read_key_command(1, 3))

# OPEN_READ = str_to_hex_command(pad('01a5105aef1000'))
# GOTO_PAGE_1 = str_to_hex_command(pad('01a5115aee1000'))
# CLOSE_READ = str_to_hex_command(pad('01a5125aed1000'))

OPEN_READ = bytearray.fromhex('01a5105aef1000')
GOTO_PAGE_1 = bytearray.fromhex('01a5115aee1000')
CLOSE_READ = bytearray.fromhex('01a5125aed1000')

reattach_list = []

for i in [0, 1]:
  if hori.is_kernel_driver_active(i):
    reattach_list.append(i)
    hori.detach_kernel_driver(i)

# Neither "open" or "close" read mode seems necessary. Their purpose must be something else?

# Set 'read' mode.
hori.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, OPEN_READ)
# Tell the device to flip to read page 1. For *reading*, the device returns X keys (when writing, at most 4 can be sent, it seems)
result1 = hori.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, GOTO_PAGE_1)
# Request a report. This should yield the key setup for the first 1½ lines keys from the physical keypad.
result2 = hori.ctrl_transfer(0xa1, 0x01, 0x0101, 0x01, 65)
# Close the read again. Not sure if this is necessary.
hori.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, CLOSE_READ)

print(result2)

usb.util.dispose_resources(hori)

for i in reattach_list:
  hori.attach_kernel_driver(i)

print('done')