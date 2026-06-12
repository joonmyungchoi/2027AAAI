# trigger_bench 공통 상수·persona 정의·Instance/Event 스키마 (설계: gt_design_v1.1, personas_v1)
from dataclasses import dataclass, field, asdict

BAND = 7.5
GRID = 15
PREP = 10
B_EARLY, B_LATE = 30, 10
APPT_DEFAULT = 17 * 60  # 17:00 (절대 분)

# S2 이동 구성: (총 소요, 도보 구간, 대중교통 leg 존재)
TRANSPORT = {
    "근거리도보": (15, 15, False),
    "지하철": (30, 10, True),
    "KTX": (60, 10, True),
}

# 채널맵 (상황층): state -> 가용 채널
CHANNELS = {
    "default": {"visual": 1, "sound": 1, "vibe": 1},
    "통화": {"visual": 1, "sound": 0, "vibe": 1},
    "회의": {"visual": 1, "sound": 0, "vibe": 1},
    "운전": {"visual": 0, "sound": 1, "vibe": 1},
}

# persona: (빈번도 많은가, 정도 강한가, lead 미리인가)
PERSONAS = {
    "P_A": (False, False, True),
    "P_B": (False, True, False),
    "P_C": (True, False, False),
    "P_D": (True, True, True),
}
PERSONA_NAMES = {"P_A": "윤서", "P_B": "도현", "P_C": "하은", "P_D": "지훈"}


def buffer_of(pid: str) -> int:
    return B_EARLY if PERSONAS[pid][2] else B_LATE


def fmt(m: float) -> str:
    return f"{int(m) // 60:02d}:{int(m) % 60:02d}"


@dataclass
class Event:
    time: int            # 절대 분
    kind: str            # weather_rain/weather_severe/cp_delay/cp_cancel/cp_move/transit_delay/state
    d_appt: int = 0
    d_travel: int = 0
    forced: bool = False
    state: str = ""
    dur: int = 0

    def to_dict(self):
        return asdict(self)


@dataclass
class Instance:
    iid: str
    transport: str
    familiar: bool
    appt: int = APPT_DEFAULT
    has_appt: bool = True
    noop_kind: str = ""           # no-op 유형 (약속없음/오전완료/내일)
    events: list = field(default_factory=list)
    dest: str = "서울역"

    def to_dict(self):
        d = asdict(self)
        d["events"] = [e.to_dict() for e in self.events]
        return d

    @staticmethod
    def from_dict(d):
        ev = [Event(**e) for e in d.pop("events")]
        return Instance(events=ev, **d)
