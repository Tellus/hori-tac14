def is_even(value: float | int) -> bool:
  """Returns true if the input value is an even number, false otherwise."""
  return value/2 == value//2

def pad(input: str, to_length: int = 64) -> str:
  return input.ljust(len(input) - to_length, '0')

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
