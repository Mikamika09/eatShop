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

tab1, tab2 = st.tabs(["🍽️ お店探し＆提案", "🚃 お店の情報＆総予算シミュレーション"])

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
# タブ2：お店の情報＆総予算シミュレーション
# ==========================================
with tab2:
    st.header("お出かけ前の総予算シミュレーション👛")
    st.write("行きたいお店の情報を入れて、APIで予算を自動リサーチ！交通費込みの総額を出すよ✨")
    
    start_point = st.text_input("📍 出発地（今いる場所や最寄駅）", placeholder="例：長瀬駅、近大前 など")
    
    st.write("---")
    st.write("🍽️ **行きたいお店の情報**（お店の名前だけは必須！）")
    restaurant_name = st.text_input("お店の名前（必須）", placeholder="例：HARBS、鳥貴族、OKOGE など")
    
    # 💡 改善：店舗名と最寄駅を横並びで別々に入力できるようにした！
    col1, col2 = st.columns(2)
    with col1:
        branch_name = st.text_input("店舗名（任意）", placeholder="例：なんばパークス店")
    with col2:
        dest_station = st.text_input("目的地の駅（任意）", placeholder="例：難波駅")
    
    if st.button("お店を特定して総予算を計算する！🚃"):
        if not start_point or not restaurant_name:
            st.error("出発地とお店の名前は絶対教えてね！")
        else:
            search_keywords = [restaurant_name]
            if branch_name:
                search_keywords.append(branch_name)
            if dest_station:
                search_keywords.append(dest_station)
            
            if not branch_name and not dest_station:
                search_query = f"{restaurant_name} {start_point}"
                fallback_query = restaurant_name 
            else:
                search_query = " ".join(search_keywords)
                fallback_query = search_query
            
            st.write(f"「{search_query}」の店舗データをAPIで検索中...🔍🏃‍♀️💨")
            
            hotpepper_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
            
            try:
                # 💡 変更：countを1から「10」に増やして、候補をたくさん引っ張ってくる！
                params = {"key": HOTPEPPER_API_KEY, "keyword": search_query, "format": "json", "count": 10}
                res = requests.get(hotpepper_url, params=params)
                shops = res.json().get("results", {}).get("shop", [])
                
                if not shops and not branch_name and not dest_station:
                    st.write("出発地の近くにはなさそう！エリアを広げて最大10店舗探してみるね！💦")
                    params["keyword"] = fallback_query
                    res = requests.get(hotpepper_url, params=params)
                    shops = res.json().get("results", {}).get("shop", [])

                if not shops:
                    st.warning("ごめん！APIでお店が特定できなかった😭 名前の書き方を少し変えてみて！")
                else:
                    st.success(f"お店の候補を {len(shops)}件 見つけたよ！ここからAIが一番近い店舗を選ぶね！🎯")
                    
                    # 💡 追加：見つかった最大10件の店舗情報を全部テキストにまとめる！
                    shop_list_text = ""
                    for i, shop in enumerate(shops):
                        s_name = shop.get("name")
                        s_address = shop.get("address", "住所不明")
                        s_budget = shop.get("budget", {}).get("name", "予算情報なし")
                        s_genre = shop.get("genre", {}).get("name", "美味しいご飯")
                        s_catch = shop.get("catch", "")
                        shop_list_text += f"【候補{i+1}】店名:{s_name}\n住所:{s_address}\n予算目安:{s_budget}\nジャンル:{s_genre}\nキャッチコピー:{s_catch}\n\n"
                    
                    # 💡 変更：Geminiに「一番近い店舗を選んで」と指示を出す！
                    route_message = f"""
                    あなたは優秀な交通案内AI兼、テンション高めのギャルプランナーです。
                    ユーザーは「{start_point}」から「{restaurant_name}」に向かいたいと考えています。
                    
                    【見つかった店舗の候補リスト】
                    {shop_list_text}
                    
                    【あなたのミッション】
                    1. 上記の候補リストの中で、「{start_point}」から電車で一番近くてアクセスしやすい店舗を**1つだけ**選んでください。
                       （例：ユーザーが長瀬駅や近大周辺にいる場合、梅田よりも難波や天王寺の店舗の方が圧倒的に近くて便利です！）
                    2. 選んだ店舗について、以下の内容をマークダウンで出力してください。
                    
                    【出力してほしい構成】
                    ### 🎯 選ばれたのは「（選んだ店名）」！
                    （なぜこの店舗が一番近い/アクセスが良いと判断したか、理由をギャルっぽく教えて！）
                    
                    1. 🚃 おおよそのルートと往復の交通費
                       - 選んだ店舗の住所から最寄り駅を推測して、{start_point}からの往復交通費を計算して！
                    2. 💰 必要な総予算の計算（推測した往復交通費 ＋ 選んだお店の予算目安 ＝ 必要な総額）
                    3. 💡 ワンポイントアドバイス
                       - ギャルっぽく明るいテンションで！選んだお店のジャンルやキャッチコピーの事実に基づいたアドバイスにして！
                    """
                    
                    route_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=route_message
                    )
                    st.markdown(route_response.text)
            except Exception as e:
                st.error(f"エラーが発生したよ：{e}")