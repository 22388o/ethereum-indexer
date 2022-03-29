class Config:
    """
    Each Config instance contains all the required information for end-to-end
    working of indexer and transformer.
    """

    def __init__(
        self, address: str, log_filename: str, transformer_name: str, network_id: int
    ) -> None:
        self._address = address
        self._log_filename = log_filename
        self._transformer_name = transformer_name
        self._network_id = network_id

    # Protecc the private attributes

    def __setattr__(self, key, value):
        # https://towardsdatascience.com/how-to-create-read-only-and-deletion-proof-attributes-in-your-python-classes-b34cd1019c2d

        forbid_reset_on = [
            "_address",
            "_log_filename",
            "_transformer_name",
            "_network_id",
        ]
        for k in forbid_reset_on:
            if key == k and hasattr(self, k):
                raise AttributeError(
                    "The value of the address attribute has already been set,"
                    " and can not be re-set."
                )

        self.__dict__[key] = value

    # Getters for the private attributes

    def get_address(self) -> str:
        """
        Getter function for private attribute _address.

        Returns:
            str: address that is indexed and transformed.
        """
        return self._address

    def get_log_filename(self) -> str:
        """
        Getter function for private attribute _log_filename.

        Returns:
            str: name of the log file that will be used to
            log everything related to the transformer and
            indexer.
        """
        return self._log_filename

    def get_transformer_name(self) -> str:
        """
        Getter function for private attribute _transformer_name.

        Returns:
            str: this is the name of the transformer folder
            where the logic that transforms the raw transaction
            data sits.
        """
        return self._transformer_name

    def get_network_id(self) -> int:
        """
        Getter function for private attribute _network_id.

        Returns:
            str: this indictes what network the contract is on.
        """
        return self._network_id

    # Presets

    @classmethod
    def sylvester(cls):
        """
        Factory method for Sylvester indexer and transformer configuration presets.

        Contract address: 0xa8D3F65b6E2922fED1430b77aC2b557e1fa8DA4a
        Log filename: sylvester.log
        Transformer Name: sylvester
        Network: 1 (Ethereum Mainnet).

        Returns:
            (Config): Sylvester Indexer/Transformer Config instance.
        """

        address = "0xa8D3F65b6E2922fED1430b77aC2b557e1fa8DA4a"
        log_filename = "sylvester.log"
        transformer_name = "sylvester"
        network_id = 1

        return cls(address, log_filename, transformer_name, network_id)

    @classmethod
    def azrael(cls):
        """
        Factory method for Azrael indexer and transformer configuration presets.

        Contract address: 0x94D8f036a0fbC216Bb532D33bDF6564157Af0cD7
        Log filename: azrael.log
        Transformer Name: azrael
        Network: 1 (Ethereum Mainnet).

        Returns:
            (Config): Azrael Indexer/Transformer Config instance.
        """

        address = "0x94D8f036a0fbC216Bb532D33bDF6564157Af0cD7"
        log_filename = "azrael.log"
        transformer_name = "azrael"
        network_id = 1

        return cls(address, log_filename, transformer_name, network_id)

    @classmethod
    def example_rumble_kong_league(cls):
        """
        Returns instance of an example_rumble_kong_league
        indexer and transformer. It collects all the raw
        transactions from rumble kong league collection and
        transforms them such that you can learn about which
        address holds what kong NFTs (ids).

        Network: Ethereum Mainnet.

        Returns:
            (Config): instance of this Config class instantiated with the correct
            configs.
        """

        address = "0xEf0182dc0574cd5874494a120750FD222FdB909a"
        log_filename = "example_rumble_kong_league.log"
        transformer_name = "example_rumble_kong_league"
        network_id = 1

        return cls(address, log_filename, transformer_name, network_id)

    @classmethod
    def rkl_club_auction(cls):
        """
        Returns instance of an rkl_club_auction
        indexer and transformer. It collects all the raw
        transactions from rkl club mint pass auction
        contract and transforms them such that you can learn
        about which address bid what amount in total.

        Network: Ethereum Kovan.

        Returns:
            (Config): instance of this Config class instantiated with the correct
            configs.
        """

        address = "0xa10bEa6303E89225D6fA516594632DddB6FBF3b5"
        log_filename = "rkl_club_auction.log"
        transformer_name = "rkl_club_auction"
        network_id = 42

        return cls(address, log_filename, transformer_name, network_id)
