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

  let socket = null;
  let authed = false;

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

    // 더미 영상(로컬 이미지, 사이즈: 750 x 600)
    streamEl.width = 750;
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
  window.__initJoystick('joyL', (x, y) => {
    if (!authed) return; 
    socket.emit('stick', { side:'left', x, y });
  });
  window.__initJoystick('joyR', (x, y) => {
    if (!authed) return; 
    socket.emit('stick', { side:'right', x, y });
  });

  // 음성 초기화(디자인 모드에선 브라우저 음성만 사용하고, 이벤트는 콘솔만)
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
