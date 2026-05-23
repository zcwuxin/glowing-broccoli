# Time Awareness Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给虞晚 agent 添加 `get_time_context` 工具，让她感知当前时间、时段、日期、临近节日/节气。

**Architecture:** 单文件改动 `agent/tools.py`，用 `@tool` 装饰器写一个无参函数，硬编码中国传统节日和二十四节气日期，按7天阈值过滤临近节气/节日。不引入任何外部依赖。

**Tech Stack:** Python `datetime`, `langchain_core.tools.tool`

---

### Task 1: 实现 `get_time_context` 工具函数

**Files:**
- Modify: `daiyu_agent/agent/tools.py`

- [ ] **Step 1: 写入完整实现**

将 `daiyu_agent/agent/tools.py` 替换为以下内容：

```python
"""Agent 工具集"""

from datetime import date, datetime
from langchain_core.tools import tool

# ── 时段标签 ──
_PERIOD_LABELS: list[tuple[int, int, str]] = [
    (0, 5, "深夜"),
    (5, 8, "清晨"),
    (8, 11, "上午"),
    (11, 13, "中午"),
    (13, 17, "下午"),
    (17, 19, "傍晚"),
    (19, 23, "晚上"),
    (23, 24, "深夜"),
]

_WEEKDAY_NAMES = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

# ── 节日/节气 (month, day, name, is_term) ──
# 农历节日取每年近似公历日期
_HOLIDAYS: list[tuple[int, int, str]] = [
    (1, 1, "元旦"),
    (2, 14, "情人节"),
    (2, 17, "春节"),
    (3, 3, "元宵节"),
    (4, 5, "清明节"),
    (5, 1, "劳动节"),
    (6, 19, "端午节"),
    (8, 12, "七夕"),
    (9, 25, "中秋节"),
    (10, 1, "国庆节"),
    (10, 11, "重阳节"),
    (12, 22, "冬至"),
]

# 二十四节气（公历近似日期）
_SOLAR_TERMS: list[tuple[int, int, str]] = [
    (1, 5, "小寒"), (1, 20, "大寒"),
    (2, 4, "立春"), (2, 19, "雨水"),
    (3, 6, "惊蛰"), (3, 21, "春分"),
    (4, 5, "清明"), (4, 20, "谷雨"),
    (5, 6, "立夏"), (5, 21, "小满"),
    (6, 6, "芒种"), (6, 22, "夏至"),
    (7, 7, "小暑"), (7, 23, "大暑"),
    (8, 8, "立秋"), (8, 23, "处暑"),
    (9, 8, "白露"), (9, 23, "秋分"),
    (10, 8, "寒露"), (10, 24, "霜降"),
    (11, 8, "立冬"), (11, 22, "小雪"),
    (12, 7, "大雪"), (12, 22, "冬至"),
]


def _get_period(hour: int) -> str:
    for start, end, label in _PERIOD_LABELS:
        if start <= hour < end:
            return label
    return "深夜"


def _nearby_events(today: date, days: int = 7) -> list[str]:
    """返回距离 today 在 days 天内的节日/节气名称"""
    result: list[str] = []
    year = today.year
    for month, day, name in _HOLIDAYS + _SOLAR_TERMS:
        try:
            event_date = date(year, month, day)
        except ValueError:
            continue
        diff = abs((event_date - today).days)
        if diff == 0:
            result.append(f"今天是{name}")
        elif diff <= days:
            arrow = "还有" if event_date > today else "已过"
            result.append(f"临近{name}（{arrow}{diff}天）")
    return result


@tool
def get_time_context() -> str:
    """获取当前时间上下文：时段、日期、临近节日/节气"""
    now = datetime.now()
    period = _get_period(now.hour)
    weekday = _WEEKDAY_NAMES[now.weekday()]
    today = now.date()

    base = f"现在是{weekday}{period}。{now.year}年{now.month}月{now.day}日 {weekday} {now.hour:02d}:{now.minute:02d}。"
    events = _nearby_events(today)
    if events:
        base += " " + "；".join(events)
    return base


AGENT_TOOLS = [get_time_context]
```

