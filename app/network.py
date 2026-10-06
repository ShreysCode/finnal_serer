import socket

from zeroconf import AsyncZeroconf, ServiceInfo

from app.config import settings


SERVICE_TYPE = "_curly._tcp.local."
SERVICE_NAME = "Curly LLM._curly._tcp.local."


class CurlyServiceDiscovery:

    def __init__(self):
        self.zeroconf = None
        self.service_info = None

    async def start(self):
        try:
            local_ip = self._get_local_ip()
            service_port = settings.port

            self.zeroconf = AsyncZeroconf()

            self.service_info = ServiceInfo(
                SERVICE_TYPE,
                SERVICE_NAME,
                addresses=[socket.inet_aton(local_ip)],
                port=service_port,
                properties={
                    "api": "curly",
                    "version": "1.0",
                },
            )

            await self.zeroconf.async_register_service(
                self.service_info,
                allow_name_change=True,
            )

            print(
                "Curly mDNS service advertised: "
                f"{SERVICE_NAME} -> {local_ip}:{service_port}"
            )

        except Exception as e:
            print(
                "Curly mDNS advertisement failed: "
                f"{type(e).__name__}: {e}"
            )

            if self.zeroconf is not None:
                await self.zeroconf.async_close()

            self.zeroconf = None
            self.service_info = None

    async def stop(self):
        if self.zeroconf is not None:
            try:
                if self.service_info is not None:
                    await self.zeroconf.async_unregister_service(
                        self.service_info
                    )

            except Exception as e:
                print(
                    "Curly mDNS unregister failed: "
                    f"{type(e).__name__}: {e}"
                )

            finally:
                await self.zeroconf.async_close()

                self.zeroconf = None
                self.service_info = None

    @staticmethod
    def _get_local_ip():
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]

        finally:
            sock.close()