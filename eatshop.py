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
    st.write("行きたいお店の名前を入れるだけで、APIが予算を自動リサーチ！交通費込みの総額を出すよ✨")
    
    start_point = st.text_input("📍 出発地（今いる場所）", placeholder="例：長瀬駅、近大前 など")
    
    # 💡 変更：予算の入力欄を消して、お店の名前だけ聞くようにした！
    restaurant_keyword = st.text_input("🍽️ 行きたいお店の名前（＋駅名）", placeholder="例：OKOGE 大阪駅、鳥貴族 長瀬 など")
    
    if st.button("お店を特定して総予算を計算する！🚃"):
        if not start_point or not restaurant_keyword:
            st.error("出発地とお店の名前を入力してね！")
        else:
            st.write(f"「{restaurant_keyword}」の正確なデータと予算をAPIで検索中...🔍🏃‍♀️💨")
            
            # 💡 追加：Tab2でもホットペッパーAPIを使って、入力されたお店をピンポイントで探す！
            hotpepper_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
            params = {
                "key": HOTPEPPER_API_KEY, 
                "keyword": restaurant_keyword, 
                "format": "json", 
                "count": 1 # 1番上に出てきたお店だけ特定すればOK！
            }
            
            try:
                res = requests.get(hotpepper_url, params=params)
                shops = res.json().get("results", {}).get("shop", [])
                
                if not shops:
                    st.warning("ごめん！APIでお店が特定できなかった😭 お店の名前や駅名を少し変えてみて！")
                else:
                    # 見つかったお店の「本物のデータ」を抜き出す！
                    target_shop = shops[0]
                    shop_name = target_shop.get("name")
                    shop_budget = target_shop.get("budget", {}).get("name", "予算情報なし（大体3000円くらいかな🤔）")
                    shop_genre = target_shop.get("genre", {}).get("name", "美味しいご飯")
                    shop_catch = target_shop.get("catch", "")
                    
                    st.success(f"お店を特定したよ！🎯【{shop_name}】(予算目安: {shop_budget})")
                    st.write("このリアルな予算を使って、交通費とアドバイスをAIがまとめるね！🤔💭")
                    
                    # 💡 変更：推測じゃなく、APIで取った「本物のデータ」をAIに渡す！
                    route_message = f"""
                    あなたは優秀な交通案内AI兼、テンション高めのギャルプランナーです。
                    ユーザーは「{start_point}」から以下の実在するお店に向かいます。
                    
                    【特定したお店のリアルデータ】
                    ・店名: {shop_name}
                    ・ジャンル: {shop_genre}
                    ・キャッチコピー: {shop_catch}
                    ・予算目安: {shop_budget}
                    
                    以下の内容をマークダウンで出力して！
                    1. 🚃 おおよそのルートと往復の交通費（推測でOK）
                    2. 💰 必要な総予算の計算（推測した往復交通費 ＋ お店の予算目安 ＝ 必要な総額）
                    3. 💡 「{shop_name}」に行く前のワンポイントアドバイス
                       - ギャルっぽく明るいテンションで！
                       - お店のジャンル（{shop_genre}）やキャッチコピー（{shop_catch}）の事実に基づいた、リアルで役に立つアドバイスにして！知ったかぶりはNG！
                    """
                    
                    route_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=route_message
                    )
                    st.markdown(route_response.text)
            except Exception as e:
                st.error(f"エラーが発生したよ：{e}")