"""
Azrael contract structs

Lending, Renting, LendingRenting, NFTs
"""

# pylint: disable=invalid-name,relative-beyond-top-level

from dataclasses import dataclass, field, asdict
from typing import List, Union
from dacite import from_dict
from .event import (RentedEvent, ReturnedEvent, LendingStoppedEvent,
                         LentEvent, CollateralClaimedEvent)

@dataclass(frozen=True)
class NFT:
    """NFT DTO"""

    nftAddress: str
    tokenId: str

    def to_dict(self):
        """Return a dict representation of this struct"""
        return asdict(self)

@dataclass(frozen=True, order=True)
class Lending:
    """Lending DTO"""

    # pylint: disable=too-many-instance-attributes
    lendingId: int = field(compare=True)
    lentAmount: int
    maxRentDuration: int
    paymentToken: int
    lendersAddress: str
    dailyRentPrice: float
    nftPrice: float
    isERC721: bool

    @classmethod
    def from_lent_event(cls, event: LentEvent):
        """Factory method for Lending"""

        return cls(
            lendingId=event.lendingId,
            lentAmount=event.lentAmount,
            maxRentDuration=event.maxRentDuration,
            paymentToken=event.paymentToken,
            lendersAddress=event.lendersAddress,
            dailyRentPrice=event.dailyRentPrice,
            nftPrice=event.nftPrice,
            isERC721=event.isERC721,
        )

    def to_dict(self):
        """Return a dict representation of this struct"""
        return asdict(self)

@dataclass(unsafe_hash=True)
class Renting:
    """Renting DTO"""

    renterAddress: str
    rentDuration: int
    rentedAt: int
    returnedAt: Union[int, None]  = field(default=None)

    @classmethod
    def from_rented_event(cls, event: RentedEvent):
        """Factory method for Renting"""
        return cls(
            renterAddress=event.renterAddress,
            rentDuration=event.rentDuration,
            rentedAt=event.rentedAt,
        )

    def to_dict(self):
        """Return a dict representation of this struct"""
        return asdict(self)

@dataclass
class LendingRenting:
    """LendingRenting DTO"""

    nft: NFT
    lending: Lending
    _id: int = field(default=None, compare=True) # id for mongodb doc
    stoppedAt: Union[int, None] = field(default=None)
    collateralClaimedAt: Union[int, None] = field(default=None)
    rentings: List[Renting] = field(default_factory=lambda: [])

    def __post_init__(self):
        self._id = self.lending.lendingId

    @staticmethod
    def from_mongo_doc(mongo_doc):
        """Parses mongo doc to LendingRenting dataclass"""
        return from_dict(data_class=LendingRenting, data=mongo_doc)

    def to_dict(self):
        """Return a dict representation of this struct"""
        return asdict(self)

    def insert_rented(self, event: RentedEvent):
        """Insert rented event"""

        self.rentings.append(Renting.from_rented_event(event))
        self._sort_and_reduce_rentings()

    def insert_collateral_claimed(self, event: CollateralClaimedEvent):
        """Insert CollateralClaimedEvent"""
        self.collateralClaimedAt = event.claimedAt

    def insert_lending_stopped(self, event: LendingStoppedEvent):
        """Insert StopLendingEvent"""
        self.stoppedAt = event.stoppedAt

    def insert_returned(self, event: ReturnedEvent):
        """Insert returned event"""
        self.rentings.append(event)
        self._sort_and_reduce_rentings()

    def _sort_and_reduce_rentings(self):
        """
        Merges Returned and Rented events into Rented events. Organizes cronologically
        """

        # Need 2 or more elements to sort/reduce
        if len(self.rentings) < 2:
            return

        # shallow copy + remove duplicates
        aux_list = list(set(self.rentings))

        def sort_by(dto: Union[RentedEvent, ReturnedEvent]):
            return dto.rentedAt if hasattr(dto, 'rentedAt') else dto.returnedAt

        # put them in cronological order
        aux_list.sort(key=sort_by)

        # reduce ReturnedEvents + RentedEvents into only RentedEvents (with returnedAt field populated)
        index = 1
        while index <= len(aux_list) - 1:
            a = aux_list[index - 1]
            b = aux_list[index]
            if hasattr(b, 'returnedAt'):
                if hasattr(a, 'rentedAt'):
                    a.returnedAt = b.returnedAt
                    aux_list[index] = None # Null out the ReturnedEvent

            index += 1

        # Remove Nulled ReturnedEvents
        aux_list = list(filter(lambda x: x is not None, aux_list))
        self.rentings = aux_list


    @classmethod
    def from_lent_event(cls, event: LentEvent):
        """Factory method for LendingRenting"""

        lending = Lending.from_lent_event(event)

        nft = NFT(nftAddress=event.nftAddress, tokenId=event.tokenId)

        return cls(lending=lending, nft=nft)
