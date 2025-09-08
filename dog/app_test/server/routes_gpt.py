from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from dog import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
from dog import OpenAiHelper   # OpenAiHelper가 있는 경로로 수정
import os, time

router = APIRouter()

# 헬퍼 싱글톤
helper = OpenAiHelper(
    api_key=OPENAI_API_KEY,
    assistant_id=OPENAI_ASSISTANT_ID,
    assistant_name="bot",
)

# 텍스트 채팅: 키보드 입력
class ChatReq(BaseModel):
    text: str
    speak: bool = True         # 응답 음성 생성 여부
    voice: str = "alloy"       # TTS 보이스
    lang: str = "ko"           # TTS/표시용 언어 힌트

@router.post("/api/chat")  # JSON {text, speak?, voice?, lang?}
async def chat_endpoint(req: ChatReq):
    reply = helper.dialogue(req.text) or ""
    audio_url = None

    if req.speak and reply:
        # 파일명 생성 및 TTS 출력
        ts = int(time.time() * 1000)
        out_dir = "static/tts"
        os.makedirs(out_dir, exist_ok=True)
        out_path = f"{out_dir}/reply_{ts}.mp3"

        ok = helper.text_to_speech(
            text=reply,
            output_file=out_path,
            voice=req.voice,
            response_format="mp3",
            speed=1.0,
        )
        if ok:
            audio_url = f"/static/tts/reply_{ts}.mp3"

    return {"reply": reply, "audio_url": audio_url}

# 음성 채팅: 브라우저에서 Blob 업로드 (multipart/form-data)
@router.post("/api/chat-voice")  # form-data: file=<audio>, lang=ko 등
async def chat_voice_endpoint(
    file: UploadFile = File(...),
    lang: str = Form("ko"),
    speak: bool = Form(True),
    voice: str = Form("alloy"),
):
    wav_bytes = await file.read()
    text = helper.stt_whisper_from_bytes(wav_bytes, language=lang) or ""
    if not text:
        return {"error": "stt_failed"}

    reply = helper.dialogue(text) or ""
    audio_url = None

    if speak and reply:
        ts = int(time.time() * 1000)
        out_dir = "static/tts"
        os.makedirs(out_dir, exist_ok=True)
        out_path = f"{out_dir}/reply_{ts}.mp3"
        ok = helper.text_to_speech(reply, out_path, voice=voice, response_format="mp3")
        if ok:
            audio_url = f"/static/tts/reply_{ts}.mp3"

    return {"text": text, "reply": reply, "audio_url": audio_url}
