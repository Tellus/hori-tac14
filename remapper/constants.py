VENDOR_ID = 0x0f0d
PRODUCT_ID = 0x013a

CMD_PREFIX = '01a5'

KEYBOARD_ONLY_MODE = 0
ANALOG_MODE = 1

# Source: https://www.win.tue.nl/~aeb/linux/kbd/scancodes-14.html
USB_SCANCODES = {
  0: "NoEventError",
  1: "ErrorRollOverError",
  2: "POSTFailError",
  3: "ErrorUndefinedError",
  4: "A",
  5: "B",
  6: "C",
  7: "D",
  8: "E",
  9: "F",
  10: "G",
  11: "H",
  12: "I",
  13: "J",
  14: "K",
  15: "L",
  16: "M",
  17: "N",
  18: "O",
  19: "P",
  20: "Q",
  21: "R",
  22: "S",
  23: "T",
  24: "U",
  25: "V",
  26: "W",
  27: "X",
  28: "Y",
  29: "Z",
  30: "1",
  31: "2",
  32: "3",
  33: "4",
  34: "5",
  35: "6",
  36: "7",
  37: "8",
  38: "9",
  39: "0",
  40: "Enter",
  41: "Escape",
  42: "Backspace",
  43: "Tab",
  44: "Space",
  45: "-/_",
  46: "=/+",
  47: "[/{",
  48: "]/}",
  49: "\\/|",
  50: "...",
  51: ";/:",
  52: "'/\"",
  53: "'/~",
  54: ",/<",
  55: "./>",
  56: "//?",
  57: "Caps Lock",
  58: "F1",
  59: "F2",
  60: "F3",
  61: "F4",
  62: "F5",
  63: "F6",
  64: "F7",
  65: "F8",
  66: "F9",
  67: "F10",
  68: "F11",
  69: "F12",
  70: "Print Screen",
  71: "Scroll Lock",
  72: "Pause",
  73: "Insert",
  74: "Home",
  75: "PageUp",
  76: "Delete",
  77: "End",
  78: "PageDown",
  79: "Right",
  80: "Left",
  81: "Down",
  82: "Up",
  83: "Num Lock",
  84: "Keypad /",
  85: "Keypad *",
  86: "Keypad -",
  87: "Keypad +",
  88: "Keypad Enter",
  89: "Keypad 1 / End",
  90: "Keypad 2 / Down",
  91: "Keypad 3 / PageDown",
  92: "Keypad 4 / Left",
  93: "Keypad 5",
  94: "Keypad 6 / Right",
  95: "Keypad 7 / Home",
  96: "Keypad 8 / Up",
  97: "Keypad 9 / PageUp",
  98: "Keypad 0 / Insert",
  99: "Keypad . / Delete",
  100: "...",
  101: "Application", # literally says "Applic" in document
  102: "Power",
  103: "Keypad =",
  104: "F13",
  105: "F14",
  106: "F15",
  107: "F16",
  108: "F17",
  109: "F18",
  110: "F19",
  111: "F20",
  112: "F21",
  113: "F22",
  114: "F23",
  115: "F24",
  116: "Execute",
  117: "Help",
  118: "Menu",
  119: "Select",
  120: "Stop",
  121: "Again",
  122: "Undo",
  123: "Cut",
  124: "Copy",
  125: "Paste",
  126: "Find",
  127: "Mute",
  128: "VolumeUp",
  129: "VolumeDown",
  130: "Locking Caps Lock",
  131: "Locking Num Lock",
  132: "Locking Scroll Lock",
  133: "Keypad ,",
  134: "Keypad =",
  135: "International", # literally "Internat" in source document
  136: "International", # literally "Internat" in source document
  137: "International", # literally "Internat" in source document
  138: "International", # literally "Internat" in source document
  139: "International", # literally "Internat" in source document
  140: "International", # literally "Internat" in source document
  141: "International", # literally "Internat" in source document
  142: "International", # literally "Internat" in source document
  143: "International", # literally "Internat" in source document
  144: "LANG",
  145: "LANG",
  146: "LANG",
  147: "LANG",
  148: "LANG",
  149: "LANG",
  150: "LANG",
  151: "LANG",
  152: "LANG",
  153: "Alt Erase",
  154: "SysRequest", # SysR in source doc
  155: "Cancel",
  156: "Clear",
  157: "Prior",
  158: "Return",
  159: "Separ",
  160: "Out",
  161: "Oper",
  162: "Clear / Again",
  163: "CrSel / Props",
  164: "ExSel",
  165: "<BLANK>",
  166: "<BLANK>",
  167: "<BLANK?>",
  168: "",

  224: "LeftControl", # So this is 224
  225: "LeftShift", # And this is 225
  226: "LeftAlt",
  227: "LGUI",
  228: "RightControl",
  229: "RightShift",
  230: "RightAlt",
  231: "RGUI",
}

GAMEPAD_CODES = {
  1: "A", # 0x01
  2: "B", # 0x02
  3: "X", # 0x03
  4: "Y", # 0x04
  5: "LeftBumper", # 0x05
  6: "RightBumper", # 0x06
  7: "LeftTrigger", # 0x07
  8: "RightTrigger", # 0x08
  9: "LSB", # 0x09
  10: "RSB", # 0x0a
  11: "DPadUp", # 0x0b
  12: "DpadDown", # 0x0c
  13: "DpadLeft", # 0x0d
  14: "DpadRight", # 0x0e
  15: "DpadUpRight", # 0x0f
  16: "DPadDownRight", # 0x10
  17: "DpadDownLeft", # 0x11
  18: "DpadUpLeft", # 0x12
  19: "LeftStickUp", # 0x13
  20: "LeftStickDown", # 0x14
  21: "LeftStickLeft", # 0x15
  22: "UNKNOWN", # 0x16
  23: "LeftStickUpRight", # 0x17
  24: "LeftStickDownRight", # 0x18
  25: "LeftStickDownLeft", # 0x19
  26: "LeftStickUpLeft", # 0x1a
  27: "RightStickUp", # 0x1b
  28: "RightStickDown", # 0x1c
  29: "RightStickLeft", # 0x1d
  30: "RightStickRight", # 0x1e
  31: "RightStickUpRight", # 0x1f
  32: "RightStickDownRight", # 0x20
  33: "RightStickDownLeft", # 0x21
  34: "RightStickUpLeft", # 0x22
  35: "Start", # 0x23
  36: "Back", # 0x24
}