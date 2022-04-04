from dataclasses import dataclass
from typing import List

from .renting import Renting
from .lending import Lending

@dataclass
class User:
    "id here is user's Ethereum address"
    id: str
    "each Lending and Renting in the arrays here will have DIFFERENT nftAddress and tokenId"
    lending: List[Lending]
    renting: List[Renting]