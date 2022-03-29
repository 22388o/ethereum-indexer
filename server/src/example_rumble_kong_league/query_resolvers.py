"""RKL Holders Graphql Resolver"""

from typing import Dict, List

from db import DB
from tartiflette import Resolver

DATABASE_NAME = 'ethereum-indexer'
COLLECTION_NAME = '0xEf0182dc0574cd5874494a120750FD222FdB909a-state'

db = DB()

@Resolver("Query.kongsByAddress")
async def resolve_kongs_by_address(_parent, args, _ctx, _info) -> Dict:
    """
    Resolves 'kongsByAddress' graphql query for the Graphql Engine.

    Returns:
        Dict: Mapping of kong id to wallet address, compatible with RKL Graphql schema.
    """
    wallet_address = args['address']

    result  = await db.get_item(1, DATABASE_NAME, COLLECTION_NAME)
    return result[wallet_address]



@Resolver("Query.kongHolders")
async def resolve_kong_holders(_parent, _args, _ctx, _info) -> List[str]:    
    """
    Resolves 'kongHolders' graphql query for the Graphql Engine.

    Returns:
        List[str]: List of wallet addresses that are kong holders, compatible with RKL Graphql schema.
    """

    result  = await db.get_item(1, DATABASE_NAME, COLLECTION_NAME)

    del result['_id'] # remove index
    return list(result.keys())
