# DiffSync

## Small backstory
DiffSync is a tool created by Network to code. Its used to Sync two or more systems together. They use it a lot in their Nautbot apps. Its a great tool and you should check out the [documentation](https://diffsync.readthedocs.io/en/latest/). Here a link to the [repo](https://github.com/networktocode/diffsync). I decided I wanted to write some real world automations and test out my skills to learn someone else's code and see how I would use this. This first script I created is to take devices from DNAC and populate my netbox instance. 

If you are like me and you had problems keeping Netbox/Nautobot/Any SOT tool in sync with your controllers, you should check out the tool. It's overall works great.

## How to use
In order for these scripts to work you must run it from the platform's directory. There are ways you can make this better by converting this deployment into a package, but that is outside the scope of this repo.
In the real world, I would create this as package, then I can have the ```CustomNetbox``` and the ```CustomDnac``` be shared where ever I need other scripts to use it. For ease of use I put these in the same directory area, under ```utils``` file/directory.

```bash
 cd dna_center/
```

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
For my specific use case I have created some custom fields. If you use this script the way it was created you will have to add these to Netbox or you will have to delete those attributes from the code.
Custom gields I use and you would need to set in order to make this work for you. Or playaround with the files.
- platform_object_uuid #This I use to help me know the UUID of the device in the platform. I use this for other tasks a lot.
- device_discovery_address #This is used for ansible playbooks or other python scripts I use.
- data_source #This helps me know to where the device came from.

## Notes
- I decided to only use the first member of a stack instead of the whole stack. That is why I use the convert_serial_number and the convert_platform_id. That is because I have not fully fleshed out how I want a stacked device to look.
- You will see the following in my code. This is a technique I use to drop values that are None, and I don't want to pass None values to Netbox. Netbox will update a value with None sometimes and I don't want to delete good data.
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
- If you are having some problems running this script let me know and I'll see if I can fix it.
