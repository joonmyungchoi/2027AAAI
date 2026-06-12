# persona 행동 로그 생성기 — 정형 event_type, 축별 신호 패턴 + noise 25% (설계: personas_v1 §2)
import random
from datetime import datetime, timedelta

from core import PERSONAS, PERSONA_NAMES

FAMILIAR_POOL = ["서울역", "강남역 카페", "회사(판교)", "헬스장(역삼)"]  # 익숙 목적지 풀 (방문 N회)
HOME = "자택(서대문)"

NOISE_EVENTS = [
    ("youtube", "video_play", "{}"),
    ("messenger", "msg_recv", "{}"),
    ("shopping", "app_open", "{}"),
    ("game", "app_open", "{}"),
    ("news", "article_read", "{}"),
]


def _ts(day, h, m):
    return (datetime(2026, 5, 4) + timedelta(days=day, hours=h, minutes=m)).strftime("%Y-%m-%dT%H:%M")


def generate(pid, weeks=4, noise_ratio=0.25, seed=7):
    """persona 1명의 clean/noise 로그 생성. entry = dict(time, app, location, event_type, params, label, category)"""
    freq_high, depth_high, lead_early = PERSONAS[pid]
    rng = random.Random(seed + hash(pid) % 1000)
    clean = []

    for day in range(weeks * 7):
        # lead 신호: 약속 도착 패턴 (주 2~3회 약속 가정)
        if day % 3 == 0:
            dest = rng.choice(FAMILIAR_POOL)
            appt_h = rng.choice([14, 17, 19])
            early = rng.randint(40, 60) if lead_early else rng.randint(0, 10)
            clean.append(dict(time=_ts(day, appt_h, -early), app="calendar_geo", location=dest,
                              event_type="event_arrive", params=f"early_min={early}",
                              label="signal", category="lead"))
            if lead_early:
                clean.append(dict(time=_ts(day, 8, rng.randint(0, 50)), app="calendar", location=HOME,
                                  event_type="app_open", params="morning_check",
                                  label="signal", category="lead"))
            else:
                clean.append(dict(time=_ts(day, appt_h, -(early + 5)), app="maps", location=HOME,
                                  event_type="route_search", params=f"dest={dest};depth=basic",
                                  label="signal", category="lead"))

        # 빈번도 신호: 업데이트성 알림 반응
        if day % 2 == 0:
            if freq_high:
                clean.append(dict(time=_ts(day, 12, rng.randint(0, 59)), app="weather", location=HOME,
                                  event_type="notif_tap", params="kind=update;dwell_s=12",
                                  label="signal", category="frequency"))
                clean.append(dict(time=_ts(day, 18, rng.randint(0, 59)), app="system", location=HOME,
                                  event_type="notif_center_open", params="",
                                  label="signal", category="frequency"))
            else:
                clean.append(dict(time=_ts(day, 12, rng.randint(0, 59)), app="weather", location=HOME,
                                  event_type="notif_dismiss", params="kind=update;dwell_s=2",
                                  label="signal", category="frequency"))
                if day % 4 == 0:
                    clean.append(dict(time=_ts(day, 21, 0), app="system", location=HOME,
                                      event_type="dnd_on", params="until=07:00",
                                      label="signal", category="frequency"))

        # 정도 신호: modality 설정·조회 깊이
        if day % 3 == 1:
            if depth_high:
                clean.append(dict(time=_ts(day, 9, 0), app="weather", location=HOME,
                                  event_type="app_open", params="forecast_view",
                                  label="signal", category="depth"))
                clean.append(dict(time=_ts(day, 10, 0), app="maps", location=HOME,
                                  event_type="route_search", params="dest=신규장소;depth=exit+alt_route",
                                  label="signal", category="depth"))
                if day % 6 == 1:
                    clean.append(dict(time=_ts(day, 10, 5), app="system", location=HOME,
                                      event_type="ringer_mode", params="mode=sound+vibrate",
                                      label="signal", category="depth"))
            else:
                if day % 6 == 1:
                    clean.append(dict(time=_ts(day, 10, 0), app="system", location=HOME,
                                      event_type="ringer_mode", params="mode=silent",
                                      label="signal", category="depth"))

        # 익숙도: 익숙 풀 방문 (위 lead 항목과 별개의 일상 방문)
        if day % 4 == 2:
            clean.append(dict(time=_ts(day, 19, 0), app="geo", location=rng.choice(FAMILIAR_POOL),
                              event_type="place_visit", params="",
                              label="signal", category="familiarity"))

    clean.sort(key=lambda e: e["time"])
    n_noise = int(len(clean) * noise_ratio / (1 - noise_ratio))
    noisy = list(clean)
    for _ in range(n_noise):
        app, et, params = rng.choice(NOISE_EVENTS)
        noisy.append(dict(time=_ts(rng.randint(0, weeks * 7 - 1), rng.randint(8, 23), rng.randint(0, 59)),
                          app=app, location=HOME, event_type=et, params=params,
                          label="noise", category="noise"))
    noisy.sort(key=lambda e: e["time"])
    return clean, noisy


def linearize(entries):
    """agent 노출용 — 숨김 메타(label/category) 제외 (KnowU 방식 차용)."""
    return "\n".join(f"[{e['time']}] ({e['location']}) {e['app']}.{e['event_type']}"
                     + (f" {e['params']}" if e["params"] else "") for e in entries)
