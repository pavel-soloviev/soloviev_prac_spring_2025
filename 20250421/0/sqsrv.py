import asyncio
import quadratic


async def echo(reader, writer):
    while data := await reader.readline():
        try:
            res = quadratic.sqroots(data.strip().decode())
        except ValueError:
            res = ""
        writer.write(f"{res}\n".encode())
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()


def serve():
    asyncio.run(main())
