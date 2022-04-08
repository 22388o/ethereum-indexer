"""
IDB Implementation using pymongo package
"""
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pymongo import MongoClient

from interfaces.idb import IDB

load_dotenv()


def check_environ(env_var: str) -> None:
    """
    Checks if environment variable is set

    Args:
        env_var (str): environment variable to check for
    """
    if not os.getenv(env_var):
        raise ValueError(f"{env_var} environment variable not set.")


check_environ("MONGO_URI")


class DB(IDB):
    """@inheritdoc IDB"""

    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI"))

    def put_item(self, item: Dict, database_name: str, collection_name: str) -> None:
        db = self.client[database_name]
        db[collection_name].replace_one({"_id": item["_id"]}, item, upsert=True)

    def put_items(
        self, items: List[Any], database_name: str, collection_name: str
    ) -> None:
        if len(items) == 0:
            return

        db = self.client[database_name]
        db[collection_name].insert_many(items)

    def get_item(
        self, identifier: str, database_name: str, collection_name: str
    ) -> Any:
        db = self.client[database_name]
        try:
            return db[collection_name].find({"_id": identifier})[0]
        except Exception:
            return None

    # todo: concrete type for options
    def get_all_items(
        self, database_name: str, collection_name: str, options: Optional[Dict] = None
    ) -> List[Any]:
        db = self.client[database_name]

        if options is None:
            return list(db[collection_name].find())

        if "sort" in options:
            # todo: validation
            sort_by = options["sort"]["sort_by"]
            direction = options["sort"]["direction"]

            query_clause = {}

            if "query_clause" in options:
                query_clause = options["query_clause"]

            return list(
                db[collection_name]
                .find(query_clause, allow_disk_use=True)
                .sort(sort_by, direction)
            )

        # todo: not really needed here, but pylint will complain
        # todo if removed
        return list(db[collection_name].find())

    def get_any_item(
        self, database_name: str, collection_name: str, _: Optional[Dict] = None
    ) -> Any:
        """
        MongoDB will return an empty list is collection does not exist
        """
        all_items = self.get_all_items(database_name, collection_name)
        if len(all_items) == 0:
            return None
        return all_items[0]
