# ethereum-indexer

Personal blockchain indexer to not depend on services like The Graph, which proved to be incredibly unreliable.

Currently, only supports Ethereum mainnet.

## How It Works

**Extract [Raw Txn Data]** All transactions for a given address are downloaded and stored in a db. This process does not terminate when it has downloaded all the data. It runs to poll for any new blocks containing our address.

**Transform & Load [Maintaining State]** Next, according to the rules of how to parse the above, state starts to build up. Once it catches up with the head of the blockchain, it continues to run checking in the db if there were any new raw txn data entries from the above.

**Serve [Serving State]** `graphql` server is spawned up with which you can query all the above state. Each response item will contain the block number, to indicate up to what block number the response state is valid.

## Implementation Dependencies

In our implementation, we choose [Covalent](https://www.covalenthq.com/) as the source of historical transactions pertaining to an address. The infrastructure of this code heavily depends on implementing interfaces, thus is very modular and developers can choose to remove this dependency in their extractors.

## Conventions

Interfaces are first described before implementation to enforce modularity. All interface functions are described and this description is avoided in implementations.

## Tests

In `src`, run

`python -m pytest tests`

This should be ran in your `poetry` environment. To drop into poetry environment, first run `poetry install`, and then `poetry shell`. You might need to change your python version to `3.9` for it to install the virtual environment for you.

### Implementation Specific Details

To change the network that covalent extracts transactions from, go to `extractor/covalent.py`

### For Developers

It is paramount that you follow the linting and formatting conventions of this repository.

Make sure to lint and format modules individually before pushing. Otherwise, the pylint and black git actions will fail. Both linting and formatting should be done on a per-module basis. That is to say, lint/format `indexer` and `server` separately.

To lint a module, navigate to the root module directory (`server/` or `indexer/`), enter poetry shell by running `poetry shell`, and execute `pylint --recursive=y .` and `black .`.

Note: Linting and formatting with pre-commit has been deprecated because it does not play well with the monolithic structure of the project.

### TODO

1. Dockerfile
2. back ups
3. remove the disable of duplicate code in .pylintrc (i.e. refactor the code such that there is no duplicate code)
