import streamlit as st
import pandas as pd
from datetime import datetime
import os

# NQ Multiplier: 1 full index point = $20 per contract
NQ_MULTIPLIER = 20

# Page layout configuration (Hiding sidebar entirely for a clean canvas)
st.set_page_config(page_title="NQ Open Trading Journal", layout="wide", initial_sidebar_state="collapsed")

st.title("📊 NQ Open Trading Journal")
st.caption("Joey and Nihals Profitable Ahh Journal | NY AM Session")

# --- USER SELECTION (each user gets their own separate journal & images) ---
USERS = ["Joey", "Nihal"]
selected_user = st.selectbox("👤 Who's logging in?", USERS)

CSV_FILE = f"nq_trading_journal_{selected_user}.csv"
IMAGE_DIR = f"trade_images_{selected_user}"

st.markdown(f"### Currently viewing: **{selected_user}'s Journal**")
st.markdown("---")

# Ensure required directories exist locally
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "Trade ID", "Date", "Setup Type", "Direction", "Contracts", 
        "Dollar PnL", "Points PnL", "News Day", "Discipline Grade", "Behavioral Tags", "Notes", "Screenshot Path"
    ])
    df_init.to_csv(CSV_FILE, index=False)

# Helper function to load data safely
def load_data():
    df = pd.read_csv(CSV_FILE)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df["Behavioral Tags"] = df["Behavioral Tags"].fillna("")
        df["Screenshot Path"] = df["Screenshot Path"].fillna("None")
    return df

df = load_data()

# --- THREE TOP TABS LAYOUT ---
tab1, tab2, tab3 = st.tabs([
    "📥 Log Session",
    f"📊 {selected_user}'s Performance Metrics",
    f"🔍 {selected_user}'s Chart Reviewer"
])

