import logging
from typing import Any, List

from db import DB
from transform.covalent import Covalent
from transformers.sylvester.event import (
    LendEvent,
    RentClaimedEvent,
    RentEvent,
    StopLendEvent,
    StopRentEvent,
    SylvesterEvent,
)
from transformers.sylvester.util import unpack_price


# todo: needs to inherit an interface that implements flush
# todo: every instance should also take the address it transforms
# todo: as a constructor argument
class Transformer:
    """
    ReNFT Sylvester Transformer

    The Extractor stores on-chain Sylvester transactions on disk.
    The Transformer transforms these transcations into events emitted
    by the Sylvester contract. Using these events an on-chain state can
    be reconstructed off-chain.

    Sylvester Events of interest are: Lend, Rent, StopRent, StopLend, RentClaimed
    """

    def __init__(self, address: str):

        self._address = address

        self._transformed = []

        self._db_name = "ethereum-indexer"
        self._collection_name = f"{self._address}-state"
        self._events_of_interest = [
            "Lend",
            "Rent",
            "StopLend",
            "StopRent",
            "RentClaimed",
        ]

        self._flush_state = False

        self._db = DB()

    # todo: type that returns transformed transaction
    # TODO: documentation
    def entrypoint(self, txn) -> None:
        """_summary_

        Args:
            txn (_type_): _description_
        """

        # 1. check if there is state in the db
        # 2. if there is state in the db, update memory with it
        self.update_memory_state()

        # routes and performs any additional logic
        logging.info(f'Handling transaction at: {txn["block_height"]} block')

        log_events = txn["log_events"]
        # * ensures that events are supplied in the correct order
        log_events = sorted(log_events, key=lambda x: x["log_offset"])

        for event in log_events:

            # * means the event was emitted by a contract that is
            # * not of interest
            if event["sender_address"] != self._address.lower():
                continue

            # todo: this is not good.
            # todo: if this were to happen in an event that pertains to
            # todo: our address, it would corrupt the state
            if event["decoded"] is None:
                logging.warning(f"No name for event: {event}")
                continue

            # events: Rented, Lent, CollateralClaimed, LendingStopped, Returned
            if event["decoded"]["name"] in self._events_of_interest:
                decoded_params = Covalent.decode(event)

                if event["decoded"]["name"] == "Lend":
                    self._on_lend(event, decoded_params)
                elif event["decoded"]["name"] == "Rent":
                    self._on_rent(event, decoded_params)
                elif event["decoded"]["name"] == "StopLend":
                    self._on_stop_lend(event, decoded_params)
                elif event["decoded"]["name"] == "StopRent":
                    self._on_stop_rent(event, decoded_params)
                elif event["decoded"]["name"] == "RentClaimed":
                    self._on_rent_claimed(event, decoded_params)

            logging.info(event)

        self._flush_state = True

    # todo: should be part of the interface
    # todo: acts as the means to sync with db state
    def update_memory_state(self) -> None:
        """_summary_"""

        if len(self._transformed) > 0:
            return

        state = self._db.get_all_items(self._db_name, self._collection_name)

        if state is None:
            return

        self._transformed = state

    def _add_transformed(self, event: SylvesterEvent) -> None:
        self._transformed.append(event.to_dict())

    # todo: should be part of the interface
    def flush(self) -> None:
        """_summary_"""

        if self._flush_state:
            # * write to the db
            self._db.put_items(self._transformed, self._db_name, self._collection_name)
            self._flush_state = False

    def _on_rent_claimed(self, event: Any, decoded_params: List[Any]) -> None:
        # RentClaimed(uint256 indexed rentingID, uint32 collectedAt)

        event = RentClaimedEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            renting_id=int(decoded_params[0]),
            collected_at=int(decoded_params[1]),
        )

        self._add_transformed(event)

    def _on_stop_rent(self, event: Any, decoded_params: List[Any]) -> None:
        # StopRent(indexed uint256 rentingID, uint32 stoppedAt)

        event = StopRentEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            renting_id=int(decoded_params[0]),
            stopped_at=int(decoded_params[1]),
        )

        self._add_transformed(event)

    def _on_stop_lend(self, event: Any, decoded_params: List[Any]) -> None:
        # StopLend(uint256 indexed lendingID, uint32 stoppedAt)

        event = StopLendEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            lending_id=int(decoded_params[0]),
            stopped_at=int(decoded_params[1]),
        )

        self._add_transformed(event)

    def _on_rent(self, event: Any, decoded_params: List[Any]) -> None:
        # Rent(indexed address renterAddress, indexed uint256 lendingID, indexed uint256 rentingID,
        # uint16 rentAmount, uint8 rentDuration, uint32 rentedAt)

        event = RentEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            renter_address=decoded_params[0],
            lending_id=int(decoded_params[1]),
            renting_id=int(decoded_params[2]),
            rent_amount=int(decoded_params[3]),
            rent_duration=int(decoded_params[4]),
            rented_at=int(decoded_params[5]),
        )

        self._add_transformed(event)

    def _on_lend(self, event: Any, decoded_params: List[Any]) -> None:
        # Lend(bool is721, indexed address lenderAddress, indexed address nftAddress,
        # indexed uint256 tokenID,
        # uint256 lendingID, uint8 maxRentDuration, bytes4 dailyRentPrice,
        # uint16 lendAmount, uint8 paymentToken)

        event = LendEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            is_721=decoded_params[0],
            lender_address=decoded_params[1],
            nft_address=decoded_params[2],
            token_id=decoded_params[3],
            lending_id=int(decoded_params[4]),
            max_rent_duration=int(decoded_params[5]),
            daily_rent_price=unpack_price(decoded_params[6]),
            lend_amount=int(decoded_params[7]),
            payment_token=int(decoded_params[8]),
        )

        self._add_transformed(event)


# todo: do not save empty lists
# todo: block height state is incorrect
