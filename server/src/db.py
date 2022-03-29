"""DB Implementation"""

import os
from typing import Any, Dict, List, Optional

import motor.motor_asyncio
from dotenv import load_dotenv

from interfaces.idb import IDB

# TODO: A lot of this code is duplicated in the indexer. Need to clean that up at some point.

load_dotenv()

#pylint: disable=line-too-long
MONGO_URI = f"mongodb://{os.environ['MONGO_USER']}:{os.environ['MONGO_PASSWORD']}@{os.environ['MONGO_HOST']}:{os.environ['MONGO_PORT']}"

class DB(IDB):
    """@inheritdoc IDB"""

    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

    def _get_collection(self, database_name: str, collection_name: str):
        return self.client[database_name][collection_name]

    async def get_item(self, identifier: str, database_name: str, collection_name: str) -> Any:
        cursor = self._get_collection(database_name, collection_name)

        result  = await cursor.find_one({"_id": identifier})
        return result

    async def count_documents(self, database_name: str, collection_name: str, options: Optional[Dict] = None) -> int:
        cursor = self._get_collection(database_name, collection_name)

        return await cursor.count_documents(options['query'] if 'query' in options else {})


    async def get_all_items(self, database_name: str, collection_name: str, limit: int = -1, options: Optional[Dict] = None) -> List[Any]:
        cursor = self._get_collection(database_name, collection_name)

        if limit == -1:
            limit = await self.count_documents(database_name, collection_name, options)

        if options is not None:

            if 'query' in options:
                cursor = cursor.find(options['query'])
            else: 
                cursor = cursor.find()

            if "sort" in options:
                # [('fieldName1', pymongo.ASCENDING), ('fieldName2', pymongo.DESCENDING)]
                cursor.sort(options["sort"])
                
            if 'collation' in options:
                cursor.collation(options["collation"])

            cursor.allow_disk_use(True)

            return await cursor.to_list(length=limit)

        return await cursor.find().to_list(length=limit)
