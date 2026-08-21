# generated

这里存放由 `tools/compile_storyboards.py` 生成的 `chNN.h3.json` 与 `index.json`。生成结果不提交，避免分镜修改后出现双重事实源。

```bash
python AI生产/H3生产包/tools/compile_storyboards.py \
  AI生产/H3生产包/config/qingcs-h3-manifest.json
```

每份 `chNN.h3.json` 含 10 个可验证 H3 任务；真正执行仍由 `tools/run_h3_batch.py` 统一转成官方 `mmx video generate` 命令。
