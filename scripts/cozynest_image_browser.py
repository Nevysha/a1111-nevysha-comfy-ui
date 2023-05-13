import asyncio
import json
import multiprocessing
import os
import threading

from PIL import Image
from PIL.ExifTags import TAGS
from modules import script_callbacks
import websockets
from websockets.server import serve


async def start_server(images_folders, server_port):
    print(f"CozyNestSocket: Starting socket server on localhost:{server_port}...")

    CLIENTS = set()

    async def handle_client(websocket, path):
        print(f"CozyNestSocket: New connection: {websocket.remote_address}")

        try:
            CLIENTS.add(websocket)
            while True:
                # Receive data from the client
                data = await websocket.recv()
                print(f"CozyNestSocket: Received data from {websocket.remote_address}: {data}")

                # decode the received data as json
                data = json.loads(data)
                res = await process(data)

                # Send a response back to the client
                if res:
                    await websocket.send(res)

        except websockets.exceptions.ConnectionClosed:
            print(f"CozyNestSocket: Connection closed: {websocket.remote_address}")

    async def process(data):
        what = data['what']
        if what == 'images':
            # scrape the images folder recursively
            images = []
            for images_folder in images_folders:
                for root, dirs, files in os.walk(images_folder):
                    for file in files:
                        if file.endswith(".png"):

                            # get exif data
                            exif = {}
                            try:
                                image = Image.open(os.path.join(root, file))
                                info = image.info
                                for tag, value in info.items():
                                    decoded = TAGS.get(tag, tag)
                                    exif[decoded] = value
                            except Exception as e:
                                print(f"CozyNestSocket: Error while getting exif data: {e}")
                                pass

                            images.append({
                                'path': os.path.join(root, file),
                                'metadata': {
                                    'date': os.path.getmtime(os.path.join(root, file)),
                                    'exif': exif
                                }
                            })

            # sort the images by date (newest first) metadata.date
            images.sort(key=lambda x: x['metadata']['date'], reverse=True)

            # send the images to the client
            data = {
                'what': 'images',
                'images': images
            }
            return json.dumps(data)

        if what == 'image_saved':
            await on_image_saved(data['data'])
            return json.dumps({
                'what': 'success',
                'data': 'None'
            })

        else:
            print(f"CozyNestSocket: Unknown data: {data}")
            return json.dumps({
                'what': 'error',
                'data': 'None',
                'error': 'Unknown data'
            })

    async def on_image_saved(data):
        print(f"CozyNestSocket: on_image_saved{data}")

        CLIENTS_COPY = CLIENTS.copy()
        CLIENTS.clear()

        for websocket in CLIENTS_COPY.copy():
            await websocket_send('dispatch_on_image_saved', data, websocket)

    async def websocket_send(what, data, websocket):
        try:
            await websocket.send(json.dumps({
                'what': what,
                'data': data
            }))
            CLIENTS.add(websocket)
        except websockets.ConnectionClosed:
            pass

    # Configure the WebSocket server
    async with serve(handle_client, 'localhost', server_port, ssl=None):
        await asyncio.Future()  # run forever
