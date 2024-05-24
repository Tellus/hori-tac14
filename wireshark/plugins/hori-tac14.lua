require "usb_scancodes"

local SET_REPORT_TYPE = 0x09
local GET_REPORT_TYPE = 0x01

local plugin_info = {
  version = "0.0.1",
  author = "Joe",
  description = "Parses the data fragments and reports of USB communication with Hori Tactical Assault FXIV black edition",
  repository = "My ass",
}

set_plugin_info(plugin_info)

-- Declare the protocol
local hori_p = Proto.new("hori_tac14", "Hori Tac14")

-- Fields to extract info from.
-- The "remaining" data in SET_REPORT requests seem to contain command information (yes?)
local data_fragment_field = Field.new("usb.data_fragment")
-- GET_REPORT test: is this actually a report request? If 0x01 it is GET, if 0x09, it is SET
-- Additionally, if the source is "host", it is a request, if the destination is "host", it is a response.
local usbhid_setup_request_field = Field.new("usbhid.setup.bRequest")
local usb_dst_field = Field.new("usb.dst")
local usb_src_field = Field.new("usb.src")
local irp_id_field = Field.new("usb.irp_id")

-- Quick first protocol field to test out the post-dissection function. In reality, should probably be a full struct or a string.
-- 01a5105aef0000
local command_field = ProtoField.bytes("hori_tac14.command", "Command string", base.NONE)
-- Should contain the mode. 0 for keyboard only, 1 for K+A.
local keyboard_mode_field = ProtoField.uint8(
  "hori_tac14.keyboard_mode",
  "Mode",
  base.DEC,
  { [0] = "Keyboard only", [1] = "Analogue + Keyboard"},
  0xF0
)
-- Should contain the profile (0-7) that the report is acting on.
local profile_field = ProtoField.uint8(
  "hori_tac14.profile",
  "Profile",
  base.DEC,
  nil,
  0x0F
)
-- Should contain the page that is being operated on (6th byte of the data fragment)
local page_field = ProtoField.uint8(
  "hori_tac14.page",
  "Page",
  base.DEC
)

local key_0_field = ProtoField.uint8(
  "hori_tac14.keys.0",
  "Key 0",
  base.HEX
)

local string_field = ProtoField.string("hori_tac14.debug", "Debug string", base.ASCII)

local protocol_fields = {
  command_field,
  keyboard_mode_field,
  profile_field,
  page_field,
  string_field,
  key_0_field,
}

key_fields = {}

for i = 0, 15 do
  -- local new_field = ProtoField.string("hori_tac14.keys." .. i, "Key " .. i, base.ASCII)
  local key_field_0 = ProtoField.uint8(
    "hori_tac14.keys." .. i .. ".0",
    "Input 0",
    base.DEC,
    scancodes,
    0xFF000000
  )

  local key_field_1 = ProtoField.uint8(
    "hori_tac14.keys." .. i .. ".1",
    "Input 1",
    base.DEC,
    scancodes,
    0x00FF0000
  )

  local key_field_2 = ProtoField.uint8(
    "hori_tac14.keys." .. i .. ".2",
    "Input 2",
    base.DEC,
    scancodes,
    0x0000FF00
  )

  local key_field_3 = ProtoField.int8(
    "hori_tac14.keys." .. i .. ".is_gamepad",
    "Gamepad",
    base.DEC,
    { [0] = "No", [-1] = "Yes" },
    0x000000FF
  )

  table.insert(key_fields, { key_field_0, key_field_1, key_field_2, key_field_3 })
  table.insert(protocol_fields, key_field_0)
  table.insert(protocol_fields, key_field_1)
  table.insert(protocol_fields, key_field_2)
  table.insert(protocol_fields, key_field_3)
end

hori_p.fields = protocol_fields

local function set_report_request_dissector(data, buffer, pinfo, tree)
  pinfo.cols.protocol = hori_p.name

  if data.type ~= ftypes.BYTES then
    print("Data fragment is incorrect type! Expected BYTES!")
    return
  end

  local command_data = data.range(0, 7)
  -- Alternate version from buffer.
  -- local command_data = buffer:range(36, 7)

  local subtree = tree:add(hori_p, command_data)

  subtree:add(command_field, command_data)

  local mode_and_profile_range = data.range(5, 1)
  local page_range = data.range(6, 1)

  subtree:add(keyboard_mode_field, mode_and_profile_range)
  subtree:add(profile_field, mode_and_profile_range)
  subtree:add(page_field, page_range)
end

-- Used to recognize received packets that essentially acknowledge the previously
-- sent report.
local ACK_PREFIX = ByteArray.new("01 A5")
local COMMAND_READ_MODE = ByteArray.new("01a5105aef0000")

