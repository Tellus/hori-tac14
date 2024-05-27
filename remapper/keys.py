from constants import GAMEPAD_CODES, USB_SCANCODES

reversed_usb_scancodes = dict(zip(USB_SCANCODES.values(), USB_SCANCODES.keys()))
reversed_gamepad_codes = dict(zip(GAMEPAD_CODES.values(), GAMEPAD_CODES.keys()))

def get_byte_for_keyname(name: str) -> bytes:
  return reversed_usb_scancodes[name]

def get_byte_for_gamepad_button(name: str) -> bytes:
  return reversed_gamepad_codes[name]

def get_name_for_scancode(scancode: int) -> str:
  """
  Given a USB scancode, returns the string representation of the key.
  """
  return USB_SCANCODES[scancode]

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

    return GAMEPAD_CODES[bytes[0]]
  
  translated = [get_name_for_scancode(keycode) for keycode in bytes[:-1] if keycode != 0]

  return translated[0] if len(translated) == 1 else translated