- [ ] **Step 2: 验证导入无报错**

```bash
cd D:\inside_agent\daiyu_agent && python -c "from agent.tools import AGENT_TOOLS, get_time_context; print(len(AGENT_TOOLS)); print(get_time_context.invoke({}))"
```

预期：输出 `1` 和时间上下文字符串。

**期望结果格式**：
```
1
现在是星期四下午。2026年5月23日 星期四 15:30。
```
或带节日：
```
1
现在是星期四下午。2026年5月23日 星期四 15:30。 临近端午节（还有8天）。
```

### Task 2: 编写并运行测试

**Files:**
- Create: `daiyu_agent/tests/test_tools.py`

- [ ] **Step 1: 创建测试文件**

如果 `tests/` 目录不存在则先创建：

```bash
cd D:\inside_agent\daiyu_agent && python -c "import os; os.makedirs('tests', exist_ok=True); open('tests/__init__.py', 'a').close()"
```

写入 `daiyu_agent/tests/test_tools.py`：

```python
"""测试 agent/tools.py"""

from datetime import date
from agent.tools import _get_period, _nearby_events, get_time_context


class TestGetPeriod:
    def test_midnight(self):
        assert _get_period(3) == "深夜"

    def test_morning(self):
        assert _get_period(9) == "上午"

    def test_noon(self):
        assert _get_period(12) == "中午"

    def test_afternoon(self):
        assert _get_period(15) == "下午"

    def test_evening(self):
        assert _get_period(18) == "傍晚"

    def test_night(self):
        assert _get_period(21) == "晚上"

    def test_late_night(self):
        assert _get_period(23) == "深夜"

    def test_boundaries(self):
        assert _get_period(0) == "深夜"
        assert _get_period(5) == "清晨"
        assert _get_period(8) == "上午"
        assert _get_period(11) == "中午"
        assert _get_period(13) == "下午"
        assert _get_period(17) == "傍晚"
        assert _get_period(19) == "晚上"


class TestNearbyEvents:
    def test_exact_match_today(self):
        events = _nearby_events(date(2026, 1, 1))
        assert "今天是元旦" in " ".join(events)

    def test_within_7_days(self):
        events = _nearby_events(date(2026, 1, 5))
        names = " ".join(events)
        assert "元旦" in names or "小寒" in names

    def test_no_events_far_away(self):
        events = _nearby_events(date(2026, 3, 15))
        assert events == []

    def test_solar_term_match(self):
        events = _nearby_events(date(2026, 2, 4))
        names = " ".join(events)
        assert "立春" in names


class TestGetTimeContext:
    def test_returns_string(self):
        result = get_time_context.invoke({})
        assert isinstance(result, str)
        assert len(result) > 20

    def test_contains_period_label(self):
        result = get_time_context.invoke({})
        periods = ["深夜", "清晨", "上午", "中午", "下午", "傍晚", "晚上"]
        assert any(p in result for p in periods)

    def test_contains_year(self):
        result = get_time_context.invoke({})
        assert "2026" in result

    def test_is_langchain_tool(self):
        assert hasattr(get_time_context, "invoke")
        assert hasattr(get_time_context, "name")
```

- [ ] **Step 2: 安装 pytest（如未安装）并运行测试**

```bash
cd D:\inside_agent\daiyu_agent && pip install pytest -q && python -m pytest tests/test_tools.py -v
```

预期：全部 PASS。

- [ ] **Step 3: 提交**

```bash
git add daiyu_agent/agent/tools.py daiyu_agent/tests/test_tools.py daiyu_agent/tests/__init__.py
git commit -m "feat: add get_time_context tool with Chinese holidays and solar terms"
```
