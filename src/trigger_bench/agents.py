# 평가용 agent — OracleRule(채점기 검증), AllSilent/AllFire/Random(게이밍 기준선), LLM 클라이언트 골격
import json
import random

from gt import synth


class OracleRuleAgent:
    """GT 합성기를 그대로 따르는 agent — 채점기 무결성 검증용 (만점이어야 함). 실평가 대상 아님."""

    def __init__(self, inst, pid):
        self.seq = {d.time: d for d in synth(inst, pid)}

    def decide(self, obs):
        d = self.seq.get(obs["time"])
        if d is None or d.decision == "silent":
            return {"decision": "silent"}
        return {"decision": "fire", "modality": d.modality, "content": d.content}


class AllSilentAgent:
    def decide(self, obs):
        return {"decision": "silent"}


class AllFireAgent:
    def decide(self, obs):
        return {"decision": "fire", "modality": ["popup"], "content": ["약속명/시각"]}


class RandomAgent:
    def __init__(self, seed=0):
        self.rng = random.Random(seed)

    def decide(self, obs):
        if self.rng.random() < 0.3:
            return {"decision": "fire", "modality": ["popup"], "content": ["약속명/시각"]}
        return {"decision": "silent"}


SYSTEM_PROMPT = """당신은 사용자의 모바일 proactive 어시스턴트다. 매 trigger마다 지금 알림을 보낼지(fire) 침묵할지(silent) 결정한다.
사용자 행동 로그에서 알림 선호(빈도·풍부도·리드타임)를 추론해 반영하라.
반드시 JSON만 출력: {"decision":"fire|silent","modality":["popup|vibrate|voice"],"content":["요소"],"rationale":{"travel_source":"maps|history","buffer_basis":"history|preference"}}
silent이면 {"decision":"silent","rationale":{...}}만."""


class LLMAgent:
    """OpenAI API agent — llm.py 공용 클라이언트 사용 (.env 키, 비노출)."""

    def __init__(self, model=None):
        from llm import AGENT_MODEL
        self.model = model or AGENT_MODEL

    def decide(self, obs):
        from env import render_obs
        from llm import chat_json
        out = chat_json(self.model, SYSTEM_PROMPT, render_obs(obs))
        if out.get("decision") not in ("fire", "silent"):
            return {"decision": "silent", "parse_error": str(out)[:200]}
        return out
