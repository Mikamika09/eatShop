import streamlit as st
from google import genai

# ★ API設定
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- 画面の基本設定 ---
st.set_page_config(page_title="気分でご飯決めAI", page_icon="🍽️", layout="centered")
st.title("🍽️ キラみか専用！今日のご飯決めAI 🤤")

st.header("今の気分を教えて！")
st.write("選択肢から選ぶか、『その他』で自由に教えてね🍔")

# 💡 気分のプリセット（選択肢）
mood_presets = [
    "🍖 ガッツリお肉！限界まで食べたい",
    "🍣 さっぱり海鮮・和食の気分",
    "🍝 おしゃれなカフェ飯・イタリアン",
    "🌶️ 汗かくくらい辛いもので刺激が欲しい！",
    "その他（自分で入力）"
]

selected_mood = st.selectbox("どんな気分？", mood_presets)

if selected_mood == "その他（自分で入力）":
    target_mood = st.text_input("今の気分を直感で！", placeholder="例：とにかくチーズが伸びるやつ！、二日酔いだから汁物…など")
else:
    target_mood = selected_mood

st.write("---")
st.subheader("💭 さらに具体的なワガママ（任意）")
details_memo = st.text_area(
    "場所、予算、絶対に食べたい食材などがあれば書いてね！", 
    placeholder="例：大学の近くがいい！、予算は1000円以内、友達とゆっくり話せる場所、など"
)

if st.button("AIに候補を考えてもらう！✨"):
    if not target_mood:
        st.error("気分を入力してね！")
    else:
        st.write("美味しいお店の候補を爆速でリサーチ中...🤤💭🪄")
        
        if details_memo:
            detail_condition = f"追加の希望・条件：「{details_memo}」"
        else:
            detail_condition = "特に追加の条件はありません。指定された気分に合うものを幅広く提案して！"
            
        # 💬 AIへの指示（グルメアドバイザーになってもらう！）
        user_message = f"""
        あなたはセンス抜群のグルメアドバイザーです。
        ユーザーが今、「{target_mood}」という気分でご飯屋さんを探しています。
        
        【条件】
        {detail_condition}
        
        【出力してほしい構成】
        以下の内容をマークダウン形式で見やすく、ギャルっぽく明るいテンションで提案してください！
        1. 🍽️ おすすめのご飯ジャンル＆お店の候補（3つ）
           - 提案する具体的なメニューやジャンル（例：サムギョプサル、スパイスカレーなど）と、なぜ今の気分にピッタリ合うのかの理由。
        2. 💡 お店選び・検索のワンポイントアドバイス
           - 実際にお店を探すときの検索キーワード（例：「〇〇駅 個室 カフェ」で検索するといいよ！）などを教えてください。
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_message
            )
            st.success("候補が見つかったよ！✨")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"エラーが発生したよ：{e}")