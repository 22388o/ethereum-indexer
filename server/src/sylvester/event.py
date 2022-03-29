"""
This class defines ALL events emitted by the sylvester contract.

Event List: Lend, Rent, StopRent, StopLend, RentClaimed
"""

from abc import ABC
from dataclasses import dataclass


@dataclass
class SylvesterEvent(ABC):
    """
    Abstract sylvester Event. Holds txHash and txOffset, togther they are a unique
    identifier for sylvester events.
    """

    # pylint: disable=invalid-name
    txHash: str
    txOffset: int

    @staticmethod
    def parse_id(_id: str):
        """
        Parses '_id' to txHash and txOffset.

        Args:
            _id (str): mongodb '_id'
            e.i. 0xf79edc5500218427d22d4215799fb51064c633ca919c0406b830ed5dc3c6eb1a_100

        Returns:
            str: txHash
            int: txOffset
        """
        _id = _id.split("_")

        return _id[0], int(_id[1])


@dataclass
class LendEvent(SylvesterEvent):
    """
    LendEvent DTO (Data Transfer Object)

    Holds the event data for sylvester 'Lend' event.
    """

    # pylint: disable=invalid-name,too-many-instance-attributes
    is721: bool
    lenderAddress: str
    nftAddress: str
    tokenID: str
    lendingID: int
    maxRentDuration: int
    dailyRentPrice: float
    lendAmount: int
    paymentToken: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'Lend' sylvester event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = SylvesterEvent.parse_id(doc["_id"])

        del doc["_id"]
        del doc["event"]

        return cls(txHash, txOffset, **doc)


@dataclass
class RentEvent(SylvesterEvent):
    """
    RentEvent DTO (Data Transfer Object)

    Holds the event data for sylvester 'Rent' event.
    """

    # pylint: disable=invalid-name
    lendingID: int
    renterAddress: str
    rentDuration: int
    rentAmount: int
    rentingID: int
    rentedAt: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'Rent' sylvester event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = SylvesterEvent.parse_id(doc["_id"])

        del doc["_id"]
        del doc["event"]

        return cls(txHash, txOffset, **doc)


@dataclass
class StopRentEvent(SylvesterEvent):
    """
    StopRentEvent DTO (Data Transfer Object)

    Holds the event data for sylvester 'StopRent' event.
    """

    # pylint: disable=invalid-name
    rentingID: int
    stoppedAt: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'StopRent' sylvester event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = SylvesterEvent.parse_id(doc["_id"])

        return cls(
            txHash, txOffset, rentingID=doc["rentingID"], stoppedAt=doc["stoppedAt"]
        )


@dataclass
class StopLendEvent(SylvesterEvent):
    """
    StopLendEvent DTO (Data Transfer Object)

    Holds the event data for sylvester 'StopLend' event.
    """

    # pylint: disable=invalid-name
    lendingID: int
    stoppedAt: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'StopLend' sylvester event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = SylvesterEvent.parse_id(doc["_id"])

        return cls(
            txHash, txOffset, lendingID=doc["lendingID"], stoppedAt=doc["stoppedAt"]
        )


@dataclass
class RentClaimedEvent(SylvesterEvent):
    """
    RentClaimedEvent DTO (Data Transfer Object)

    Holds the event data for sylvester 'RentClaimed' event.
    """

    # pylint: disable=invalid-name
    rentingID: int
    collectedAt: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'RentClaimed' sylvester event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = SylvesterEvent.parse_id(doc["_id"])

        return cls(
            txHash, txOffset, rentingID=doc["rentingID"], collectedAt=doc["collectedAt"]
        )
