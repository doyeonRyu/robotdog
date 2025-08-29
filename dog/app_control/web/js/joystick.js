// 가상 조이스틱 입력을 -100~100 범위로 변환해 콜백으로 전달
(function(){
  function clamp(v, min, max){ return Math.max(min, Math.min(max, v)); }

  window.__initJoystick = function(id, onMove){
    const el = document.getElementById(id);
    let dragging = false;
    let rect = null;

    const send = (clientX, clientY) => {
      if (!rect) rect = el.getBoundingClientRect();
      const cx = rect.left + rect.width/2;
      const cy = rect.top + rect.height/2;
      const dx = clientX - cx;
      const dy = clientY - cy;
      const r = Math.sqrt(dx*dx + dy*dy);
      const maxR = rect.width/2;
      const nx = clamp(Math.round((dx / maxR) * 100), -100, 100);
      const ny = clamp(Math.round((dy / maxR) * 100), -100, 100);
      onMove(nx, ny * -1); // 화면 좌표계를 로봇 좌표계로 반전
    };

    el.addEventListener('pointerdown', e => { dragging = true; el.setPointerCapture(e.pointerId); send(e.clientX, e.clientY); });
    el.addEventListener('pointermove', e => { if(dragging) send(e.clientX, e.clientY); });
    el.addEventListener('pointerup',   e => { dragging = false; onMove(0,0); });
    el.addEventListener('pointercancel', e => { dragging = false; onMove(0,0); });
  }
})();
