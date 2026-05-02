import sys

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    try:
        import uvicorn

        uvicorn.run("app.web:app", host=host, port=port, reload=False, factory=False, access_log=True, forwarded_allow_ips='*')
    except ModuleNotFoundError:
        try:
            import hypercorn.asyncio
            from hypercorn.config import Config

            cfg = Config()
            cfg.bind = [f"{host}:{port}"]
            hypercorn.asyncio.run(hypercorn.asyncio.serve(app, cfg))
        except ModuleNotFoundError:
            sys.stderr.write(
                "❌ Не найден uvicorn или hypercorn. "
                "Установите:  pip install uvicorn[standard]\n"
            )
            sys.exit(1)