# ==========================================================
# TAB 1: LOG SESSION (Data entry window)
# ==========================================================
with tab1:
    st.subheader(f"Log {selected_user}'s Morning Session Data")
    st.markdown("Keep it simple. Enter your final metrics below right after the market open wraps up.")
    
    with st.form(key="main_trade_form", clear_on_submit=True):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            trade_date = st.date_input("Trade Date", datetime.now())
            setup_type = st.text_input("Setup / Strategy Type (Type anything, e.g., NQ Sweep)", value="")
            direction = st.selectbox("Direction", ["Long", "Short"])
            contracts = st.number_input("Contracts Size", min_value=1, value=1, step=1)
            dollar_pnl = st.number_input("Net Dollar PnL ($) (Use minus sign for losses)", value=0.0, step=50.0)
            
        with col_form2:
            news_day = st.selectbox("Major Morning News? (CPI/NFP/FOMC)", ["No", "Yes"])
            discipline_grade = st.slider("Discipline Grade (1 = Rules Broken, 5 = Flawless Execution)", 1, 5, 5)
            
            leak_options = [
                "Perfect Execution (No Issues)", 
                "Overtrading", 
                "Impatience / No Confirmation", 
                "FOMO", 
                "Overconfidence", 
                "Failure to Recognize Bad Market Conditions", 
                "Random / Unbacktested Trade"
            ]
            selected_tags = st.multiselect("Behavioral Tags (Select all that apply)", options=leak_options)
            uploaded_file = st.file_uploader("Upload Trade Screenshot (Drag & Drop PNG/JPG)", type=["png", "jpg", "jpeg"])
            
        notes = st.text_area("Trade Psychology & Market Context Notes", placeholder="What went through your head during the execution? Was the bias clear?")
        
        submit_button = st.form_submit_button(label="Securely Write Trade to Journal Database")

    if submit_button:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        trade_id = f"TRADE_{timestamp_str}"
        saved_img_path = "None"
        
        if uploaded_file is not None:
            file_extension = os.path.splitext(uploaded_file.name)[1]
            saved_img_name = f"{trade_id}{file_extension}"
            saved_img_path = os.path.join(IMAGE_DIR, saved_img_name)
            with open(saved_img_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
        points_pnl = dollar_pnl / (NQ_MULTIPLIER * contracts)
        tags_string = ", ".join(selected_tags) if selected_tags else "None"
        
        new_data = pd.DataFrame([{
            "Trade ID": trade_id,
            "Date": trade_date.strftime("%Y-%m-%d"),
            "Setup Type": setup_type if setup_type.strip() != "" else "Unspecified",
            "Direction": direction,
            "Contracts": contracts,
            "Dollar PnL": round(dollar_pnl, 2),
            "Points PnL": round(points_pnl, 2),
            "News Day": news_day,
            "Discipline Grade": discipline_grade,
            "Behavioral Tags": tags_string,
            "Notes": notes,
            "Screenshot Path": saved_img_path
        }])
        
        new_data.to_csv(CSV_FILE, mode='a', header=False, index=False)
        st.success("Trade data successfully written to your computer disk! Check out the Performance or Review tabs now.")
        st.experimental_rerun()


# ==========================================================
# TAB 2: PERFORMANCE METRICS (Pure mathematical statistics)
# ==========================================================
with tab2:
    if not df.empty:
        st.subheader(f"{selected_user}'s Core Performance Statistics")
        
        # Calculate clean mathematical stats
        total_trades = len(df)
        winning_trades = df[df["Dollar PnL"] > 0]
        losing_trades = df[df["Dollar PnL"] < 0]
        
        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0
        avg_win = winning_trades["Dollar PnL"].mean() if not winning_trades.empty else 0.0
        avg_loss = losing_trades["Dollar PnL"].mean() if not losing_trades.empty else 0.0
        total_pnl = df["Dollar PnL"].sum()
        
        # Display simplified high-level metric rows without confusing arrows
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Win Rate", f"{win_rate:.1f}%")
        col2.metric("Avg Winning Session", f"${avg_win:,.2f}")
        col3.metric("Avg Losing Session", f"${avg_loss:,.2f}")
        
        # Display raw Net P&L separately and clearly, colored green/red
        pnl_color = "#2ECC71" if total_pnl >= 0 else "#E74C3C"
        st.markdown(
            f"### Net Cumulative PnL: <span style='color:{pnl_color}; font-weight:bold;'>${total_pnl:,.2f}</span>",
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        # --- SIMPLE BEHAVIORAL MISTAKE TALLY BOX ---
        st.subheader("📋 Behavioral Mistake Tracker")
        st.markdown("A pure mathematical tally of how many sessions each psychological roadblock was documented.")
        
        # Define base dictionary to aggregate counts
        mistake_tally = {
            "Overtrading": 0,
            "Impatience / No Confirmation": 0,
            "FOMO": 0,
            "Overconfidence": 0,
            "Failure to Recognize Bad Market Conditions": 0,
            "Random / Unbacktested Trade": 0
        }
        
        # Scan data to compute active counts
        for idx, row in df.iterrows():
            tags_str = str(row["Behavioral Tags"])
            for issue in mistake_tally.keys():
                if issue in tags_str:
                    mistake_tally[issue] += 1
        
        # Formulate a clean Pandas summary table out of the counts
        tally_df = pd.DataFrame(list(mistake_tally.items()), columns=["Trading Issue / Mistake", "Days Logged / Count"])
        
        # Display as a clean, high-contrast table
        st.table(tally_df)
        
        st.markdown("---")
        st.subheader("Historical Trade Ledger")

        def color_pnl(val):
            color = "#2ECC71" if val >= 0 else "#E74C3C"
            return f"color: {color}; font-weight: bold;"

        styled_df = (
            df.sort_values(by="Date", ascending=False)
            .drop(columns=["Trade ID", "Screenshot Path"])
            .style.applymap(color_pnl, subset=["Dollar PnL"])
        )

        st.dataframe(styled_df, use_container_width=True)
        
    else:
        st.info(f"{selected_user}'s performance charts will generate automatically once there's a first recorded trade entry in the Log Session tab.")


# ==========================================================
# TAB 3: CHART REVIEWER (Full screen screenshot inspection)
# ==========================================================
with tab3:
    if not df.empty:
        st.subheader(f"🔍 {selected_user}'s Deep-Dive Chart Reviewer")
        st.markdown("Select a past trading session from the selection box below to analyze your visual chart setup side-by-side with your mindset notes.")
        
        df_sorted = df.sort_values(by="Date", ascending=False)
        trade_options = []
        trade_id_map = {}
        
        for idx, row in df_sorted.iterrows():
            label = f"{row['Date'].strftime('%Y-%m-%d')} | {row['Setup Type']} ({row['Direction']}) | PnL: ${row['Dollar PnL']}"
            trade_options.append(label)
            trade_id_map[label] = row["Trade ID"]
            
        selected_label = st.selectbox("Choose a historical session to review:", options=trade_options)
        
        if selected_label:
            selected_id = trade_id_map[selected_label]
            trade_row = df[df["Trade ID"] == selected_id].iloc[0]
            
            st.markdown("---")
            rev_col1, rev_col2 = st.columns([1, 2])
            
            with rev_col1:
                st.markdown("### Session Context")
                st.markdown(f"**Strategy Setup Applied:** `{trade_row['Setup Type']}`")
                st.markdown(f"**Execution Vector:** {trade_row['Direction']} ({int(trade_row['Contracts'])} Contracts)")

                session_pnl = trade_row['Dollar PnL']
                session_color = "#2ECC71" if session_pnl >= 0 else "#E74C3C"
                st.markdown(
                    f"**Net Session Result:** <span style='color:{session_color}; font-weight:bold;'>${session_pnl}</span> ({trade_row['Points PnL']} NQ Points)",
                    unsafe_allow_html=True
                )

                st.markdown(f"**Macro News Morning:** {trade_row['News Day']}")
                st.markdown(f"**Discipline Score:** {trade_row['Discipline Grade']} / 5")
                st.error(f"**Identified Psychology Leaks:** {trade_row['Behavioral Tags']}")
                st.info(f"**Session Execution Notes:**\n\n{trade_row['Notes']}")
                
            with rev_col2:
                st.markdown("### Execution Screenshot")
                img_path = trade_row["Screenshot Path"]
                if img_path != "None" and os.path.exists(img_path):
                    st.image(img_path, caption=f"Chart setup snapshot logged for trade date: {trade_row['Date'].strftime('%Y-%m-%d')}", use_container_width=True)
                else:
                    st.warning("No visual screenshot file was attached to this historical trade entry upon logging.")
    else:
        st.info(f"{selected_user}'s review terminal will activate once there is data saved in this journal.")