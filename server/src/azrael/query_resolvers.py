"""azrael Graphql query resolver"""

from typing import Callable, Dict, List, Optional

import pymongo
from db import DB
from tartiflette import Resolver

from azrael.event import (AzraelEvent, CollateralClaimedEvent,
                             LendingStoppedEvent, LentEvent, RentedEvent,
                             ReturnedEvent)

DATABASE_NAME = 'ethereum-indexer'
COLLECTION_NAME = '0x94D8f036a0fbC216Bb532D33bDF6564157Af0cD7-state'

db = DB()

# TODO: This method is almost identical to one inside sylvester.query_resolver
async def resolve_event(name: str, args: Dict, transformer: Callable, 
    sort_by: Optional[str] = 'lendingId') -> List[AzraelEvent]:
    """
    Resolves azrael event graphql query generically.

    Args:
        name (str): name of the event
        args (Dict): Graphql function parameters specified in query
        transformer (Callable): Callable function that map a mongodb doc to azrael event
        sort_by (Optional[str]): Index to sort mongodv results by. Defaults to 'lendingId'

    Returns:
        List[Event]: List of azrael events.
    """

    limit = args['limit']
    order = pymongo.ASCENDING if args['ascending'] else pymongo.DESCENDING

    query  = {'event': name}
    sort = [(sort_by, order)]

    options = {'query': query, 'sort': sort}

    results  = await db.get_all_items(DATABASE_NAME, COLLECTION_NAME, limit, options)

    return list(map(transformer, results))

@Resolver("Query.getLentEvents")
async def resolve_get_lent_events(_parent, args, _ctx, _info) -> List[LentEvent]:
    """
    Resolves 'getLentEvents' graphql query for the Graphql Engine.

    Returns:
        List[LentEvent]: Event instance compatible with LentEvent Azrael Graphql schema.
    """

    return await resolve_event('Lent', args, LentEvent.from_doc)



@Resolver("Query.getRentedEvents")
async def resolve_get_rented_events(_parent, args, _ctx, _info) -> List[RentedEvent]:
    """
    Resolves 'getRentedEvents' graphql query for the Graphql Engine.

    Returns:
        List[RentedEvent]: Event instance compatible with RentedEvent Azrael Graphql schema.
    """

    return await resolve_event('Rented', args, RentedEvent.from_doc)


@Resolver("Query.getReturnedEvents")
async def resolve_get_returned_events(_parent, args, _ctx, _info) -> List[ReturnedEvent]:
    """
    Resolves 'getReturnedEvents' graphql query for the Graphql Engine.

    Returns:
        List[ReturnedEvent]: Event instance compatible with ReturnedEvent Azrael Graphql schema.
    """

    return await resolve_event('Returned', args, ReturnedEvent.from_doc)


@Resolver("Query.getLendingStoppedEvents")
async def resolve_get_lending_stopped_events(_parent, args, _ctx, _info
    ) -> List[LendingStoppedEvent]:
    """
    Resolves 'getLendingStoppedEvents' graphql query for the Graphql Engine.

    Returns:
        List[LendingStoppedEvent]: Event instance compatible with LendingStopped
        Azrael Graphql schema.
    """

    return await resolve_event('LendingStopped', args, LendingStoppedEvent.from_doc)


@Resolver("Query.getCollateralClaimedEvents")
async def resolve_get_collateral_claimed_events(_parent, args, _ctx, _info
    ) -> List[CollateralClaimedEvent]:
    """
    Resolves 'getCollateralClaimedEvents' graphql query for the Graphql Engine.

    Returns:
        List[CollateralClaimedEvent]: Event instance compatible with CollateralClaimed 
        Azrael Graphql schema.
    """

    return await resolve_event('CollateralClaimed', args, CollateralClaimedEvent.from_doc)
