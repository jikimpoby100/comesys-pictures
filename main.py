import streamlit as st
import requests
import base64
from datetime import datetime

# GitHub secrets
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
        st.image(github_url, caption=filename, use_container_width=True)
        st.markdown(f"[🔗 GitHub 이미지 링크]({github_url})")
    else:
        st.error(f"❌ {filename} 업로드 실패")
        st.write("Status Code:", result.status_code)
        st.write("Response:", result.text)

def fetch_github_image_list():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}?ref={GITHUB_BRANCH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        files = response.json()
        images = [f for f in files if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))]
        return images
    else:
        st.error("❌ 이미지가 없습니다.")
        return []

def upload_description(filename_base, description_text):
    desc_filename = f"{filename_base}.txt"
    desc_content = description_text.encode("utf-8")
    return upload_to_github(desc_filename, desc_content)

def main():
    st.title("📷 이미지 자동 업로드 & 이미지 보기")

    tab1, tab2, tab3 = st.tabs(["📤 한 장 업로드 (자동)", "📤 여러 장 업로드 (자동)", "📁 업로드된 이미지 보기"])

    with tab1:
        uploaded_file = st.file_uploader("이미지를 선택하세요", type=["jpg", "jpeg", "png"], key="single_auto")
        description = st.text_input("이미지 설명을 입력하세요", key="desc1")
        if uploaded_file is not None:
            index = 0
            now = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"{now}_{index}"
            handle_upload(uploaded_file, index=0)
            upload_description(base_filename, description)

    with tab2:
        uploaded_files = st.file_uploader("여러 이미지를 선택하세요", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="multi_auto")
        if uploaded_files:
            for idx, file in enumerate(uploaded_files):
                base_filename = datetime.now().strftime('%Y%m%d_%H%M%S') + f"_{idx}"
                description = st.text_input(f"설명 입력 ({file.name})", key=f"desc_multi_{idx}")
                handle_upload(file, index=idx)
                upload_description(base_filename, description)

    with tab3:
        st.subheader("📁 현재 GitHub에 저장된 이미지 목록")
        images = fetch_github_image_list()
        if images:
            for img in images:
                img_name = img["name"]
                if img_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    base_name = img_name.rsplit(".", 1)[0]
                    github_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_PATH}/{img_name}"
                    desc_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_PATH}/{base_name}.txt"
                    st.image(github_url, caption=img_name, use_container_width=True)
                    try:
                        desc_response = requests.get(desc_url)
                        if desc_response.status_code == 200:
                            st.markdown(f"📄 설명: {desc_response.text}")
                    except:
                        pass
                    st.markdown(f"[🔗 {img_name}]({github_url})", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
