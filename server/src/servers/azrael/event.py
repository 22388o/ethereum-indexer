"""
This class defines ALL events emitted by the azrael contract.

Event List: Lent, Rented, Returned, LendingStopped, CollateralClaimed
"""

from abc import ABC
from dataclasses import dataclass


@dataclass
class AzraelEvent(ABC):
    """
    Abstract azrael Event. Holds txHash and txOffset, togther they are a unique
    identifier for azrael events.
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
class LentEvent(AzraelEvent):
    """
    LentEvent DTO (Data Transfer Object)

    Holds the event data for azrael 'Lent' event.
    """

    # pylint: disable=invalid-name,too-many-instance-attributes
    lendingId: int
    lentAmount: int
    maxRentDuration: int
    paymentToken: int
    nftAddress: str
    tokenId: str
    lendersAddress: str
    dailyRentPrice: float
    nftPrice: float
    isERC721: bool
    paymentToken: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'Lent' azrael event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = AzraelEvent.parse_id(doc["_id"])

        del doc["_id"]
        del doc["event"]

        return cls(txHash, txOffset, **doc)


@dataclass
class RentedEvent(AzraelEvent):
    """
    RentedEvent DTO (Data Transfer Object)

    Holds the event data for azrael 'Rented' event.
    """

    # pylint: disable=invalid-name
    lendingId: int
    renterAddress: str
    rentDuration: int
    rentedAt: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'Rented' azrael event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = AzraelEvent.parse_id(doc["_id"])

        del doc["_id"]
        del doc["event"]

        return cls(txHash, txOffset, **doc)


@dataclass
class ReturnedEvent(AzraelEvent):
    """
    ReturnedEvent DTO (Data Transfer Object)

    Holds the event data for azrael 'Returned' event.
    """

    # pylint: disable=invalid-name
    lendingId: int
    returnedAt: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'Returned' azrael event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = AzraelEvent.parse_id(doc["_id"])

        return cls(
            txHash, txOffset, lendingId=doc["lendingId"], returnedAt=doc["returnedAt"]
        )


@dataclass
class LendingStoppedEvent(AzraelEvent):
    """
    LendingStopped DTO (Data Transfer Object)

    Holds the event data for azrael 'LendingStopped' event.
    """

    # pylint: disable=invalid-name
    lendingId: int
    stoppedAt: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'LendingStopped' azrael event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = AzraelEvent.parse_id(doc["_id"])

        return cls(
            txHash, txOffset, lendingId=doc["lendingId"], stoppedAt=doc["stoppedAt"]
        )


@dataclass
class CollateralClaimedEvent(AzraelEvent):
    """
    CollateralClaimed DTO (Data Transfer Object)

    Holds the event data for azrael 'CollateralClaimed' event.
    """

    # pylint: disable=invalid-name
    lendingId: int
    claimedAt: int

    @classmethod
    def from_doc(cls, doc):
        """
        Parses a mongodb document into a 'CollateralClaimed' azrael event.

        Args:
            doc (Dict): a mongodb document

        Returns:
            _type_: instance of this class with the correct
            configs.
        """

        txHash, txOffset = AzraelEvent.parse_id(doc["_id"])

        return cls(
            txHash, txOffset, lendingId=doc["lendingId"], claimedAt=doc["claimedAt"]
        )
