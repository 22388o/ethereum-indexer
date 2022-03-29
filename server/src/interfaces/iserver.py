"""
We use formal interfaces to enforce **modularity** first and foremost, and then structure
onto all of the code that is to be written.

About server implicit assumptions:

You specify which server to use from the servers
directory. Each server must sit in its separate folder and
must include a query_resolver.py and a "sdl" directory that contains all the types,
queries, subscriptions, and mutations specific to that server.

Name your files such that there is a part that gives your
server a recognisable slug and a part that versions them.

Only those servers that are specified by the user will be
used (i.e. not all of the servers will be used).

Example:
src
 |
 | main.py (IServer Implementation)
 | rumble-kong-league-0.0.1
 |  |
 |  | query_resolver.py
 |  | sdl
 |  |  | Query.graphql
 |  |  | Subscription.graphql (if needed)
 | libs
 |  |
 |  | custom scalars, directives and modules shared across servers


"""

import abc


class IServer(metaclass=abc.ABCMeta):
    #pylint: disable=missing-class-docstring

    @abc.abstractmethod
    def start(self) -> None:
        """
        Start graphql server.

        Raises:
            NotImplementedError: If this function is not
            implemented.
        """
        raise NotImplementedError

    def __call__(self):
        """
        Before starting server, ensure that data exists for querying.

        It is the responsibility of the implementer to wait between
        the calls if required.
        """
        self.start()