local function get_report_response_dissector(buffer, pinfo, tree)
  pinfo.cols.protocol = hori_p.name

  local data = buffer:range(28)
  local prefix = data:range(0,2)

  if prefix:bytes() == ACK_PREFIX then
    pinfo.cols.protocol = hori_p.name .. "_ACK"
    print("ACK - no tree view here, yet!")

    tree:add(hori_p, "Ack string")

    return
  end

  local subtree = tree:add(hori_p, buffer)

  -- Should contain 9 x ... 8?
  local key_entry_bytes = data:bytes()
  local bytecount = key_entry_bytes:len()
  -- local bytecount = 8
  local key_count = bytecount / 4

  for offset=0, bytecount - 4, 4 do
    -- print("Key #" .. offset / 4)
    local single_key_range = data:range(offset, 4)
    -- print(single_key_range)
    local is_gamepad = single_key_range:range(3, 1):int() < 0

    local key_scancodes = {}

    for key_component_index=0, 3, 1 do
      local key = single_key_range:range(key_component_index, 1):bytes()
      local key_hex = key:tohex(false, "")
      local key_dec = key:uint()

      -- print(key_component_index, key, key_dec)
      if key_component_index == 0 and key_dec == 0 then
        -- print("Breaking on 00-prefixed key - assuming empty (" .. single_key_range:bytes():tohex(false, " ") .. ")")
        break
      end

      if key_dec > 0 then
        table.insert(key_scancodes, scancodes[key_dec])
      elseif key_dec == 0 then
        table.insert(key_scancodes, tostring(key_dec))
      else
        print("!!!!!", key, key_dec)
      end
    end

    local proto_f_key = (offset / 4) + 1
    local proto_fields = key_fields[proto_f_key]

    if is_gamepad == true and single_key_range:range(0, 1):int() == 9 then
      subtree:add(single_key_range, "Gamepad LSB")
    elseif is_gamepad == true and single_key_range:range(0, 1):int() == 38 then
      subtree:add(single_key_range, "Fn key")
    else
      local key_subtree = subtree:add("Key " .. offset / 4 .. "(" .. single_key_range:bytes():tohex(false, " ") .. ")")
      if key_scancodes[1] ~= "0" then
        key_subtree:add(proto_fields[1], single_key_range)
      end

      if key_scancodes[2] ~= "0" then
        key_subtree:add(proto_fields[2], single_key_range)
      end

      if key_scancodes[3] ~= "0" then
        key_subtree:add(proto_fields[3], single_key_range)
      end

      if key_scancodes[4] ~= "0" then
        key_subtree:add(proto_fields[4], single_key_range)
      end
    end
  end
end

local function set_report_response_dissector(buffer, pinfo, tree)
  -- print("NYI: set_report_response_dissector")
end

local function get_report_request_dissector(buffer, pinfo, tree)
  -- print("NYI: get_report_request_dissector")
end

-- The actual dissector function.
function hori_p.dissector(buffer, pinfo, tree)
  -- Ignore anything without a buffer.
  local length = buffer:len()
  if length == 0 then return end

  -- If this yields a value, it's because we're dissecting a SET_REPORT request.
  local request_type = usbhid_setup_request_field()
  -- The combination of destination and request_type is enough to determine which
  -- subdissector we want to use.
  -- If we have a request type (i.e. a SET_REPORT), we're only interested in outbound
  -- communication (dst == "host"). If we do NOT have a request type and the
  -- packet is *inbound*, we assume that it's the response to GET_REPORT (the
  -- other packet type we want to inspect).
  -- In other words: we want to dissect outbound SET_REPORT and inbound GET_REPORT.
  -- Anything else is just noise to us.
  local dst = usb_dst_field()

  -- Dissectors are supposed to be stateless, so we can't directly query what happened
  -- in a previous packet... but we *want* to. We'd like to be able to match the
  -- parameters (data fragment) of a SET_REQUEST to the matching data incoming from a
  -- later GET_REQUEST. This is just to make it easier to piece together the
  -- command/response parts of the protocol. Instead of looking at the first and last
  -- entry in a four-packet series (SET_REPORT request/response, GET_REPORT request/response),
  -- it would be much easier to read it as "given this SET_REPORT, we got this result"
  -- in the last packet's details.
  -- This wall of text is just to say that irp_id is a unique id for 
  
  -- The two types of packets we're interested in is SET_REPORT request and GET_REPORT response.
  -- Unfortunately, the only direct way of querying packet type is in the "Info" column, which
  -- we can't query from within a dissector. That means we can't directly determine which sort
  -- of inbound request we're looking at.
  -- One solution is to store outbound IRP_IDs globally, and query them every time we get an
  -- inbound. It's leaky, it's probably slow, but it's a very direct way to being sure.
  -- The alternative is a bit more fragile. Buffer length. Inbound SET_REPORT is 28 bytes,
  -- while inbound GET_REPORT is 92 bytes. It's a much cheaper and simpler check - but fragile.

  if dst.value == "host" then
    if length == 28 then
      -- Inbound response to SET_REPORT
      return set_report_response_dissector(buffer, pinfo, tree)
    elseif length == 92 then
      -- Inbound response to GET_REPORT
      return get_report_response_dissector(buffer, pinfo, tree)
    end
  end

  if not request_type then
    print("Skipping outbound packet without request_type")
  elseif dst.value ~= "host" then
    -- Outbound
    if request_type.value == SET_REPORT_TYPE then
      -- SET_REPORT requests have some setup data. We use this information to store some state for the response package.

      local data = data_fragment_field()

      return set_report_request_dissector(data, buffer, pinfo, tree)
    -- elseif request_type.value == GET_REPORT_TYPE then
    --   return get_report_request_dissector(cached_request, buffer, pinfo, tree)
    end
  end
  -- elseif dst.value == "host" then
    -- Inbound
    
    -- if request_type.value == GET_REPORT_TYPE then
    --   -- print("Popping previous request ", rid)
  
    --   local prev_request = all_requests[rid]
    --   all_requests[rid] = nil -- Wipe it to keep the table smaller.
  
    --   if prev_request and prev_request.request_type and prev_request.request_type == GET_REPORT_TYPE then
    --     -- print("Guessing at GET_REPORT response")
    --     get_report_response_dissector(prev_request, buffer, pinfo, tree)
    --   end
    -- end
  -- end
end

register_postdissector(hori_p)