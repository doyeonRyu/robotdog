# 맨 위로 이동
from io import BytesIO
import json
from openai import OpenAI
import os
from dog import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
import shutil
import time

def chat_print(label, message):
    """
    챗 메세지 출력
    - <label>: 메세지 레이블
    - <message>: 출력할 메세지
    """
    width = shutil.get_terminal_size().columns # 
    msg_len = len(message)
    line_len = width - 27

    # --- normal print ---
    print(f'{time.time():.3f} {label:>6} >>> {message}')
    return

class OpenAiHelper():
    STT_OUT = "stt_output.wav"
    TTS_OUTPUT_FILE = 'tts_output.mp3'
    TIMEOUT = 30  # seconds

    def __init__(self, api_key, assistant_id, assistant_name, timeout=TIMEOUT) -> None:
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.assistant_name = assistant_name

        self.client = OpenAI(api_key=api_key, timeout=timeout)
        # 스레드 생성 (사용자 메시지 없이 run을 바로 돌릴 필요는 없음)
        self.thread = self.client.beta.threads.create()
        
    def stt_whisper_from_bytes(self, wav_bytes: bytes, language: str = "en", prompt: str | None = None):
        try:
            f = BytesIO(wav_bytes)
            f.name = getattr(self, "STT_OUT", "input.wav")  # 파일명 필요
            resp = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                prompt=prompt or "robot conversation context"
            )
            return resp.text
        except Exception as e:
            print(f"[STT] from bytes error: {e}")
        return False

    def stt_whisper_via_sdk(self, audio, language: str = "en", prompt: str | None = None):
        try:
            wav_bytes = audio.get_wav_data()
            wav_data = BytesIO(wav_bytes)
            wav_data.name = getattr(self, "STT_OUT", "input.wav")

            resp = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=wav_data,
                language=language,
                prompt=prompt or "robot conversation context"
            )
            return resp.text
        except Exception as e:
            print(f"[STT] Whisper SDK error: {e}")
            return False

    def _latest_assistant_text(self):
        """가장 최근 assistant 메시지 텍스트를 반환"""
        msgs = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        # SDK는 보통 최신이 앞에 옵니다. assistant만 필터 후 첫 번째 사용
        for m in msgs.data:
            if m.role == "assistant":
                for block in m.content:
                    if getattr(block, "type", "") == "text":
                        return block.text.value
        return None
    
    def dialogue(self, msg: str):
        chat_print("user", msg)
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id, role="user", content=msg
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id, assistant_id=self.assistant_id,
        )
        if run.status != "completed":
            print(f"[assistant run] {run.status}")
            return None

        value = self._latest_assistant_text()
        if value is None:
            return None

        chat_print(self.assistant_name, value)

        # 안전하게 JSON 시도 → 실패 시 원문 문자열 반환
        try:
            return json.loads(value)
        except Exception:
            return value

    def dialogue_with_img(self, msg: str, img_path: str):
        chat_print("user", msg)

        img_file = self.client.files.create(
            file=open(img_path, "rb"), purpose="vision"
        )
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=[
                {"type": "text", "text": msg},
                {"type": "image_file", "image_file": {"file_id": img_file.id}},
            ],
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id, assistant_id=self.assistant_id,
        )
        if run.status != "completed":
            print(f"[assistant run] {run.status}")
            return None

        value = self._latest_assistant_text()
        if value is None:
            return None

        chat_print(self.assistant_name, value)
        try:
            return json.loads(value)
        except Exception:
            return value

    def text_to_speech(self, text, output_file, voice='alloy', response_format="mp3", speed=1):
        '''
        voice: alloy, echo, fable, onyx, nova, shimmer
        '''
        try:
            dirpath = os.path.dirname(output_file)
            # 디렉터리 지정이 없으면 생성 스킵
            if dirpath:
                os.makedirs(dirpath, exist_ok=True)

            with self.client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format=response_format,
                speed=speed,
            ) as response:
                response.stream_to_file(output_file)

            return True
        except Exception as e:
            print(f"tts err: {e}")
            return False
