#!/usr/bin/env python
"""
Entrypoint for GraphQL server.
"""
# pylint: disable=too-few-public-methods

import logging
import os
import sys
from aiohttp import web
from tartiflette_aiohttp import register_graphql_handlers

from config import Config


from interfaces.iserver import IServer


class Server(IServer):
    """
    IServer Implementation

    to_server: The server namespace to serve
    host: the host address to serve on (default: 0.0.0.0)
    port: the port to serve on (default: 8080)
    graphiql_debug: Whether to serve GraphiQL debug client on http://host/graphiql (default: False)
    """

    def __init__(
        self,
        config: Config
    ) -> None:
        self._config = config
        self.to_serve = self._config.get_server_name()
        self.host = self._config.get_host()
        self.port = self._config.get_port()
        self.graphiql_debug = self._config.with_graphiql_debug()

    def start(self) -> None:
        """@inheritdoc IServer"""
        # loop = asyncio.get_event_loop()

        # Init aiohttp server
        app = web.Application()

        root_path = os.path.dirname(os.path.abspath(__file__))

        sdl_path = f"{root_path}/servers/{self.to_serve}/sdl"

        register_graphql_handlers(
            app,
            engine_sdl=sdl_path,
            engine_modules=[
                f"servers.{self.to_serve}.query_resolvers",
            ],
            executor_http_endpoint="/graphql",
            executor_http_methods=["POST"],
            graphiql_enabled=self.graphiql_debug,
        )

        # Bind aiohttp to asyncio
        web.run_app(app, host=self.host, port=self.port)
        return 0


def main():
    """Graphql Server Entrypoint"""

    config = Config.sylvester(graphiql_debug=True)

    logging.basicConfig(
        filename=config.get_log_filename(),
        level=logging.DEBUG,
        format="%(relativeCreated)6d %(process)d %(message)s",
    )

    server = Server(config)
    server()


if __name__ == "__main__":
    sys.exit(main())
