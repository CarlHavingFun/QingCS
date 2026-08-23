# my-agent.com.cn route map

- UTC: 2026-08-23T11:22:37Z
- Method: GET without credentials, no mutation, redirects not followed.

| Path | HTTP | Location | Content-Type | Bytes |
|---|---:|---|---|---:|
| `/` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/robots.txt` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/.well-known/openid-configuration` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/healthz` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/api/health` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/openapi.json` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/comfy` | `302` | `https://my-agent.com.cn/comfy/` | `text/html` | `145` |
| `/comfy/` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/comfy/api` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/comfy/api/system_stats` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/comfy/system_stats` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/comfy/object_info` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/comfy/queue` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/comfy/history` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/comfy/prompt` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/comfy/ws` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/api/comfy/system_stats` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/mcp` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/mcp/` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/devspace` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/devspace/` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/godot` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/godot/` | `200` | `none` | `text/html; charset=UTF-8` | `748` |
| `/iterm2` | `302` | `https://my-agent.com.cn/iterm2/` | `text/html` | `145` |
| `/iterm2/` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/ssh` | `302` | `https://my-agent.com.cn/ssh/` | `text/html` | `145` |
| `/ssh/` | `302` | `https://my-agent.com.cn/auth/` | `text/html` | `145` |
| `/auth/api/state` | `200` | `none` | `application/json; charset=utf-8` | `148` |
