import streamlit as st
from db import insert_item, get_all_items, delete_item, get_monthly_recap, get_target_bulan_ini, set_target_bulan_ini, register_user, authenticate_user
from sambanova_llm import extract_item, extract_delete_item
import plotly.graph_objects as go
from datetime import datetime
import pytz

def get_jakarta_now():
    return datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Jakarta'))

st.title("Spending Tracker AI Bot")

def login_form():
    st.session_state["login_error"] = False
    st.session_state["register_error"] = False
    st.write(":lock: Login untuk akses data")
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass", on_change=None)
        def submit_login():
            if authenticate_user(username, password):
                st.session_state["logged_in"] = True
                st.session_state["user"] = username
            else:
                st.session_state["login_error"] = True
        if st.button("Login") or (password and st.session_state.get("login_pass") and st.session_state.get("login_user")):
            submit_login()
        if st.session_state.get("login_error"):
            st.error("Username/password salah!")

    with tab_register:
        new_username = st.text_input("Username baru", key="register_user")
        new_password = st.text_input("Password baru", type="password", key="register_pass", on_change=None)
        def submit_register():
            if register_user(new_username, new_password):
                st.success("Registrasi berhasil! Silakan login.")
            else:
                st.session_state["register_error"] = True
        if st.button("Register") or (new_password and st.session_state.get("register_user") and st.session_state.get("register_pass")):
            submit_register()
        if st.session_state.get("register_error"):
            st.error("Username sudah digunakan.")

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

# === FITUR TARGET BULANAN ===
# (Fitur target bulanan di-nonaktifkan sementara)
# now = get_jakarta_now()
# bulan_ini = now.month
# tahun_ini = now.year
# bulan_ini_recap = next((rec for rec in monthly_recap if rec['_id']['year']==tahun_ini and rec['_id']['month']==bulan_ini), None)
# total_bulan_ini = bulan_ini_recap['total'] if bulan_ini_recap else 0

# def_target = 2000000  # default 2 juta
# # Ambil target dari database
# init_target = get_target_bulan_ini(user, tahun_ini, bulan_ini)
# if init_target is None:
#     init_target = def_target

# st.subheader('Target/Budget Pengeluaran Bulan Ini')
# target = st.number_input('Masukkan target pengeluaran bulan ini (Rp)', min_value=0, value=init_target, step=100000, format='%d', key='target_bulan_ini_input')
# # Simpan ke database jika berubah
# if target != init_target:
#     set_target_bulan_ini(user, tahun_ini, bulan_ini, target)

# progress = min(total_bulan_ini/target, 1.0) if target > 0 else 0
# st.progress(progress, text=f"{total_bulan_ini:,} / {target:,}")
# if target > 0:
#     if total_bulan_ini >= target:
#         st.error('Pengeluaran bulan ini sudah melebihi target!')
#     elif total_bulan_ini >= 0.8*target:
#         st.warning('Pengeluaran bulan ini sudah >80% dari target!')

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

st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
