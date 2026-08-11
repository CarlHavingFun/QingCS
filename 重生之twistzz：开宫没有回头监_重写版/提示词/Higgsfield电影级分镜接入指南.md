# Higgsfield电影级分镜接入指南

## 结论

Higgsfield官方skills对QingCS**有帮助，但主要帮助生成层，不负责把小说自动变成好电影**。真正的顺序仍是：

`正文 → 节拍 → 走位 → 导演书 → 镜头表 → 关键帧 → Higgsfield/其他视频模型生成 → animatic → QC`

直接把整章正文交给视频模型，只会得到若干漂亮但不连续的画面。

## 最值得使用的能力

1. **身份/参考一致性**：核心五席、皇帝、教练先做标准正面、三分之二侧面、全身和工作动作参考，再用于每镜。
2. **图生视频运动提示**：起始图固定后，只写“谁怎么动、镜头怎么动、动作停在哪里”。
3. **首尾帧过渡**：现代休息室→宫廷服务器房、鼠标点击→枪口火光、朱门开合等镜头，用起始帧和结束帧降低漂移。
4. **短片分段**：15秒生产单元可以拆成2—4个更短镜头，再在剪辑中组合，不让模型一次完成群像、证据、对白和转场。
5. **音频/环境层**：风扇、门禁、纸张、脚步和枪声作为剪辑桥；角色对白独立制作或后期处理，避免多人嘴型失控。
6. **失败镜头定点重做**：保留通过的镜头，只对身份、手部、地理或动作失败的镜头换方法。

## 不适合直接照搬的部分

- 视频解说skill的“每块一行旁白＋一幅画”不适合本项目多人对白和连续表演。
- 品牌广告、UGC、产品棚拍流程不能替代叙事导演。
- 模型推荐会变化，项目规则不绑定一个永远有效的模型名。
- “电影感”不能只靠焦段、景深和光斑；观众是否看懂人物关系优先。

## QingCS角色连续性串示例

```text
REFERENCE: same approved QingCS character sheet and same approved location keyframe.
ACTION: only the movement in this shot.
CAMERA: one motivated camera behavior.
BLOCKING: start position, path, final position, eyeline and screen direction.
PERFORMANCE: visible reaction, no mind-reading.
END STATE: exact pose, prop location and facial state at cut.
CONTINUITY: same face, hair, training uniform, light direction, door side, medal in left hand.
NEGATIVE: identity drift, random hairstyle, extra people, random text, unmotivated orbit, instant emotional acceptance.
```

## 第01章高风险镜头建议

- **场馆群像：** 先做空间关键帧，观众、奖杯、选手席位置通过后再动镜头。
- **残局：** 游戏内地理和人数提示后期合成，视频只负责清楚动作。
- **时空叠化：** 同一锁定机位制作现代、局部越界、完全大清三张关键帧。
- **身体确认：** 先手腕、声音、衣袖和倒影，避免身体凝视。
- **队友反应：** 分别拍吐槽、停顿、担心和查证，不生成“全员同时震惊”的站桩群像。
- **收尾住处：** 用奖牌、临时卡、训练便签和短簪盒完成证据静物，给主角的呼吸和思考留时间。
