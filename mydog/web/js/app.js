(() => {
  const socket = io();
  let authed = false;
  const tokenEl = document.getElementById('token');
  const connectBtn = document.getElementById('connectBtn');
  const streamEl = document.getElementById('stream');
  const distEl = document.getElementById('dist');
  const faceToggle = document.getElementById('faceToggle');

  // 영상 스트림 주소 구성(같은 호스트 가정)
  const base = window.location.origin.replace(/:\\d+$/, ':9000');
  streamEl.src = `${base}/mjpg`;

  connectBtn.onclick = () => {
    socket.emit('auth', { token: tokenEl.value || '000000' });
  };

  socket.on('auth_result', ({ok, msg}) => {
    authed = ok;
    alert(ok ? '연결됨' : `연결 실패: ${msg||''}`);
  });

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

  // 상태 수신
  socket.on('state', (payload) => {
    if (payload.distance != null) distEl.textContent = payload.distance;
  });

  // 조이스틱 초기화(joystick.js에서 제공)
  window.__initJoystick('joyL', (x, y) => {
    if (!authed) return; 
    socket.emit('stick', { side:'left', x, y });
  });
  window.__initJoystick('joyR', (x, y) => {
    if (!authed) return; 
    socket.emit('stick', { side:'right', x, y });
  });

  // 음성 초기화
  const voiceBtn = document.getElementById('voiceBtn');
  let rec = null;
  voiceBtn.onclick = () => {
    if (!authed) return alert('먼저 연결하세요');
    if (!rec) {
      rec = window.__startVoice((text) => socket.emit('voice', { text }));
      voiceBtn.textContent = '음성 정지';
    } else {
      rec.stop();
      rec = null;
      voiceBtn.textContent = '음성 시작/정지';
    }
  };
})();
