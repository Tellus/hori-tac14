When writing a configuration, the vanilla GUI sends a SET_REPORT request for
each quartet of keys to be saved. Where a read request gets 16 keys, a write
request sends only 4. The size of a page is thus different, as is the number of
requests (8 -> 32).

The sequence of SET_REPORT requests looks like this.

The sequence is for writing to A+K mode, profile 1, standard sequence of keyboard inputs (1-9, 0, A-done). Backlight OFF.

- `0x01a5105aef1000` - reference of read start
- `0x01a5115aee1000` - reference of read page
- `0x01a5205adf1000` - "start write" request?
- GET_REPORT
  - `0x01a5205adf1000` - "ack" string
  - `0xaa000000` - meaning unknown
  - [4] empty
  - `0xb9020000` - meaning unknown
  - [8] empty
- `0x01a5215adeMPGG`, 32 times:
  - [4] Key configurations following the same value conventions as when reading.
  - [2] Empty? Padding?
- `0x01a5225add10` - "end write" request?
- GET_REPORT:
  - `0x01a5225add1000` - "ack" string
  - `0xaa000000` - meaning unknown
  - [3] empty
  - `0x290e0000` - meaning unknown
  - `0xf0020000` - meaning unknown
  - [8] empty
- `0x01a5235adc10` - ... another "end write" request?
- GET_REPORT:
  - `0x01a5235adc1000` - "ack" string
  - [6] empty