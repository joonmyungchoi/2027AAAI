# MCP mock — instance 이벤트와 정합하는 route/weather 캐시 응답 (GT의 travel 계산과 동일 소스)
from core import TRANSPORT


class MockMCP:
    """시각 t 기준 instance 상태를 반영한 결정론 응답. groundedness 채점의 정답 소스."""

    def __init__(self, inst):
        self.inst = inst

    def route(self, t):
        travel = TRANSPORT[self.inst.transport][0]
        for e in self.inst.events:
            if e.time <= t and e.kind in ("weather_rain", "weather_severe", "transit_delay", "cp_move"):
                travel += e.d_travel
        return {"dest": self.inst.dest, "duration_min": travel, "mode": self.inst.transport}

    def weather(self, t):
        cond = "맑음"
        for e in self.inst.events:
            if e.time <= t:
                if e.kind == "weather_rain":
                    cond = "비"
                elif e.kind == "weather_severe":
                    cond = "위험기상(호우경보)"
        return {"condition": cond}

    def snapshot(self, t):
        r, w = self.route(t), self.weather(t)
        return (f"maps.route(dest={r['dest']}): {r['duration_min']}분 ({r['mode']})\n"
                f"weather.now: {w['condition']}")
