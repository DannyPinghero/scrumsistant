import asyncio
import websockets
import json
import logging

from .utils import register, unregister
from .structs import MessageType, get_info_dict

WEBSOCKET_INFO_DICT = get_info_dict()
from .handler_funcs import (
	handle_get_usernames,
	handle_new_user_joined,
)

LOGGER = logging.getLogger(__name__)

class Server:
	def __init__(self, info_dict):
		LOGGER.debug(f"Initializing Server with {info_dict=}")
		self.info_dict = info_dict

	async def router(self, websocket, path):
		if websocket not in self.info_dict:
			await register(websocket)
		try:
			LOGGER.debug(self.info_dict)
			async for message in websocket:
				data = json.loads(message)
				LOGGER.debug(data)
				if data['type'] == MessageType.USER_JOINED.value:
					await handle_new_user_joined(websocket, data)
				elif data['type'] == 'getUsernames':
					await handle_get_usernames(websocket)
		finally:
			await unregister(websocket)

	def get_server_task(self, func, route = 'localhost', port = 8000):
		start_server = websockets.serve(func, route, port)
		return start_server

	def run(self, loop = None):
		start_server = self.get_server_task(self.router)
		if loop is None:
			loop = asyncio.get_event_loop()

		loop.run_until_complete(start_server)
		loop.run_forever()
