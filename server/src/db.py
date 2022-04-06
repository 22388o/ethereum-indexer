"""DB Implementation"""

import os
from typing import Any, Dict, List, Optional

import motor.motor_asyncio
from dotenv import load_dotenv

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
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))

    def _get_collection(self, database_name: str, collection_name: str):
        return self.client[database_name][collection_name]

    async def get_item(
        self, identifier: str, database_name: str, collection_name: str
    ) -> Any:
        cursor = self._get_collection(database_name, collection_name)

        result = await cursor.find_one({"_id": identifier})
        return result

    async def count_documents(
        self, database_name: str, collection_name: str, options: Optional[Dict] = None
    ) -> int:
        cursor = self._get_collection(database_name, collection_name)

        return await cursor.count_documents(
            options["query"] if "query" in options else {}
        )

    async def get_all_items(
        self,
        database_name: str,
        collection_name: str,
        limit: int = -1,
        options: Optional[Dict] = None,
    ) -> List[Any]:
        cursor = self._get_collection(database_name, collection_name)

        if limit == -1:
            limit = await self.count_documents(database_name, collection_name, options)

        if options is not None:

            if "query" in options:
                cursor = cursor.find(options["query"])
            else:
                cursor = cursor.find()

            if "sort" in options:
                # [('fieldName1', pymongo.ASCENDING), ('fieldName2', pymongo.DESCENDING)]
                cursor.sort(options["sort"])

            if "collation" in options:
                cursor.collation(options["collation"])

            cursor.allow_disk_use(True)

            return await cursor.to_list(length=limit)

        return await cursor.find().to_list(length=limit)
