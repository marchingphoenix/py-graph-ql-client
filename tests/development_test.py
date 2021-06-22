from py_graph_ql_client.Query import Fragment, Query, Resource

query = Query('DeviceFetch', {'$search': 'DeviceSearch', '$order': '[ConnectionOrder]', '$first': 'Int'})

asset = Resource('asset', sub_resource=True)
asset.add_simple_properties(['id', 'name'])
fragment = Fragment('asset', asset)
devices = Resource('devices', {'first': '$first', 'search': '$search', 'after': '""', "order": "$order"}, page_info=True, cursor=True, name_override="device")
devices.add_simple_properties(['id', 'name'])
devices.add_fragment('asset', fragment)

query.add_resource(devices)

print(query.generate_query())