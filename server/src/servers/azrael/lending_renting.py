"""
Azrael contract structs

Lending, Renting, LendingRenting, NFTs
"""

# See URL: 
# https://stackoverflow.com/questions/33533148
# /how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations


# pylint: disable=invalid-name,relative-beyond-top-level

from dataclasses import dataclass, field, asdict
from typing import List, Union
from dacite import from_dict

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
    def from_mongo_doc(doc) -> LendingRenting:
        """Parses mongo doc to LendingRenting dataclass"""
        return from_dict(data_class=LendingRenting, data=doc)
