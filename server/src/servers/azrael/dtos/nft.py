from dataclasses import dataclass
from typing import List, Union

from .renting import Renting
from .lending import Lending


@dataclass
class Nft:

    "id is nftAddress::tokenId::lentAmount"
    id: str
    "each Lending and Renting in the arrays here will have the SAME nftAddress and tokenId!!!!!! As per the id of this entity"
    lending: List[Lending]
    renting: List[Renting]