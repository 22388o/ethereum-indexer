"""
We use formal interfaces to enforce **modularity** first and foremost, and then structure
onto all of the code that is to be written.

Think of this as mathematical axioms, with which you then build proofs which you then use
together to build new proofs.
"""
import abc
from typing import Any, Dict, List, Optional

# TODO: some of the items below can raise. Write docs for it
# TODO: A lot of this code is duplicated in the indexer. Need to clean that up at some point.


class IDB(metaclass=abc.ABCMeta):
    #pylint: disable=missing-class-docstring

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "get_item")
            and callable(subclass.get_item)
            or NotImplemented
        )

    @abc.abstractmethod
    async def get_item(
        self, identifier: str, database_name: str, collection_name: str
    ) -> Any:
        """_summary_

        Args:
            identifier (str): the document '_id'
            database_name (str): name of the database
            collection_name (str): name of the collection

        Raises:
            NotImplementedError: _description_

        Returns:
            Any: _description_
        """
        raise NotImplementedError


    @abc.abstractmethod
    async def get_all_items(
        self, database_name: str, collection_name: str, limit: int, options: Optional[Dict]
    ) -> List[Any]:
        """_summary_

        Args:
            database_name (str): name of the database
            collection_name (str): name of the collection
            limit (int): Maximum amount of items to fetch
            options (Optional[Dict]): "query", "sort"

        Raises:
            NotImplementedError: _description_

        Returns:
            List[Any]: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def count_documents(
        self, database_name: str, collection_name: str, options: Optional[Dict]
    ) -> int:
        """_summary_

        Args:
            database_name (str): name of the database
            collection_name (str): name of the collection

        Raises:
            NotImplementedError: _description_

        Returns:
            Any: _description_
        """
        raise NotImplementedError
