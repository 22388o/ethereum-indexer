import logging

from db import DB
from transform.covalent import Covalent


# todo: needs to inherit an interface that implements flush
# todo: every instance should also take the address it transforms
# todo: as a constructor argument
class Transformer:
    """RKL Kong Holder Transformer"""

    def __init__(self, address: str):

        self._address = address

        self._transformed = {"_id": 1}

        self._db_name = "ethereum-indexer"
        self._collection_name = f"{self._address}-state"
        self._events_of_interest = ["Transfer"]

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

            if event["decoded"]["name"] in self._events_of_interest:
                decoded_params = Covalent.decode(event)
                if event["decoded"]["name"] == "Transfer":
                    from_, to, value = (
                        decoded_params[0],
                        decoded_params[1],
                        decoded_params[2],
                    )
                    self._on_transfer(from_, to, value)

            logging.info(event)

        self._flush_state = True

    # todo: should be part of the interface
    # todo: acts as the means to sync with db state
    def update_memory_state(self) -> None:
        """_summary_"""

        state = self._db.get_any_item(self._db_name, self._collection_name)

        if state is None:
            return

        self._transformed = state

    # todo: should be part of the interface
    def flush(self) -> None:
        """_summary_"""

        if self._flush_state:
            # * write to the db
            self._db.put_item(self._transformed, self._db_name, self._collection_name)
            self._flush_state = False

    def _on_transfer(self, from_, to_, value_) -> None:
        # Transfer(indexed address from, indexed address to, uint256 value)

        # todo: make this a constant somewhere
        if from_ != "0x0000000000000000000000000000000000000000":
            prev = self._transformed[from_]
            prev.remove(value_)

            if len(prev) == 0:
                del self._transformed[from_]
            else:
                self._transformed[from_] = prev

        if to_ in self._transformed:
            self._transformed[to_].append(value_)
        else:
            self._transformed[to_] = [value_]


# todo: do not save empty lists
# todo: block height state is incorrect
