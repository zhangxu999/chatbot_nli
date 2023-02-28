from sanic.request import Request
from typing import Text, Dict, Any, Optional
from common.constants import *
from common.log import logger_metadata
from rasa.core.channels.rest import RestInput


class MyIO(RestInput):
    def name(self) -> Text:
        """Name of your custom channel."""
        return "myio"
    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        ### 获取所有房间和设备
        origin = request.json.get("metadata")
        logger_metadata.info("\n\n")
        logger_metadata.info(origin)
        // to do
        newOrigin = {
            CUSTOM_CHANNEL_DEVICE_NAMES: deviceName,
            CUSTOM_CHANNEL_DEVICE_IDS: deiveId,
            CUSTOM_CHANNEL_DEVICE_CATEGORIES: deviceCategory,
            CUSTOM_CHANNEL_DEVICE_IS_ONLINE: deviceisOnline,
            CUSTOM_CHANNEL_ROOM_NAMES: roomName,
            CUSTOM_CHANNEL_ROOM_DEVICES: roomDeviceid,
            "devices": devices,
            "device_name_to_id": device_name_to_id,
            "rooms": rooms
        }
        return newOrigin