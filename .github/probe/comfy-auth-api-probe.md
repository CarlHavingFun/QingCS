# Authelia public API probe

- UTC: 2026-08-23T09:29:33Z

## `/auth/api/configuration`
- HTTP: `403`
- Content-Type: `text/plain; charset=utf-8`
- Bytes: `13`
- Effective URL: `https://my-agent.com.cn/auth/api/configuration`
```text
403 Forbidden
```

## `/auth/api/state`
- HTTP: `200`
- Content-Type: `application/json; charset=utf-8`
- Bytes: `148`
- Effective URL: `https://my-agent.com.cn/auth/api/state`
```json
{
  "status": "OK",
  "data": {
    "username": "",
    "authentication_level": 0,
    "factor_knowledge": false,
    "default_redirection_url": "https://my-agent.com.cn/iterm2/"
  }
}
```

## `/auth/api/firstfactor`
- HTTP: `405`
- Content-Type: `text/plain; charset=utf-8`
- Bytes: `22`
- Effective URL: `https://my-agent.com.cn/auth/api/firstfactor`
```text
405 Method Not Allowed
```

## `/auth/api/secondfactor`
- HTTP: `404`
- Content-Type: `text/plain; charset=utf-8`
- Bytes: `13`
- Effective URL: `https://my-agent.com.cn/auth/api/secondfactor`
```text
404 Not Found
```

## `/auth/api/oidc/device-authorization`
- HTTP: `405`
- Content-Type: `text/plain; charset=utf-8`
- Bytes: `22`
- Effective URL: `https://my-agent.com.cn/auth/api/oidc/device-authorization`
```text
405 Method Not Allowed
```
