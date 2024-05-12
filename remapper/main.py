import usb.core
import usb.util
import usb.control

VENDOR_ID = 0x0f0d
PRODUCT_ID = 0x013a

hori: usb.core.Device = usb.core.find(idVendor = VENDOR_ID, idProduct = PRODUCT_ID)

def is_even(value: float | int) -> bool:
  """Returns true if the input value is an even number, false otherwise."""
  return value/2 == value//2

def str_to_hex_command(input: str) -> list[int]:
  """ Converts a string of hex numbers to a list of integer values. The
  characters of the string are converted in pairs (so the string must have an
  event number of characters), and are converted to hex (so valid characters are
  0-9, A-F).
  """
  if not is_even(len(input)):
    raise Exception("Bad length on input string (must be multiple of 2)")
  
  return [
    int(input[i:i+2], 16) for i in range(0, len(input), 2)
  ]

def build_read_key_command(page: int, profile: int) -> list[int]:
  """
  Constructs a command line used in the `data` field of a SET_REPORT
  request.
  """
  # ALL commands seem to start with this. I don't know if it has any special meaning. Would be nice to know about the chipset in the device.
  cmdline = "01a5"

  cmdline += "5115aee"

  # TODO: use something more elegant than just replacing the 0x prefix.
  cmdline += hex(0x10 + profile).replace("0x", "")

  cmdline += hex(page).replace("0x", "")

  return cmdline

print("Getting page 1 of profile 3 should be: %s" % build_read_key_command(1, 3))

def read_key_configuration(page: int, profile: int = 0):
  """ Reads back the current key configuration of the device. By default, reads
  from the first profile (0) out of 8 (so, max 7). Each page contains 16 keys.
  Indexing starts from key 0 which is the physical "Esc" key on the pad!
  
  To get the config for the key labeled "3" you need to request page 0 and look
  at the fourth returned element.

  To get the config for the key labeled "17", request page 1 and look at the
  second item (index 1).
  """
  pass

OPEN_READ = str_to_hex_command("01a5105aef10000000000000000000000000000000000000000000000000000000")
GOTO_PAGE_1 = str_to_hex_command("01a5115aee10000000000000000000000000000000000000000000000000000000")
CLOSE_READ = str_to_hex_command("01a5125aed10000000000000000000000000000000000000000000000000000000")

reattach_list = []

for i in [0, 1]:
  if hori.is_kernel_driver_active(i):
    reattach_list.append(i)
    hori.detach_kernel_driver(i)

# Set "read" mode.
hori.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, OPEN_READ)
# Tell the device to flip to read page 1. For *reading*, the device returns X keys (when writing, at most 4 can be sent, it seems)
result1 = hori.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, GOTO_PAGE_1)
# Request a report. This should yield the key setup for the first 1½ lines keys from the physical keypad.
result2 = hori.ctrl_transfer(0xa1, 0x01, 0x0101, 0x01, 65)
# Close the read again. Not sure if this is necessary.
hori.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, CLOSE_READ)

usb.util.dispose_resources(hori)

for i in reattach_list:
  hori.attach_kernel_driver(i)

print("done")