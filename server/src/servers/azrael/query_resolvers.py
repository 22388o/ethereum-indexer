"""Azrael Graphql query resolver"""

from typing import Callable, Dict, List, Optional


# disable this pylint to preserve modularity
# pylint: disable=relative-beyond-top-level

import pymongo
from azrael.lending_renting import LendingRenting
from .dtos.lending import Lending
from tartiflette import Resolver
from db import DB




DATABASE_NAME = "ethereum-indexer"
COLLECTION_NAME = "0x94D8f036a0fbC216Bb532D33bDF6564157Af0cD7-state"

db = DB()

async def get_lending_renting(identifier) -> LendingRenting:
    """Fetches and parses mongo doc into LendingRenting Dataclass"""
    doc = await db.get_item(
        identifier=int(identifier),
        database_name=DATABASE_NAME,
        collection_name=COLLECTION_NAME
    )

    return LendingRenting.from_mongo_doc(doc)

@Resolver("Query.Lending")
async def resolve_get_lent_events(_parent, args, _ctx, _info) -> Lending:
    """
    Resolves 'Lending' graphql query for the Graphql Engine.

    Args:
        ID (int): lendingId

    Returns:
        Lending: ReNFT Lending
    """

    lending_renting: LendingRenting = await get_lending_renting(args['id'])

    # Missing Nft and lenderUser fields
    lending = Lending.from_lending_renting(lending_renting)

    return lending
