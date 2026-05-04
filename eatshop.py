import streamlit as st
from google import genai
import requests

# ★ API設定
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
HOTPEPPER_API_KEY = st.secrets["HOTPEPPER_API_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- 画面の基本設定 ---
st.set_page_config(page_title="スマートご飯決めAI", page_icon="🍽️", layout="centered")
st.title("🍽️ キラみか専用！スマートご飯決めAI 🤤")

tab1, tab2 = st.tabs(["🍽️ お店探し＆提案", "🚃 交通費＆総予算シミュレーション"])

# ==========================================
# タブ1：お店探し＆提案（ワガママ全開OK！）
# ==========================================
with tab1:
    st.header("気分とワガママからお店を探すよ！")
    
    st.subheader("📍 どこで食べる？")
    col1, col2 = st.columns([1, 2])
    with col1:
        prefectures = ["大阪府", "京都府", "兵庫県", "奈良県", "東京都", "その他（自分で入力）"]
        selected_pref = st.selectbox("都道府県", prefectures)
        if selected_pref == "その他（自分で入力）":
            final_pref = st.text_input("都道府県を教えて！", placeholder="例：北海道、福岡県")
        else:
            final_pref = selected_pref
            
    with col2:
        target_location = st.text_input("駅名や地名", placeholder="例：長瀬、梅田 など")

    st.subheader("💭 今の気分は？")
    mood_presets = ["🍖 ガッツリお肉！", "🍣 さっぱり和食", "🍝 おしゃれカフェ", "🌶️ 刺激的な辛さ", "その他"]
    selected_mood = st.selectbox("どんな気分？", mood_presets)
    if selected_mood == "その他":
        target_mood = st.text_input("自由に教えて！", placeholder="例：チーズたっぷり！")
    else:
        target_mood = selected_mood

    # 💡 復活！具体的なワガママ枠
    details_memo = st.text_area(
        "さらに具体的なワガママ（任意）", 
        placeholder="例：予算は1000円以内、友達とゆっくり話せる場所、デザートも食べたい！など"
    )

    if st.button("AIにガチのお店を選んでもらう！✨"):
        if not target_location or not target_mood or (selected_pref == "その他（自分で入力）" and not final_pref):
            st.error("場所と気分はしっかり入力してね！")
        else:
            search_keyword = f"{final_pref} {target_location}"
            st.write(f"「{search_keyword}」周辺をリサーチ中...🔍🏃‍♀️💨")
            
            hotpepper_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
            params = {"key": HOTPEPPER_API_KEY, "keyword": search_keyword, "format": "json", "count": 15}
            
            try:
                res = requests.get(hotpepper_url, params=params)
                shops = res.json().get("results", {}).get("shop", [])
                
                if not shops:
                    st.warning("お店が見つからなかった😭 別の場所で試してみて！")
                else:
                    shop_list_text = ""
                    for i, shop in enumerate(shops):
                        shop_list_text += f"店名:{shop.get('name')}, ジャンル:{shop.get('genre',{}).get('name')}, 予算:{shop.get('budget',{}).get('name')}, URL:{shop.get('urls',{}).get('pc')}\n"
                    
                    user_message = f"""
                    あなたはセンス抜群のグルメアドバイザーです。
                    「{search_keyword}」周辺で「{target_mood}」な気分のユーザーに、以下の【実在するお店リスト】から最大3つお店を選んで提案して！
                    追加のワガママ：「{details_memo if details_memo else '特になし'}」
                    
                    出力はマークダウン形式で、ギャルっぽく明るいテンションでお願いします！選んだ理由やURLも添えてね！
                    
                    【お店リスト】\n{shop_list_text}
                    """
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=user_message)
                    st.success("最高の候補が見つかったよ！✨")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"エラー：{e}")

# ==========================================
# タブ2：交通費＆総予算計算（結局いくら必要！？）
# ==========================================
with tab2:
    st.header("お出かけ前の総予算シミュレーション👛")
    st.write("行く場所が決まったら、交通費とご飯代を合わせて『結局いくら用意すればいいか』を計算しよう！")
    
    start_point = st.text_input("📍 出発地（今いる場所）", placeholder="例：長瀬駅、近大前 など")
    end_point = st.text_input("🏁 目的地（お店の最寄駅）", placeholder="例：梅田駅、なんば駅 など")
    # 💡 所持金ではなく、お店で使う予定の予算を入力させる！
    food_budget = st.number_input("🍽️ ご飯の予算目安（円）", min_value=500, value=3000, step=500)
    
    if st.button("総予算を計算する！🚃"):
        if not start_point or not end_point:
            st.error("出発地と目的地を入力してね！")
        else:
            st.write("経路と運賃をAIが推測中...🤔💭")
            
            # 💡 計算式を「引き算」から「足し算」に変更！
            route_message = f"""
            あなたは優秀な交通案内AI兼、プランナーです。
            ユーザーは「{start_point}」から「{end_point}」へ向かいます。
            現地でのご飯の予算は「{food_budget}円」を想定しています。
            
            以下の内容をマークダウンで出力してください。
            1. 🚃 おおよそのルートと往復の交通費（推測でOKです）
            2. 💰 必要な総予算の計算（推測した往復交通費 ＋ ご飯予算 {food_budget}円 ＝ 必要な総額）
            3. 💡 お出かけ前のワンポイントアドバイス（ギャルっぽく明るいテンションで！）
            """
            
            try:
                route_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=route_message
                )
                st.success("計算完了！これだけ用意すれば安心だよ！✨")
                st.markdown(route_response.text)
            except Exception as e:
                st.error(f"エラー：{e}")