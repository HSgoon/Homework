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

Hasher.hash_passwords(config['credentials'])
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
)

# authenticator = stauth.Authenticate(
#     'config.yaml'
# )

try:
    authenticator.login()
except LoginError as e:
    st.error(e)


def reset_password():
    if st.session_state['authentication_status']:
        try:
            if authenticator.reset_password(st.session_state['username']):
                st.success('비밀번호 변경이 완료되었습니다.')
        except (CredentialsError, ResetError) as e:
            st.error(e)


def signup():
    try:
        (email_of_registered_user,
            username_of_registered_user,
            name_of_registered_user) = authenticator.register_user()
        if email_of_registered_user:
            st.success(
                #축하그림
                'MANGO의 멤버가 되신걸 환영합니다!'
            )
    except RegisterError as e:
        st.error(e)

def forget_password():
    try:
        (username_of_forgotten_password,
            email_of_forgotten_password,
            new_random_password) = authenticator.forgot_password()
        if username_of_forgotten_password:
            st.success('새로운 비밀번호가 생성되었습니다.')
            # Random password to be transferred to the user securely
        elif not username_of_forgotten_password:
            st.error('Username을 찾을 수 없습니다.')
    except ForgotError as e:
        st.error(e)

def forget_username():
    try:
        (username_of_forgotten_username,
            email_of_forgotten_username) = authenticator.forgot_username()
        if username_of_forgotten_username:
            st.success('Username sent securely')
            # Username to be transferred to the user securely
        elif not username_of_forgotten_username:
            st.error('이메일을 찾지 못했습니다.')
    except ForgotError as e:
        st.error(e)

#업데이트
if st.session_state['authentication_status']:
    try:
        if authenticator.update_user_details(st.session_state['username']):
            st.success('업데이트 완료')
    except UpdateError as e:
        st.error(e)

# Saving config file
with open('../config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)

def main():
    #https://as1.ftcdn.net/v2/jpg/00/87/97/06/1000_F_87970620_Tdgw6WYdWnrZHn2uQwJpVDH4vr4PINSc.jpg
    st.title("메인페이지")
    st.write("Main Page")
    try:
        authenticator.login()
    except LoginError as e:
        st.error(e)

def not_logged_in():
    def empty_page():
        pass

    pg = st.navigation([st.Page(empty_page)])
    pg.run()
    st.stop()

pages ={
    "Features": [
        st.Page(
            main,
            title="Home",
            icon="🏠",
        ),
        st.Page(
            "pages/sample.py",
            title="샘플",
            icon="🗒",
        ),
        st.Page(
            "pages/profile.py",
            title="프로필필",
            icon="🗒",
        ),
    ],
    "Accounts": [
        st.Page(
            signup,
            title="Signup",
            icon="🏠",
        ),
            st.Page(
            forget_username,
            title="FU",
            icon="🏠",
        ),
            st.Page(
            forget_password,
            title="FP",
            icon="🏠",
        ),
    ],
}


# Authenticating user
if st.session_state['authentication_status']:
    authenticator.logout()
    st.write(f'안녕하세요 *{st.session_state["name"]}*님!')
    st.title('Some content')
    page = st.navigation(pages)
    page.run()

elif st.session_state['authentication_status'] is False:
    st.error('아이디 혹은 비밀번호가 잘못되었습니다.')
    not_logged_in()

elif st.session_state['authentication_status'] is None:
    st.warning('아이디 혹은 비밀번호를 기입해주세요.')
    not_logged_in()


# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# def login():
#     try:
#         email_of_registered_user, \
#         username_of_registered_user, \
#         name_of_registered_user = authenticator.register_user(pre_authorized=config['pre-authorized']['emails'])
#         if email_of_registered_user:
#             st.success('User registered successfully')
#     except Exception as e:
#         st.error(e)

# def signup():
#     if st.button("Sign up"):
#         st.rerun()

# def logout():
#     if st.button("Log out"):
#         st.session_state.logged_in = False
#         st.rerun()

# def main():
#     #https://as1.ftcdn.net/v2/jpg/00/87/97/06/1000_F_87970620_Tdgw6WYdWnrZHn2uQwJpVDH4vr4PINSc.jpg
#     login()
#     st.title("메인페이지")
#     st.write("Main Page")

# login_page = st.Page(login, title="Log in", icon=":material/login:")
# logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
# signup_page = st.Page(signup, title="Sign up")

# main_page = st.Page(main, title="Main")
# profile = st.Page("pages/profile.py", title="Profile", icon=":material/bug_report:")
# chatbot = st.Page("pages/chatbot.py", title="Chatbot", icon=":material/dashboard:", default=True)
# sample = st.Page("pages/sample.py", title="Sample", icon=":material/notification_important:")

# # search = st.Page("tools/search.py", title="Search", icon=":material/search:")
# # history = st.Page("tools/history.py", title="History", icon=":material/history:")

# if st.session_state.logged_in:
#     pg = st.navigation(
#         {
#             "Features": [main_page, profile, chatbot, sample],
#             "Account": [signup_page, logout_page],
#             #"Tools": [search, history],
#         }
#     )
# else:
#     pg = st.navigation([main_page])

# pg.run()