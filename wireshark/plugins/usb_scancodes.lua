-- Source: https://www.win.tue.nl/~aeb/linux/kbd/scancodes-14.html
scancodes = { "NoEventError", -- "ErrorRollOverError",
  "POSTFailError",
  "ErrorUndefinedError",
  "A",
  "B",
  "C",
  "D",
  "E",
  "F",
  "G",
  "H",
  "I",
  "J",
  "K",
  "L",
  "M",
  "N",
  "O",
  "P",
  "Q",
  "R",
  "S",
  "T",
  "U",
  "V",
  "W",
  "X",
  "Y",
  "Z",
  "1",
  "2",
  "3",
  "4",
  "5",
  "6",
  "7",
  "8",
  "9",
  "0",
  "Enter",
  "Escape",
  "Backspace",
  "Tab",
  "Space",
  "-/_",
  "=/+",
  "[/{",
  "]/}",
  "\\/|",
  "...",
  ";/:",
  "'/\"",
  "`/~",
  ",/<",
  "./>",
  "//?",
  "Caps Lock",
  "F1",
  "F2",
  "F3",
  "F4",
  "F5",
  "F6",
  "F7",
  "F8",
  "F9",
  "F10",
  "F11",
  "F12",
  "Print Screen",
  "Scroll Lock",
  "Pause",
  "Insert",
  "Home",
  "PageUp",
  "Delete",
  "End",
  "PageDown",
  "Right",
  "Left",
  "Down",
  "Up",
  "Num Lock",
  "Keypad /",
  "Keypad *",
  "Keypad -",
  "Keypad +",
  "Keypad Enter",
  "Keypad 1 / End",
  "Keypad 2 / Down",
  "Keypad 3 / PageDown",
  "Keypad 4 / Left",
  "Keypad 5",
  "Keypad 6 / Right",
  "Keypad 7 / Home",
  "Keypad 8 / Up",
  "Keypad 9 / PageUp",
  "Keypad 0 / Insert",
  "Keypad . / Delete",
  "...",
  "Application", -- literally says "Applic" in document.
  "Power",
  "Keypad =",
  "F13",
  "F14",
  "F15",
  "F16",
  "F17",
  "F18",
  "F19",
  "F20",
  "F21",
  "F22",
  "F23",
  "F24",
  "Execute",
  "Help",
  "Menu",
  "Select",
  "Stop",
  "Again",
  "Undo",
  "Cut",
  "Copy",
  "Paste",
  "Find",
  "Mute",
  "VolumeUp",
  "VolumeDown",
  "Locking Caps Lock",
  "Locking Num Lock",
  "Locking Scroll Lock",
  "Keypad ,",
  "Keypad =",
  "International", -- literally "Internat" in source document.
  "International", -- literally "Internat" in source document.
  "International", -- literally "Internat" in source document.
  "International", -- literally "Internat" in source document.
  "International", -- literally "Internat" in source document.
  "International", -- literally "Internat" in source document.
  "International", -- literally "Internat" in source document.
  "International", -- literally "Internat" in source document.
  "International", -- literally "Internat" in source document.
  "LANG",
  "LANG",
  "LANG",
  "LANG",
  "LANG",
  "LANG",
  "LANG",
  "LANG",
  "LANG",
  "Alt Erase",
  "SysRequest", -- SysRq
  "Cancel",
  "Clear",
  "Prior",
  "Return",
  "Separ",
  "Out",
  "Oper",
  "Clear / Again",
  "CrSel / Props",
  "ExSel",
  "<BLANK>",
  "<BLANK>",
  "<BLANK?>",
  "",
}

scancodes[224] = "LeftControl"
scancodes[225] = "LeftShift"
scancodes[226] = "LeftAlt"
scancodes[227] = "LGUI"
scancodes[228] = "RightControl"
scancodes[229] = "RightShift"
scancodes[230] = "RightAlt"
scancodes[231] = "RGUI"
