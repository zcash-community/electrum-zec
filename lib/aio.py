import asyncio
import json
from . import bitcoin

wallet = None

async def read_reply(reader):
    print("read reply called")
    obj = b""
    while True:
      obj += await reader.read(1)
      print("obj now", obj)
      try:
        obj = json.loads(obj.decode("ascii"))["result"]
      except ValueError:
        continue
      else:
        print("got", obj)
        return obj

def rpc_request(method, *params):
    return json.dumps({"jsonrpc": "2.0", "id": 1, "params": params, "method": method}).encode("ascii") + b"\n"

def get_request_response_fun(reader, writer):
    async def send_request_get_response(method, *params):
        writer.write(rpc_request(method, *params))
        await writer.drain()
        return await read_reply(reader)
    return send_request_get_response

async def slow_operation(future):
    reader, writer = await asyncio.open_connection("148.251.87.112", 51002)
    req = get_request_response_fun(reader, writer)

    hash = bitcoin.address_to_scripthash("mttiY9WTf17eNgdwJ8zJPg3ETd4wcUY7o4")
    print(await req("server.version", "1.1", "1.1"))
    hash_height_pairs = await req("blockchain.scripthash.get_history", hash)
    print(hash_height_pairs)
    for dict in hash_height_pairs:
        # also available: dict["height"]
        print(dict["tx_hash"])
        print(await req("blockchain.transaction.get", dict["tx_hash"]))
    writer.close()
    future.set_result('Future is done!')

def asyncio_test(thiswallet):
    global wallet
    wallet = thiswallet
    loop = asyncio.get_event_loop()
    future = asyncio.Future()
    asyncio.ensure_future(slow_operation(future))
    loop.run_until_complete(future)
    loop.close()
    return future.result()

class SocketPipe:
    def __init__(self, hostname_port, loop):
        print("ignoring " + hostname_port)
        #self.hostname_port = hostname_port
        self.hostname_port = "148.251.87.112:51002"
        self.reader = self.writer = None
        self.loop = loop
        self.lock = asyncio.Lock(loop=loop)
    async def _get_read_write(self):
        async with self.lock:
            if self.reader is not None and self.writer is not None:
                return self.reader, self.writer
            print("making reader and writer")
            host, port = self.hostname_port.split(":")[0], int(self.hostname_port.split(":")[1])
            print(host, port, self.loop)
            reader, writer = await asyncio.open_connection(host, port, loop=self.loop)
            print("opened connection")
            self.reader = reader
            self.writer = writer
            return self.reader, self.writer
    async def send_all(self, list_of_requests):
        _, w = await self._get_read_write()
        print(len(list_of_requests))
        for i in list_of_requests:
            w.write(json.dumps(i).encode("ascii") + b"\n")
        await w.drain()
        print("sent and drained", list_of_requests)
    async def close(self):
        _, w = await self._get_read_write()
        w.close()
    async def get(self):
        r, w = await self._get_read_write()
        return await read_reply(r)
    def idle_time():
        return 0
