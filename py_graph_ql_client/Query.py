from __future__ import annotations

from typing import List, Optional, Tuple


class Query:
    def __init__(self, name: str, variables: Optional[dict] = None) -> None:
        "Initialize query Constructor"
        self.name = name
        self.variables = variables
        self._resources: List[Resource] = list()

    def generate_query(self) -> str:
        if self.variables:
            args = [f"{k}: {v}" for k, v in self.variables.items()]
        else:
            args = []
        resources = [x.generate_query() for x in self.resources]
        query = f"query {self.name}({', '.join(args)}){''.join(resources)}"
        return query

    def validate_fragments(self):
        pass

    @property
    def resources(self):
        return self._resources

    def add_resource(self, resource: Resource):
        self._resources.append(resource)


class Fragment:
    def __init__(self, name) -> None:
        self.name = name


class Resource:
    def __init__(
        self,
        name: str,
        variables: Optional[dict] = None,
        sub_resource: bool = False,
        page_info: bool = False,
        cursor: bool = False,
        name_override: Optional[str] = None
    ) -> None:
        self.name = name
        self.variables = variables
        self._properties: List[str, Tuple[str, Fragment], Resource] = list()
        self.is_sub_resource = sub_resource
        self.page_info = page_info
        self.cursor = cursor
        self.name_override = name_override

    @property
    def properties(self):
        return self._properties

    def add_simple_properties(self, properties: List[str]):
        self._properties.extend(properties)

    def add_sub_resource(self, resource: Resource):
        if resource.is_sub_resource:
            self._properties.append(resource)
        else:
            # TODO: Some sort of Error Handling
            pass

    def add_fragment(self, property: str, fragment: Fragment):
        self._properties.append((property, fragment))

    def generate_query(self):
        if self.is_sub_resource:
            pass
        else:
            if self.variables:
                args = [f"{k}: {v}" for k, v in self.variables.items()]
            else:
                args = []
            if self.page_info:
                page_info = "{pageInfo{hasNextPage matchCount} "
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
            properties = list()
            for property in self.properties:
                if isinstance(property, Resource):
                    properties.append(property.generate_query())
                if isinstance(property, tuple):
                    properties.append(f"{property[0]}: ...{property[1].name}")
                else:
                    properties.append(f"{property}")
            query = f"{{{self.name}({', '.join(args)}){{{page_info}edges{{{cursor}{nodes}{{{' '.join(properties)}}}}}}}}}"

            return query
