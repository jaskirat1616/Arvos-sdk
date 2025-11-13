#!/usr/bin/env python3
"""Helper script to launch the ARVOS WebSocket server."""

import argparse
import asyncio
import os
import signal
import sys
from typing import Optional


def resolve_repo_root() -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, ".."))


def ensure_local_package_available(repo_root: str) -> None:
    python_src = os.path.join(repo_root, "python")
    if os.path.isdir(python_src) and python_src not in sys.path:
        sys.path.insert(0, python_src)


def verify_dependencies() -> None:
    try:
        import arvos  # noqa: F401
    except ModuleNotFoundError as exc:  # pragma: no cover - simple guard
        missing = exc.name
        if missing in {"arvos", "qrcode", "websockets"}:
            print(
                "❌ Missing dependency: "
                f"{missing}. Install requirements with `pip install -r "
                "../requirements.txt` from the repo root."
            )
            sys.exit(1)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ARVOS WebSocket server")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind")
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port to bind the WebSocket server (default: 8765)",
    )
    return parser


async def run_server(host: str, port: int) -> None:
    from arvos import ArvosServer  # noqa: WPS433 - imported lazily after guards

    server = ArvosServer(host=host, port=port)
    server.print_qr_code = lambda: None  # type: ignore[assignment]

    async def handle_connect(client_id: str) -> None:
        print(f"✅ ARVOS iOS connected: {client_id}")

    async def handle_disconnect(client_id: str) -> None:
        print(f"👋 ARVOS iOS disconnected: {client_id}")

    server.on_connect = handle_connect
    server.on_disconnect = handle_disconnect

    print(f"🔌 Starting ARVOS WebSocket server on {host}:{port}")
    await server.start()


def main() -> None:
    repo_root = resolve_repo_root()
    ensure_local_package_available(repo_root)
    verify_dependencies()

    parser = build_parser()
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    stop_event = asyncio.Event()

    def _signal_handler(_: int, __: Optional[object]) -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _signal_handler)

    async def runner() -> None:
        server_task = asyncio.create_task(run_server(args.host, args.port))
        await stop_event.wait()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

    try:
        loop.run_until_complete(runner())
    except KeyboardInterrupt:  # pragma: no cover - manual interruption
        pass
    finally:
        print("🛑 ARVOS WebSocket server stopped")
        loop.close()


if __name__ == "__main__":
    main()
