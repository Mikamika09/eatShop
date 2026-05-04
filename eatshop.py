import streamlit as st
from google import genai
import requests
import json

# ★ API設定（両方の鍵を使うよ！）
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
HOTPEPPER_API_KEY = st.secrets["HOTPEPPER_API_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- 画面の基本設定 ---
st.set_page_config(page_title="ガチご飯決めAI", page_icon="🍽️", layout="centered")
st.title("🍽️ キラみか専用！ガチご飯決めAI 🤤")
st.write("ホットペッパーのデータから、今すぐ行ける『実在するお店』だけを提案するよ！✨")

st.write("---")
# 📍 追加：場所の指定
st.subheader("📍 どこで食べる？")
target_location = st.text_input("駅名や地名を教えて！", placeholder="例：梅田、長瀬、難波、近大前 など")

st.write("---")
st.subheader("💭 今の気分は？")
mood_presets = [
    "🍖 ガッツリお肉！限界まで食べたい",
    "🍣 さっぱり海鮮・和食の気分",
    "🍝 おしゃれなカフェ飯・イタリアン",
    "🌶️ 汗かくくらい辛いもので刺激が欲しい！",
    "その他（自分で入力）"
]
selected_mood = st.selectbox("どんな気分？", mood_presets)

if selected_mood == "その他（自分で入力）":
    target_mood = st.text_input("今の気分を直感で！", placeholder="例：とにかくチーズが伸びるやつ！")
else:
    target_mood = selected_mood

details_memo = st.text_area(
    "さらに具体的なワガママ（任意）", 
    placeholder="例：予算は1000円以内、友達とゆっくり話せる場所、など"
)

if st.button("AIにガチのお店を選んでもらう！✨"):
    if not target_location or not target_mood:
        st.error("「場所」と「気分」は両方入力してね！")
    else:
        st.write(f"「{target_location}」周辺のお店をホットペッパーで検索中...🔍🏃‍♀️💨")
        
        # 1️⃣ ホットペッパーAPIでお店データを大量取得！
        hotpepper_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
        params = {
            "key": HOTPEPPER_API_KEY,
            "keyword": target_location, # 入力した場所をキーワードにして検索
            "format": "json",
            "count": 15 # 15件のお店をリストアップ！
        }
        
        try:
            res = requests.get(hotpepper_url, params=params)
            data = res.json()
            shops = data.get("results", {}).get("shop", [])
            
            if not shops:
                st.warning(f"ごめん！「{target_location}」周辺でお店が見つからなかった😭 別の駅名で試してみて！")
            else:
                st.success(f"本物の店舗データを {len(shops)}件 ゲットしたよ！ここからAIが厳選するね🤔💭🪄")
                
                # 2️⃣ 取得したお店の情報をAIが読めるようにテキストにまとめる
                shop_list_text = ""
                for i, shop in enumerate(shops):
                    name = shop.get("name", "名前なし")
                    genre = shop.get("genre", {}).get("name", "")
                    catch = shop.get("catch", "")
                    budget = shop.get("budget", {}).get("name", "")
                    access = shop.get("access", "")
                    url_pc = shop.get("urls", {}).get("pc", "")
                    
                    shop_list_text += f"【候補{i+1}】\n店名: {name}\nジャンル: {genre}\nキャッチコピー: {catch}\n予算: {budget}\nアクセス: {access}\nURL: {url_pc}\n\n"
                    
                # 3️⃣ Geminiに「この中から選んで！」とお願いする
                user_message = f"""
                あなたはセンス抜群のグルメアドバイザーです。
                ユーザーが「{target_location}」周辺で、「{target_mood}」という気分でご飯屋さんを探しています。
                追加のワガママ：「{details_memo if details_memo else '特になし'}」
                
                以下の【取得した実在するお店リスト】の中から、ユーザーの気分に一番合いそうなお店を最大3つ厳選して、ギャルっぽく明るいテンションで提案してください！
                ※重要：絶対にこのリストの中にあるお店だけを紹介し、架空のお店は絶対に作らないでください。
                
                【取得した実在するお店リスト】
                {shop_list_text}
                
                【出力してほしい構成（マークダウン形式）】
                1. 🍽️ キラみかに超おすすめのガチ店舗（選んだ理由、予算、URLも一緒に！）
                2. 💡 お店選びのワンポイントアドバイス
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_message
                )
                st.write("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"エラーが発生したよ：{e}")