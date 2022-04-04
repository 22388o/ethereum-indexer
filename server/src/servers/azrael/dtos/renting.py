from dataclasses import dataclass

from .lending import Lending

@dataclass
class Renting:
    id: int

    renterAddress: str
    rentDuration: int
    rentedAt: int

    lending: Lending

    "id := nftAddress::tokenId::lentAmount"
    # nft: Nft
    # renterUser: User
