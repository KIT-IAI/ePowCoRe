"""A set of wrapper classes around standard networkx views.
These wrappers restrict access and manipulation to the underlying data,
and in turn provide type guarantees for the accessed data.
"""

from collections.abc import Iterable
from typing import Iterator

import networkx as nx

from epowcore.gdf.component import Component


class ComponentNodeView:
    """A typed wrapper around networkx's NodeView.

    This wrapper supports the most important access methods for nodes.
    Further functionality can be added, when needed.
    """

    # More methods can be added accoring to collections.abc:
    # https://docs.python.org/3/library/collections.abc.html

    def __init__(self, node_view: nx.classes.reportviews.NodeView) -> None:
        self._node_view = node_view

    def __len__(self) -> int:
        return len(self._node_view)

    def __iter__(self) -> Iterator[Component]:
        return iter(self._node_view)

    def __getitem__(self, n: Component) -> dict:
        # No types specified for node attributes.
        return self._node_view[n]

    def __contains__(self, n: Component) -> bool:
        return n in self._node_view

    def __str__(self) -> str:
        return str(self._node_view)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({tuple(self)})"


class ComponentEdgeView:
    """A typed wrapper around networkx's EdgeView.

    This wrapper cleans up the data access interface, making each method less flexible,
    and in turn more expressive and more strictly typed.
    """

    def __init__(
        self, edge_view: nx.classes.reportviews.EdgeView
    ) -> None:
        self._edge_view = edge_view

    def __len__(self) -> int:
        return len(self._edge_view)

    def __iter__(self) -> Iterator[tuple[Component, Component]]:
        return iter(self._edge_view)

    def __getitem__(self, e: tuple[Component, Component]) -> dict[int, list[str]]:
        return self._edge_view[e]

    def __contains__(self, e: tuple[Component, Component]) -> bool:
        return e in self._edge_view

    def __str__(self) -> str:
        return str(self._edge_view)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({tuple(self)})"

    def __call__(
        self, nbunch: Component | Iterable[Component] | None = None
    ) -> Iterable[tuple[Component, Component]]:
        # Same as .edges, optional filter for node(s)
        return self._edge_view(nbunch=nbunch)

    def data(
        self, nbunch: Component | Iterable[Component] | None = None
    ) -> Iterable[tuple[Component, Component, dict[int, list[str]]]]:
        """Return an iterable with tuples of edges and their corresponding data as a dict.
        Like the original method, just without the option to filter by key. Use `.attr(key)` instead.

        Args:
            nbunch (Component | Iterable[Component] | None, optional): Nodes to include. Defaults to None.

        Returns:
            Iterable[tuple[Component, Component, dict[int, list[str]]]]: An iterable with tuples of edges and edge data.
        """
        return self._edge_view.data(data=True, nbunch=nbunch)

    def attr(
        self,
        key: int,
        default: list[str] | None = None,
        nbunch: Component | Iterable[Component] | None = None,
    ) -> Iterable[tuple[Component, Component, list[str] | None]]:
        """Return an iterable with tuples of edges and the given attribute.
        This replaces the original `.edges.data(key)` of networkx.

        Args:
            key (int): The key of the attribute.
            default (list[str] | None, optional): A default value for the attribute. Defaults to None.
            nbunch (Component | Iterable[Component] | None, optional): Nodes to include. Defaults to None.

        Returns:
            Iterable[tuple[Component, Component, list[str] | None]]: An iterable of tuples with edges and the requested attribute.
        """
        return self._edge_view.data(data=key, default=default, nbunch=nbunch)  # type: ignore

    def update(
        self, u_of_edge: Component, v_of_edge: Component, data: dict[int, list[str]]
    ) -> None:
        """Update the data attached to the specified edge.

        This is the preferred method to update/set edge data,
        compared to the traditional `.edges[u, v].update(data)`.

        Args:
            u_of_edge (Component): One node of the edge.
            v_of_edge (Component): The other node of the edge.
            data (dict[int, list[str]]): The data to add to the edge data dict.
        """
        self._edge_view[u_of_edge, v_of_edge].update(data)
