"""
Azrael contract structs

Lending, Renting, LendingRenting, NFTs
"""

# pylint: disable=invalid-name,relative-beyond-top-level

from dataclasses import dataclass, field
from typing import List, Union, Tuple
import operator
import itertools
from .event import (RentedEvent, ReturnedEvent, LendingStoppedEvent,
                         LentEvent, CollateralClaimedEvent)

@dataclass(frozen=True)
class NFT:
    """NFT"""

    nftAddress: str
    tokenId: str

@dataclass(frozen=True, order=True)
class Lending:
    """Lending"""

    # pylint: disable=too-many-instance-attributes
    lendingId: int = field(compare=True)
    lentAmount: int
    maxRentDuration: int
    paymentToken: int
    lendersAddress: str
    dailyRentPrice: float
    nftPrice: float
    isERC721: bool
    collateralClaimedAt: int


@dataclass(frozen=True)
class Renting:
    """Renting"""

    renterAddress: str
    rentDuration: int
    rentedAt: int
    returnedAt: Union[int, None]

@dataclass
class LendingRenting:
    """LendingRenting"""


    Events = Union[
        LentEvent, RentedEvent, ReturnedEvent,
        LendingStoppedEvent, CollateralClaimedEvent
    ]

    _id: str # for mongodb
    nft: NFT
    lending: Lending
    rentings: List[Renting] = field(default=list)


    @classmethod
    def from_events(cls, events: List[Events]):
        """Factory method for LendingRenting"""

        lent_event: LentEvent = events[0]

        if lent_event['event'] != 'Lent':
            raise Exception("Weird. Lent event should always be the first event.")

        # List of Rented events, preserve cronological order
        rented_events: List[RentedEvent] = list(filter(lambda x: x['event'] == 'Rented', events))

        # List of Returned events, preserve cronological order
        returned_events: List[ReturnedEvent] = list(filter(lambda x: x['event'] == 'Returned', events))

        # Group them into tuples of (RentedEvent, ReturnedEvent), (RentedEvent, ReturnedEvent), ...
        # Notice that the last tuple may be (RentedEvent, None) if the rental has not been returned
        rented_returned: List[Tuple(RentedEvent, ReturnedEvent)] = itertools.zip_longest(
            rented_events, returned_events, fillvalue=None
        )

        rentings: List[Renting] = []
        for rented, returned in rented_returned:
            renting: Renting = Renting(
                renterAddress=rented['renterAddress'],
                rentDuration=rented['rentDuration'],
                rentedAt=rented['rentedAt'],
                # the rental may not be returned yet
                returnedAt=returned['returnedAt'] if returned is not None else None
            )

            rentings.append(renting)


        collateral_claimed_events: List[CollateralClaimedEvent] = list(
            filter(lambda x: x['event'] == 'CollateralClaimed', events)
        )
        collateral_claimed_at: Union[int, None] = None
        if len(collateral_claimed_events) > 0:
            # If collateral was claimed, it will always be the last event
            collateral_claimed_at = collateral_claimed_events[0]['claimedAt']

        lending = Lending(
            lendingId=lent_event['lendingId'],
            lentAmount=lent_event['lentAmount'],
            maxRentDuration=lent_event['maxRentDuration'],
            paymentToken=lent_event['paymentToken'],
            lendersAddress=lent_event['lendersAddress'],
            dailyRentPrice=lent_event['dailyRentPrice'],
            nftPrice=lent_event['nftPrice'],
            isERC721=lent_event['isERC721'],
            collateralClaimedAt=collateral_claimed_at
        )

        nft = NFT(nftAddress=lent_event['nftAddress'], tokenId=lent_event['tokenId'])

        return LendingRenting(
            _id=lending.lendingId,
            nft=nft,
            lending=lending,
            rentings=rentings
        )
