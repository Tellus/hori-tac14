import usb.core
from usb.core import Device

from constants import PRODUCT_ID, VENDOR_ID

def get_devices() -> Device | None:
  return usb.core.find(idVendor = VENDOR_ID, idProduct = PRODUCT_ID)