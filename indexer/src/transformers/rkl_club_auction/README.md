Collects bids across all the given auctions.

There will be a separate collection for each auction.

**Generally, there shouldn't be two auctions running in parallel. This means that once one auction has finished, there is no need to keep it running, and so the process can be stopped and a new extractor / transform process for new auction spawned.**

Will look like

```json
{
    "_id": "0xe8b6a57cbebaa8842edd9a2fb2856f8d222",
    "bids": [
        {"amount": 1.1, "timestamp": 11223277},
        {"amount": 0.2, "timestamp": 12231113},
        ...
    ]
}
```

Where `_id` is the bidder address lowercased.

There is no need to have auction address in that data, because that will be the name of the collection.

This helps us link with the Auction table that holds
meta around timestamps of each auction. We can create a
view this way, between these two collections (auction & biddings)

## Dev Notes

In the case of kovan testing, none of the transaction / event
details were decoded. So they must be decoded manually.

example of a possible event

```json
[
    "0xe694ab314354b7ccad603c48b44dce6ade8b6a57cbebaa8842edd9a2fb2856f8",
    "0x000000000000000000000000000000724350d0b24747bd816dc5031acb7efe0b",
    "0x000000000000000000000000000000000000000000000000002bd72a24874000"
]
```

## TODO

TODO: server for rkl club auctions will no longer work with these changes
