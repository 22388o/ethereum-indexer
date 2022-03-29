import importlib
import logging
import time
from typing import List

from config import Config
from db import DB
from interfaces.itransform import ITransform

SLEEP_TIMER = 10


class Transform(ITransform):
    """@inheritdoc ITransform"""
    
    def __init__(self, config: Config):
        self._config = config

        # * name of the module that will perform transforming
        self._to_transform = self._config.get_transformer_name()

        # todo: validate that the address in config is valid
        # todo: validate that the address is being scraped (i.e. is in the db)
        # todo: validate that the name of the events is lower cased event name
        # from the scraped transactions

        # block number up to which the extraction has happened
        self._block_height: int = 0

        full_module_name = f"transformers.{self._to_transform}.main"
        transformer_module = importlib.import_module(full_module_name)

        # this implies that every transformer will take the address it transforms
        # as a constructor argument
        self._transformer = transformer_module.Transformer(self._config.get_address())

        self._db_name = "ethereum-indexer"

        # * to read the raw transactions from the database
        self._db = DB()

    def __setattr__(self, key, value):
        # https://towardsdatascience.com/how-to-create-read-only-and-deletion-proof-attributes-in-your-python-classes-b34cd1019c2d

        forbid_reset_on = [
            "_to_transform",
            "_config",
            "_db_name",
            "_db",
            "_transformer",
        ]
        for k in forbid_reset_on:
            if key == k and hasattr(self, k):
                raise AttributeError(
                    "The value of the address attribute has already been set,"
                    " and can not be re-set."
                )

        self.__dict__[key] = value

    def _get_state_collection_name(self) -> str:
        # !: will be more than one address later
        return f"{self._config.get_address()}-state"

    def _get_events_of_interest(self) -> List[str]:
        return self._get_events_from_config()

    def _get_events_from_config(self) -> List[str]:
        return self._config["events"]

    def _get_block_height_collection_name(self) -> str:
        return f"{self._config.get_address()}-block-height-state"

    def _determine_block_height(self) -> None:
        """
        This ensures we do not extract all the data all the time, but only
        the new stuff. This is also helpful in case the binary raises and
        we need to restart it.
        """

        block_height_item = self._db.get_any_item(
            self._db_name, self._get_block_height_collection_name()
        )
        # If it is None, then we have already set it to 0 in the __init__
        if block_height_item is None:
            return

        self._block_height = block_height_item["block_height"]

    # todo: func docs
    def _update_block_height(self, new_block_height: int) -> None:
        """
        Args:
            new_block_height (int): _description_
            for_address (str): _description_
        """

        collection_name = self._get_block_height_collection_name()
        # _id: 1, because we are only ever storing single block_height value per address
        item = {"_id": 1, "block_height": new_block_height}
        self._db.put_item(item, self._db_name, collection_name)

    # todo: return type
    def _read_raw_transactions_after_block(self):
        """
        Pulls all transactions after block height, and sorts them in ascending order
        """

        raw_transactions = self._db.get_all_items(
            self._db_name,
            self._config.get_address(),
            {
                "query_clause": {"block_height": {"$gt": self._block_height}},
                "sort": {"sort_by": "block_height", "direction": 1},
            },
        )

        return raw_transactions

    def transform(self) -> None:
        """@inheritdoc ITransform"""

        # 1. Retrieve the last block up to which we have transformed the txns
        # 2. Read the raw transactions after that block
        # 3. Pass in the right order these transactions into individual handlers
        # 4. Handlers return transformed data which we store here in memory
        # 5. Determine the newest block from these txns
        # 6. Update the last block

        # 1.
        self._determine_block_height()

        # 2.
        raw_transactions = self._read_raw_transactions_after_block()

        # 3.
        for txn in raw_transactions:
            # 4.
            self._transformer.entrypoint(txn)

        # 5.
        if len(raw_transactions) == 0:
            return
        # transactions are supplied in ascending order
        # so we should write the last transaction's block number
        latest_block = raw_transactions[-1]["block_height"]

        # 6.
        self._update_block_height(latest_block)

    def flush(self) -> None:
        """@inheritdoc ITransform"""

        # this way the responsibility of maintaining complex state and
        # writing it to db is with the transformer
        self._transformer.flush()

        logging.info("Transformer sleeping...")
        time.sleep(SLEEP_TIMER)
