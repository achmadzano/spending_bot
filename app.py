import streamlit as st
from sambanova_llm import extract_item
from db import insert_item, get_all_items
import plotly.graph_objects as go

st.title("Spending Tracker AI Bot")

with st.sidebar:
    user = st.radio("Pilih user:", ["zano", "juditemi"], horizontal=True)
    st.write(f"Mode: User {user}")

def handle_submit():
    user_input = st.session_state.get("input_pengeluaran", "")
    if user_input:
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

col1, col2 = st.columns([8, 1])
with col1:
    st.text_input(
        "Masukkan pengeluaran (misal: terea 30ribu)",
        key="input_pengeluaran",
        placeholder="Contoh: terea 30ribu",
        label_visibility="collapsed",
        on_change=handle_submit
    )
with col2:
    if st.button("Kirim", use_container_width=True):
        st.session_state["trigger_submit"] = True

items = get_all_items(user)

if items:
    st.subheader("Daftar Pengeluaran")
    st.table(items)
    # Grafik batang pengeluaran
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[item['nama'] for item in items],
        y=[int(item['harga'].replace('.', '')) for item in items],
        marker_color='indianred',
        name='Pengeluaran'
    ))
    fig.update_layout(title="Grafik Pengeluaran", xaxis_title="Barang", yaxis_title="Harga (Rp)", height=400)
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
    # Tampilkan dua grafik berdampingan
    col_bar, col_pie = st.columns(2)
    with col_bar:
        st.plotly_chart(fig, use_container_width=True)
    with col_pie:
        st.plotly_chart(pie_fig, use_container_width=True)
    total = sum(int(i['harga'].replace('.', '').replace('ribu','000').replace(' ','').replace('Rp','')) for i in items)
    st.write(f"Total: Rp{total:,}")
    max_item = max(items, key=lambda x: int(x['harga'].replace('.', '').replace('ribu','000').replace(' ','').replace('Rp','')))
    min_item = min(items, key=lambda x: int(x['harga'].replace('.', '').replace('ribu','000').replace(' ','').replace('Rp','')))
    st.write(f"Termahal: {max_item['nama']} ({max_item['harga']})")
    st.write(f"Termurah: {min_item['nama']} ({min_item['harga']})")
else:
    st.info("Belum ada data pengeluaran.")
