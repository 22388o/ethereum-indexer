"""
An indexer transformer for ReNft Azrael Contract
"""
import logging
from typing import Any, List, Dict
from functools import cmp_to_key
from .azrael_structs import LendingRenting
from db import DB
from transform.covalent import Covalent

# disable this pylint to preserve modularity
# pylint: disable=relative-beyond-top-level

from .event import (
    AzraelEvent,
    CollateralClaimedEvent,
    LendingStoppedEvent,
    LentEvent,
    RentedEvent,
    ReturnedEvent,
)
from .util import unpack_price, compare_azrael_events

# todo: needs to inherit an interface that implements flush
# todo: every instance should also take the address it transforms
# todo: as a constructor argument
class Transformer:
    """
    ReNFT Azrael Transformer implementation

    The Extractor stores on-chain Azrael transactions on disk.
    The Transformer transforms these transcations into events emitted
    by the Azrael contract. The events are then transformed into LendingRentings.

    Azrael Events of interest are: Lent, Rented, Returned, LendingStopped, CollateralClaimed
    """

    def __init__(self, address: str):

        self._address = address

        self._transformed: Dict[int, LendingRenting] = dict()
        self._events: List[AzraelEvent] = []

        self._db_name = "ethereum-indexer"
        self._collection_name = f"{self._address}-state"
        self._events_of_interest = [
            "Rented",
            "Lent",
            "CollateralClaimed",
            "LendingStopped",
            "Returned",
        ]

        self._flush_state = False

        self._db = DB()

    # todo: type that returns transformed transaction
    # todo: documentation
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

                if event["decoded"]["name"] == "Rented":
                    self._on_rented(event, decoded_params)
                elif event["decoded"]["name"] == "Lent":
                    self._on_lent(event, decoded_params)
                elif event["decoded"]["name"] == "Returned":
                    self._on_returned(event, decoded_params)
                elif event["decoded"]["name"] == "LendingStopped":
                    self._on_lending_stopped(event, decoded_params)
                elif event["decoded"]["name"] == "CollateralClaimed":
                    self._on_collateral_claim(event, decoded_params)

            logging.info(event)

        # Need events to transform
        if len(self._events) > 0:
            # Remove duplicates
            self._events = list(set(self._events))

            # Sort them by priority
            self._events.sort(key=cmp_to_key(compare_azrael_events))

            # Consume the events; FIFO
            event = self._events.pop(0)
            while event is not None:
                self._transform_event(event)
                event = self._events.pop(0) if len(self._events) > 0 else None

            self._flush_state = True

    # todo: should be part of the interface
    # todo: acts as the means to sync with db state
    def update_memory_state(self) -> None:
        """_summary_"""

        state = self._db.get_all_items(self._db_name, self._collection_name)

        if state is None:
            return

        for doc in state:
            lending_renting: LendingRenting = LendingRenting.from_mongo_doc(doc)
            self._transformed[lending_renting.lending.lendingId] = lending_renting


    # todo: should be part of the interface
    def flush(self) -> None:
        """_summary_"""

        if self._flush_state:
            print("Flushing transformer state")

            as_docs = list(map(lambda x: x.to_dict(), list(self._transformed.values())))

            # * write to the db
            self._db.put_items(as_docs, self._db_name, self._collection_name)

            self._events = []
            self._flush_state = False

    def _transform_event(self, event: AzraelEvent):
        if event.event == 'Lent' and not event.lendingId in self._transformed:
            self._transformed[event.lendingId] = LendingRenting.from_lent_event(event)
        elif event.event == 'Rented':
            self._transformed[event.lendingId].insert_rented(event)
        elif event.event == 'Returned':
            self._transformed[event.lendingId].insert_returned(event)
        elif event.event == 'CollateralClaimed':
            self._transformed[event.lendingId].insert_collateral_claimed(event)
        elif event.event == 'LendingStopped':
            self._transformed[event.lendingId].insert_lending_stopped(event)

    def _on_collateral_claim(self, event: Any, decoded_params: List[Any]) -> None:
        # CollateralClaimed(indexed uint256 lendingId, uint32 claimedAt)

        event = CollateralClaimedEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            lending_id=int(decoded_params[0]),
            claimed_at=int(decoded_params[1]),
        )

        self._events.append(event)

    def _on_lending_stopped(self, event: Any, decoded_params: List[Any]) -> None:
        # LendingStopped(indexed uint256 lendingId, uint32 stoppedAt)

        event = LendingStoppedEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            lending_id=int(decoded_params[0]),
            stopped_at=int(decoded_params[1]),
        )

        self._events.append(event)

    def _on_returned(self, event: Any, decoded_params: List[Any]) -> None:
        # Returned(indexed uint256 lendingId, uint32 returnedAt)

        event = ReturnedEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            lending_id=int(decoded_params[0]),
            returned_at=int(decoded_params[1]),
        )

        self._events.append(event)

    def _on_rented(self, event: Any, decoded_params: List[Any]) -> None:
        # Rented(uint256 lendingId, indexed address renterAddress, uint8 rentDuration,
        # uint32 rentedAt)

        event = RentedEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            lending_id=int(decoded_params[0]),
            renter_address=decoded_params[1],
            rent_duration=int(decoded_params[2]),
            rented_at=int(decoded_params[3]),
        )

        self._events.append(event)

    # todo: typing for event
    def _on_lent(self, event: Any, decoded_params: List[Any]) -> None:
        # Lent(indexed address nftAddress, indexed uint256 tokenId, uint8 lentAmount,
        # uint256 lendingId, indexed address lenderAddress, uint8 maxRentDuration,
        # bytes4 dailyRentPrice, bytes4 nftPrice, bool isERC721, uint8 paymentToken)

        event = LentEvent.create(
            tx_hash=event["tx_hash"],
            log_offset=event["log_offset"],
            nft_address=decoded_params[0],
            token_id=decoded_params[1],
            lent_amount=int(decoded_params[2]),
            lending_id=int(decoded_params[3]),
            lender_address=decoded_params[4],
            max_rent_duration=int(decoded_params[5]),
            daily_rent_price=unpack_price(decoded_params[6]),
            nft_price=unpack_price(decoded_params[7]),
            is_ERC721=decoded_params[8],
            payment_token=int(decoded_params[9]),
        )

        self._events.append(event)
