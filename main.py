const RAILWAY = "https://mindful-essence-production-3202.up.railway.app";

export default {
  async fetch(request) {
    const ua = request.headers.get("User-Agent") || "";
    const url = new URL(request.url);
    const path = url.pathname;
    
    // Route ALL P&S callbacks through Railway (production has wrong secret)
    if (path.startsWith("/api/petersons/") || path.startsWith("/petersons/")) {
      const target = RAILWAY + path + url.search;
      const h = new Headers(request.headers);
      h.set("Host", new URL(RAILWAY).host);
      return fetch(target, {
        method: request.method, headers: h,
        body: request.method !== "GET" ? request.body : undefined,
      });
    }
    
    // Route Java/1.8 Betsoft callbacks through Railway
    if (ua.includes("Java/1.") && (path.startsWith("/api/betsoft/") || path.startsWith("/betsoft/"))) {
      const target = RAILWAY + path + url.search;
      const h = new Headers(request.headers);
      h.set("Host", new URL(RAILWAY).host);
      return fetch(target, {
        method: request.method, headers: h,
        body: request.method !== "GET" ? request.body : undefined,
      });
    }
    
    return fetch(request);
  },
};
Can you do both updates? Start with the Worker code (faster to deploy).

Mar 9, 12:58 AM

Rollback


