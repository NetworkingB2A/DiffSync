# Local Imports
from utils.utils import (
    custom_field_mapping,
)

# Third-party Imports

from diffsync import DiffSyncModel
import structlog

# System Imports
from typing import Optional, Union
import os

logger = structlog.get_logger(__name__)


class Device(DiffSyncModel):

    _modelname = "device"
    _identifiers = ("name",)
    _attributes = (
        "role",
        "model",
        "platform",
        "serial",
        "status",
        "platform_object_uuid",  # Custom field > This is a field I bring over that has the UUID of a device.
        "primary_ip",  # Custom field > This is a field I created to allow for easier device discovery.
    )

    name: str
    role: Optional[str]
    vendor: Union[str, None]
    model: Union[str, None]
    platform: Optional[str]
    serial: Union[str, None]
    status: Optional[str]
    platform_object_uuid: Union[str, None]
    primary_ip: Union[str, None]


class DNACDevice(Device):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)


class NetboxDevice(Device):
    netbox_id: Union[str, None]

    @classmethod
    def create(cls, adapter, ids, attrs):
        try:
            adapter.netbox_api.dcim.devices.create(
                {
                    "name": ids["name"],
                    "role": {"name": attrs["role"]},
                    "device_type": {"part_number": attrs["model"]},
                    **(
                        {"serial": attrs["serial"]}
                        if attrs["serial"] is not None
                        else {}
                    ),
                    "site": {"name": "Default"},
                    "status": attrs["status"].lower(),
                    "platform": {"name": attrs.get("platform")},
                    "custom_fields": {
                        "platform_object_uuid": attrs.get("platform_object_uuid"),
                        "device_discovery_address": attrs.get("primary_ip"),
                        "data_source": "dnac",
                    },
                }
            )
            attrs["vendor"] = "Cisco"
            attrs["netbox_id"] = None
            return super().create(ids=ids, adapter=adapter, attrs=attrs)
        except Exception as e:
            logger.error(f"Error creating device in NetBox: {e}")
            return None

    def update(self, attrs):
        custom_fields = custom_field_mapping(attrs)
        cisco_device = {
            "id": int(self.netbox_id),
            **(
                {"role": {"name": attrs["role"]}}
                if attrs.get("role") is not None
                else {}
            ),
            **(
                {"device_type": {"part_number": attrs["model"]}}
                if attrs.get("model") is not None
                else {}
            ),
            **({"serial": attrs["serial"]} if attrs.get("serial") is not None else {}),
            **(
                {"status": attrs["status"].lower()}
                if attrs.get("status") is not None
                else {}
            ),
            **(
                {"platform": {"name": attrs["platform"]}}
                if attrs.get("platform") is not None
                else {}
            ),
            **({"custom_fields": custom_fields} if custom_fields is not None else {}),
        }
        self.adapter.netbox_api.dcim.devices.update([cisco_device])
        return super().update(attrs)

    def delete(self):
        self.adapter.netbox_api.dcim.devices.delete([self.netbox_id])
        return super().delete()
