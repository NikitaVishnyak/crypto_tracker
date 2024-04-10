import argparse

import aiohttp

from application.app import create_app

parser = argparse.ArgumentParser(description="Demo project")
parser.add_argument('--host', help='Host to listen', default='127.0.0.1')
parser.add_argument('--port', help='Port to accept connections', default=8000)

args = parser.parse_args()

app = create_app()

if __name__ == '__main__':
    aiohttp.web.run_app(app, host=args.host, port=args.port)
