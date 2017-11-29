import asyncio
import json
from . import bitcoin

wallet = None

async def read_reply(reader):
    obj = b""
    while True:
      obj += await reader.read(1)
      try:
        return json.loads(obj.decode("ascii"))
      except ValueError:
        continue

def rpc_request(method, *params):
    return json.dumps({"jsonrpc": "2.0", "id": 1, "params": params, "method": method}).encode("ascii") + b"\n"

async def slow_operation(future):
    reader, writer = await asyncio.open_connection("148.251.87.112", 51002)
    hash = bitcoin.address_to_scripthash("mttiY9WTf17eNgdwJ8zJPg3ETd4wcUY7o4")
    writer.write(rpc_request("server.version", "1.1", "1.1"))
    await writer.drain()
    print(await read_reply(reader))
    writer.write(rpc_request("blockchain.scripthash.get_history", hash))
    await writer.drain()
    print(await read_reply(reader))
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
