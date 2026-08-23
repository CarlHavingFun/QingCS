# ComfyUI public bridge probe

- UTC: 2026-08-23T09:27:29Z
- Base: `https://my-agent.com.cn/comfy`

## DNS
```text
139.196.7.123   STREAM my-agent.com.cn
139.196.7.123   DGRAM  
139.196.7.123   RAW    
```

## Endpoints

### `/system_stats`
- Initial HTTP: `302`
- Redirect: `https://my-agent.com.cn/auth/`
- Final HTTP: `200`
- Final URL: `https://my-agent.com.cn/auth/`
- Content-Type: `text/html; charset=utf-8`
- Bytes: `1137`

## Authentication page structure (values redacted)
```text
forms= []
inputs= []
buttons= []
visible_text= You need to enable JavaScript to run this app.
script_hints= ['src=./static/js/index.CXslS62G.js']
```

### `/queue`
- Initial HTTP: `302`
- Redirect: `https://my-agent.com.cn/auth/`
- Final HTTP: `200`
- Final URL: `https://my-agent.com.cn/auth/`
- Content-Type: `text/html; charset=utf-8`
- Bytes: `1137`

### `/history`
- Initial HTTP: `302`
- Redirect: `https://my-agent.com.cn/auth/`
- Final HTTP: `200`
- Final URL: `https://my-agent.com.cn/auth/`
- Content-Type: `text/html; charset=utf-8`
- Bytes: `1137`

### `/object_info`
- Initial HTTP: `302`
- Redirect: `https://my-agent.com.cn/auth/`
- Final HTTP: `200`
- Final URL: `https://my-agent.com.cn/auth/`
- Content-Type: `text/html; charset=utf-8`
- Bytes: `1137`
