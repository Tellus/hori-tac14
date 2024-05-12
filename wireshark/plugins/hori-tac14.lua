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
data_fragment_field = Field.new("usb.data_fragment")
-- Returned data from GET_REPORT
get_report_data_field = Field.new("frame")
-- GET_REPORT test: is this actually a report request? If 0x01 it is GET, if 0x09, it is SET
-- Additionally, if the source is "host", it is a request, if the destination is "host", it is a response.
usbhid_setup_request_field = Field.new("usbhid.setup.bRequest")
usb_dst_field = Field.new("usb.dst")
usb_src_field = Field.new("usb.src")
irp_id_field = Field.new("usb.irp_id")

-- Quick first protocol field to test out the post-dissection function. In reality, should probably be a full struct or a string.
local command = ProtoField.bytes("hori_tac14.command", "Command string", base.NONE)
-- Should contain the profile (0-7) that the report is acting on.
local profile_field = ProtoField.int8("hori_tac14.profile", "Profile", base.DEC)
-- Should contain the page that is being operated on (6th byte of the data fragment)
local page_field = ProtoField.int8("hori_tac14.page", "Page", base.DEC)

-- Contains all previous requests that we've dissected. This is such a performance killer...
local all_requests = {}

hori_p.fields = {
  command,
  profile_field,
  page_field,
}

key_fields = {}

for i = 1, 16 do
  local new_field = ProtoField.string("hori_tac14.keys." .. i, "Key " .. i, base.ASCII)
  table.insert(key_fields, new_field)
  table.insert(hori_p.fields, new_field)
end

function set_report_request_dissector(request_cache, data, buffer, pinfo, tree)
  pinfo.cols.protocol = hori_p.name
  
  if data.type ~= ftypes.BYTES then
    print("Data fragment is incorrect type! Expected BYTES!")
    return
  end
  
  local subtree = tree:add(hori_p, data)
  
  print("SET " .. data.label)

  subtree:add(command, data.range(0, 7))
  local profile_data_range = data.range(5,1)
  local profile_index = profile_data_range:int() - 16
  
  subtree:add(profile_field, profile_data_range, profile_index)
  subtree:add(page_field, data.range(6, 1))
  
  request_cache.profile = profile_index
  request_cache.page = data.range(6, 1):int()
end

local has_printed = false

-- Used to recognize received packets that essentially acknowledge the previously
-- sent report.
local ACK_PREFIX = ByteArray.new("01 A5")

function get_report_response_dissector(request, buffer, pinfo, tree)
  pinfo.cols.protocol = hori_p.name
  
  local raw_data = get_report_data_field()
  
  -- Not for us.
  if not raw_data or raw_data.len ~= 92 then
    print("NO RAW DATA! BAILING!")
    return
  end
  
  -- The data we're actually interested in starts here.
  local data = raw_data.range(28)
  
  print("GET " .. data:bytes():tohex(false, ":"))
  
  local subtree = tree:add(hori_p, data)
  
  subtree:add(page_field, 8)
  
  local prefix = data:range(0,2)
  
  if prefix:bytes() == ACK_PREFIX then
    -- print("ACK string")
    return
  end
  
  -- Should contain 9 x ... 8?
  key_entry_byte_range = raw_data.range(28)
  key_entry_bytes = key_entry_byte_range:bytes()
  bytecount = key_entry_bytes:len()
  
  local offset = 0
  
  while offset < bytecount do
    local range = key_entry_byte_range:range(offset, 4)
    
    keycode = key_entry_bytes:uint(offset, 1)
    
    print("key " .. keycode)
--    print(key_entry_bytes:subset(offset, 4))
    
    mod1 = key_entry_bytes:uint(offset + 1, 1)
    mod2 = key_entry_bytes:uint(offset + 2, 1)
    mod3 = key_entry_bytes:uint(offset + 3, 1)
    
    if (keycode + mod1 + mod2 + mod3) == 0 then
      -- Empty entry. Ignore.
    -- If no modifier fields were set, this is a "pure" keypress.
    elseif (mod1 + mod2 + mod3) == 0 then
      subtree:add(key_fields[(offset / 4) + 1], range, scancodes[keycode])
      -- Pure keypress
--      print("Key: " .. scancodes[keycode])
    end

    offset = offset + 4
  end
  --print(key_entries)
end

function hori_p.dissector(buffer, pinfo, tree)
--  length = buffer:len()
-- usb.data_len
--  if length == 0 then return end

  -- Looks like data should be ftypes.BYTES
  local data = data_fragment_field()
  local request_type = usbhid_setup_request_field()
  local src = usb_src_field()
  local dst = usb_dst_field()
  
  local irp_id = irp_id_field()
  
  local rid = irp_id.range():bytes():tohex()
  
  if request_type and (request_type.value == 1 or request_type.value == 9) then
    local cached_data = {}
    
    cached_data.request_type = request_type.value
    
    all_requests[rid] = cached_data
    
    if data and src.value == "host" then
      -- Is GET_REPORT or SET_REPORT. Store frame data.
      print("Encountered request ", rid, request_type.value)
      
      
      
      return set_report_request_dissector(cached_data, data, buffer, pinfo, tree)
    end
  end
  
  if dst.value == "host" then
    print("Popping previous request ", rid)
    
    local prev_request = all_requests[rid]
    all_requests[rid] = nil -- Wipe it to keep the table smaller.
    
    if prev_request and prev_request.request_type and prev_request.request_type == GET_REPORT_TYPE then
      print("Guessing at GET_REPORT response")
      get_report_response_dissector(prev_request, buffer, pinfo, tree)
    end
  end
end

register_postdissector(hori_p)