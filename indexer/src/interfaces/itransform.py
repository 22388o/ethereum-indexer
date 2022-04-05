"""
We use formal interfaces to enforce **modularity** first and foremost, and then structure
onto all of the code that is to be written.

About transform implicit assumptions:

You specify which transformers to use from the transformers
directory. Each transformer must sit in its separate folder and
must include a main.py file that describes the handlers for the
events. There also must be a config file in that directory.

Name your files such that there is a part that gives your
transformer recognisable slug and a part that versions them.

Only those transformers that are specified by the user will be
used (i.e. not all of the transformers will be used).

Example:

src
 |
 |transformers
 |  |
 |  |rumble-kong-league-0.0.1
 |  |  |
 |  |  |main.py
 |  |  |config.json
 |  |  |

Where ``config.json`` looks like

...

And ``main.py`` looks like
"""
import abc


class ITransform(metaclass=abc.ABCMeta):
    """
    Takes a config dict to perform its work.
    The dict must include the following information:
      - event abis of interest
    Like extract, it runs indefinitely. It checks the database
      every 5 seconds to see if there are any new transactions
      that require transforming.
    No need to provide any paths, since it will look for
    required filed in `transformers` folder.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "transform")
            and callable(subclass.transform)
            and hasattr(subclass, "flush")
            and callable(subclass.flush)
            or NotImplemented
        )

    @abc.abstractmethod
    def transform(self) -> None:
        """
        Transforms the raw transactions' events.

        Raises:
            NotImplementedError: If this function is not
            implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def flush(self) -> None:
        """
        Persists the transformed data. Could be through the means
        of writing to the database.

        Raises:
            NotImplementedError: If this function is not
            implemented.
        """
        raise NotImplementedError

    def __call__(self):
        """
        Before transforming, ensure that configs' addresses are all
        in the database. If they are not, produce soft warning and
        continue working on the ones that are in the database.

        It is the responsibility of the implementer to wait between
        the calls if required.
        """
        while True:
            self.transform()
            self.flush()
