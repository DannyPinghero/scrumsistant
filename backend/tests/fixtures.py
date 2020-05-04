import fakeredis
import pytest
import websockets

from ..flask_main import create_app as create_flask_server
from ..flask_main import import_routes as import_flask_routes
from ..server import Server

WEBSOCKET_URI = "ws://localhost:8000"


@pytest.fixture
def flask_client(event_loop):
    test_config = {'TESTING': True}
    app = create_flask_server(test_config=test_config)
    import_flask_routes()
    with app.test_client() as flask_client_obj:
        import pdb

        pdb.set_trace()
        yield flask_client_obj


@pytest.fixture
async def websocket_server(event_loop):
    server_ = Server(redis_client=fakeredis.FakeRedis())
    task = server_.get_server_task(server_.router)
    server = await task
    yield
    try:
        # sometimes this throws an exception, trying to close the thread twice
        # not 100000000% sure wtf that's about, but this seems ok
        server_._redis_pubsub_thread.stop()
    except ValueError:
        # the exception is
        # ValueError: Invalid file descriptor: -1
        pass
    server.close()
    await server.wait_closed()


@pytest.fixture
async def websocket_client(event_loop):
    async with websockets.connect(WEBSOCKET_URI) as websocket:
        yield websocket


@pytest.fixture
async def send_message(websocket_server, websocket_client, event_loop):
    async def _send_message(message):
        await websocket_client.send(message)
        greeting = await websocket_client.recv()
        return greeting

    return _send_message
