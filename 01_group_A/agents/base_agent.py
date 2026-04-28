"""기본 에이전트 클래스"""
import os
import warnings
# FutureWarning 억제 (deprecated 패키지 경고)
warnings.filterwarnings('ignore', category=FutureWarning)
import google.generativeai as genai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def get_available_model(api_key: str, preferred_model: str = None):
    """사용 가능한 모델을 찾아 반환"""
    genai.configure(api_key=api_key)
    # 실제 사용 가능한 모델 목록 확인 (안전하게 접근)
    available_models = []
    try:
        models = genai.list_models()
        for m in models:
            # 안전하게 속성 가져오기
            name = getattr(m, 'name', None)
            methods = getattr(m, 'supported_generation_methods', None) or getattr(m, 'supported_methods', None)
            if not name:
                continue
            model_name_clean = name.replace('models/', '')
            # methods가 있는 경우 몇몇 대표 메서드명을 허용
            if methods:
                method_names = []
                for mm in methods:
                    if isinstance(mm, str):
                        method_names.append(mm)
                    else:
                        method_names.append(getattr(mm, 'name', str(mm)))
                allowed = ('generateContent', 'generate', 'chat', 'generateText', 'generate_text')
                if any(x in method_names for x in allowed):
                    available_models.append(model_name_clean)
            else:
                # 메서드 정보가 없으면 목록에 추가(폴백으로 사용)
                available_models.append(model_name_clean)

        if available_models:
            print(f"사용 가능한 모델 목록: {', '.join(available_models[:10])}")
    except Exception as e:
        print(f"모델 목록 조회 실패: {str(e)[:200]}")
        available_models = []
    
    # 환경 변수에서 모델 이름 가져오기 (우선순위: 환경 변수 > preferred_model > 기본값)
    # 우선순위: 환경변수 MODEL_NAME > 함수 인자 preferred_model > API로 조회된 목록 > 폴백
    env_model = os.getenv('MODEL_NAME')
    preferred_model_name = env_model or preferred_model

    model_names_to_try = []
    # 환경변수나 전달된 선호 모델을 우선 시도
    if preferred_model_name:
        model_names_to_try.append(preferred_model_name)
    # API로 조회된 모델을 그 다음에 시도 (중복 제외)
    for am in available_models:
        if am not in model_names_to_try:
            model_names_to_try.append(am)

    # 최신/권장 폴백 모델들
    fallback_models = [
        'gemini-2.0-flash-lite',
        'gemini-2.0-flash-lite-001',
        'gemini-2.5-pro',
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-pro',
    ]

    for fallback in fallback_models:
        if fallback not in model_names_to_try:
            model_names_to_try.append(fallback)
    
    # 모델 시도
    for model_name in model_names_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            print(f"모델 '{model_name}' 초기화 성공")
            return model, model_name
        except Exception as e:
            print(f"모델 '{model_name}' 시도 실패: {str(e)[:200]}")
            continue
    
    raise ValueError("사용 가능한 모델을 찾을 수 없습니다. API 키와 모델 접근 권한을 확인하세요.")

