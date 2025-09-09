// web/app.js

// 같은 8000 포트에서 서빙 + API 호출이면 BASE 비워도 됨
// (IP를 고정해서 쓰고 싶으면 기존처럼 const BASE = "http://192.168.0.151:8000"; 사용)
const BASE = "";//"http://192.168.0.151:8000";
const JSONHDR = { "Content-Type": "application/json" };

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
  // 같은 호스트/포트 기준
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/control`);
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
let recState = "idle";
let voiceBtn;

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

    try {
      const fd = new FormData();
      const filename = `voice_${Date.now()}.${blob.type.includes("webm") ? "webm" : "ogg"}`;
      fd.append("file", blob, filename);
      fd.append("lang", "ko");
      fd.append("speak", "true");
      fd.append("voice", "alloy");

      appendBubble("user", "🎙️ (음성 인식 중...)");

      const res = await fetch(`${BASE}/api/chat-voice`, { method: "POST", body: fd });
      const data = await res.json();
      console.log("[voice chat ok]", data);

      if (data.text) appendBubble("user", data.text);
      if (data.reply) appendBubble("bot", data.reply);

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
  mediaRecorder.start(100);
  recState = "recording";
  setVoiceHint("● 녹음 중… 떼면 전송");
}

function stopRecording() {
  if (!mediaRecorder || recState !== "recording") return;
  mediaRecorder.stop();
}

function setVoiceHint(text) {
  if (voiceBtn) voiceBtn.textContent = text;
}


// =============== 카메라 ===============
export function mountCamera(imgEl) {
  // ✅ 프록시 경로 사용 (server/app.py에 /camera 라우트 구현되어 있어야 함)
  imgEl.src = "/camera";

  // 직접 접근을 쓰려면 아래를 사용(프록시 제거 가능)
  // imgEl.src = `http://${location.hostname}:9000/?action=stream`;
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

  document.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => actionButtons(btn.dataset.action));
  });

  const input = document.getElementById("chat-input");
  const send = document.getElementById("chat-send");
  if (send && input) {
    send.addEventListener("click", () => {
      const text = input.value;
      input.value = "";
      handleChatSend(text);
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const text = input.value;
        input.value = "";
        handleChatSend(text);
      }
    });
  }

  voiceBtn = document.getElementById("chat-voice");
  if (voiceBtn) {
    try {
      await setupRecorder();
    } catch (e) {
      console.error("마이크 권한 필요:", e);
      setVoiceHint("🎤(권한 필요)");
    }
    voiceBtn.addEventListener("mousedown", (e) => { e.preventDefault(); startRecording(); });
    voiceBtn.addEventListener("mouseup",   (e) => { e.preventDefault(); stopRecording(); });
    voiceBtn.addEventListener("mouseleave",(e) => { if (recState === "recording") stopRecording(); });
    voiceBtn.addEventListener("touchstart",(e) => { e.preventDefault(); startRecording(); }, { passive: false });
    voiceBtn.addEventListener("touchend",  (e) => { e.preventDefault(); stopRecording(); }, { passive: false });
    setVoiceHint("🎤");
  }
});
