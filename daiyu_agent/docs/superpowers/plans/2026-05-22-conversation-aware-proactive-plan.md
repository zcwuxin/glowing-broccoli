# 对话语境驱动的主动消息 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在对话活跃期（聊天窗口开着或关闭后 5 分钟内）将主动消息从电脑状态驱动切换为对话上下文驱动，避免割裂对话语境。

**Architecture:** 在 `pet_tk.py` 中增加对话活跃状态追踪和对话历史收集，在 `_check_proactive()` 中根据活跃状态分流。`pet_tk.py` 与后端是独立进程通过 HTTP 通信，因此 prompt 常量在两端各自定义。

**Tech Stack:** Python, Tkinter, requests, 无新依赖

---

### Task 1: 新增 CONVERSATION_CONTINUE_PROMPT 到 persona.py

**Files:**
- Modify: `daiyu_agent/agent/persona.py`（末尾追加）

- [ ] **Step 1: 在 persona.py 末尾追加 prompt**

```python
CONVERSATION_CONTINUE_PROMPT = """## 对话状态
用户暂时没有回复，但对话还没结束。以下是最近的对话内容：

{history}

请根据上下文做出自然的反应——可以表达情绪、撒娇、或者带着宠溺催促一下。保持御姐人设，不要提问，不超过30字，直接说出话语。"""
```

- [ ] **Step 2: 验证语法**

```bash
python -c "from agent.persona import CONVERSATION_CONTINUE_PROMPT; print('OK')"
```

- [ ] **Step 3: 提交**

```bash
git add daiyu_agent/agent/persona.py
git commit -m "feat: add CONVERSATION_CONTINUE_PROMPT for conversation-aware proactive messaging"
```

---

### Task 2: 在 pet_tk.py 添加常量和实例变量

**Files:**
- Modify: `desktop_pet/pet_tk.py`

- [ ] **Step 1: 在 PROACTIVE_MESSAGES 之后添加新常量**

在 `PROACTIVE_MESSAGES = {...}` 之后（约第 136 行），插入：

```python
# 对话活跃窗口参数
CONVERSATION_ACTIVE_WINDOW = 300  # 聊天窗口关闭后 5 分钟内视为对话活跃
MAX_HISTORY_ROUNDS = 10           # 保留最近 10 轮对话

CONVERSATION_CONTINUE_PROMPT = """## 对话状态
用户暂时没有回复，但对话还没结束。以下是最近的对话内容：

{history}

请根据上下文做出自然的反应——可以表达情绪、撒娇、或者带着宠溺催促一下。保持御姐人设，不要提问，不超过30字，直接说出话语。"""
```

> `pet_tk.py` 通过 HTTP 与后端通信，不直接 import daiyu_agent 模块，因此在此独立定义 prompt 常量。

- [ ] **Step 2: 在 PetApp.__init__ 添加新实例变量**

在 `self._last_proactive_time = 0.0` 之后（约第 254 行），插入：

```python
self._chat_closed_time = 0.0
self._conversation_history = []  # [(user_msg, ai_reply), ...]
```

- [ ] **Step 3: 验证语法**

```bash
python -c "import ast; ast.parse(open('desktop_pet/pet_tk.py').read()); print('OK')"
```

- [ ] **Step 4: 提交**

```bash
git add desktop_pet/pet_tk.py
git commit -m "feat: add conversation state constants and fields to PetApp"
```

---

### Task 3: 实现 _is_conversation_active 判定方法

**Files:**
- Modify: `desktop_pet/pet_tk.py`

- [ ] **Step 1: 在 _check_proactive 方法之前添加 _is_conversation_active**

```python
def _is_conversation_active(self) -> bool:
    """判断对话是否处于活跃期"""
    if self.chat_open:
        return True
    if self._chat_closed_time and time.time() - self._chat_closed_time < CONVERSATION_ACTIVE_WINDOW:
        return True
    return False
```

- [ ] **Step 2: 验证语法**

```bash
python -c "import ast; ast.parse(open('desktop_pet/pet_tk.py').read()); print('OK')"
```

- [ ] **Step 3: 提交**

```bash
git add desktop_pet/pet_tk.py
git commit -m "feat: add _is_conversation_active helper to PetApp"
```

---

### Task 4: 在 _do_chat 中收集对话历史

**Files:**
- Modify: `desktop_pet/pet_tk.py`

- [ ] **Step 1: 在 _do_chat 中追加对话历史**

在 `_do_chat` 方法中，`self.last_reply = reply` 之后（约第 670 行），插入：

```python
# 收集对话历史（保留最近 N 轮）
self._conversation_history.append((text, reply))
if len(self._conversation_history) > MAX_HISTORY_ROUNDS:
    self._conversation_history = self._conversation_history[-MAX_HISTORY_ROUNDS:]
```

- [ ] **Step 2: 验证语法**

```bash
python -c "import ast; ast.parse(open('desktop_pet/pet_tk.py').read()); print('OK')"
```

- [ ] **Step 3: 提交**

```bash
git add desktop_pet/pet_tk.py
git commit -m "feat: collect conversation history in _do_chat"
```

