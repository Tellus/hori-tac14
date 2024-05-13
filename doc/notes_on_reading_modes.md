*Throughout this file I'll be referring to profile and page numbers. Unless
otherwise specified, these are zero-indexed in the source data.*

The following is the basic structure of the configuration's data model, as seen
through the USB traffic:

Mode (A+K or K) -> Profile -> Page

These are all set using the last four bytes of the "command string" (the first
14 bytes of the SET_REPORT data fragment).

`MP GG`, where:

- `M` is `0` for keyboard-only and `1` for A+K
- `P` is the profile number, starting with `0` and ending at `7`
- `GG` is the page, starting from `00` and running up to `07` on reads (over
`0x1e` = 30 on writes??)

The following 8 pages of configurations are read back by the vanilla GUI
whenever you start the program, switch modes, profiles, or toggle the `Fn+`
alternate keys. All eight pages are *always* read back, regardless of whether
you're currently working on the alternate set of keys or not.

- Page `0`:
  - `Esc` (unknown if it can be rebound)
  - Keys labeled `1` to `15`
- Page `1`:
  - Keys labeled `16` to `22`
  - The thumb button, next to the stick
  - *An empty key - possibly padding*
  - In A+K mode, `0x090000FF` is returned for LSB (see the gamepad notes).
  - In Keyboard only mode, the following are also returned:
    - LSB (default: `F`)
    - Up
    - Down
    - Right
    - Left
    - Right-Up - all diagonals are set automatically as composites by the GUI.
    - Right-Down
    - Left-Down
    - Left-Up
  - *An empty key - possibly padding*
  - An unknown field (`0x090000FF` on both modes, profile 8 and 1)
  - An unknown field (`0x0A0000FF` on both modes, profile 8 and 1) -- this could possibly also be deadzone?
  - *11 empty fields - padding?*
- Page `3`:
  - [4] Unknown config (`x0a0a0a0a`)
  - Deadzone (Keyboard only?). Default is 10% (`0x0a`). Setting it to 70%
yielded the value `0x46` (70) in this field.
  - LED setting.
    - On keyboard profile `0` (black/clear), this value is `0x0104`
    - On keyboard profile `7` (white), this value is `0x0101`
    - *I don't know if it's possible to customize the LED color independently of its profile.*
  - [10] Padding fields (?)
- Page `4`: *alternate button set to page `0`, activated by holding the `Fn` button*
- Page `5`: *alternate button set to page `1`, activated by holding the `Fn` button*
- Page `6`: *alternate button set to page `2`, activated by holding the `Fn` button*
- Page `7`: *alternate set of data for page `3`*
  - Confirmed that the deadzone setting differs on this field.

## Setting gamepad inputs on keys

Generally, it seems that when a gamepad input has been set on a key, the last
byte of the key is set to `0xff`. For "gamepad button Back", for example, this
value is `0x240000ff`.

I've mapped out the values for gamepad input as follows:

- Back: `0x24`
- Start: `0x23`
- A: `0x01`
- B: `0x02`
- X: `0x03`
- Y: `0x4`
- LeftTrigger: `0x07`
- LeftBumper: `0x05`
- RightTrigger: `0x08`
- RightBumper: `0x06`
- LSB: `0x09`
- LeftStickLeft: `0x15`
- LeftStickUpLeft: `0x1a`
- LeftStickUp: `0x13`
- LeftStickUpRight: `0x17`
- LeftStickDownRight: `0x18`
- LeftStickDown: `0x14`
- LeftStickDownLeft: `0x19`
- DPadUp: `0x0b`
- DpadRight: `0x0e`
- DpadDown: `0x0c`
- DpadLeft: `0x0d`
- DpadUpLeft: `0x12`
- DpadUpRight: `0x0f`
- DpadDownLeft: `0x11`
- DPadDownRight: `0x10`
- RSB: `0x0a`
- RightStickLeft: `0x1d`
- RightStickUpLeft: `0x22`
- RightStickUp: `0x1b`
- RightStickUpRight: `0x1f`
- RightStickRight: `0x1e`
- RightStickDownRight: `0x20`
- RightStickDown: `0x1c`
- RightStickDownLeft: `0x21`
