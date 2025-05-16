# Local Imports
from dnacentersdk.api import DNACenterAPI

# System Imports
import re

from pynetbox.core.query import Request
from typing import Optional, Dict, Any
import pynetbox


class CustomNetbox(pynetbox.api):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def graphql_query(self, query: str, variables: Optional[Dict[str, Any]] = None):
        if not isinstance(query, str):
            raise TypeError(
                f"Query should be of type string, not of type {type(query)}"
            )

        # Check that variables coming in is a dictionary
        if variables is not None and not isinstance(variables, dict):
            raise TypeError(
                f"Variables should be of type dictionary, not of type {type(variables)}"
            )

        payload = {"query": query, "variables": variables}
        response = Request(
            base=self.base_url.replace("api", "graphql"),
            token=self.token,
            http_session=self.http_session,
        ).post(data=payload)
        return response

    def bulk_crud_action(
        self,
        item_list: list,
        application: str,
        model: str,
        verb: str,
        offset: int = 0,
        limit: int = 500,
    ):

        if len(item_list) <= 0:
            print("Empty list provided in to function")
            return {"results": None, "return": "Empty list provided in to function"}

        # Navigate to the target object
        target = self
        for part in [application, model]:
            target = getattr(target, part)

        # Get the method to call
        method = getattr(target, verb)
        results = []

        while True:
            if offset + limit < len(item_list):
                print(f"offset/total: {offset}/{len(item_list)}")
                results.append(method(item_list[offset : offset + limit]))
            elif offset + limit > len(item_list):
                print(f"offset/total: {offset}/{len(item_list)}")
                results.append(method(item_list[offset:]))
                break
            offset += limit

        return results


class CustomDNAC(DNACenterAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_all_dnac_devices(
        self,
        offset: int = 1,
        family: tuple = None,
    ) -> list[dict]:
        all_dnac_devices = []
        while True:
            dnac_devices = self.devices.get_device_list(offset=offset, family=family)[
                "response"
            ]
            all_dnac_devices.extend(dnac_devices)
            if len(dnac_devices) < 500:
                break
            else:
                offset += 500
        return all_dnac_devices

    def get_all_devices_with_tags(
        self, offset: int = 1, limit: int = 500
    ) -> list[dict]:
        all_dnac_device_tags = []
        while True:
            dnac_device_tags = self.tag.retrieve_tags_associated_with_network_devices(
                offset=offset,
                limit=limit,
            )["response"]
            all_dnac_device_tags.extend(dnac_device_tags)
            if len(dnac_device_tags) < 500:
                break
            else:
                offset += 500

        return all_dnac_device_tags


def validate_attributes(obj: object) -> None:
    if obj.serial == None or obj.model == None:
        raise AttributeError(
            f"Attribute not defined: One of the follow cannot be 'None' - {obj.name=}, {obj.serial=}, {obj.model=}"
        )
    elif "Unknown Error" in obj.status.title():
        raise AttributeError(
            f"Status unknown error - {obj.status} - {obj.name=}, {obj.dnac_id=}"
        )


def convert_device_status(error_code: str) -> str:
    """
    Converts a device error code to a corresponding DeviceStatus enum value.

    Args:
        error_code (str): The error code associated with the device.

    Returns:
        DeviceStatus: The DeviceStatus enum value corresponding to the provided error code.
    """

    if error_code is None:
        return "active"
    elif error_code in [
        "DEV-UNREACHED",
        "ERROR-CONNECTION",
        "ERROR-TIMEOUT",
        "ERROR-CONNECTION-CLOSED",
    ]:
        return "offline"
    elif error_code in [
        "SNMP-FAILED",
        "SNMP-TIMEOUT",
        "CLI-AUTH-ERROR",
        "ERROR-ENABLE-PASSWORD",
        "MISSING-ENABLE-PASSWORD",
        "ERROR-NETCONF-CONNECTION",
        "UNKNOWN",
    ]:
        return "failed"
    else:
        return f"Unknown Error: {error_code}"


def convert_platform_id(platform_id: str) -> str:
    """
    Converts a C9xxx switches to remove -E or -A from the platform_id

    Args:
        platform_id (str): platform id to check

    Returns:
        platform_id: Either the original platform id or the modified one.
    """
    if not platform_id:
        return platform_id
    if re.search("^CISCO[1|2|4]", platform_id):
        return re.sub("CISCO", "ISR", platform_id)
    if re.search(r"^C9.+(-E|-A)$", platform_id):
        return re.sub("-E|-A", "", platform_id)
    # Needed to reduce stack to the first member in the stack
    platform_id = platform_id.split(",")[0].strip()

    return platform_id


def convert_serial_number(serial_number: str) -> str:
    """
    Converts a serial number to a standard format.

    Args:
        serial_number (str): The serial number to convert.

    Returns:
        str: The converted serial number.
    """
    if not serial_number:
        return serial_number
    serial_number = serial_number.split(",")[0].strip()
    return serial_number


def is_truthy(word: str | int | bool | None) -> bool:
    if word == None:
        return False
    if isinstance(word, bool):
        return word
    truthy_patterns = r"enabled|yes|true|1"
    if re.search(truthy_patterns, word, re.IGNORECASE):
        return True
    return False


def custom_field_mapping(attrs: any) -> dict:
    custom_fields = {"data_source": "dnac"}
    for k, v in attrs.items():
        if k in [
            "platform_object_uuid",
        ]:
            custom_fields[k] = v
        elif k == "primary_ip":
            custom_fields["device_discovery_address"] = v
    return custom_fields
