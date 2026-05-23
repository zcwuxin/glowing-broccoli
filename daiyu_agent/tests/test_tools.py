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
        assert "元旦" in names   # 4 days ago
        assert "小寒" in names   # exact match today

    def test_no_events_far_away(self):
        events = _nearby_events(date(2026, 7, 15))
        assert events == []

    def test_solar_term_match(self):
        events = _nearby_events(date(2026, 2, 4))
        names = " ".join(events)
        assert "立春" in names

    def test_year_boundary_dec_30_sees_new_year(self):
        """12月30日应该能看到元旦（1月1日）"""
        events = _nearby_events(date(2026, 12, 30))
        names = " ".join(events)
        assert "元旦" in names

    def test_year_boundary_jan_2_sees_new_year_passed(self):
        """1月2日应该能看到元旦已过"""
        events = _nearby_events(date(2027, 1, 2))
        names = " ".join(events)
        assert "元旦" in names

    def test_no_duplicate_qingming(self):
        """清明不应重复出现"""
        events = _nearby_events(date(2026, 4, 5))
        清明_count = sum(1 for e in events if "清明" in e)
        assert 清明_count == 1


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
        assert str(date.today().year) in result

    def test_is_langchain_tool(self):
        assert hasattr(get_time_context, "invoke")
        assert hasattr(get_time_context, "name")
