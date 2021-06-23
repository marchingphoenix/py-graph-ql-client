from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import chain
from typing import List, Optional, Tuple, Union


class GQLObject(ABC):
    name = str()
    variables = None

    @abstractmethod
    def generate_query(self):
        raise NotImplementedError

    def args_list_to_query(self) -> str:
        if self.variables:
            return ", ".join([f"{k}: {v}" for k, v in self.variables.items()])
        else:
            return str()


class Query(GQLObject):
    def __init__(self, name: str, variables: Optional[dict] = None) -> None:
        "Initialize query Constructor"
        self.name = name
        self.variables = variables
        self._resources: List[Resource] = list()

    def generate_query(self) -> str:
        fragments = list()
        resources = list()
        for resource in self.resources:
            resources.append(resource.generate_query())
            fragments.extend(resource.fragment_queries)
        query = f"query {self.name}({self.args_list_to_query()}){''.join(resources)}"
        if fragments:
            query = f"{' '.join(fragments)} {query}"
        return query

    def validate_fragments(self):
        pass

    @property
    def resources(self):
        return self._resources

    def add_resource(self, resource: Resource):
        self._resources.append(resource)


class Fragment(GQLObject):
    def __init__(self, name: str, resource: Resource) -> None:
        self.name = name
        self.resource = resource

    def generate_query(self) -> str:
        return f"fragment {self.name} on {self.resource.name} {{{self.resource.properties_to_string()}}}"


class Resource(GQLObject):
    def __init__(
        self,
        name: str,
        variables: Optional[dict] = None,
        sub_resource: bool = False,
        page_info: bool = False,
        cursor: bool = False,
        name_override: Optional[str] = None,
    ) -> None:
        self.name = name
        self.variables = variables
        self._properties: List[Union[str, Resource]] = list()
        self.is_sub_resource = sub_resource
        self.page_info = page_info
        self.cursor = cursor
        self.name_override = name_override
        self._fragments: List[Tuple[str, Fragment]] = list()

    @property
    def properties(self):
        for property in chain(self._properties, self._fragments):
            yield property

    @property
    def fragment_queries(self):
        if self._fragments:
            return [x[1].generate_query() for x in self._fragments]
        else:
            return list()

    def add_simple_properties(self, properties: List[str]):
        self._properties.extend(properties)

    def add_sub_resource(self, resource: Resource):
        self._properties.append(resource)

    def add_fragment(self, property: str, fragment: Fragment):
        self._fragments.append((property, fragment))

    def properties_to_string(self) -> str:
        properties = list()
        for property in self.properties:
            if isinstance(property, Resource):
                properties.append(property.generate_query())
            if isinstance(property, tuple):
                properties.append(f"{property[0]} {{...{property[1].name}}}")
            else:
                properties.append(f"{property}")
        return " ".join(properties)

    def generate_query(self) -> str:
        if self.is_sub_resource:
            pass
        else:
            if self.page_info:
                page_info = "pageInfo{hasNextPage matchCount} "
            else:
                page_info = ""
            if self.cursor:
                cursor = "cursor "
            else:
                cursor = ""
            if self.name_override:
                nodes = f"{self.name_override}: "
            else:
                nodes = ""
            query = f"{{{self.name}({self.args_list_to_query()}){{{page_info}edges{{{cursor}{nodes}{{{self.properties_to_string()}}}}}}}}}"

            return query
