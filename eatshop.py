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

# 💡 結果を忘れないためのポケット（Tab3の分も追加！）
if "tab1_result" not in st.session_state:
    st.session_state.tab1_result = None
if "tab2_result" not in st.session_state:
    st.session_state.tab2_result = None
if "tab3_result" not in st.session_state:
    st.session_state.tab3_result = None

# 💡 変更：タブを3つに分割！
tab1, tab2, tab3 = st.tabs(["🍽️ お店探し＆提案", "🚃 総予算シミュレーション", "🗺️ 1日神プラン作成"])

# ==========================================
# タブ1：お店探し＆提案
# ==========================================
with tab1:
    st.header("気分とワガママからお店を探すよ！")
    
    st.subheader("📍 どこで食べる？")
    col1, col2 = st.columns([1, 2])
    with col1:
        prefectures = ["大阪府", "京都府", "兵庫県", "奈良県", "東京都", "その他（自分で入力）"]
        selected_pref = st.selectbox("都道府県", prefectures, key="pref1")
        if selected_pref == "その他（自分で入力）":
            final_pref = st.text_input("都道府県を教えて！", placeholder="例：北海道、福岡県", key="pref_free1")
        else:
            final_pref = selected_pref
            
    with col2:
        target_location = st.text_input("駅名や地名", placeholder="例：長瀬、梅田 など", key="loc1")

    st.subheader("💭 今の気分は？")
    mood_presets = ["🍖 ガッツリお肉！", "🍣 さっぱり和食", "🍝 おしゃれカフェ", "🌶️ 刺激的な辛さ", "その他"]
    selected_mood = st.selectbox("どんな気分？", mood_presets, key="mood1")
    if selected_mood == "その他":
        target_mood = st.text_input("自由に教えて！", placeholder="例：チーズたっぷり！", key="mood_free1")
    else:
        target_mood = selected_mood

    details_memo = st.text_area("さらに具体的なワガママ（任意）", placeholder="例：予算は1000円以内など", key="memo1")

    if st.button("AIにガチのお店を選んでもらう！✨", key="btn1"):
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
                        photo_url = shop.get('photo', {}).get('pc', {}).get('l', '')
                        shop_list_text += f"店名:{shop.get('name')}, ジャンル:{shop.get('genre',{}).get('name')}, 予算:{shop.get('budget',{}).get('name')}, URL:{shop.get('urls',{}).get('pc')}, 写真URL:{photo_url}\n"
                    
                    user_message = f"""
                    あなたはセンス抜群のグルメアドバイザーです。
                    「{search_keyword}」周辺で「{target_mood}」な気分のユーザーに、以下の【実在するお店リスト】から最大3つお店を選んで提案して！
                    追加のワガママ：「{details_memo if details_memo else '特になし'}」
                    
                    出力はマークダウン形式で、ギャルっぽく明るいテンションでお願いします！選んだ理由やURLも添えてね！
                    ★超重要：必ずリストにある「写真URL」を使って、マークダウンで画像を表示させてください（例： `![お店の写真](写真URL)` ）。
                    
                    【お店リスト】\n{shop_list_text}
                    """
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=user_message)
                    st.session_state.tab1_result = response.text
            except Exception as e:
                st.error(f"エラーが発生したよ：{e}")

    if st.session_state.tab1_result:
        st.success("最高の候補が見つかったよ！写真も見てみてね！📸✨")
        st.markdown(st.session_state.tab1_result)

