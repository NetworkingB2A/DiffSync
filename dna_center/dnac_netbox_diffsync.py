# Local Imports
from adapters.dnac_netbox_adapters import (
    DNACAdapter,
    NetboxAdapter,
)

# Third-party Imports
from diffsync.logging import enable_console_logging
from dotenv import load_dotenv
import structlog

# System Imports
from pprint import pprint
import argparse
import os

logger = structlog.get_logger("dnac_netbox_diffsync")

help_description = """
This tool is to help you keep your Netbox instance in sync with your DNA Center.
The current configuration of this tool will make DNAC as the inventory truth source and preform CRUD actions to Netbox based on DNAC data.
This can be used, but its main goal is to show you a real world example of using DiffSync."""


def get_netbox_env_vars():
    netbox_url = os.getenv("NETBOX_API")
    netbox_token = os.getenv("NETBOX_TOKEN")
    return netbox_url, netbox_token


def get_dnac_env_vars():
    dnac_url = os.getenv("DNAC_URL")
    dnac_username = os.getenv("DNAC_USERNAME")
    dnac_password = os.getenv("DNAC_PASSWORD")
    return dnac_url, dnac_username, dnac_password


def arg_parse_config():
    parser = argparse.ArgumentParser(
        "DNAC diff sync",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=help_description,
    )
    parser.add_argument("--verbosity", "-v", default=0, action="count")
    parser.add_argument(
        "--diff",
        "-d",
        action="store_true",
        help="Use this flag if you would like see the difference that this tool finds",
    )
    parser.add_argument(
        "--sync",
        "-s",
        action="store_true",
        help="Use this flag if you would like the tool to make changes in netbox for you.",
    )
    return parser


args = arg_parse_config().parse_args()


if not args.sync and not args.diff:
    arg_parse_config.error("please select (--diff, -d) or (--sync, -s)")

load_dotenv()


netbox_url, netbox_token = get_netbox_env_vars()
dnac_url, dnac_username, dnac_password = get_dnac_env_vars()

enable_console_logging(verbosity=args.verbosity)

dnac_adapter = DNACAdapter(
    url=dnac_url,
    username=dnac_username,
    password=dnac_password,
    version="3.1.3.0",
    verify=False,
)
dnac_adapter.load_devices()

netbox_adapter = NetboxAdapter(url=netbox_url, token=netbox_token)
netbox_adapter.load_devices()

# destination.diff_from(source)
diff = netbox_adapter.diff_from(dnac_adapter)

if args.diff:
    pprint(netbox_adapter.dict())
    pprint(dnac_adapter.dict())
    pprint(diff.dict())
if args.sync:
    netbox_adapter.sync_from(dnac_adapter, diff=diff)
print(diff.str())
logger.info(diff.summary())
