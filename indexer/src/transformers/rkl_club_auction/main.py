import logging

from db import DB
from eth_abi import decode_single

# ! this code is taken from: https://github.com/rumble-kong-league/club-nft-auction
# ! they should be exactly the same

PLACE_BID_EVENT = "0xe694ab314354b7ccad603c48b44dce6ade8b6a57cbebaa8842edd9a2fb2856f8"


# todo: needs to inherit an interface that implements flush
# todo: every instance should also take the address it transforms
# todo: as a constructor argument
class Transformer:
    """RKL Club Auction Transformer"""

    def __init__(self, address: str):

        self._address = address

        self._transformed = {"_id": 1}

        self._db_name = "ethereum-indexer"
        self._collection_name = f"{self._address}-state"

        self._flush_state = False

        self._db = DB()

    @staticmethod
    def hexstring_to_bytes(hexstring: str) -> bytes:
        """
        Casts the hexstring to bytes.

        Args:
            hexstring (str): hexstring to conver to bytes

        Raises:
            ValueError: if hexstring does not start with 0x

        Returns:
            bytes: bytes value of the hexstring
        """
        if not hexstring.startswith("0x"):
            raise ValueError("Not a hexstring")

        return bytes.fromhex(hexstring[2:])

    # todo: txn dataclass
    # TODO: documentation
    def entrypoint(self, txn):
        """
        Main entrypoint for transforming the raw data. Responsible
        for routing the events into the correct handlers.

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

            # In the case of kovan testing, none of the transaction / event
            # details were decoded. So they must be decoded manually.

            # example of a possible event
            # [
            #     '0xe694ab314354b7ccad603c48b44dce6ade8b6a57cbebaa8842edd9a2fb2856f8',
            #     '0x000000000000000000000000000000724350d0b24747bd816dc5031acb7efe0b',
            #     '0x000000000000000000000000000000000000000000000000002bd72a24874000'
            # ]

            if event["raw_log_topics"][0] != PLACE_BID_EVENT:
                continue

            bidder = decode_single(
                "address", self.hexstring_to_bytes(event["raw_log_topics"][1])
            )
            # * since the price is always ether, diving by 1e18 here
            price = decode_single(
                "uint256", self.hexstring_to_bytes(event["raw_log_topics"][2])
            )
            price /= 1e18

            self._on_place_bid(bidder, price)

            logging.info(event)

        self._flush_state = True

    # todo: should be part of the interface
    # todo: acts as the means to sync with db state
    def update_memory_state(self) -> None:
        """
        If the script was cancelled previously, this pulls the latest
        transformed state from the db.
        """

        state = self._db.get_any_item(self._db_name, self._collection_name)

        if state is None:
            return

        self._transformed = state

    # todo: should be part of the interface
    def flush(self) -> None:
        """
        Write the transformed state to the db.
        """

        if self._flush_state:
            # * write to the db
            self._db.put_item(self._transformed, self._db_name, self._collection_name)
            self._flush_state = False

    def _on_place_bid(self, bidder: str, price: float) -> None:
        # PlaceBid(address indexed bidder, uint256 indexed price)

        if bidder in self._transformed:
            self._transformed[bidder] += price
        else:
            self._transformed[bidder] = price