# ==========================================
# タブ2：総予算シミュレーション（お金とルートに特化！）
# ==========================================
with tab2:
    st.header("お出かけ前の総予算シミュレーション👛")
    st.write("行くお店が決まったら、交通費込みのリアルな総額を計算しよう！")
    
    start_point2 = st.text_input("📍 出発地（今いる場所）", placeholder="例：長瀬駅", key="start2")
    restaurant_name2 = st.text_input("🍽️ お店の名前（必須）", placeholder="例：HARBS", key="rest2")
    
    col1_2, col2_2 = st.columns(2)
    with col1_2:
        branch_name2 = st.text_input("店舗名（任意）", placeholder="例：なんばパークス店", key="branch2")
    with col2_2:
        dest_station2 = st.text_input("目的地の駅（任意）", placeholder="例：難波駅", key="dest2")
    
    if st.button("総予算を計算する！🚃", key="btn2"):
        if not start_point2 or not restaurant_name2:
            st.error("出発地とお店の名前は絶対教えてね！")
        else:
            search_keywords = [restaurant_name2]
            if branch_name2: search_keywords.append(branch_name2)
            if dest_station2: search_keywords.append(dest_station2)
            
            search_query = f"{restaurant_name2} {start_point2}" if not branch_name2 and not dest_station2 else " ".join(search_keywords)
            fallback_query = restaurant_name2 if not branch_name2 and not dest_station2 else search_query
            
            st.write(f"「{search_query}」の予算を検索中...🔍")
            hotpepper_url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
            
            try:
                params = {"key": HOTPEPPER_API_KEY, "keyword": search_query, "format": "json", "count": 10}
                res = requests.get(hotpepper_url, params=params)
                shops = res.json().get("results", {}).get("shop", [])
                
                if not shops and not branch_name2 and not dest_station2:
                    params["keyword"] = fallback_query
                    res = requests.get(hotpepper_url, params=params)
                    shops = res.json().get("results", {}).get("shop", [])

                if not shops:
                    st.warning("お店が特定できなかった😭")
                else:
                    shop_list_text = ""
                    for i, shop in enumerate(shops):
                        shop_list_text += f"【候補{i+1}】店名:{shop.get('name')}\n住所:{shop.get('address', '不明')}\n予算:{shop.get('budget', {}).get('name', '不明')}\n\n"
                    
                    route_message = f"""
                    あなたは交通案内AIです。ユーザーは「{start_point2}」から「{restaurant_name2}」に向かいます。
                    【店舗候補】\n{shop_list_text}
                    
                    一番近い店舗を1つ選び、以下をギャル語で出力して！
                    1. 選んだ店舗名
                    2. 🚃 往復の交通費（推測）
                    3. 💰 総予算（交通費＋お店の予算）
                    """
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=route_message)
                    st.session_state.tab2_result = response.text
            except Exception as e:
                st.error(f"エラー：{e}")

    if st.session_state.tab2_result:
        st.markdown(st.session_state.tab2_result)

# ==========================================
# 💡 新規追加：タブ3（1日の神プラン作成に特化！）
# ==========================================
with tab3:
    st.header("🗺️ ご飯までの神プランを作ろう！")
    st.write("お店に行くまでの時間、どうやって遊ぶ？AIが最高の暇つぶしプランを考えるよ！✨")
    
    start_point3 = st.text_input("📍 どこからスタートする？", placeholder="例：長瀬駅", key="start3")
    restaurant_name3 = st.text_input("🍽️ 最終目的地（決まったお店）", placeholder="例：HARBS なんばパークス店", key="rest3")
    
    time_to_kill = st.selectbox(
        "⏳ ご飯までどれくらい遊ぶ？", 
        ["1〜2時間（サクッとカフェやウィンドウショッピング）", "半日（がっつりデート・遊び！）", "1日中（朝から晩まで最高のコース！）"],
        key="time3"
    )
    
    # 💡 追加：ユーザーのワガママ（要望）を聞く枠！
    free_request = st.text_area(
        "📝 やりたいこと・ワガママ（任意）", 
        placeholder="例：プリクラ撮りたい！、歩き疲れないまったりコースがいい、古着屋さん見たい！など", 
        key="req3"
    )

    if st.button("1日の神プランを作成！🪄", key="btn3"):
        if not start_point3 or not restaurant_name3:
            st.error("スタート地点と最終目的地（お店）を教えてね！")
        else:
            st.write("周辺の映えスポットや遊べる場所をAIがリサーチ中...🤔💭🪄")
            
            plan_message = f"""
            あなたはカリスマ的なギャルプランナー兼、最高のツアコンです！
            ユーザーは「{start_point3}」から出発し、最終的に「{restaurant_name3}」でご飯を食べます。
            ご飯までの遊べる時間は「{time_to_kill}」です。
            
            ユーザーからのリクエスト（ワガママ）：「{free_request if free_request else '特になし！AIのおすすめで！'}」
            
            この条件とリクエストに合わせて、ユーザーが絶対にテンションが上がる「神プラン（スケジュール）」を提案してください！
            
            【出力してほしい構成（マークダウン）】
            ### 💖 {start_point3}〜{restaurant_name3} 満喫プラン！
            - ギャルっぽく明るいテンションで、具体的な地名やおすすめスポット（カフェ、服屋、プリクラ、映えスポットなど）を入れてね！
            - タイムスケジュール風（例：13:00 〇〇集合、14:00 〇〇でショッピング...）に書いてくれると嬉しい！
            - ユーザーのリクエスト（{free_request if free_request else 'なし'}）を最大限プランに盛り込んでね！
            - 最後はしっかり「{restaurant_name3}」でのご飯に繋がるようにして！
            """
            
            try:
                plan_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=plan_message
                )
                st.session_state.tab3_result = plan_response.text
            except Exception as e:
                st.error(f"エラーが発生したよ：{e}")

    if st.session_state.tab3_result:
        st.success("神プラン完成！！これで当日は迷わず遊べるね！🎉✨")
        st.markdown(st.session_state.tab3_result)