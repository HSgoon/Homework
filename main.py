import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                            ForgotError,
                                            Hasher,
                                            LoginError,
                                            RegisterError,
                                            ResetError,
                                            UpdateError)

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# authenticator = stauth.Authenticate(
#     '../config.yaml'
# )


# # 초기상태 설정
# if "current_page" not in st.session_state:
#     st.session_state["current_page"] = "Home"

# # 사이드바 버튼
# with st.sidebar:
#     if st.button("홈"):
#         st.session_state["current_page"] = "Home"

#     if st.button("로그인"):
#         st.session_state["current_page"] = "Login"

#     if st.button("회원가입"):
#         st.session_state["current_page"] = "Register"

# Authenticating user
if st.session_state['authentication_status']:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["nickname"]}*')
    st.title('Some content')
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')

# 상태 초기화시에도 회원가입 데이터 input값 유지
if "register_mode" not in st.session_state:
    st.session_state["register_mode"] = False

if "registration_data" not in st.session_state:
    st.session_state["registration_data"] = {
        "username": "아이디",
        "password": "",
        "repeat_password": "",
        "nickname": "닉네임",
        "gender": "밝히지않음",
        "age": 0,
    }

#### 페이지별 렌더링
if st.session_state["current_page"] == "Home": #### 홈페이지 구성
    st.title("Welcome to Our Website")
    st.image(
        "https://via.placeholder.com/1000x500.png?text=Welcome",
        use_column_width=True,
    )
    st.markdown(
        """
        ## 안녕하세요 [data{'nickname'}]님!
        """
    )


##회원가입버튼
if st.sidebar.button("회원가입"):
    st.session_state["register_user"] = True

#회원가입 화면표시
if st.session_state["register_user"]:
    st.title("회원가입")
    try:
        # 사용자 입력 상태 관리
        st.session_state["registration_data"]["username"] = st.text_input(
            "Username", value=st.session_state["registration_data"]["username"]
        )
        st.session_state["registration_data"]["password"] = st.text_input(
            "Password", type="password", value=st.session_state["registration_data"]["password"]
        )
        st.session_state["registration_data"]["repeat_password"] = st.text_input(
            "Repeat Password", type="password", value=st.session_state["registration_data"]["repeat_password"]
        )
        st.session_state["registration_data"]["nickname"] = st.text_input(
            "Nickname", value=st.session_state["registration_data"]["nickname"]
        )
        st.session_state["registration_data"]["gender"] = st.selectbox(
            "Gender", ["남성", "여성", "밝히지않음"],
            index=0 if st.session_state["registration_data"]["gender"] == "" else ["남성", "여성", "밝히지않음"].index(st.session_state["registration_data"]["gender"]),
        )
        st.session_state["registration_data"]["age"] = st.number_input(
            "Age", min_value=0, step=1, value=st.session_state["registration_data"]["age"]
        )

        if st.button("제출하기"):
            data = st.session_state["registration_data"]
            if (
                data["username"]
                and data["password"]
                and data["repeat_password"]
                and data["nickname"]
                and data["gender"]
                and data["age"]
            ):
                if data["password"] != data["repeat_password"]:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif len(data["password"]) < 6:
                    st.error("비밀번호는 최소 6자 이상으로 설정해주세요.")
                elif data["username"] in config["credentials"]["usernames"]:
                    st.error("이미 존재하는 아이디입니다.")
                else:
                    # 비밀번호 암호화 및 등록
                    hashed_password = stauth.Hasher([data["password"]]).generate()[0]
                    config["credentials"]["usernames"][data["username"]] = {
                        "password": hashed_password,
                        "nickname": data["nickname"],
                        "gender": data["gender"],
                        "age": data["age"],
                    }

                    with open("config.yaml", "w") as file:
                        yaml.dump(config, file, default_flow_style=False)

                    st.success(f"Successfully registered, {data['nickname']}!")
                    st.balloons()
                    st.session_state["register_mode"] = False
            else:
                st.warning("모든 빈칸을 채워주세요.")
    except Exception as e:
        st.error(e)

if st.sidebar.button("로그인"):  # 로그인 버튼
    st.title("로그인")  # 페이지 제목
    try:
        # 로그인 위젯 표시
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
        name, authentication_status, username = authenticator.login("Login", "main")
        if authentication_status:
            st.success(f"반갑습니다. {data['nickname']}님님!")
        elif authentication_status is False:
            st.error("아이디 혹은 비밀번호가 잘못되었습니다.")
        elif authentication_status is None:
            st.warning("아이디나 비밀번호를 입력해주세요.")
    except LoginError as e:
        st.error(e)
elif st.session_state['authentication_status']: #비밀번호 리셋 #로그인 시에만 나옵니다.
    if st.sidebar.button("비밀번호 리셋"):
        st.title("비밀번호 리셋")
        try:
            if authenticator.reset_password(st.session_state['username']):
                st.success("비밀번호가 성공적으로 리셋되었습니다.")
                st.balloons()  # 성공 시 풍선 효과
        except (CredentialsError, ResetError) as e:
            st.error(e)
elif st.session_state['authentication_status']: #비밀번호를 잃어버렸을때
    if st.sidebar.button("비밀번호 분실"):
        st.title("비밀번호 분실")
        try:
            (username_of_forgotten_password,
                new_random_password) = authenticator.forgot_password()
            if username_of_forgotten_password:
                st.success('새로운 비밀번호가 생성되었습니다.')
            elif not username_of_forgotten_password:
                st.error('아이디를 찾을 수 없습니다.')
        except ForgotError as e:
            st.error(e)


# Creating an update user details widget
if st.session_state['authentication_status']:
    try:
        if authenticator.update_user_details(st.session_state['username']):
            st.success('Entry updated successfully')
    except UpdateError as e:
        st.error(e)

#chatbot

# Saving config file
with open('config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)
