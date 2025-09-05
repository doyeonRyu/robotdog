from openai import OpenAI
import os
from gpt.keys import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
from dog import Mydog
import time
import sys

# OpenAI API 클라이언트 생성 (환경 변수 키 사용)
client = OpenAI()

def main():
    print("GPT API test")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in (["q", "quit", "exit"]):
                print("[대화 종료]")
                break

            # GPT 호출
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages = [ # 대화 내용
                    {"role": "system", "content": "You are a helpful assistant."}, 
                    {"role": "user", "content": user_input}
                ]
            )

            # 출력
            reply = response.choices[0].message.content
            print(f"GPT: {reply}")
        
        except KeyboardInterrupt:
            print("[대화 종료]")
            break

if __name__ == "__main__":
    main()