import streamlit as st
from db import insert_item, get_all_items, delete_item, get_monthly_recap
from sambanova_llm import extract_item, extract_delete_item
import plotly.graph_objects as go

st.title("Spending Tracker AI Bot")

# Simple user-password mapping (sebaiknya simpan di env/secret untuk produksi)
USER_PASSWORDS = {
    "zano": "temi",
    "juditemi": "dudul"
}

def login_form():
    st.session_state["login_error"] = False
    st.write(":lock: Login untuk akses data")
    username = st.selectbox("User", ["zano", "juditemi"], key="login_user")
    def submit_login():
        password = st.session_state.get("login_pass", "")
        if USER_PASSWORDS.get(username) == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
        else:
            st.session_state["login_error"] = True
    st.text_input("Password", type="password", key="login_pass", on_change=submit_login)
    if st.button("Login", key="login_btn"):
        submit_login()
    if st.session_state.get("login_error"):
        st.error("Username/password salah!")

# Cek login
if not st.session_state.get("logged_in"):
    login_form()
    st.stop()
user = st.session_state["user"]

def handle_submit():
    user_input = st.session_state.get("input_pengeluaran", "")
    if user_input:
        if user_input.lower().startswith("hapus"):
            item = extract_delete_item(user_input)
            if item:
                delete_item(item, user)
                st.success(f"Dihapus: {item}")
            else:
                st.error("Gagal ekstrak data dari perintah hapus.")
        else:
            item = extract_item(user_input)
            if item:
                insert_item(item, user)
                st.success(f"Tersimpan: {item}")
            else:
                st.error("Gagal ekstrak data dari input.")
        st.session_state["input_pengeluaran"] = ""

# Trigger submit jika tombol Kirim ditekan
if st.session_state.get("trigger_submit", False):
    handle_submit()
    st.session_state["trigger_submit"] = False

col1, _ = st.columns([1, 0.01])
with col1:
    st.text_input(
        "Masukkan pengeluaran (misal: terea 30ribu)",
        key="input_pengeluaran",
        placeholder="Contoh: terea 30ribu",
        label_visibility="collapsed",
        on_change=handle_submit
    )

items = get_all_items(user)

# Tampilkan recap bulanan
monthly_recap = get_monthly_recap(user)
if monthly_recap:
    st.subheader('Rekap Pengeluaran per Bulan')
    recap_data = []
    for rec in monthly_recap:
        year = rec['_id']['year']
        month = rec['_id']['month']
        total = rec['total']
        recap_data.append({
            'Bulan': f"{month:02d}-{year}",
            'Total': f"Rp{total:,}"
        })
    st.table(recap_data)

if items:
    st.subheader("Daftar Pengeluaran")
    st.table(items)
    # Pie chart setengah lingkaran
    pie_fig = go.Figure(go.Pie(
        labels=[item['nama'] for item in items],
        values=[int(item['harga'].replace('.', '')) for item in items],
        hole=0.5,
        direction='clockwise',
        sort=False,
        showlegend=True
    ))
    pie_fig.update_traces(textinfo='label+percent', pull=[0.05]*len(items), rotation=180)
    pie_fig.update_layout(title="Proporsi Pengeluaran", height=400, margin=dict(t=60, b=0),
                         legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    st.plotly_chart(pie_fig, use_container_width=True)
    total = sum(int(i['harga'].replace('.', '').replace('ribu','000').replace(' ','').replace('Rp','')) for i in items)
    st.write(f"Total: Rp{total:,}")
    max_item = max(items, key=lambda x: int(x['harga'].replace('.', '').replace('ribu','000').replace(' ','').replace('Rp','')))
    min_item = min(items, key=lambda x: int(x['harga'].replace('.', '').replace('ribu','000').replace(' ','').replace('Rp','')))
    st.write(f"Termahal: {max_item['nama']} ({max_item['harga']})")
    st.write(f"Termurah: {min_item['nama']} ({min_item['harga']})")
else:
    st.info("Belum ada data pengeluaran.")
