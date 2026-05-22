# 对话语境驱动的主动消息

## 问题

桌面宠物实时监控电脑状态（活动窗口），通过主动循环触发 AI 回复。当用户正在与 AI 聊天时（包括聊天窗口开着、或关掉后不久还在自然延续的对话），主动消息仍基于电脑状态生成（如"还在写代码啊"），割裂了对话语境。

## 设计目标

- 对话活跃期内，主动消息基于对话上下文延续，而非电脑状态
- 对话活跃期结束后，恢复原有的电脑状态驱动逻辑
- 改动集中在前端 `pet_tk.py`，后端仅新增一个 prompt 模板

## 具体设计

### 1. 对话活跃窗口

`pet_tk.py` 新增状态：

| 属性 | 类型 | 说明 |
|---|---|---|
| `_chat_closed_time` | `float` | 聊天窗口关闭的时间戳，0 表示未关过 |
| `_conversation_history` | `list[tuple]` | 最近 N 轮 `(用户消息, AI回复)` |

常量：

```python
CONVERSATION_ACTIVE_WINDOW = 300  # 聊天窗口关闭后 5 分钟内视为对话活跃
MAX_HISTORY_ROUNDS = 10           # 保留最近 10 轮对话
```

**状态判定**：

- 聊天窗口开着 (`self.chat_open == True`) → 对话活跃
- 聊天窗口关了，距离 `_chat_closed_time` < 300s → 对话活跃
- 否则 → 对话不活跃，恢复电脑状态驱动

### 2. 活跃期内主动消息

`_check_proactive()` 触发前增加判断：

- 如果对话活跃 → 使用 `PROACTIVE_CONVERSATION_CONTINUE` 消息模板
- 带入最近 5 轮对话历史，不带电脑状态 context
- 如果对话不活跃 → 保持原有逻辑（电脑状态驱动）

新增消息模板（`persona.py`）：

```python
CONVERSATION_CONTINUE_PROMPT = """## 对话状态
用户暂时没有回复，但对话还没结束。以下是最近的对话内容：

{history}

请根据上下文做出自然的反应——可以表达情绪、追问、撒娇、或者带着宠溺催促一下。保持御姐人设，不要提问，不超过30字，直接说出话语。"""
```

`{history}` 格式化为：

```
用户：xxx
虞晚：xxx
用户：xxx
虞晚：xxx
```

兜底：如果对话活跃但 `_conversation_history` 为空（极端情况），回退到原有电脑状态驱动逻辑，避免空历史发给 AI。

### 3. 对话历史收集

- `_do_chat()` 中，每次收到完整回复后，将 `(用户消息, AI回复)` 追加到 `_conversation_history`
- `open_chat()` 时不清空历史
- `close_all()` 时只记录 `_chat_closed_time = time.time()`，不清空历史
- 新的对话开始时（用户发出第一条消息时，若 `_conversation_history` 为空，或距离 `_chat_closed_time` 超过活跃窗口），清空旧历史

### 4. 影响范围

| 文件 | 改动 |
|---|---|
| `desktop_pet/pet_tk.py` | 新增活跃窗口判断、对话历史收集、主动消息分流逻辑 |
| `daiyu_agent/agent/persona.py` | 新增 `CONVERSATION_CONTINUE_PROMPT` |

不涉及后端 API 改动，不涉及数据库/文件存储改动。

## 测试要点

- 聊天窗口开着时，15-25s 后主动消息是否基于对话上下文
- 聊天窗口关掉后 4 分钟时，主动消息是否仍基于对话上下文
- 聊天窗口关掉后 6 分钟时，是否恢复电脑状态驱动
- 对话历史为空时，活跃期内是否回退到电脑状态驱动（兜底）
- 新开对话时，旧对话历史是否被正确清空
