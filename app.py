import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection # 引入 Google 試算表套件

# 網頁基本設定
st.set_page_config(page_title="學生成績大樹成長系統", page_icon="🌳", layout="centered")

# 樹木視覺化的 HTML/CSS 模板 (這段都不用變)
def render_tree(level, progress_score):
    tree_data = {
        "5_茂盛大樹": {"emoji": "🌳✨🌿🍃", "desc": "卓越進步！大樹茂盛，充滿生機", "color": "#2E7D32"},
        "4_微幅成長": {"emoji": "🌳🌿", "desc": "穩定成長！新葉逐漸發芽", "color": "#4CAF50"},
        "3_小樹苗": {"emoji": "🌱", "desc": "維持現狀，這是一株潛力無窮的小樹苗", "color": "#8BC34A"},
        "2_些微落葉": {"emoji": "🍂🌿🪵", "desc": "些微退步，葉子開始變黃掉落了", "color": "#FF9800"},
        "1_枯萎樹木": {"emoji": "🥀🪵🍂", "desc": "嚴重退步，樹木逐漸枯萎，需要多加努力灌溉", "color": "#F44336"}
    }
    info = tree_data.get(level, tree_data["3_小樹苗"])
    html_content = f"""
    <div style="background-color: {info['color']}15; border: 2px solid {info['color']}; border-radius: 15px; padding: 30px; text-align: center; margin-bottom: 20px;">
        <div style="font-size: 80px; margin-bottom: 15px;">{info['emoji']}</div>
        <h3 style="color: {info['color']}; margin: 0;">{info['desc']}</h3>
        <p style="font-size: 20px; font-weight: bold; color: #333; margin-top: 10px;">
            進步幅度：{progress_score:+.1f} 分
        </p>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

# --- 主程式區塊 ---
st.title("🌱 學生成績「大樹成長」視覺化系統")
st.write("透過量化的樹木成長狀態，一起見證學習的進步！")

try:
    # 【關鍵改變】建立與 Google 試算表的連線 (快取時間設為 10 分鐘，ttl=600秒)
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="學生成績與樹木狀態", ttl=600)
    
    # 清理可能讀取到的空白列
    df = df.dropna(subset=['姓名'])
    
    # 建立側邊欄來選擇學生
    st.sidebar.header("🧑‍🎓 選擇學生")
    student_list = df['姓名'].tolist()
    selected_student = st.sidebar.selectbox("請選擇要查看的學生：", student_list)

    # 取得該位學生的資料
    student_data = df[df['姓名'] == selected_student].iloc[0]
    
    # 將成績卡片分為兩欄顯示
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="📊 本次綜合分數", value=f"{student_data['本次綜合分數']:.1f}" if pd.notna(student_data['本次綜合分數']) else "尚未計算")
    with col2:
        st.metric(label="📉 上次綜合分數", value=f"{student_data['上次綜合分數']:.1f}")

    st.markdown("---")
    
    # 顯示樹木視覺化
    if pd.notna(student_data['樹木等級']) and pd.notna(student_data['進步幅度']):
        st.subheader(f"🌳 {selected_student} 的專屬樹木狀態")
        render_tree(student_data['樹木等級'], student_data['進步幅度'])
    else:
        st.info("資料不足，無法顯示樹木狀態，請確認試算表中已填入完整成績。")

    with st.expander("查看各項成績細節"):
        st.dataframe(pd.DataFrame(student_data).T)

except Exception as e:
    st.error(f"⚠️ 無法讀取 Google 試算表，請確認 Secrets 設定是否正確。 錯誤訊息: {e}")
