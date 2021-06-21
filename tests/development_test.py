from py_graph_ql_client.Query import Query, Resource

query = Query('DeviceFetch', {'$search': 'DeviceSearch', '$order': '[ConnectionOrder]', '$first': 'Int'})

resource = Resource('devices', {'first': '$first', 'search': '$search', 'after': '""', "order": "$order"}, page_info=True, cursor=True, name_override="device")
resource.add_simple_properties(['id', 'name'])

query.add_resource(resource)

print(query.generate_query())