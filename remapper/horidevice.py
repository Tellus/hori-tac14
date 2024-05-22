import usb.core
from usb.core import Device

from constants import VENDOR_ID, PRODUCT_ID, KEYBOARD_ONLY_MODE, ANALOG_MODE
import keys

# TODO: should this be a namedtuple or SimpleNamespace instead?
class ThumbstickConfig(object):
  """
  Structured representation of the mapping of the thumbstick in keyboard-only
  mode.
  """
  def __init__(self, keys_as_bytes: list[list[int]] | list[str]) -> None:
    # This is possibly the ugliest copy list expression I've ever seen.
    self.__raw_source = keys_as_bytes.copy() if keys_as_bytes[0] is str else [[inner_key for inner_key in key] for key in keys_as_bytes]

    self.up = keys_as_bytes[0]
    self.down = keys_as_bytes[1]
    self.left = keys_as_bytes[2]
    self.right = keys_as_bytes[3]
    self.up_right = keys_as_bytes[4]
    self.down_right = keys_as_bytes[5]
    self.down_left = keys_as_bytes[6]
    self.up_left = keys_as_bytes[7]

  def as_name_dict(self):
    if self.up is str:
      return self
    else:
      return ThumbstickConfig([keys.get_key_for_bytes(k) for k in self.__raw_source])
    
  def __str__(self) -> str:
    return str({
      'up': self.up,
      'down': self.down,
      'left': self.left,
      'right': self.right,
      'up_right': self.up_right,
      'down_right': self.down_right,
      'down_left': self.down_left,
      'up_left': self.up_left,
    })

