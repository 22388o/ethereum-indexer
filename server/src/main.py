#!/usr/bin/env python
"""
Entrypoint for GraphQL server.
"""
# pylint: disable=too-few-public-methods

import logging
import os
import sys
from typing import Optional

from aiohttp import web
from tartiflette_aiohttp import register_graphql_handlers

from interfaces.iserver import IServer


class Server(IServer):
    """@inheritdoc IServer"""

    def __init__(
        self,
        to_serve: str,
        host: Optional[str] = "0.0.0.0",
        port: Optional[int] = 8080,
        graphiql_debug: Optional[bool] = False,
    ) -> None:
        self.to_serve = to_serve
        self.host = host
        self.graphiql_debug = graphiql_debug
        self.port = port

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

    log_file = "sylvester.log"
    to_serve = "sylvester"

    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(relativeCreated)6d %(process)d %(message)s",
    )

    server = Server(to_serve, port=8080, graphiql_debug=True)
    server()


if __name__ == "__main__":
    sys.exit(main())
