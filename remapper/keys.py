import yaml

# https://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-the-currently-running-scrip
import os
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

scancodes = []
modifiers = []
gamepad = []

with open(os.path.join(__location__, 'scancodes.yml')) as input_stream:
  parsed = yaml.safe_load(input_stream)
  scancodes = parsed['normal']
  modifiers = parsed['modifiers']
  gamepad = parsed['gamepad']

def get_name_for_scancode(scancode: int) -> str:
  """
  Given a USB scancode, returns the string representation of the key.
  """
  if scancode < 224:
    return scancodes[scancode]
  else:
    return modifiers[scancode - 224]
  
def get_key_for_bytes(bytes: list[int]) -> str | list[str]:
  """
  Given a sequence of four integers (bytes), returns the human-readable name of
  the corresponding key.
  Currently:
  - First byte set, rest is zero: single keyboard key
  - First two or three bytes set, last is zero: keyboard key with modifier(s)
  - First byte is non-zero, last byte is FF: gamepad key
  - First byte is 38, last byte is FF: Function key (... why?)
  TODO: other sequences?
  """
  if len(bytes) != 4:
    raise ValueError('Input sequence must be exactly length 4')
  
  if bytes[-1] == 0xFF:
    if bytes[0] == 38:
      return 'Fn'

    return gamepad[bytes[0]]
  
  translated = [get_name_for_scancode(keycode) for keycode in bytes[:-1] if keycode != 0]

  return translated[0] if len(translated) == 1 else translated