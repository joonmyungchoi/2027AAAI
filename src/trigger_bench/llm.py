# OpenAI 공용 클라이언트 — .env에서 키 로드(비노출), 재시도·파라미터 호환 처리
import json
import os
import time
from pathlib import Path

AGENT_MODEL = os.environ.get("TB_AGENT_MODEL", "gpt-5.5")
JUDGE_MODEL = os.environ.get("TB_JUDGE_MODEL", "gpt-5.5-pro")
RENDER_MODEL = os.environ.get("TB_RENDER_MODEL", "gpt-5.5")
PROBE_WEAK_MODEL = os.environ.get("TB_PROBE_WEAK", "gpt-5-mini")


def _load_key():
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    # repo 루트의 .env 탐색 (이 파일 기준 2단계 위)
    for p in [Path(__file__).resolve().parents[2] / ".env", Path.cwd() / ".env"]:
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip()
    raise RuntimeError(".env에서 OPENAI_API_KEY를 찾지 못함")


_client = None


def client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=_load_key())
    return _client


_RESPONSES_ONLY = set()  # chat completions 미지원 모델 캐시 (예: gpt-5.5-pro)


def _responses_call(model, system, user):
    """Responses API 경로 (gpt-5.5-pro 등 chat completions 미지원 모델용)."""
    r = client().responses.create(model=model, instructions=system, input=user)
    return r.output_text


def chat(model, system, user, json_mode=True, retries=3):
    """단일 호출. 미지원 파라미터 자동 제거, chat 미지원 모델은 Responses API로 폴백."""
    if model in _RESPONSES_ONLY:
        return _responses_call(model, system, user)
    kwargs = dict(model=model,
                  messages=[{"role": "system", "content": system},
                            {"role": "user", "content": user}],
                  temperature=0)
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    last = None
    for i in range(retries):
        try:
            r = client().chat.completions.create(**kwargs)
            return r.choices[0].message.content
        except Exception as e:
            msg = str(e)
            if "not a chat model" in msg:
                _RESPONSES_ONLY.add(model)
                return _responses_call(model, system, user)
            if "temperature" in msg and "temperature" in kwargs:
                kwargs.pop("temperature")
                continue
            if "response_format" in msg and "response_format" in kwargs:
                kwargs.pop("response_format")
                continue
            last = e
            time.sleep(2 ** i)
    raise last


def chat_json(model, system, user, retries=3):
    txt = chat(model, system, user, json_mode=True, retries=retries)
    try:
        return json.loads(txt[txt.find("{"):txt.rfind("}") + 1])
    except Exception:
        return {"_parse_error": txt[:300]}
