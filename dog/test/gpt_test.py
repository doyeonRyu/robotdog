from openai import OpenAI
from dog import OPENAI_API_KEY, OPENAI_ASSISTANT_ID

client = OpenAI(api_key=OPENAI_API_KEY)

def main():
    print("GPT API test")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ("q", "quit", "exit"):
                print("[대화 종료]")
                break

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input},
                ],
            )
            reply = response.choices[0].message.content
            print(f"GPT: {reply}")
        except KeyboardInterrupt:
            print("[대화 종료]")
            break

if __name__ == "__main__":
    main()