---

### Task 5: 在 close_all / open_chat 中管理活跃窗口

**Files:**
- Modify: `desktop_pet/pet_tk.py`

- [ ] **Step 1: close_all 记录关闭时间**

在 `close_all` 方法中，`self.label.configure(image=self.idle_img)` 之后（约第 521 行），插入：

```python
self._chat_closed_time = time.time()
```

- [ ] **Step 2: open_chat 超时清空旧历史**

在 `open_chat` 方法中，`self.chat_open = True` 之后（约第 504 行），插入：

```python
# 超过活跃窗口的旧对话历史视为已结束，清空
if self._chat_closed_time and time.time() - self._chat_closed_time >= CONVERSATION_ACTIVE_WINDOW:
    self._conversation_history = []
self._chat_closed_time = 0.0
```

- [ ] **Step 3: 验证语法**

```bash
python -c "import ast; ast.parse(open('desktop_pet/pet_tk.py').read()); print('OK')"
```

- [ ] **Step 4: 提交**

```bash
git add desktop_pet/pet_tk.py
git commit -m "feat: manage conversation active window in close_all and open_chat"
```

---

### Task 6: 实现对话续接方法和 _check_proactive 分流

**Files:**
- Modify: `desktop_pet/pet_tk.py`

- [ ] **Step 1: 添加 _do_conversation_continue 方法**

在 `_do_proactive_chat` 方法之前（约第 418 行），插入：

```python
def _do_conversation_continue(self, message):
    """发送基于对话上下文的主动消息（不带电脑状态）"""
    try:
        if not self.session_id:
            self.session_id = uuid.uuid4().hex[:16]

        logger.info("对话续接 | session=%s | history_rounds=%d",
                   self.session_id, len(self._conversation_history))

        r = requests.post(f"{API}/api/chat/bijou", json={
            "session_id": self.session_id,
            "message": message,
            "context": "",  # 不带电脑状态
        }, timeout=60)
        reply = r.json().get("reply", "")
        self.last_reply = reply
        self._last_proactive_time = time.time()

        logger.info("对话续接回复 | session=%s | reply=%s", self.session_id, reply[:60])

        self.root.after(0, lambda r=reply: self._show_proactive_bubble(r))
        self.play_tts(reply)

    except Exception:
        logger.exception("对话续接失败")
```

- [ ] **Step 2: 在 _check_proactive 开头加入对话活跃分支**

在 `_check_proactive` 方法中，`duration = now - self._activity_start` 之后、`trigger_type = None` 之前，插入对话活跃判断块。即将：

```python
        duration = now - self._activity_start
        trigger_type = None
```

改为：

```python
        duration = now - self._activity_start

        # 对话活跃期：基于对话上下文而非电脑状态
        if self._is_conversation_active():
            if not self._conversation_history:
                return  # 无历史则跳过，不发主动消息
            recent = self._conversation_history[-5:]
            history_lines = []
            for user_msg, ai_reply in recent:
                history_lines.append(f"用户：{user_msg}")
                history_lines.append(f"虞晚：{ai_reply}")
            message = CONVERSATION_CONTINUE_PROMPT.format(
                history="\n".join(history_lines))
            self._do_conversation_continue(message)
            return

        trigger_type = None
```

- [ ] **Step 3: 验证语法**

```bash
python -c "import ast; ast.parse(open('desktop_pet/pet_tk.py').read()); print('OK')"
```

- [ ] **Step 4: 提交**

```bash
git add desktop_pet/pet_tk.py
git commit -m "feat: add conversation-aware branching in proactive loop"
```

---

### Task 7: 端到端验证

- [ ] **Step 1: 启动后端**

```bash
cd daiyu_agent && python main.py
```
预期：看到 "Uvicorn running on http://0.0.0.0:8001"

- [ ] **Step 2: 启动桌面宠物**

```bash
cd desktop_pet && python pet_tk.py
```
预期：宠物窗口正常显示，无报错

- [ ] **Step 3: 测试对话活跃期内主动消息**

1. 点击宠物打开聊天窗口
2. 发送一条消息（如"今天好累"）
3. 等待 AI 回复
4. 不关闭聊天窗口，等待 15-25 秒
5. 观察主动消息是否基于对话上下文（如催促、表达情绪）而不是评论电脑状态

- [ ] **Step 4: 测试关闭后缓冲期**

1. 关闭聊天窗口
2. 在 5 分钟内等待主动消息
3. 确认消息仍是对话上下文驱动

- [ ] **Step 5: 测试缓冲期过后**

1. 关闭聊天窗口后等待 6 分钟以上
2. 确认主动消息恢复为电脑状态驱动

- [ ] **Step 6: 测试无历史时兜底**

1. 启动宠物后不打开聊天窗口，等待主动消息 -- 应为电脑状态驱动（正常）
2. 打开聊天窗口但立即关闭（不发送任何消息），等待缓冲期内主动消息 -- 应跳过不发

- [ ] **Step 7: 提交（如有微调）**

```bash
git add desktop_pet/pet_tk.py
git commit -m "chore: final adjustments after manual testing"
```
