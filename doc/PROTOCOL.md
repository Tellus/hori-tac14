# HORI Tac14 USB protocol

This file is an effort to document the communication protocol used by the HORI
Tactical Assault F14 Black edition.

Everything has been discovered by sniffing traffic between the FFXIV keymapping
tool and the USB device, using Wireshark.

I am not a USB expert, so expect me to conflate the workings of the HORI with
mechanisms that are normal for any USB device.

## Normal operation

The HORI (idVendor `0x0f0d`) presents itself as multiple devices:

- A USB hub to encompass its constituents
- A USB HID, the keypad - idProduct `0x013a`
- A joystick (game controller?) - idProduct `0x013b`

The joystick is only active/present/available when the HORI i in Analog+Keyboard
mode (as opposed to pure Keyboard mode).

The keypad portion is a USB HID class. When the user presses a butotn, the HORI
sends an interrupt containing the USB scan code of the pressed button. On
release, another interrupt is sent.

From what I can tell, the *base* functionality of the HORI works on Linux and
Steam out of the box, as long as the user has access rights to the device.
There should be a udev rule file in this repository that can be dumped in
`/etc/udev/rules.d/`. I expect this should work for most modern "user-friendly"
distros. If you're not using udev or systemd, or for some reason might have
other spicy features in your system, I expect you're enough of an expert to know
how to get access to the USB devices on your own :D

## Command line

By "command line", I meant the common 7 bytes used in all SET_REPORT operations.
When writing, there are more parts to the data sent to the device, but the 7
bytes always denote the general type of command.

**All** commands have this general form:

- `01a5`: **always** the first two bytes.
- Read or write mode. `1` on read, `2` on write.
- "Phase" of operation. This always seems to start with `0` when starting read/write, `2` when ending read/write, and `1` for all intermediate operations.
- `5a`: **always** the case. It almost looks like `a5` and `5a` are "bookds" visually, but that's probably just me.
- Read or write mode. `e` on read, `d` on write. I don't like how there's two groups of bits denoting reading/writing.
- "Phase", again. Instead of `0`, `1`, `2`, it's `f`, `e`, `d` (decreasing, instead).
- Page parameters.
  - Mode, `0` for keyboard only, `1` for A+K
  - Profile, zero-indexed (so, `0` to `7`)
  - Page, zero-indexed (`00` to `31`). Reads stop at `7` (because they return more data), writes go up to `31`.

In other words: `01 a5 WH 5a WH MFPP`, where `W` is read/write mode, `H` is phase, `M` is mode, `F` is profile and `PP` is page.

The following tables break down the commands into hexadecimal/binary components, for visual comparisons.

| Command     | Prefix     | Mode/phase   | Postfix    | Mode/phase     | Analog/Profile | Page   |
| ----------- | ---------- | ------------ | ---------- | -------------- | -------------- | ------ |
| Read start  | `0xa5`     | `0x10`       | `0x5a`     | `0xef`         | `0x11`         | `0x00` |
|             | `10100101` | `00010000`   | `01011010` | `11101111`     |                |        |
| Read page 0 | `0xa5`     | `0x11`       | `0x5a`     | `0xee`         | `0x11`         | `0x00` |
|             | `10100101` | `00010001`   | `01011010` | `11101110`     |                |        |
| Read end    | `0xa5`     | `0x12`       | `0x5a`     | `0xed`         | `0x11`         | `0x00` |
|             | `10100101` | `00010010`   | `01011010` | `11101101`     |                |        |


| Command     | Prefix     | Mode/phase   | Postfix    | Mode/phase     | Analog/Profile | Page   |
| ----------- | ---------- | ------------ | ---------- | -------------- | -------------- | ------ |
| Write start | `0xa5`     | `0x20`       | `0x5a`     | `0xdf`         | `0x11`         | `0x00` |
|             | `10100101` | `00100000`   | `01011010` | `11011111`     |                |        |
| Write page 0| `0xa5`     | `0x21`       | `0x5a`     | `0xde`         | `0x11`         | `0x00` |
|             | `10100101` | `00100001`   | `01011010` | `11011110`     |                |        |
| Write end   | `0xa5`     | `0x22`       | `0x5a`     | `0xdd`         | `0x11`         | `0x00` |
|             | `10100101` | `00100010`   | `01011010` | `11011101`     |                |        |
| Unknown     | `0xa5`     | `0x23`       | `0x5a`     | `0xdc`         | `0x11`         | `0x00` |
|             | `10100101` | `00100011`   | `01011010` | `11011100`     |                |        |

