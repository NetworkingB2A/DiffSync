# Local Imports
from models.base import DNACDevice, NetboxDevice
from utils.utils import (
    convert_platform_id,
    convert_serial_number,
    validate_attributes,
    CustomNetbox,
    CustomDNAC

)

# Third-party Imports
from diffsync import Adapter
import structlog
import diffsync

logger = structlog.get_logger("dnac_netbox_adapters")


class DNACAdapter(Adapter):
    device = DNACDevice
    top_level = ["device"]

    def __init__(
        self, url, username, password, version='3.1.3.0', verify=False, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.dnac_api = CustomDNAC(
            username=username,
            password=password,
            base_url=url,
            version=version,
            verify=verify,
        )

    def load_devices(self):
        cisco_devices = self.dnac_api.get_all_dnac_devices()

        for device in cisco_devices:
            cisco_device = self.device(
                name=device.get("hostname"),
                role=device.get("role").capitalize(),
                model=convert_platform_id(device.get("platformId")),
                platform=(
                    device.get("softwareType") if device["softwareType"] else "IOS"
                ),
                serial=convert_serial_number(device.get("serialNumber")),
                status="Active",
                platform_object_uuid=device.get("instanceUuid"),
                primary_ip=device.get("managementIpAddress"),
                vendor="cisco",
            )
            try:
                validate_attributes(cisco_device)
                self.add(cisco_device)
            except diffsync.exceptions.ObjectAlreadyExists:
                logger.error(
                    f"Multiple devices found in DNAC error: {device.get('hostname')}"
                )
            except AttributeError as att_error:
                logger.error(att_error)


class NetboxAdapter(Adapter):
    device = NetboxDevice
    top_level = ["device"]

    def __init__(self, url, token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.netbox_api = CustomNetbox(url, token)

    def load_devices(self):
        GRAPH_QUERY = """
        query MyQuery {
        device_list(filters: {platform: ["cisco-ios-xe"]}) {
            id
            name
            status
            role {
            name
            }
            device_type {
            id
            part_number
            manufacturer {
                name
            }
            }
            serial
            site {
            id
            name
            }
            platform {
            id
            name
            }
            custom_fields
        }
        }"""

        cisco_devices = self.netbox_api.graphql_query(GRAPH_QUERY)
        for device in cisco_devices["data"]["device_list"]:
            custom_fields = device["custom_fields"]
            cisco_device = self.device(
                name=device.get("name"),
                role=device["role"]["name"],
                model=device["device_type"]["part_number"],
                platform=device["platform"]["name"],
                serial=device.get("serial"),
                status=device.get("status").capitalize(),
                platform_object_uuid=custom_fields.get("platform_object_uuid"),
                primary_ip=custom_fields.get("device_discovery_address"),                
                vendor=device["device_type"]["manufacturer"]["name"],
                netbox_id=device.get("id"),
            )
            self.add(cisco_device)
