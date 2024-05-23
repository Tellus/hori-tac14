import argparse
import raw
import horidevice
import keys

import constants

def print_devices(args) -> None:
  devices = raw.get_devices()

  if type(devices) is raw.Device:
    print(f'Found {hex(devices.idVendor)}:{hex(devices.idProduct)}')
  elif devices is None:
    print('Could not find any valid devices!')
  else:
    print('Unknown or unsupported return value from get_devices()')
    print(devices)

def print_profile_func(args) -> None:
  print(f'Getting profile {args.profile}')

  device = horidevice.HoriDevice()

  print("KEYBOARD ONLY")
  all_keys = device.get_configuration(0, constants.KEYBOARD_ONLY_MODE)

  # Filter away zero values or unknown value types.
  # all_keys = [i for i in all_keys if i[0] != 0 and i[1] == 0 and i[2] == 0]
  # print(all_keys['keys'])
  print('Normal keys:')
  print(str(all_keys['keys']))
  print('Normal thumbstick keys:')
  print(all_keys['thumbstick_keys'].as_name_dict())
  # print([keys.get_key_for_bytes(k) for k in all_keys['thumbstick_keys']])
  print('Alternate keys:')
  print(str(all_keys['alt_keys']))
  print('Alternate thumbstick keys:')
  # print([keys.get_key_for_bytes(k) for k in all_keys['alt_thumbstick_keys']])

  print("ANALOG")
  all_keys = device.get_configuration(0, constants.ANALOG_MODE)

  # Filter away zero values or unknown value types.
  # all_keys = [i for i in all_keys if i[0] != 0 and i[1] == 0 and i[2] == 0]
  print('Normal keys:')
  print(str(all_keys['keys']))
  print('Alternate keys:')
  print(str(all_keys['alt_keys']))

parser = argparse.ArgumentParser(
  prog='Hori14Remapper',
)

subparsers = parser.add_subparsers(title='Commands')

list_devices_parser = subparsers.add_parser('list-devices')
list_devices_parser.set_defaults(func=print_devices)

get_profile_parser = subparsers.add_parser('get-profile')
get_profile_parser.add_argument('profile')
get_profile_parser.set_defaults(func=print_profile_func)

args = parser.parse_args()

if 'func' in args:
  args.func(args)