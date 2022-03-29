import logging
import os
import time
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# ETHEREUM_MAINNET_CHAIN_ID = 1
# ETHEREUM_KOVAN_CHAIN_ID = 42

# * notes
# - possible to pull from a different blockchain if `chain_id` is different
# - `block_signed_at=false` pulls all transactions putting most recent ones
# at the top
COVALENT_TRANSACTIONS_URI = lambda address, page_number, network_id: (
    f"https://api.covalenthq.com/v1/{network_id}/address/"
    + str(address)
    + "/transactions_v2/?quote-currency=USD"
    + "&format=JSON&block-signed-at-asc=false"
    + "&no-logs=false&page-number="
    + str(page_number)
    + "&key="
    + os.environ["COVALENT_API_KEY"]
    + "&page-size=100"
)

REQUEST_TRANSACTIONS_SLEEP = 5  # in seconds


class Covalent:
    """Client for interacting with Covalent API"""

    def __init__(self, network_id: int):
        self._network_id = network_id

    @staticmethod
    def _validate_transactions_response(response: Dict[str, Any]) -> None:
        """_summary_

        Args:
            response (Dict[str, Any]): _description_

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """

        # When the address has no transactions yet, you will get a response like
        # the following
        # {
        #     "data": {
        #         "address": "0x94d8f036a0fbc216bb532d33bdf6564157af0cd7",
        #         "updated_at": "2022-02-23T15:27:52.250901272Z",
        #         "next_update_at": "2022-02-23T15:32:52.250901422Z",
        #         "quote_currency": "USD",
        #         "chain_id": 1,
        #         "items": [],
        #         "pagination": {
        #             "has_more": false,
        #             "page_number": 11,
        #             "page_size": 100,
        #             "total_count": null
        #         }
        #     },
        #     "error": false,
        #     "error_message": null,
        #     "error_code": null
        # }

        if "data" not in response:
            raise ValueError("No data found in covalent response.")

        # Should never happen. But since we are using this key elsewhere,
        # this check is required.
        if "error" not in response:
            raise ValueError("No error found in response.")

        if "items" not in response["data"]:
            raise ValueError("No items found in data.")

    def request_transactions(
        self, for_address: str, page_number: int
    ) -> requests.Response:
        """
        Response json looks like this
        {
            "data": {
                "address": "0x94d8f036a0fbc216bb532d33bdf6564157af0cd7",
                "updated_at": "2022-02-22T12:29:52.068887528Z",
                "next_update_at": "2022-02-22T12:34:52.068887688Z",
                "quote_currency": "USD",
                "chain_id": 1,
                "items": [<transaction #1>, <transaction #2>, ...],
                "pagination": {
                    "has_more": true,
                    "page_number": 0,
                    "page_size": 100,
                    "total_count": null
                },
                "error": false,
                "error_message": null,
                "error_code": null
            }
        }

        Args:
            for_address (str): _description_
            page_number (int): _description_

        Returns:
            Any: _description_
        """

        logging.info(
            f"Extracting for: {for_address}, covalent page number: {page_number}"
        )

        request_uri = COVALENT_TRANSACTIONS_URI(
            for_address, page_number, self._network_id
        )

        response = requests.get(request_uri)

        if response.status_code != 200:
            logging.warning(
                f"Can't pull transactions. Response status code:{response.status_code}.",
                f" Response:{response.text}. Retrying...",
            )
            # todo: might need tweaking
            time.sleep(REQUEST_TRANSACTIONS_SLEEP)
            return self.request_transactions(for_address, page_number)

        response_json = response.json()
        self._validate_transactions_response(response_json)

        if response_json["error"] is not False:
            logging.warning(
                f"Covalent data error. Error code:{response_json['error_code']}.",
                f" Error message:{response_json['error_message']}. Retrying...",
            )
            # todo: might need tweaking
            time.sleep(REQUEST_TRANSACTIONS_SLEEP)
            return self.request_transactions(for_address, page_number)

        return response

    # todo: return type
    def get_transactions(self, response: requests.Response) -> Any:
        """_summary_

        Args:
            response (requests.Response): _description_

        Returns:
            Any: _description_
        """

        response_json = response.json()
        self._validate_transactions_response(response_json)

        transactions = response_json["data"]["items"]

        return transactions

    # todo: transaction type
    @staticmethod
    def get_block_height_from_transaction(transaction: Any) -> int:
        """_summary_

        Args:
            transaction (Any): _description_

        Returns:
            int: _description_
        """
        return transaction["block_height"]

    def get_block_height(self, response: requests.Response) -> Optional[int]:
        """
        Given a raw response from the transactions endpoint, gives you the
        block height. This assumes that the URI uses to request the transactions
        had a query param to order the transactions in the descending order.
        This means that we are taking the first item on the items list and returning
        its block height.

        Args:
            response (requests.Response): _description_

        Returns:
            Optional[int]: _description_
        """

        transactions = self.get_transactions(response)

        if len(transactions) == 0:
            return None

        return self.get_block_height_from_transaction(transactions[0])
