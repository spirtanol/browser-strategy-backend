from starlette.routing import Mount, Route, WebSocketRoute

from fastapi import FastAPI


def dump_routes(app: FastAPI):
    def walk(prefix, routes):
        for r in routes:
            if isinstance(r, Mount):
                print(f"MOUNT      {prefix + r.path} -> {type(r.app).__name__}")
                # рекурсивно обойти вложенные
                walk(prefix + r.path, getattr(r.app, "routes", []) or getattr(r, "routes", []))
            elif isinstance(r, Route):
                methods = ",".join(sorted(r.methods or []))
                print(f"ROUTE {methods:7} {prefix + r.path} -> {getattr(r.endpoint,'__name__', r.name)}")
            elif isinstance(r, WebSocketRoute):
                print(f"WS               {prefix + r.path} -> {r.name}")
    walk("", app.router.routes)