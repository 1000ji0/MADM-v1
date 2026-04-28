"""공통 BaseAgent - 모델 초기화 및 기본 유틸"""
import os
import json
import re
import warnings
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
warnings.filterwarnings("ignore", category=FutureWarning)


def get_model(api_key: str) -> genai.GenerativeModel:
    """환경 변수 MODEL_NAME 우선, 없으면 gemini-pro 사용"""
    model_name = os.getenv("MODEL_NAME", "gemini-pro")
    genai.configure(api_key=api_key)
    # 시도 순서
    candidates: List[str] = [model_name, "gemini-pro", "gemini-1.5-pro-latest", "gemini-1.5-flash-latest"]
    tried = set()
    for name in candidates:
        if name in tried:
            continue
        tried.add(name)
        try:
            model = genai.GenerativeModel(name)
            print(f"[MODEL] '{name}' 사용")
            return model
        except Exception as e:
            print(f"[MODEL] '{name}' 실패: {str(e)[:80]}")
            continue
    raise RuntimeError("사용 가능한 Gemini 모델을 찾을 수 없습니다. MODEL_NAME과 키를 확인하세요.")


class BaseAgent:
    """모든 에이전트의 기본 클래스"""

    def __init__(self, agent_id: str, agent_name: str, system_prompt: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY가 .env에 설정되어야 합니다.")
        self.model = get_model(api_key)
        # agent_prompt.md에서 해당 agent_id 섹션이 있으면 시스템 프롬프트 앞에 삽입
        try:
            prompt_md = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'agent_prompt.md')
            if os.path.exists(prompt_md):
                with open(prompt_md, 'r', encoding='utf-8') as f:
                    md = f.read()
                # 섹션 분리: '## '로 분리한 뒤 각 섹션의 첫 줄에서 ID 추출
                sections = {}
                parts = md.split('\n## ')
                for p in parts:
                    if not p.strip():
                        continue
                    first_line, *rest = p.splitlines()
                    # 첫 줄에서 ID 추출 (예: "A101: Menu Planner & Mediator...")
                    header = first_line.strip()
                    header_id = header.split(':', 1)[0].strip()
                    content = header + '\n' + '\n'.join(rest)
                    sections[header_id] = '## ' + content
                if self.agent_id in sections:
                    # agent-specific guidance를 시스템 프롬프트 앞에 추가
                    self.system_prompt = sections[self.agent_id].strip() + "\n\n" + self.system_prompt
        except Exception:
            # 실패해도 진행
            pass

        # 기본 응답 길이 제한: 환경변수로 오버라이드 가능
        try:
            resp_max = os.getenv('RESPONSE_MAX_CHARS')
            self.response_max_chars = int(resp_max) if resp_max is not None else 500
        except Exception:
            self.response_max_chars = 500

        try:
            resp_total = os.getenv('RESPONSE_TOTAL_MAX_CHARS')
            self.response_total_max_chars = int(resp_total) if resp_total is not None else 550
        except Exception:
            self.response_total_max_chars = 550

        # 마지막 응답 시간(초)
        self.last_response_time: Optional[float] = None
        self.stm: List[Dict[str, str]] = []
        self.ltm: Dict[str, Any] = {}

    def load_ltm(self, user_profile: Dict[str, Any]):
        self.ltm.update(user_profile)

    def add_to_stm(self, role: str, content: str):
        self.stm.append({"role": role, "content": content})

    def get_last_response_time(self) -> Optional[float]:
        return self.last_response_time

    def _format_context(self, context: Dict[str, Any]) -> str:
        return json.dumps(context, ensure_ascii=False, indent=2)

    def _build_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        parts = [self.system_prompt]
        if self.ltm:
            parts.append(f"[사용자 프로필]\n{self._format_context(self.ltm)}")
        if context:
            parts.append(f"[컨텍스트]\n{self._format_context(context)}")
        if self.stm:
            recent = "\n".join(f"{m['role']}: {m['content']}" for m in self.stm[-5:])
            parts.append(f"[최근 대화]\n{recent}")
        parts.append(f"[현재 요청]\n{user_input}")
        # 응답 지시 문구가 없으면 간결한 한국어, 길이 제한 지시 추가
        joined = "\n\n".join(parts)
        if '응답' not in joined:
            joined += "\n\n응답 지시: 한국어로 간결하게 답변하세요. 출력은 최대 {n}자 이내로 제한하세요.".replace('{n}', str(self.response_max_chars))
        return joined

    def generate_response(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        prompt = self._build_prompt(user_input, context)
        self.add_to_stm("user", user_input)
        import time
        try:
            start = time.time()
            resp = self.model.generate_content(prompt)
            elapsed = time.time() - start
            self.last_response_time = elapsed
            text = resp.text
            # 응답 길이 후처리: 기본 300자 지침, 전체 출력 캡 350자(기본)
            try:
                # 1) 우선 모델 지시용 내부 제한(지침)으로 response_max_chars 유지
                if self.response_max_chars and len(text) > self.response_max_chars:
                    # 문장 경계에서 자르기
                    cut = re.search(r'(?s).{0,%d}\b[\.!?]?'.replace('{0,%d}', '{0,' + str(self.response_max_chars) + '}'), text)
                    if cut and cut.group(0).strip():
                        text = cut.group(0).rstrip()
                    else:
                        text = text[: self.response_max_chars].rstrip()

                # 2) 전체 출력 총 캡을 넘는다면, JSON 구조 보존 시도
                total_cap = getattr(self, 'response_total_max_chars', None)
                if total_cap and len(text) > total_cap:
                    # JSON 형태인지 확인
                    parsed = None
                    try:
                        parsed = json.loads(text)
                    except Exception:
                        parsed = None

                    if isinstance(parsed, dict):
                        # 줄이기 우선순위 필드
                        priority_keys = ["instructions", "steps", "recipe", "조리법", "방법", "description", "notes"]
                        for key in priority_keys:
                            if key in parsed and isinstance(parsed[key], str) and len(parsed[key]) > 20:
                                # 문장 경계에서 자르기
                                cutoff = parsed[key][:total_cap]
                                m = re.search(r'(?s).{0,%d}\b[\.!?]?'.replace('{0,%d}', '{0,' + str(max(50, int(total_cap/2))) + '}'), cutoff)
                                if m and m.group(0).strip():
                                    parsed[key] = m.group(0).rstrip() + "..."
                                else:
                                    parsed[key] = cutoff.rstrip() + "..."
                                # 재생성해서 길이 체크
                                text = json.dumps(parsed, ensure_ascii=False)
                                if len(text) <= total_cap:
                                    break
                        # 마지막 수단: 필수 아닌 키 제거
                        if len(text) > total_cap:
                            for k in list(parsed.keys()):
                                if k not in ("ingredients", "instructions", "cost_breakdown"):
                                    parsed.pop(k, None)
                                    text = json.dumps(parsed, ensure_ascii=False)
                                    if len(text) <= total_cap:
                                        break
                    else:
                        # JSON이 아니면 문장 경계에서 안전하게 잘라냄
                        m = re.search(r'(?s).{0,%d}\b[\.!?]?'.replace('{0,%d}', '{0,' + str(total_cap) + '}'), text)
                        if m and m.group(0).strip():
                            text = m.group(0).rstrip() + "..."
                        else:
                            text = text[:total_cap].rstrip() + "..."
            except Exception:
                pass
            self.add_to_stm("assistant", text)
            return text
        except Exception as e:
            return f"오류 발생: {str(e)}"