class HoriDevice(object):
  """
  Abstraction over the Hori Tac 14 USB device. Has high-level functions for
  manipulating the device without you having to dive deep into the protocol.
  """

  def __detach_kernel_drivers(self):
    """
    Detaches all kernel drivers currently attached to the device. This must be
    done in order for us to have I/O access to the device.
    """
    self.__reattach_list = []

    for i in [0, 1]:
      if self.__device.is_kernel_driver_active(i):
        self.__device.detach_kernel_driver(i)
        self.__reattach_list.append(i)
        # print(f'Detached interface {i}')

  def __reattach_kernel_drivers(self):
    """
    Re-attaches any kernel drivers that were previously detached when this
    object was created.
    """
    # print(f'Reattaching {self.__reattach_kernel_drivers}')
    for i in self.__reattach_list:
      self.__device.attach_kernel_driver(i)

  def __init__(self):
    device = usb.core.find(idVendor = VENDOR_ID, idProduct = PRODUCT_ID)

    if device is None:
      raise BaseException('Could not find any valid devices!')
    
    self.__device: Device = device

    self.__detach_kernel_drivers()

  def __del__(self):
    """
    Destructor. Makes sure to release any resources and re-attach any kernel
    drivers that were detached when the object was created. This *should* leave
    the device in the same connection state before/after object use.

    If all else fails, simply disconnecting/reconnecting the device's USB cable
    will restore its default connection state.
    """
    usb.util.dispose_resources(self.__device)
    self.__reattach_kernel_drivers()

  def __get_report(self, wLength: int):
    """
    Simple wrapper for the GET_REPORT operation.
    """
    return self.__device.ctrl_transfer(0xa1, 0x01, 0x0101, 0x01, wLength)

  def __set_report(self, cmd: list[int]):
    """
    Simple wrapper for the SET_REPORT operation.
    """
    return self.__device.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, cmd)

  def __get_profile_page(self, profile: int = 0, page: int = 0, mode: int = KEYBOARD_ONLY_MODE) -> bytearray:
    """
    Retrieves the configuration present at a given profile's page for a specific
    mode (A+K or K).

    :param int profile: The profile to read from (0-7)
    :param int page: The page to read from (0-7)
    :param int mode: The keypad mode to read from (KEYBOARD_ONLY_MODE or ANALOG_MODE)
    """

    if not (0 <= page < 7):
      raise ValueError(f'Page must be 0-7. Actual: {page}')
    
    if not (0 <= profile < 7):
      raise ValueError(f'Profile must be 0-7. Actual: {profile}')
    
    if mode != KEYBOARD_ONLY_MODE and mode != ANALOG_MODE:
      raise ValueError(f'Unsupported mode requested: {mode}')

    # Switch to page.
    GOTO_PAGE = bytearray.fromhex(f'01a5115aee{mode}{profile}{page:02x}')
    self.__set_report(GOTO_PAGE)
    # Retrieve data.
    return self.__get_report(65)

  def get_configuration(self, profile:int = 0, mode: int = KEYBOARD_ONLY_MODE) -> any:
    # The meaning of OPEN_READ and CLOSE_READ are still uncertain. The commands
    # for paging and getting configs seem to work just fine without them.
    OPEN_READ = bytearray.fromhex(f'01a5105aef{mode}{profile}00')
    
    self.__set_report(OPEN_READ)

    # Contains keys 0-15 (labeled "Esc", and "1" to "15")
    keys_0_result = self.__get_profile_page(profile, 0, mode)
    keys_0 = [(keys_0_result[i : i + 4]) for i in range(0, len(keys_0_result), 4)]
    # Contains keys 16-22, LeftThumbStick, and keys for stick (in keyboard mode)
    keys_1_result = self.__get_profile_page(profile, 1, mode)
    keys_1 = [(keys_1_result[i : i + 4]) for i in range(0, len(keys_1_result), 4)]
    # Contains last two thumbstick directions in keyboard only mode.
    keys_2_result = self.__get_profile_page(profile, 2, mode)
    keys_2 = [(keys_2_result[i : i + 4]) for i in range(0, len(keys_2_result), 4)]

    # Contains keys 0-15 (labeled "Esc", and "1" to "15") when Fn is held down ("alt" keys)
    alt_keys_0_result = self.__get_profile_page(profile, 4, mode)
    alt_keys_0 = [(alt_keys_0_result[i : i + 4]) for i in range(0, len(alt_keys_0_result), 4)]
    # Contains keys 16-22, LeftThumbStick, and keys for stick (in keyboard mode) when Fn is held down ("alt" keys)
    alt_keys_1_result = self.__get_profile_page(profile, 5, mode)
    alt_keys_1 = [(alt_keys_1_result[i : i + 4]) for i in range(0, len(alt_keys_1_result), 4)]
    # Contains last two thumbstick directions in keyboard only mode when Fn is held down ("alt" keys")
    alt_keys_2_result = self.__get_profile_page(profile, 6, mode)
    alt_keys_2 = [(alt_keys_2_result[i : i + 4]) for i in range(0, len(alt_keys_2_result), 4)]

    CLOSE_READ = bytearray.fromhex(f'01a5125aed{mode}{profile}00')
    self.__set_report(CLOSE_READ)

    # returnvalue = [(result[i : i + 4]) for i in range(0, len(result), 4)]

    # return returnvalue
    return {
      'escape': keys_0[0],
      'keys': keys_0[1:] + keys_1[0:7],
      'left_thumbstick_button': keys_1[8],
      'thumbstick_keys': ThumbstickConfig(keys_1[10:18] + keys_2[:2]) if mode == KEYBOARD_ONLY_MODE else None, # 8 keys, for each cardinal direction. Only in keyboard mode.

      'alt_escape': alt_keys_0[0],
      'alt_keys': alt_keys_0[1:] + alt_keys_1[0:7],
      'alt_left_thumbstick_button': alt_keys_1[8],
      'alt_thumbstick_keys': ThumbstickConfig(alt_keys_1[10:18] + alt_keys_2[:2]) if mode == KEYBOARD_ONLY_MODE else None, # 8 keys, for each cardinal direction. Only in keyboard mode.
    }

    # # Set "read" mode.
    # self.__device.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, OPEN_READ)
    # # Tell the device to flip to read page 1. For *reading*, the device returns X keys (when writing, at most 4 can be sent, it seems)
    # result1 = self.__device.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, GOTO_PAGE_1)
    # # Request a report. This should yield the key setup for the first 1½ lines keys from the physical keypad.
    # result2 = self.__device.ctrl_transfer(0xa1, 0x01, 0x0101, 0x01, 65)
    # # Close the read again. Not sure if this is necessary.
    # self.__device.ctrl_transfer(0x21, 0x09, 0x0201, 0x01, CLOSE_READ)