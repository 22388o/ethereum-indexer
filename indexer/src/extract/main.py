import logging
import time

from config import Config
from db import DB
from interfaces.iextract import IExtract

from extract.covalent import Covalent

# todo: eventually would want each extractor running in its own process
# for now the solution around that would be to simply run this pipeline
# multiple times

EXTRACT_SLEEP_TIME = 15 # in seconds


class Extract(IExtract):
    """@inheritdoc IExtract"""

    def __init__(self, config: Config):
        """
        Args:
            address (str): address for which to extract the raw historical
        transaction data.
        """

        self._config = config

        # TODO: validate to ensure that this address is not in the db

        self._address: str = self._config.get_address()
        # block number up to which the extraction has happened
        self._block_height: int = 0

        self._covalent = Covalent(self._config.get_network_id())

        self._db_name = "ethereum-indexer"

        self._db = DB()

        # todo: type of transactions
        self._transactions = []

    def __setattr__(self, key, value):
        # https://towardsdatascience.com/how-to-create-read-only-and-deletion-proof-attributes-in-your-python-classes-b34cd1019c2d

        # re-setting the _address, _db_name, _db, _load is not allowed
        forbid_reset_on = ["_config", "_address", "_db_name", "_db"]
        for k in forbid_reset_on:
            if key == k and hasattr(self, k):
                raise AttributeError(
                    "The value of the address attribute has already been set,",
                    " and can not be re-set.",
                )

        self.__dict__[key] = value

    @staticmethod
    def _get_block_height_collection_name(address: str) -> str:
        return f"{address}-block-height"

    def _determine_block_height(self) -> None:
        """
        This ensures we do not extract all the data all the time, but only
        the new stuff. This is also helpful in case the binary raises and
        we need to restart it.
        """

        block_height_item = self._db.get_any_item(
            self._db_name, self._get_block_height_collection_name(self._address)
        )
        # If it is None, then we have already set it to 0 in the
        # __init__. This will signal the extractor to extract
        # the complete history of the address
        if block_height_item is None:
            return

        self._block_height = block_height_item["block_height"]

    def _update_block_height(self, new_block_height: int, for_address: str) -> None:
        """
        After extracting the transactions update the db with the latest block height.

        Args:
            new_block_height (int): _description_
            for_address (str): _description_
        """

        collection_name = self._get_block_height_collection_name(for_address)
        # _id: 1, because we are only ever storing single block_height value per address
        item = {"_id": 1, "block_height": new_block_height}
        self._db.put_item(item, self._db_name, collection_name)

    def _request_transactions(self, for_address: str, page_number: int) -> None:
        response = self._covalent.request_transactions(for_address, page_number)
        return response

    def _extract_txn_history_since(self, block_height: int, for_address: str) -> None:
        """
        Makes requests to Covalent, and only extracts transactions after `block_height`
        block number.

        Args:
            block_height (int): We have data for this address up to and including this
            block number. Our goal is to obtain transactions after this block number
            (if there are any).
            for_address (str): We are extracting transactions for this address.
        """

        logging.info(f"Extracting {for_address} since block: {block_height}")

        page_number = 0
        last_block_height = block_height
        latest_block_height = 0
        keep_looping = True

        while keep_looping:

            response = self._request_transactions(for_address, page_number)
            block_height = self._covalent.get_block_height(response)

            if page_number == 0:
                latest_block_height = block_height

            transactions = self._covalent.get_transactions(response)

            for txn in transactions:
                # * block height cannot be zero here due to the check earlier
                block_height = self._covalent.get_block_height_from_transaction(txn)

                if (block_height is None) or (block_height <= last_block_height):
                    keep_looping = False
                    break

                if block_height > last_block_height:
                    txn["_id"] = txn["tx_hash"]
                    self._transactions.append(txn)

            if not keep_looping:
                break

            if block_height is None:
                break

            if block_height > last_block_height:
                page_number += 1

        if latest_block_height > last_block_height:
            self._update_block_height(latest_block_height, for_address)

        logging.info("Extractor sleeping...")
        time.sleep(EXTRACT_SLEEP_TIME)

    # Interface Implementation

    def flush(self) -> None:
        """@inheritdoc IExtract"""

        if len(self._transactions) == 0:
            return

        self._db.put_items(self._transactions, self._db_name, self._address)

        self._transactions = []

    def extract(self) -> None:
        """@inheritdoc IExtract"""

        # Running this ensures we know what transactions to extract in the code
        # will follow. This avoids extracting all the transactions all the time.
        self._determine_block_height()

        # - check if the db has transactions, if it has, then download the new ones
        # if it doesn't have any transactions, download all
        # - we utilise a separate collection to track what raw transactions have
        # been extracted
        self._extract_txn_history_since(self._block_height, self._address)
