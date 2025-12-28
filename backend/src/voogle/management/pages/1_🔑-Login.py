# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import asyncio
import typing
from datetime import timedelta

import streamlit as st
from voogle import auth

st.set_page_config(page_title="Voogle", page_icon="🎧")
st.title("🔑 Login")

SHOW_LOGIN_FORM = True
USERNAME_KEY = "logged_user_username"
TOKEN_KEY = "logged_user_token"


async def _login(username: str, password: str) -> typing.Optional[str]:
    if user := await auth.authenticate_user(username, password):
        delta = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        return auth.create_access_token(
            data={"sub": user.username}, expires_delta=delta
        )


async def main():
    global SHOW_LOGIN_FORM
    if USERNAME_KEY in st.session_state and TOKEN_KEY in st.session_state:
        SHOW_LOGIN_FORM = False
    if SHOW_LOGIN_FORM:
        with st.form(key="login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            clicked = st.form_submit_button("Login", use_container_width=True)
        if clicked:
            if token := await _login(username, password):
                st.session_state[USERNAME_KEY] = username
                st.session_state[TOKEN_KEY] = token
                SHOW_LOGIN_FORM = False
                st.rerun()
            else:
                st.error("Invalid credentials. Please, try again")
    else:
        username = st.session_state[USERNAME_KEY]
        st.info(f"""👤  Already logged in as **{username}**""")
        logout = st.button("Logout", use_container_width=True)
        if logout:
            del st.session_state[USERNAME_KEY]
            del st.session_state[TOKEN_KEY]
            SHOW_LOGIN_FORM = True
            st.rerun()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
