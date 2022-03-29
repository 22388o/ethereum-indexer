"""
This class defines ALL events emitted by the azrael contract.

Event List: Lent, Rented, Returned, LendingStopped, CollateralClaimed
"""

from abc import ABC
from dataclasses import asdict, dataclass
from typing import Union

ID_SEPERATOR = "_"


@dataclass
class AzraelEvent(ABC):
    """
    Abstract azrael Event. Holds txHash and txOffset, togther they are a unique
    identifier for azrael events. e.i _id=txHash_txOffset
    """

    _id: str
    event: str

    @staticmethod
    def get_id(tx_hash: str, tx_offset: Union[str, int]) -> str:
        """Creates unique identifier for Azrael Event

        Args:
            tx_hash (str): transaction hash
            tx_offset (Union[str, int]): transaction offset

        Returns:
            id (str): Unique identifier composed of txHash and txOffset.
                e.i. 0xf79edc5500218427d22d4215799fb51064c633ca919c0406b830ed5dc3c6eb1a_100
        """
        return f"{tx_hash}{ID_SEPERATOR}{tx_offset}"

    def to_dict(self):
        """Return a dict representation of this event"""
        return asdict(self)


@dataclass
class LentEvent(AzraelEvent):
    """
    LentEvent DTO (Data Transfer Object)

    Holds the event metadata for azrael 'Lent' event.
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

    # TODO: Typing for event parameters
    # pylint: disable=too-many-arguments
    @classmethod
    def create(
        cls,
        tx_hash: str,
        log_offset: Union[str, int],
        nft_address: str,
        token_id: str,
        lent_amount: int,
        lending_id: int,
        lender_address: str,
        max_rent_duration: int,
        daily_rent_price: int,
        nft_price: int,
        is_ERC721: bool,
        payment_token: int,
    ):
        """
        Factory method for 'Lent' azrael event.

        Args:
            tx_hash (str): The hash of the transaction
            log_offset (str): The offset of the transaction
            nft_address (str): Address of NFT to be lent
            token_id (str): Id of NFT being lent
            lent_amount (int): Amount of NFT of token_id to be lent
            lending_id (int): Id of the ReNFT lending
            lender_address (str): Wallet address of lender
            max_rent_duration (int): Maximum rent duration in days
            daily_rent_price (int): Daily rental price for NFT, denominated in payment_token
            nft_price (int): Full collateral sum, denominated in payment_token
            is_ERC721 (bool): True if NFT being lent is ERC721, False if NFT is ERC1155
            payment_token (int): Token to be used for rental payment

        Returns:
            (LentEvent): instance of this class with the correct
            configs.
        """

        _id = AzraelEvent.get_id(tx_hash, log_offset)

        return cls(
            _id=_id,
            event="Lent",
            nftAddress=nft_address,
            tokenId=token_id,
            lentAmount=lent_amount,
            lendingId=lending_id,
            lendersAddress=lender_address,
            maxRentDuration=max_rent_duration,
            dailyRentPrice=daily_rent_price,
            nftPrice=nft_price,
            isERC721=is_ERC721,
            paymentToken=payment_token,
        )


@dataclass
class RentedEvent(AzraelEvent):
    """
    RentedEvent DTO (Data Transfer Object)

    Holds the event metadata for azrael 'Rented' event.
    """

    # pylint: disable=invalid-name
    lendingId: int
    renterAddress: str
    rentDuration: int
    rentedAt: int

    # TODO: Typing for event parameters
    # pylint: disable=too-many-arguments
    @classmethod
    def create(
        cls,
        tx_hash: str,
        log_offset: Union[str, int],
        lending_id: int,
        renter_address: int,
        rent_duration: int,
        rented_at: int,
    ):
        """
        Factory method for 'Rented' azrael event.

        Args:
            tx_hash (str): The hash of the transaction
            log_offset (str): The offset of the transaction
            lending_id (int): Id of the ReNFT lending
            renter_address (str): Wallet address of renter
            rent_duration (int): Duration of rental in days
            rented_at (int): Block timestamp of the transaction

        Returns:
            (RentedEvent): instance of this class with the correct
            configs.
        """

        _id = AzraelEvent.get_id(tx_hash, log_offset)

        return cls(
            _id=_id,
            event="Rented",
            lendingId=lending_id,
            renterAddress=renter_address,
            rentDuration=rent_duration,
            rentedAt=rented_at,
        )


@dataclass
class ReturnedEvent(AzraelEvent):
    """
    ReturnedEvent DTO (Data Transfer Object)

    Holds the event data for azrael 'Returned' event.
    """

    # pylint: disable=invalid-name
    lendingId: int
    returnedAt: int

    # TODO: Typing for event parameters
    @classmethod
    def create(
        cls,
        tx_hash: str,
        log_offset: Union[str, int],
        lending_id: int,
        returned_at: int,
    ):
        """
        Factory method for 'Returned' azrael event.

        Args:
            tx_hash (str): The hash of the transaction
            log_offset (str): The offset of the transaction
            lending_id (int): Id of the ReNFT lending
            returned_at (int): Block timestamp of the transaction

        Returns:
            (ReturnedEvent): instance of this class with the correct
            configs.
        """

        _id = AzraelEvent.get_id(tx_hash, log_offset)

        return cls(
            _id=_id,
            event="Returned",
            lendingId=lending_id,
            returnedAt=returned_at,
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

    # TODO: Typing for event parameters
    @classmethod
    def create(
        cls, tx_hash: str, log_offset: Union[str, int], lending_id: int, stopped_at: int
    ):
        """
        Factory method for 'LendingStopped' azrael event.

        Args:
            tx_hash (str): The hash of the transaction
            log_offset (str): The offset of the transaction
            lending_id (int): Id of the ReNFT lending
            stopped_at (int): Block timestamp of the transaction

        Returns:
            (LendingStopped): instance of this class with the correct
            configs.
        """

        _id = AzraelEvent.get_id(tx_hash, log_offset)

        return cls(
            _id=_id, event="LendingStopped", lendingId=lending_id, stoppedAt=stopped_at
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

    # TODO: Typing for event parameters
    @classmethod
    def create(
        cls, tx_hash: str, log_offset: Union[str, int], lending_id: int, claimed_at: int
    ):
        """
        Factory method for 'CollateralClaimed' azrael event.

        Args:
            tx_hash (str): The hash of the transaction
            log_offset (str): The offset of the transaction
            lending_id (int): Id of the ReNFT lending
            claimed_at (int): Block timestamp of the transaction

        Returns:
            (CollateralClaimed): instance of this class with the correct
            configs.
        """

        _id = AzraelEvent.get_id(tx_hash, log_offset)

        return cls(
            _id=_id,
            event="CollateralClaimed",
            lendingId=lending_id,
            claimedAt=claimed_at,
        )
