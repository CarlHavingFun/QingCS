# ComfyUI + MiniMax-H3 一键生产包源码

- `qingcs_comfyui_pack_source.zip`：构建器、运行时与单元测试源码。
- GitHub Actions 会读取本仓库 44 章分镜，生成 440 个 FL2VA 视频 JSON、880 个首尾帧任务和 440 份可导入 ComfyUI 工作流，并上传可下载 ZIP。
- 产物不包含伪造的首尾帧 PNG；用户在本地 ComfyUI 中运行压缩包脚本生成真实图片。

源码包解压后可执行：

```bash
python -m unittest discover -s tests -v
python build_release.py --repo-root /path/to/QingCS --dist-dir /path/to/QingCS/dist
```