I hate this, but everything points to bytes 1-2 and 3-4 being each others'
inverse values. `0xa520 & 0x5adf` is 0. `0xa523 & 0x5adc` is 0. Why is it like
this?!

The NEW command structure is much simpler, though:

- `0x01` - mandatory start.
- `0xa5MH`
- ~`0xa5MH`
- `0xAF`
- `0xPP`

## Remapping

The device's keys can be remapped to any valid keyboard input (as well as some
gamepad inputs) using the remapper tool.

The remapper seems to rely entirely on SET_REPORT and GET_REPORT to perform all
editing actions on the device.

Basically, it's operations boil down to either reading current configurations or
writing new key configurations. It doesn't seem like the tool can forcefully
change the active key profile (1-8) but it CAN access the configurations from
all 8 profiles for both modes (A+K and K) at any time.

When communicating with the HORI, the remapper only sends or expects data
segments of 64 bytes. I have no idea if this is USB restriction/convention or
just how the tool is implemented. Because of this, a full configuration cannot
be sent or received with a single message, and the remapper sends several
messages covering several *pages*.

For all SET_REPORT operations, the data fragment has the form `0x01a5105aef10000000000000000000000000000000000000000000000000000000` (lots of padding). For brevity (and legibility), I'll omit bytes that seem to be unused.

### Reading

Reading key configurations goes through three phases:

#### Start with a "start read" command

SET_REPORT with the following parameters:

- bmRequestType: `0x21`
- bRequest: `0x09` (SET_REPORT)
- wValue: `0x0201`
- wIndex: `0x01`
- data: `0x01a5105aef1000`

#### "Turn" to a configuration page and read it back

First a SET_REPORT "turning the page" to the requested page of keys:

- bmRequestType: `0x21`
- bRequest: `0x09` (SET_REPORT)
- wValue: `0x0201`
- wIndex: `0x01`
- data: `0x01a5115aee1000`

The last two bytes of the data fragment is the `page`, and the third last byte
seems to be the `profile`. Thus, the first page of the first profile is `0x1000`
while the second page of the fifth profile is `0x1401`. **The page count when
reading does NOT match the page count when writing. When reading, each page
contains 16 keys. When WRITING, each page only contains 4 keys.**

Then, a GET_REPORT that returns 16 keys matching the input parameters.

- bmRequestType: `0xa1`
- bRequest: `0x01` (GET_REPORT)
- wValue: `0x0101`
- wIndex: `0x01`
- wLength: 65 <- I don't know if this is necessary to state explicitly

This returns 64 bytes of key configurations, 8 bytes per key. "Pure" keys (like
just the letter "G") are in the first 2 bytes. Compounded keys (say,
Ctrl+Shift+G) notes each modifier key's USB scan code before the final key.

- G: `0b 00 00 00`
- Ctrl+Shift+G: `e0 e1 0b 00`
- The function key is the (special?) value `26 00 00 ff`. `0x26` is "9" (I think - check notes), I don't know if this MUST be the "primary" key when defining the
function key.

#### End with a "stop reading" command

SET_REPORT with the following parameters:

- bmRequestType: `0x21`
- bRequest: `0x09` (SET_REPORT)
- wValue: `0x0201`
- wIndex: `0x01`
- data: `0x01a5125aed1000`

### Writing

WIP

## Notes

Every single operation seems prefixed with `0x01a5` but I can't tell if this has
any particular meaning.

It *seems* to be the case that four bits differ between reading and writing
operations. Two pairs of two adjacent bits are flipped. So far I haven't been
able to discern the pattern.

I don't know if it makes more sense to view the communication as hex-based
commands or look at the specific bits that are set for each message. I feel
confident in the last three bytes that point to profile and page. They seem
solid.

When reading back page 0 of any profile, the very first key is the physical
"Esc" key, "bound" to the escape USB scan code. This seems to suggest that the
key can actually be rebound, even if the tool won't allow it. Hm.

It *seems* like the LED backlight is set on page 12 (`0x0c`), 3rd parameter,
i.e. the ninth byte, i.e. index 8 (when zero-indexing).

I haven't mapped out how the data fragment / command line differs when
requesting different profiles across thw two modes, or when writing to them.
This should be a fairly simple sniff-trek with Wireshark, though.

It might be really useful to know what board the HORI is actually based on.

The board has a maintenance mode that can be activated by holding 1 and 2 while
plugging it in. This is used when updating firmware.