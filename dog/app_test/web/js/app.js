// web/app.js
// server/app.py 예시


# app_test 폴더를 루트로 서빙
app.mount("/", StaticFiles(directory="app_test", html=True), name="static")

# 여기서 /api/* 라우터들 include_router(...) 해주세요

// 기본 설정
const BASE = "http://192.168.0.151:8000";
const JSONHDR = { "Content-Type": "application/json" };

// 공통 fetch 래퍼 (타임아웃+에러 로깅)
async function api(path, payload, opt = {}) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), opt.timeout || 8000);
  try {
    const res = await fetch(`${BASE}${path}`, {
      method: "POST",
      headers: JSONHDR,
      body: JSON.stringify(payload || {}),
      signal: controller.signal,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data?.error || res.statusText);
    return data;
  } finally {
    clearTimeout(id);
  }
}

// =============== 액션 버튼 ===============
export async function actionButtons(action) {
  try {
    const data = await api("/api/action", { action });
    console.log("[action ok]", data);
    // TODO: UI 상태바 업데이트
  } catch (e) {
    console.error("[action err]", e);
  }
}

// =============== 채팅 텍스트 전송 ===============
export async function handleChatSend(text) {
  const clean = (text || "").trim();
  if (!clean) return;

  appendBubble("user", clean);

  try {
    const data = await api("/api/chat", { text: clean }); // { reply, audio_url? }
    console.log("[chat ok]", data);

    appendBubble("bot", data.reply || "");

    if (data.audio_url) {
      const audio = new Audio(`${BASE}${data.audio_url.startsWith("/") ? "" : "/"}${data.audio_url}`);
      audio.play().catch(console.warn);
    }
  } catch (e) {
    console.error("[chat err]", e);
    appendBubble("bot", "⚠️ 채팅 처리 중 오류가 발생했습니다.");
  }
}

// =============== 조이스틱 (WS) ===============
let ws;
let jsLastSend = 0;

export function initJoystickWS() {
  ws = new WebSocket(`ws://${location.hostname}:8000/ws/control`);
  ws.onopen = () => console.log("[ws] open");
  ws.onclose = () => console.log("[ws] closed");
  ws.onerror = (e) => console.error("[ws] error", e);
}

export function handleJoystick(vx, vy, wz) {
  const now = performance.now();
  if (now - jsLastSend < 50) return;
  jsLastSend = now;

  const msg = JSON.stringify({ type: "twist", vx, vy, wz });

  if (ws && ws.readyState === 1) {
    ws.send(msg);
  } else {
    fetch(`${BASE}/api/joystick`, {
      method: "POST",
      headers: JSONHDR,
      body: JSON.stringify({ vx, vy, wz }),
    }).catch(() => {});
  }
}

// =============== 음성 명령 (길게 눌러 녹음) ===============
let mediaRecorder;
let chunks = [];
let recState = "idle"; // idle | recording
let voiceBtn;

// 브라우저에서 녹음 권한 요청 & MediaRecorder 준비
async function setupRecorder() {
  if (mediaRecorder) return;
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mime = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "audio/webm;codecs=opus";
  mediaRecorder = new MediaRecorder(stream, { mimeType: mime });

  mediaRecorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) chunks.push(e.data);
  };

  mediaRecorder.onstop = async () => {
    if (!chunks.length) {
      recState = "idle";
      setVoiceHint("🎤");
      return;
    }
    const blob = new Blob(chunks, { type: mediaRecorder.mimeType });
    chunks = [];
    recState = "idle";
    setVoiceHint("🎤");

    // 업로드 (multipart/form-data)
    try {
      const fd = new FormData();
      // 백엔드 /api/chat-voice 에서 file 필드로 받도록 구현되어 있어야 함
      const filename = `voice_${Date.now()}.${blob.type.includes("webm") ? "webm" : "ogg"}`;
      fd.append("file", blob, filename);
      fd.append("lang", "ko");    // 필요 시 변경
      fd.append("speak", "true"); // 서버에서 TTS 생성 여부
      fd.append("voice", "alloy");

      // UI에 임시로 "…(인식 중)" 말풍선
      appendBubble("user", "🎙️ (음성 인식 중...)");

      const res = await fetch(`${BASE}/api/chat-voice`, { method: "POST", body: fd });
      const data = await res.json();
      console.log("[voice chat ok]", data);

      // 인식된 텍스트를 유저 말풍선으로 교체/추가
      if (data.text) appendBubble("user", data.text);

      // GPT 답변
      if (data.reply) appendBubble("bot", data.reply);

      // 음성 재생
      if (data.audio_url) {
        const audio = new Audio(`${BASE}${data.audio_url.startsWith("/") ? "" : "/"}${data.audio_url}`);
        audio.play().catch(console.warn);
      }
    } catch (err) {
      console.error("[voice chat err]", err);
      appendBubble("bot", "⚠️ 음성 처리 중 오류가 발생했습니다.");
    }
  };
}

function startRecording() {
  if (!mediaRecorder || recState === "recording") return;
  chunks = [];
  mediaRecorder.start(100); // 100ms 단위로 dataavailable
  recState = "recording";
  setVoiceHint("● 녹음 중… 떼면 전송");
}

function stopRecording() {
  if (!mediaRecorder || recState !== "recording") return;
  mediaRecorder.stop();
}

// UI 헬퍼 (보이스 버튼 레이블)
function setVoiceHint(text) {
  if (voiceBtn) voiceBtn.textContent = text;
}

// =============== 카메라 ===============
export function mountCamera(imgEl) {
  imgEl.src = "http://192.168.0.151:9000/mjpg";
}

// =============== 말풍선 유틸 ===============
function appendBubble(role, text) {
  const box = document.getElementById("chat-box");
  if (!box) return;
  const div = document.createElement("div");
  div.className = "bubble " + (role === "user" ? "bubble-user" : "bubble-bot");
  div.textContent = text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

// =============== 초기화 ===============
window.addEventListener("DOMContentLoaded", async () => {
  initJoystickWS();

  const cam = document.getElementById("camera-view");
  if (cam) mountCamera(cam);

  // 액션 버튼
  document.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => actionButtons(btn.dataset.action));
  });

  // 채팅(텍스트) 전송
  const input = document.getElementById("chat-input");
  const send = document.getElementById("chat-send");
  if (send && input) {
    send.addEventListener("click", () => {
      const text = input.value;
      input.value = "";
      handleChatSend(text);
    });
    // Enter로 전송 (Shift+Enter는 줄바꿈)
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const text = input.value;
        input.value = "";
        handleChatSend(text);
      }
    });
  }

  // 보이스(길게 누르기: 마우스/터치 지원)
  voiceBtn = document.getElementById("chat-voice");
  if (voiceBtn) {
    try {
      await setupRecorder();
    } catch (e) {
      console.error("마이크 권한 필요:", e);
      setVoiceHint("🎤(권한 필요)");
    }

    // 마우스
    voiceBtn.addEventListener("mousedown", (e) => {
      e.preventDefault();
      startRecording();
    });
    voiceBtn.addEventListener("mouseup", (e) => {
      e.preventDefault();
      stopRecording();
    });
    voiceBtn.addEventListener("mouseleave", (e) => {
      if (recState === "recording") stopRecording();
    });

    // 터치
    voiceBtn.addEventListener("touchstart", (e) => {
      e.preventDefault();
      startRecording();
    }, { passive: false });
    voiceBtn.addEventListener("touchend", (e) => {
      e.preventDefault();
      stopRecording();
    }, { passive: false });

    setVoiceHint("🎤");
  }
});
