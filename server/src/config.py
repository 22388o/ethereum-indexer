"""
Defines Server Configuration schema and factory methods.
"""
from typing import Optional


class Config:
    """
    Each Config instance contains all the required information for end-to-end
    working of graphql server.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        log_filename: str,
        server_name: str,
        host: str,
        port: int,
        graphiql_debug: bool,
    ) -> None:
        self._log_filename = log_filename
        self._server_name = server_name
        self._host = host
        self._port = port
        self._graphiql_debug = graphiql_debug

    # Protecc the private attributes

    def __setattr__(self, key, value):
        # https://towardsdatascience.com/how-to-create-read-only-and-deletion-proof-attributes-in-your-python-classes-b34cd1019c2d

        forbid_reset_on = [
            "_log_filename",
            "_server_name",
            "_host",
            "_port",
            "_graphiql_debug",
        ]
        for k in forbid_reset_on:
            if key == k and hasattr(self, k):
                raise AttributeError(
                    "The value of the address attribute has already been set,"
                    " and can not be re-set."
                )

        self.__dict__[key] = value

    # Getters for the private attributes

    def get_log_filename(self) -> str:
        """
        Getter function for private attribute _log_filename.

        Returns:
            str: name of the log file that will be used to
            log everything related to graphql server.
        """
        return self._log_filename

    def get_server_name(self) -> str:
        """
        Getter function for private attribute _server_name.

        Returns:
            str: this is the name of the server folder
            where the logic, sdl schema, and resolvers sit.
        """
        return self._server_name

    def get_host(self) -> str:
        """
        Getter function for private attribute _host.

        Returns:
            str: host name of the server
        """
        return self._host

    def get_port(self) -> int:
        """
        Getter function for private attribute _port.

        Returns:
            int: port server runs on
        """
        return self._port

    def with_graphiql_debug(self) -> bool:
        """
        Getter function for private attribute _graphiql_debug.

        Returns:
            bool: graphiql is running on http://host/graphiql
        """
        return self._graphiql_debug

    # Presets

    @classmethod
    def sylvester(
        cls,
        host: Optional[str] = "0.0.0.0",
        port: Optional[int] = 8080,
        graphiql_debug: Optional[bool] = False,
    ):
        """
        Factory method for Sylvester graphql server configuration presets.

        Log filename: sylvester.log
        Server Name: sylvester
        Host: 0.0.0.0 (default)
        Port: 8080 (default)
        graphiql_debug: False (default)

        Returns:
            (Config): Sylvester Server Config instance.
        """

        log_filename = "sylvester.log"
        server_name = "sylvester"

        return cls(log_filename, server_name, host, port, graphiql_debug)

    @classmethod
    def azrael(
        cls,
        host: Optional[str] = "0.0.0.0",
        port: Optional[int] = 8080,
        graphiql_debug: Optional[bool] = False,
    ):
        """
        Factory method for Azrael graphql server configuration presets.

        Log filename: azrael.log
        Server Name: azrael
        Host: 0.0.0.0 (default)
        Port: 8080 (default)
        graphiql_debug: False (default)

        Returns:
            (Config): Azrael Server Config instance.
        """

        log_filename = "azrael.log"
        server_name = "azrael"

        return cls(log_filename, server_name, host, port, graphiql_debug)

    @classmethod
    def example_rumble_kong_league(
        cls,
        host: Optional[str] = "0.0.0.0",
        port: Optional[int] = 8080,
        graphiql_debug: Optional[bool] = False,
    ):
        """
        Factory method for RKL Kong Holders graphql server configuration presets.

        Log filename: example_rumble_kong_league.log
        Server Name: example_rumble_kong_league
        Host: 0.0.0.0 (default)
        Port: 8080 (default)
        graphiql_debug: False (default)

        Returns:
            (Config): RKL Kong Holders Server Config instance.
        """

        log_filename = "example_rumble_kong_league.log"
        server_name = "example_rumble_kong_league"

        return cls(log_filename, server_name, host, port, graphiql_debug)
