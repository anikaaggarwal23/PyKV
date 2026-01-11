import streamlit as st
import requests
import time
import os

BASE_URL = "http://127.0.0.1:8000"
ADMIN_PASSWORD = "admin123"

st.set_page_config(
    page_title="PyKV Admin Dashboard",
    layout="wide"
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <style>
            body { background-color: #f4f2ff; }
            .login-box {
                background-color: white;
                padding: 40px;
                border-radius: 14px;
                box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            }
            .title {
                font-size: 32px;
                font-weight: 600;
                color: #6a5acd;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #777;
                margin-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<div class='title'>PyKV Admin Login</div>", unsafe_allow_html=True)

        password = st.text_input("Admin Password", type="password")

        if st.button("Login", use_container_width=True):
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

st.markdown("""
<style>
.section {
    background-color: #fafaff;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("PyKV Admin Dashboard")

st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("System Status")

c1, c2, c3, c4 = st.columns(4)

try:
    server_up = requests.get(f"{BASE_URL}/health", timeout=2).status_code == 200
except:
    server_up = False

with c1:
    st.metric("Server", "Online" if server_up else "Offline")

with c2:
    try:
        keys = requests.get(f"{BASE_URL}/keys").json()["keys"]
        st.metric("Total Keys", len(keys))
    except:
        st.metric("Total Keys", 0)

with c3:
    st.metric("Cache Policy", "LRU")

with c4:
    st.metric("Persistence", "Log-Structured")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("Key-Value Operations")

k1, k2 = st.columns(2)
with k1:
    key = st.text_input("Key", placeholder="user:1001")
with k2:
    value = st.text_input("Value", placeholder="session_data")

b1, b2, b3, b4 = st.columns(4)

if b1.button("SET", use_container_width=True):
    if key and value:
        requests.post(f"{BASE_URL}/set", json={"key": key, "value": value})
        st.success("Key stored successfully")

if b2.button("GET", use_container_width=True):
    res = requests.get(f"{BASE_URL}/get/{key}")
    st.json(res.json() if res.status_code == 200 else {"error": "Key not found"})

if b3.button("DELETE", use_container_width=True):
    requests.delete(f"{BASE_URL}/delete/{key}")
    st.warning("Key deleted")

if b4.button("LIST KEYS", use_container_width=True):
    st.json(requests.get(f"{BASE_URL}/keys").json())

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("Performance Benchmark")

operations = st.slider(
    "Number of SET operations",
    min_value=500,
    max_value=5000,
    value=1000,
    step=500
)

if st.button("Run Benchmark", use_container_width=True):
    timings = []

    for _ in range(5):
        start = time.time()
        for i in range(operations // 5):
            requests.post(
                f"{BASE_URL}/set",
                json={"key": f"bench_{time.time()}", "value": "x"}
            )
        timings.append(time.time() - start)

    st.line_chart(timings)
    st.success("Benchmark completed successfully")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("Replication Logs")

primary_log = "data/pykv.log"
replica_log = "data/replica.log"

r1, r2 = st.columns(2)

with r1:
    st.metric(
        "Primary Log Size (bytes)",
        os.path.getsize(primary_log) if os.path.exists(primary_log) else 0
    )

with r2:
    st.metric(
        "Replica Log Size (bytes)",
        os.path.getsize(replica_log) if os.path.exists(replica_log) else 0
    )

st.markdown("</div>", unsafe_allow_html=True)

st.caption("PyKV - Scalable In-Memory Key-Value Store with Persistence")
