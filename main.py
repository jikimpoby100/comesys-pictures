import streamlit as st
import requests
import base64
from datetime import datetime

# GitHub secrets 불러오기
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_BRANCH = st.secrets["GITHUB_BRANCH"]
GITHUB_PATH = st.secrets["GITHUB_PATH"]

def upload_to_github(file_name, file_content):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{file_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "message": f"Add {file_name}",
        "content": base64.b64encode(file_content).decode('utf-8'),
        "branch": GITHUB_BRANCH
    }

    response = requests.put(url, headers=headers, json=data)
    return response

def handle_upload(file, index=0):
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{now}_{index}.jpg"
    file_content = file.read()

    result = upload_to_github(filename, file_content)

    if result.status_code == 201:
        st.success(f"✅ {filename} 업로드 성공")
        github_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_PATH}/{filename}"
        st.image(github_url, caption=filename, use_column_width=True)
        st.markdown(f"[🔗 GitHub 이미지 링크]({github_url})")
    else:
        st.error(f"❌ {filename} 업로드 실패")
        st.write("Status Code:", result.status_code)
        st.write("Response:", result.text)

def main():
    st.title("📷 이미지 업로드 & GitHub Push")

    tab1, tab2 = st.tabs(["📤 한 장씩 업로드", "📤 여러 장 한 번에 업로드"])

    with tab1:
        uploaded_file = st.file_uploader("이미지를 선택하세요", type=["jpg", "jpeg", "png"], key="single")
        if uploaded_file is not None:
            if st.button("🆙 GitHub에 업로드하기"):
                handle_upload(uploaded_file, index=0)

    with tab2:
        uploaded_files = st.file_uploader("여러 이미지를 선택하세요", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="multiple")
        if uploaded_files:
            if st.button("🆙 전체 업로드"):
                for idx, file in enumerate(uploaded_files):
                    handle_upload(file, index=idx)

if __name__ == "__main__":
    main()
