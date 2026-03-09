
import os
import logging
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("game-proxy")

app = FastAPI(title="JackRoyals Game Provider Proxy")

PETERSONS_TARGET = os.environ.get("PETERSONS_TARGET", "https://petersons-debug.preview.emergentagent.com")
BETSOFT_TARGET = os.environ.get("BETSOFT_TARGET", "https://jackroyals.com")
SAFE_USER_AGENT = "JackRoyals-GameProxy/1.0"

async def proxy_request(request: Request, target_url: str) -> Response:
    body = await request.body()
    headers = {}
    for key, value in request.headers.items():
        if key.lower() not in ("host", "user-agent", "content-length"):
            headers[key] = value
    headers["User-Agent"] = SAFE_USER_AGENT
    logger.info("PROXY %s %s -> %s | body=%d", request.method, request.url.path, target_url, len(body))
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(method=request.method, url=target_url, headers=headers, content=body, params=dict(request.query_params))
        resp_headers = {}
        skip = {"transfer-encoding", "connection", "content-encoding", "content-length"}
        for key, value in resp.headers.items():
            if key.lower() not in skip:
                resp_headers[key] = value
        return Response(content=resp.content, status_code=resp.status_code, headers=resp_headers, media_type=resp.headers.get("content-type"))
    except Exception as e:
        logger.error("PROXY error: %s -> %s: %s", request.url.path, target_url, e)
        return Response(content=f"Proxy error: {e}", status_code=502)

@app.api_route("/api/petersons/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_petersons(request: Request, path: str):
    return await proxy_request(request, f"{PETERSONS_TARGET}/api/petersons/{path}")

@app.api_route("/petersons/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_petersons_compat(request: Request, path: str):
    return await proxy_request(request, f"{PETERSONS_TARGET}/petersons/{path}")

@app.api_route("/api/betsoft/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_betsoft(request: Request, path: str):
    return await proxy_request(request, f"{BETSOFT_TARGET}/api/betsoft/{path}")

@app.api_route("/betsoft/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_betsoft_compat(request: Request, path: str):
    return await proxy_request(request, f"{BETSOFT_TARGET}/betsoft/{path}")

@app.get("/")
async def root():
    return {"status": "online", "service": "JackRoyals Game Provider Proxy", "petersons_target": PETERSONS_TARGET, "betsoft_target": BETSOFT_TARGET}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
