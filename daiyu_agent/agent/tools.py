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

# ── 节日/节气 (month, day, name) ──
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