class BaseAgent:
    """모든 에이전트의 기본 클래스"""
    
    def __init__(self, agent_id: str, agent_name: str, system_prompt: str):
        """
        Args:
            agent_id: 에이전트 ID (예: A001)
            agent_name: 에이전트 이름
            system_prompt: 시스템 프롬프트
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        
        # Google Gemini API 설정
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        # 사용 가능한 모델 찾기
        try:
            model_res = get_available_model(api_key)
            # get_available_model은 (model, model_name)을 반환하도록 변경됨
            if isinstance(model_res, tuple):
                self.model, self.model_name = model_res
            else:
                self.model = model_res
                self.model_name = getattr(self.model, 'name', None)
            print(f"[{self.agent_id}] 모델 초기화 완료: {getattr(self, 'model_name', None)}")
        except Exception as e:
            raise ValueError(f"모델 초기화 실패: {str(e)}. API 키와 모델 접근 권한을 확인하세요.")
        
        # 응답 생성 기본 파라미터: 환경변수로 오버라이드 가능
        # MODEL_TEMPERATURE: 0.0~1.0 (기본 0.0 -> 결정적, 간결한 응답)
        # MODEL_MAX_OUTPUT_TOKENS: 출력 토큰 제한 (기본 512)
        try:
            temp_env = os.getenv('MODEL_TEMPERATURE')
            max_tok_env = os.getenv('MODEL_MAX_OUTPUT_TOKENS')
            self.generation_kwargs = {}
            if temp_env is not None:
                self.generation_kwargs['temperature'] = float(temp_env)
            else:
                self.generation_kwargs['temperature'] = 0.0
            if max_tok_env is not None:
                self.generation_kwargs['max_output_tokens'] = int(max_tok_env)
            else:
                self.generation_kwargs['max_output_tokens'] = 512
            # 응답 문자수 제한: 기본 200~250자 (환경변수로 오버라이드 가능)
            resp_min_env = os.getenv('RESPONSE_MIN_CHARS')
            resp_max_env = os.getenv('RESPONSE_MAX_CHARS')
            try:
                self.response_min_chars = int(resp_min_env) if resp_min_env is not None else 200
            except Exception:
                self.response_min_chars = 200
            try:
                self.response_max_chars = int(resp_max_env) if resp_max_env is not None else 250
            except Exception:
                self.response_max_chars = 250
        except Exception:
            # 환경변수 파싱 실패시 안전한 기본값
            self.generation_kwargs = {'temperature': 0.0, 'max_output_tokens': 512}
            self.response_min_chars = 200
            self.response_max_chars = 250
        # 메모리 (STM: 세션 대화, LTM: 사용자 프로필)
        self.stm = []  # Short-term memory
        self.ltm = {}  # Long-term memory (사용자 프로필 등)
        # 마지막 응답 시간 (초)
        self.last_response_time = None
    
    def add_to_stm(self, role: str, content: str):
        """STM에 대화 추가"""
        self.stm.append({'role': role, 'content': content})

    def get_last_response_time(self) -> Optional[float]:
        """마지막 응답에 소요된 시간(초)을 반환합니다. 측정값이 없으면 None 반환."""
        return getattr(self, 'last_response_time', None)
    
    def load_ltm(self, user_profile: Dict[str, Any]):
        """LTM에 사용자 프로필 로드"""
        self.ltm.update(user_profile)
    
    def generate_response(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        사용자 입력에 대한 응답 생성
        
        Args:
            user_input: 사용자 입력
            context: 추가 컨텍스트 정보
        
        Returns:
            에이전트의 응답
        """
        # 프롬프트 구성
        prompt = self._build_prompt(user_input, context)
        
        # STM에 추가
        self.add_to_stm('user', user_input)
        
        import time
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                # Gemini API 호출
                # 응답 시간 측정 시작
                start_time = time.time()
                response = self.model.generate_content(prompt)
                result = response.text
                # 응답 시간 측정 종료
                elapsed = time.time() - start_time
                # 마지막 응답 시간(초)을 속성으로 저장
                self.last_response_time = elapsed
                print(f"[{self.agent_id}] 응답시간: {elapsed:.2f}s")

                # 응답 길이 후처리 (환경변수 또는 기본 200~250자)
                maxc = getattr(self, 'response_max_chars', None)
                minc = getattr(self, 'response_min_chars', None)
                if maxc and len(result) > maxc:
                    result = result[:maxc].rstrip()
                    print(f"[{self.agent_id}] 응답이 {maxc}자로 잘려 저장됩니다.")
                elif minc and len(result) < minc:
                    print(f"[{self.agent_id}] 응답 길이가 최소 제한({minc})보다 짧습니다 ({len(result)}자).")

                # STM에 추가
                self.add_to_stm('assistant', result)

                return result
            except Exception as e:
                error_str = str(e)
                # 429 에러 (할당량 초과)인 경우 재시도
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(f"할당량 초과로 인한 재시도... ({attempt + 1}/{max_retries}) {wait_time}초 대기")
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"오류 발생: 할당량이 초과되었습니다. 잠시 후 다시 시도해주세요.\n{error_str}"
                else:
                    return f"오류 발생: {error_str}"
        
        return "오류 발생: 최대 재시도 횟수 초과"
    
    def _build_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """프롬프트 구성"""
        prompt_parts = [self.system_prompt]
        
        # LTM 정보 추가
        if self.ltm:
            prompt_parts.append(f"\n[사용자 프로필 정보]\n{self._format_ltm()}")
        
        # 컨텍스트 추가
        if context:
            prompt_parts.append(f"\n[추가 컨텍스트]\n{self._format_context(context)}")
        
        # STM (최근 대화) 추가
        if self.stm:
            recent_stm = self.stm[-5:]  # 최근 5개만
            prompt_parts.append(f"\n[최근 대화]\n{self._format_stm(recent_stm)}")
        
        # 사용자 입력 추가
        prompt_parts.append(f"\n[현재 요청]\n{user_input}")
        
        return "\n".join(prompt_parts)
    
    def _format_ltm(self) -> str:
        """LTM 포맷팅"""
        import json
        return json.dumps(self.ltm, ensure_ascii=False, indent=2)
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """컨텍스트 포맷팅"""
        import json
        return json.dumps(context, ensure_ascii=False, indent=2)
    
    def _format_stm(self, stm: list) -> str:
        """STM 포맷팅"""
        formatted = []
        for item in stm:
            formatted.append(f"{item['role']}: {item['content']}")
        return "\n".join(formatted)
    
    def clear_stm(self):
        """STM 초기화"""
        self.stm = []

