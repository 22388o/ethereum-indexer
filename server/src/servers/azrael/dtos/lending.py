from dataclasses import dataclass

from typing import Union

from .renting import Renting
from azrael.lending_renting import LendingRenting

@dataclass
class Lending:
    """Lending"""
    id: int

    nftAddress: str
    tokenId: str

    lenderAddress: str
    maxRentDuration: int
    dailyRentPrice: float
    nftPrice: float
    paymentToken: int
    lentAmount: int
    isERC721: bool
    lentAt: int

    renting: Union[Renting, None]

    collateralClaimed: bool

    # TODO: implement these types
    "id := nftAddresss::tokenId::lentAmount"
    # nft: Nft
    # lenderUser: User


    @staticmethod
    def from_lending_renting(lending_renting: LendingRenting):
        """Transforms LendingRenting to Lending Graphql DTO"""

        lending: Lending = Lending(
            id=lending_renting.lending.lendingId,
            nftAddress=lending_renting.nft.nftAddress,
            tokenId=lending_renting.nft.tokenId,
            lenderAddress=lending_renting.lending.lendersAddress,
            maxRentDuration=lending_renting.lending.maxRentDuration,
            dailyRentPrice=lending_renting.lending.dailyRentPrice,
            nftPrice=lending_renting.lending.nftPrice,
            paymentToken=lending_renting.lending.paymentToken,
            lentAmount=lending_renting.lending.lentAmount,
            isERC721=lending_renting.lending.isERC721,
            # TODO: lentAt
            lentAt=100000,
            renting=None,
            collateralClaimed=lending_renting.collateralClaimedAt is not None,
        )
        
        # Has been rented
        if len(lending_renting.rentings) > 0:
            last_rental = lending_renting.rentings[-1]
            lending.renting = Renting(
                id=lending_renting.lending.lendingId,
                renterAddress=last_rental.renterAddress,
                rentDuration=last_rental.rentDuration,
                rentedAt=last_rental.rentedAt,
                lending=lending # gross recursion here
            )


        return lending
