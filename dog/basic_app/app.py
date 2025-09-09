# app.py
from flask import Flask, request, jsonify, send_from_directory
from dog import Mydog
from pathlib import Path

app = Flask(__name__, static_folder="static", static_url_path="/static")
dog = Mydog()

@app.route("/")
def index():
    # /static/index.html 서빙
    return send_from_directory(app.static_folder, "index.html")

@app.post("/api/do_action")
def api_do_action():
    """
    '''
    함수 설명: 액션 실행 API 엔드포인트
    입력값: JSON {"name": "<action_name>"}
    출력값: JSON {status, name, target, frames} 또는 에러
    '''
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    try:
        res = dog.do_action(name)
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 400

if __name__ == "__main__":
    # 0.0.0.0로 열어 같은 네트워크에서 접속 가능
    app.run(host="0.0.0.0", port=8000, debug=True)
