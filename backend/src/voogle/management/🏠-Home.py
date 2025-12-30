# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import streamlit as st

from voogle import __version__
from voogle.management import utils

st.set_page_config(page_title="Voogle", page_icon="🎧")
st.title("🎧 Voogle Management Dashboard")
authenticated = utils.login_message(st.session_state)  # type: ignore[arg-type]

st.markdown(
    f"""**Management tools for Voogle deployments.**

- Voogle backend version: `{__version__}`

Select one menu option from the sidebar. You will need an **admin** user
to retrieve the info.

> ℹ️ If you are running Voogle from the first time, you can jump to the
>  [Tasks](./Tasks) page after you login with an admin user.

![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
 You will find more info in the [official repository](https://github.com/jbraseth/voogle)


"""
)
