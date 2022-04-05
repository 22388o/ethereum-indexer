"""We use formal interfaces to enforce **modularity** first and foremost, and then structure
onto all of the code that is to be written.
"""
import abc


class IExtract(metaclass=abc.ABCMeta):
    """
    It polls indefinitely with desired frequency the blockchain to obtain
    the latest transactions, to identify and store the ones that are
    concerned with the address.

    The job of extractor is to extract all the historical raw transaction
    data pertaining to an address and check for any new transactions
    concerning the said addresses every update_frequency.

    The said transactions are stored in memory until loader takes them
    and writes to the db. Upon successful write, they are removed from memory.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "extract")
            and callable(subclass.extract)
            and hasattr(subclass, "flush")
            and callable(subclass.flush)
            or NotImplemented
        )

    @abc.abstractmethod
    def extract(self) -> None:
        """
        Extracts the new data since the last extraction. If this
        is the first extraction, then extracts everything up to now.
        Indicates if extraction was successful upon completion.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractmethod
    def flush(self) -> None:
        """
        Flushes the extracted in memory data into the db or other
        means of storage.

        Raises:
            NotImplementedError: if this function is not implemented.
        """
        raise NotImplementedError

    def __call__(self):
        """
        It is the responsibility of the implementer to wait in between
        the calls if required.
        """
        while True:
            self.extract()
            self.flush()
