def read_key_configuration(page: int, profile: int = 0):
  """ Reads back the current key configuration of the device. By default, reads
  from the first profile (0) out of 8 (so, max 7). Each page contains 16 keys.
  Indexing starts from key 0 which is the physical "Esc" key on the pad!
  
  To get the config for the key labeled "3" you need to request page 0 and look
  at the fourth returned element.

  To get the config for the key labeled "17", request page 1 and look at the
  second item (index 1).
  """
  pass