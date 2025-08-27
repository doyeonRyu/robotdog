(function(){
  window.__startVoice = function(onText){
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { alert('브라우저가 음성 인식을 지원하지 않습니다'); return { stop(){}}; }
    const rec = new SR();
    rec.lang = 'en-US'; // 필요 시 'ko-KR'
    rec.continuous = true;
    rec.interimResults = false;
    rec.onresult = (e) => {
      const last = e.results[e.results.length - 1];
      const text = last[0].transcript.trim();
      if (text) onText(text);
    };
    rec.start();
    return rec;
  }
})();
