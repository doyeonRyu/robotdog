'''
설명:
라즈베리 파이에서 웹 없이 실행 가능한 end-to-end GPT 테스트 파일
- 입력: 키보드 입력 또는 마이크 음성 입력
- 처리: STT(Whisper) → GPT → TTS
- 출력: 터미널에 채팅 표시, 라즈베리 파이 스피커로 음성 출력

필요 패키지:
1. 의존성 설치 
    sudo apt update
    sudo apt install -y portaudio19-dev alsa-utils mpg123
    pip install speechrecognition pyaudio openai
2. 마이크 / 스피커 확인
    arecord -l   # 마이크 장치 확인
    aplay -l     # 출력 장치 확인
3. 실행
    python3 gpt_local_test.py
'''


import os
import time
import subprocess
import speech_recognition as sr
from openai import OpenAI
from io import BytesIO
from dog import OPENAI_API_KEY  # keys.py에서 불러오기

# ------------------------------------------------------------------
# GPT/STT/TTS Helper
# ------------------------------------------------------------------
class OpenAiHelper:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def stt_whisper(self, audio, language="ko"):
        """speech_recognition.AudioData -> Whisper API 텍스트 변환"""
        try:
            wav_bytes = audio.get_wav_data()
            f = BytesIO(wav_bytes)
            f.name = "input.wav"
            resp = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                prompt="conversation with a robot"
            )
            return resp.text
        except Exception as e:
            print(f"[STT error] {e}")
            return None

    def chat(self, user_text: str, system_prompt="You are a helpful assistant."):
        """GPT 대화"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[GPT error] {e}")
            return None

    def tts(self, text: str, output_file="tts_reply.mp3", voice="alloy"):
        """TTS → mp3 파일 생성"""
        try:
            with self.client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3"
            ) as response:
                response.stream_to_file(output_file)
            return output_file
        except Exception as e:
            print(f"[TTS error] {e}")
            return None

# ------------------------------------------------------------------
# Main 실행
# ------------------------------------------------------------------
def main():
    helper = OpenAiHelper(api_key=OPENAI_API_KEY)
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("GPT Local Test 시작 (키보드 입력 or 음성 입력)")
    print(" - 'k' 입력: 키보드로 질문")
    print(" - 'v' 입력: 음성으로 질문 (마이크 녹음)")
    print(" - 'q' 입력: 종료")

    while True:
        mode = input("\n모드 선택 (k/v/q): ").strip().lower()
        if mode == "q":
            print("[종료]")
            break

        if mode == "k":
            # 키보드 입력
            user_input = input("User: ")
        elif mode == "v":
            # 마이크 녹음
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("말씀하세요... (최대 5초)")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            user_input = helper.stt_whisper(audio, language="ko")
            if not user_input:
                print("[STT 실패]")
                continue
            print(f"User(voice): {user_input}")
        else:
            print("잘못된 입력입니다. 다시 선택하세요.")
            continue

        # GPT 호출
        reply = helper.chat(user_input)
        if not reply:
            print("[GPT 응답 실패]")
            continue

        print(f"GPT: {reply}")

        # 음성 출력 (스피커로 재생)
        mp3_file = helper.tts(reply, output_file="tts_reply.mp3")
        if mp3_file:
            # mpg123 설치되어 있어야 함 (sudo apt install mpg123)
            subprocess.Popen(["mpg123", "-q", mp3_file])

if __name__ == "__main__":
    main()
