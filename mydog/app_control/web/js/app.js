// 소켓 연결.인증, 이벤트 송수신, 디자인 미리보기 모드 지원
(() => {
  const search = new URLSearchParams(location.search);
  // 임시 서버(예: :3000)나 로컬호스트에서 열면 자동 디자인 모드
  const designMode =
    search.get('design') === '1' ||
    location.hostname === 'localhost' ||
    location.hostname === '127.0.0.1' ||
    (location.port && location.port !== '8000');

  const tokenEl = document.getElementById('token');
  const connectBtn = document.getElementById('connectBtn');
  const streamEl = document.getElementById('stream');
  const distEl = document.getElementById('dist');
  const faceToggle = document.getElementById('faceToggle');
  const chatLog = document.getElementById('chatLog');
  const chatText = document.getElementById('chatText');
  const sendBtn = document.getElementById('sendBtn');
  const voiceToggle = document.getElementById('voiceToggle');
  let generating = false;

  let socket = null;
  let authed = false;
  let loaderEl = null; // 로딩 말풍선 DOM

  if (designMode) {
    // 디자인 미리보기: 서버/소켓 없이도 UI를 확인할 수 있게 더미 소켓 주입
    socket = {
      emit: (event, payload) => {
        console.log(`[DESIGN EMIT] ${event}`, payload);
      },
      on: (event, handler) => {
        // state 이벤트만 간단히 모킹
        if (event === 'state') {
          // 주기적으로 더미 거리값 전송
          setInterval(() => handler({ distance: (30 + Math.random()*20).toFixed(1) }), 500);
        }
        if (event === 'auth_result') {
          // 연결 버튼을 누르면 성공 알림 발생시키기 위해 저장
          socket.__authHandler = handler;
        }
      },
      __authHandler: null
    };

    // 더미 영상(로컬 이미지, 사이즈: 800 x 600)
    streamEl.width = 800;
    streamEl.height = 600;
    streamEl.src = 'assets/placeholder.jpg';

    connectBtn.onclick = () => {
      authed = true;
      if (socket.__authHandler) socket.__authHandler({ ok: true });
      alert('디자인 모드 연결됨(더미)');
    };
  } else {
    // 실제 서버와 연결
    const ioSock = io();
    socket = ioSock;

    // 영상 스트림 주소 구성(같은 호스트 가정)
    const mjpegHost = `${location.protocol}//${location.hostname}:9000`;
    streamEl.src = `${mjpegHost}/mjpg`;

    connectBtn.onclick = () => {
      socket.emit('auth', { token: tokenEl.value || '000000' });
    };

    socket.on('auth_result', ({ok, msg}) => {
      authed = ok;
      alert(ok ? '연결됨' : `연결 실패: ${msg||''}`);
    });

    // 상태 수신
    socket.on('state', (payload) => {
      if (payload.distance != null) distEl.textContent = payload.distance;
    });

    // --- Chat events from server ---
    socket.on('chat_status', ({state}) => {
      if (state === 'thinking') {
        generating = true;
        sendBtn.disabled = true;
        appendBubble('sys', '답변 생성 중', true);
      } else if (state === 'speaking') {
        appendBubble('sys', '로봇이 말하는 중');
      }
    });
    socket.on('chat_stream', ({delta}) => {
      appendBubble('assistant', delta, false, true); // streaming append
    });
    socket.on('chat_done', ({answer, actions}) => {
      generating = false;
      sendBtn.disabled = false;
      finalizeStream(answer);
      if (actions && actions.length) {
        appendBubble('sys', `actions: ${actions.join(', ')}`);
      }
    });
    socket.on('chat_error', ({msg}) => {
      generating = false;
      sendBtn.disabled = false;
      appendBubble('sys', `오류: ${msg}`);
    });
  }

  // 버튼들 → 명령 이벤트
  document.querySelectorAll('.cmd').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!authed) return alert('먼저 연결하세요');
      socket.emit('btn', { name: btn.dataset.name });
    });
  });

  faceToggle.onchange = () => {
    if (!authed) return alert('먼저 연결하세요');
    socket.emit('toggle', { name:'face_detect', on: faceToggle.checked });
  };

  // 조이스틱 초기화(joystick.js에서 제공)
  document.querySelectorAll('.dpad').forEach(dpad => {
    const side = dpad.dataset.side || 'left';
    dpad.querySelectorAll('.dp').forEach(btn => {
      const bx = parseInt(btn.dataset.x || '0', 10);
      const by = parseInt(btn.dataset.y || '0', 10);
      const send = (x,y) => { if (!authed) return; socket.emit('stick', { side, x, y }); };
      btn.addEventListener('pointerdown', e => { btn.setPointerCapture(e.pointerId); send(bx, by); });
      const release = () => send(0,0);
      btn.addEventListener('pointerup', release);
      btn.addEventListener('pointercancel', release);
      btn.addEventListener('pointerleave', release);
    });
  });

  // 음성 초기화(디자인 모드에선 브라우저 음성만 사용하고, 이벤트는 콘솔만)
  let rec = null;
  const startVoice = () => {
    if (!authed) return alert('먼저 연결하세요');
    if (!rec) {
      rec = window.__startVoice((text) => {
        chatText.value = text;
        sendChat('voice');
      });
      voiceToggle.textContent = 'Voice Off';
     } else {
       rec.stop();
       rec = null;
      voiceToggle.textContent = 'Voice On / Off';
     }
   };
   voiceToggle.onclick = startVoice;

    // ---- Chat UI helpers ----
  function appendBubble(role, text, loading=false, streaming=false){
    if (!chatLog) return;
    // streaming: 마지막 assistant 말풍선에 텍스트 누적
    if (streaming){
      const last = chatLog.lastElementChild;
      if (last && last.dataset.role === 'assistant'){
        last.querySelector('.txt').textContent += text;
        chatLog.scrollTop = chatLog.scrollHeight;
        return;
      }
    }
    const div = document.createElement('div');
    div.className = `bubble ${role}` + (loading ? ' loading' : '');
    div.dataset.role = role;
    const span = document.createElement('span');
    span.className = 'txt';
    span.textContent = text;
    div.appendChild(span);
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
  }
  function finalizeStream(fullText){
    const last = chatLog.lastElementChild;
    if (last && last.dataset.role === 'sys' && last.classList.contains('loading')){
      last.remove(); // 생성중 로더 제거
    }
    // 스트리밍 누적 말풍선이 있으면 덮지 않고 종료
    const lastAssist = chatLog.lastElementChild;
    if (!(lastAssist && lastAssist.dataset.role === 'assistant')){
      appendBubble('assistant', fullText);
    }
  }
  function sendChat(via='text'){
    if (!authed) return alert('먼저 연결하세요');
    if (generating) return;
    const text = (chatText.value || '').trim();
    if (!text) return;
    appendBubble('user', text);
    chatText.value = '';
    socket.emit('chat_user', { text, via });
  }
  sendBtn.onclick = () => sendChat('text');
  chatText.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChat('text');
    }
  });
})();