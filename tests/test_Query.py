import pytest
from py_graph_ql_client.Query import Query, Fragment, Resource


def test_Query():
    resource = Resource(
        name="pytest",
        variables={"first": "$first"},
        page_info=True,
        cursor=True,
        name_override="pytest",
    )
    resource.add_simple_properties(["id", "name"])
    assert resource.name == "pytest"
    assert resource.name_override == "pytest"
    assert resource.variables == {"first": "$first"}
    assert resource.cursor is True
    assert resource.page_info is True
    assert resource.is_sub_resource is False
    assert list(resource.properties) == ["id", "name"]
    assert resource.properties_to_string() == "id name"
    assert resource.fragment_queries == []
    resource_query_string = resource.generate_query()
    assert (
        resource_query_string
        == "{pytest(first: $first){pageInfo{hasNextPage matchCount} edges{cursor pytest: {id name}}}}"
    )

    sub_resource = Resource("sub", sub_resource=True)
    sub_resource.add_simple_properties(["id", "name"])
    fragment = Fragment("SUB", sub_resource)
    fragment_query_string = fragment.generate_query()
    assert fragment.name == "SUB"
    assert fragment.resource is sub_resource
    assert fragment_query_string == "fragment SUB on sub {id name}"

    resource.add_fragment("sub", fragment)
    resource_query_string = resource.generate_query()
    assert (
        resource_query_string
        == "{pytest(first: $first){pageInfo{hasNextPage matchCount} edges{cursor pytest: {id name sub {...SUB}}}}}"
    )

    query = Query(name="PyTestQuery", variables={"$first": "Int"})
    query.add_resource(resource)
    assert (
        query.generate_query()
        == "fragment SUB on sub {id name} query PyTestQuery($first: Int){pytest(first: $first){pageInfo{hasNextPage matchCount} edges{cursor pytest: {id name sub {...SUB}}}}}"
    )
