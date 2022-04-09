"""
An indexer transformer for RKL Club Auctions
"""
from datetime import datetime
import logging

from eth_abi import decode_single
from db import DB

# ! this code is taken from: https://github.com/rumble-kong-league/club-nft-auction
# ! they should be exactly the same

PLACE_BID_EVENT = "0xe694ab314354b7ccad603c48b44dce6ade8b6a57cbebaa8842edd9a2fb2856f8"


# todo: needs to inherit an interface that implements flush
# todo: every instance should also take the address it transforms
# todo: as a constructor argument
class Transformer:
    """RKL Club Auction Transformer Implementation"""

    def __init__(self, address: str, network_id: int):

        self._address = address
        self._network_id = network_id

        self._transformed = []

        self._db_name = "ethereum-indexer"
        # todo: will run into problems when you have same addresses across networks
        # todo: should be named taking into account network id
        self._collection_name = f"{self._address}-{self._network_id}-state"

        self._flush_state = False

        self._db = DB()

    # todo: this should be in utils somewhere
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
    # todo: documentation
    def entrypoint(self, txn):
        """
        Main entrypoint for transforming the raw data. Responsible
        for routing the events into the correct handlers.

        Args:
            txn (_type_): _description_
        """

        # logging.info(txn)

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

            timestamp = int(
                datetime.strptime(
                    txn["block_signed_at"], "%Y-%m-%dT%H:%M:%SZ"
                ).timestamp()
            )
            self._on_place_bid(bidder, price, timestamp)

            logging.info(event)

        self._flush_state = True

    def _on_place_bid(self, bidder: str, price: float, timestamp: int) -> None:
        # PlaceBid(address indexed bidder, uint256 indexed price)

        item = self._db.get_item(bidder.lower(), self._db_name, self._collection_name)

        if item is None:
            # * could be that the item is in self._transformed
            pop_ix = None
            for ix, t in enumerate(self._transformed):
                if t["_id"] == bidder.lower():
                    pop_ix = ix
                    break

            if pop_ix is not None:
                item = self._transformed.pop(pop_ix)
                item["bids"].append({"amount": price, "timestamp": timestamp})
                self._transformed.append(item)
            else:
                self._transformed.append(
                    {
                        "_id": bidder.lower(),
                        "bids": [{"amount": price, "timestamp": timestamp}],
                    }
                )
        else:
            item["bids"].append({"amount": price, "timestamp": timestamp})
            self._transformed.append(item)

    # todo: should be part of the interface
    def flush(self) -> None:
        """
        Write the transformed state to the db.
        """

        if self._flush_state:
            for item in self._transformed:
                self._db.put_item(item, self._db_name, self._collection_name)
            self._transformed = []
            self._flush_state = False
