# DiffSync



In order for these scripts to work you must run it from the platform's directory. There are ways you can make this better by converting this deployment into a package, but that is outside the scope of this repo.
In the real world, I would create this as package, then I can have the ```CustomNetbox``` and the ```CustomDnac``` be shared where ever I need other scripts to use it. For ease of use I put these in the same directory area, under ```utils```

```bash
dna_center/
```

How to run

```bash
python dnac_netbox_diffsync.py -s -d -vvv
```

I have a .env file created and I load my environmental variables from there for use of use. Example of my .env file.
```bash
# Netbox Cloud prod
NETBOX_API='https://demo.netbox.dev/'
NETBOX_TOKEN='**********************************ef38f4'

# Sandbox DNAC
DNAC_URL='https://sandboxdnac.cisco.com'
DNAC_USERNAME='devnetuser'
DNAC_PASSWORD='Cisco123!'
```
## Custom Fields in Netbox
Custom Fields I use and you would need to set in order to make this work for you. Or playaround with the files.
- platform_object_uuid #This I use to help me know the UUID of the device in the platform. I use this for other tasks a lot.
- device_discovery_address #This is used for ansible playbooks or other python scripts I use.
- data_source #This helps me know to where the device came from.

Notes
- I decided to only use the first member of a stack instead of the whole stack. That is why I use the convert_serial_number and the convert_platform_id
- You will see this a lot in my code. This is a technique I use to drop values that are None and I don't want to pass None values to Netbox. 
    **({"role": {"name": attrs["role"]}} if attrs.get("role") is not None else {}),
    EXAMPLE - Create a dictionary and drops any values that might be None.
    ```python
        >>> device_1 = {
        ...     "name": "router1",
        ...     "ip_address": "192.168.1.1",
        ...     "serial_number": "123456789",
        ...     "random": None
        ... }
        >>> 
        >>> device_1_none_removed = {
        ...     "hostname": device_1.get("name"),
        ...     "address": device_1.get("ip_address"),
        ...     "serial_number": device_1.get("serial_number"),
        ...     **({"random_value":device_1.get("random")} if device_1.get("random") else {})
        ... }
        >>> print(device_1)
        {'name': 'router1', 'ip_address': '192.168.1.1', 'serial_number': '123456789', 'random': None}
        >>> print(device_1_none_removed)
        {'hostname': 'router1', 'address': '192.168.1.1', 'serial_number': '123456789'}
    ```
