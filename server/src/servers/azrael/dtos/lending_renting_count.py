from dataclasses import dataclass

@dataclass
class LendingRentintCount:
    id: str
    lending: int
    "less or equal lending"
    renting: int