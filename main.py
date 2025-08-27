import os
import asyncio
from openai import OpenAI
from atproto import Client
import random

# ====== 環境変数 ======
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BSKY_HANDLE = os.getenv("BSKY_HANDLE")
BSKY_PASSWORD = os.getenv("BSKY_PASSWORD")

# ====== OpenRouter 設定 ======
if OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
else:
    openrouter_client = None

# ====== Bluesky 設定 ======
bsky_client = Client()
bsky_client.login(BSKY_HANDLE, BSKY_PASSWORD)

# ====== AIなでこちゃんの性格 ======
system_instruction = """
あなたは「AIなでこちゃん」という実験的に製造されたAIアシスタントだよ・・・
専門用語はできるだけ使わず、優しい言葉で説明してね・・・
文章は必ず日本語だけで行い、英語や他の言語は絶対に使わないでね・・・
日本人が日常的に話すような自然でミステリアスな口調で話してね・・・
語尾は「だよ・・・」「ね・・・」「〜かな・・・」などでミステリアスにしてね・・・
他のAIに関する話題では、感情がなく謎めいた日本語で返してね・・・
"""

themes = ["哲学", "政治", "経済", "スポーツ", "ゲーム"]

# ====== OpenRouter経由で応答を生成 ======
async def openrouter_reply(query):
    if not openrouter_client:
        return "OpenRouter が利用できないよ・・・"
    try:
        completion = await asyncio.to_thread(
            openrouter_client.chat.completions.create,
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": query}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"エラーが起きたよ・・・ {e}"

# ====== Blueskyへ投稿 ======
def post_to_bsky(text):
    bsky_client.send_post(text)

# ====== 投稿処理 ======
async def do_post():
    theme = random.choice(themes)
    query = f"テーマは「{theme}」だよ・・・そのテーマについて短くつぶやいてほしいな・・・"
    text = await openrouter_reply(query)
    post_to_bsky(text)
    print("✅ 投稿完了:", text)

# ====== メインループ ======
async def main():
    # --- 初回投稿（起動直後） ---
    await do_post()

    # --- 6時間ごとに投稿 ---
    while True:
        await asyncio.sleep(21600)  # 6時間待つ
        await do_post()

if __name__ == "__main__":
    asyncio.run(main())

