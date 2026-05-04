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

# 💡 追加：編み物アプリの技術を応用！タブで機能を分ける
tab1, tab2 = st.tabs(["🍽️ サクッとお店探し", "🚃 交通費＆ガチ予算計算"])

# ==========================================
# タブ1：サクッとお店探し（めんどくさがり屋用！）
# ==========================================
with tab1:
    st.header("今の気分に合うお店を探すよ！")
    
    # 改善1はこっちに残す！（精度UPのため必須）
    st.subheader("📍 どこで食べる？")
    col1, col2 = st.columns([1, 2])
    with col1:
        prefectures = ["大阪府", "京都府", "兵庫県", "奈良県", "東京都", "その他"]
        selected_pref = st.selectbox("都道府県", prefectures)
    with col2:
        target_location = st.text_input("駅名や地名", placeholder="例：長瀬、梅田 など")

    st.subheader("💭 今の気分は？")
    mood_presets = ["🍖 ガッツリお肉！", "🍣 さっぱり和食", "🍝 おしゃれカフェ", "🌶️ 刺激的な辛さ", "その他"]
    selected_mood = st.selectbox("どんな気分？", mood_presets)
    if selected_mood == "その他":
        target_mood = st.text_input("自由に教えて！", placeholder="例：チーズたっぷり！")
    else:
        target_mood = selected_mood

    if st.button("サクッと探す！✨"):
        if not target_location or not target_mood:
            st.error("場所と気分を入力してね！")
        else:
            search_keyword = f"{selected_pref} {target_location}"
            st.write(f"「{search_keyword}」周辺をリサーチ中...🔍")
            
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
                    あなたはグルメアドバイザーです。「{search_keyword}」で「{target_mood}」な気分のユーザーに、以下のリストから最大3つお店を選んで、ギャルっぽく明るく提案して！
                    【お店リスト】\n{shop_list_text}
                    """
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=user_message)
                    st.success("見つかったよ！")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"エラー：{e}")

# ==========================================
# タブ2：交通費＆ガチ予算計算（行きたい店が決まってる時用！）
# ==========================================
with tab2:
    st.header("お財布と相談！交通費シミュレーション")
    st.write("「ここに行きたい！」が決まったら、交通費を計算して手持ちのお金で足りるかチェックしよう！👛")
    
    start_point = st.text_input("📍 今どこにいる？（出発駅）", placeholder="例：長瀬駅、近大前 など")
    end_point = st.text_input("🏁 行きたいお店の最寄駅（目的地）", placeholder="例：梅田駅、なんば駅 など")
    wallet_money = st.number_input("💰 今お財布にいくらある？（総予算）", min_value=500, value=3000, step=500)
    
    if st.button("交通費と残金を計算する！🚃"):
        if not start_point or not end_point:
            st.error("出発地と目的地を入力してね！")
        else:
            st.write("経路と運賃をAIが推測中...🤔💭")
            
            # 💡 ここはホットペッパーを使わず、Geminiの知識だけで計算！
            route_message = f"""
            あなたは優秀な交通案内AI兼、家計簿アドバイザーです。
            ユーザーは「{start_point}」から「{end_point}」へ向かおうとしています。
            現在の所持金（総予算）は「{wallet_money}円」です。
            
            以下の内容をマークダウンで出力してください。
            1. 🚃 おおよそのルートと往復の交通費（推測でOKです）
            2. 👛 所持金から往復交通費を引いた「実際にお店で使える残金」の計算式と結果
            3. 💡 その残金で楽しむための、少しギャルっぽいポジティブなアドバイス（例：「残金〇〇円なら、デザートまでいけちゃうね！」など）
            """
            
            try:
                route_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=route_message
                )
                st.success("計算完了！")
                st.markdown(route_response.text)
            except Exception as e:
                st.error(f"エラー：{e}")