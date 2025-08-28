import os, shlex, subprocess, threading, re, ast
from pathlib import Path

class GPTRunner:
    """
    외부 GPT 실행파일(gpt_dog.py)을 호출해 답변/액션을 수집하는 래퍼.
    - stdout에서 {'actions':[...], 'answer':'...'} 형태를 찾아 파싱
    - 상태 콜백(thinking/speaking), 스트림(옵션), 완료/에러 콜백 지원
    - (옵션) TTS: espeak-ng 로컬 재생
    """

    def __init__(self, workdir: str, python_bin: str, script: str,
                 extra_args=None, use_sudo=False, tts=True, tts_lang="ko", tts_speed="165"):
        self.workdir = os.path.expanduser(workdir)
        self.python_bin = os.path.expanduser(python_bin)
        self.script = script
        self.extra_args = extra_args or []
        self.use_sudo = use_sudo
        self.tts = tts
        self.tts_lang = tts_lang
        self.tts_speed = tts_speed

    def _build_cmd(self):
        cmd = [self.python_bin, self.script, *self.extra_args]
        if self.use_sudo:
            cmd = ["sudo", *cmd]
        return cmd

    def ask(self, prompt: str, on_status, on_stream, on_done, on_error):
        """
        prompt를 실행파일에 입력으로 전달하고, 결과를 파싱하여 콜백으로 전달.
        """
        try:
            cmd = self._build_cmd()
            print(f"[GPT] start: cwd={self.workdir} cmd={' '.join(shlex.quote(c) for c in cmd)}")
            proc = subprocess.Popen(
                cmd,
                cwd=self.workdir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
        except Exception as e:
            on_error(f"process start failed: {e}")
            return

        # 생성 시작
        on_status("thinking")

        # stdin으로 프롬프트 전달 (엔터 포함)
        try:
            if proc.stdin:
                proc.stdin.write(prompt.strip() + "\n")
                proc.stdin.flush()
        except Exception:
            pass

        answer_text = ""
        actions = []

        regex_dict = re.compile(r"\{.*\}")
        try:
            for line in proc.stdout:  # type: ignore
                ln = line.rstrip("\n")
                if ln:
                    # 너무 길면 앞부분만
                    print(f"[GPT][out] {ln[:160]}")
                # 스트림을 그대로 로그처럼 흘려보내고 싶으면 on_stream(line)
                # 여기서는 과도한 토큰 전송 방지를 위해 생략/옵션화
                m = regex_dict.search(line)
                if m:
                    try:
                        data = ast.literal_eval(m.group(0))
                        if isinstance(data, dict):
                            answer_text = str(data.get("answer", "")).strip()
                            actions = list(data.get("actions", []) or [])
                    except Exception:
                        pass
                # 'speak start' 감지 시 상태 전송
                if "speak start" in line.lower():
                    on_status("speaking")
        except Exception as e:
            on_error(f"read failed: {e}")
        finally:
            try:
                proc.terminate()
            except Exception:
                pass

        # 말하기(TTS)
        if self.tts and answer_text:
            self._speak(answer_text)

        # 완료 콜백
        if answer_text or actions:
            on_done(answer_text, actions)
        else:
            on_error("no answer parsed")

    def _speak(self, text: str):
        """espeak-ng 로 텍스트를 음성으로 재생(설치되어 있지 않으면 무시)."""
        try:
            cmd = ["espeak-ng", "-s", self.tts_speed, "-v", self.tts_lang, text]
            subprocess.run(cmd, check=False)
        except Exception:
            pass
