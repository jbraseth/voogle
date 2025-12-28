# Copyright (c) 2022-2024 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import asyncio

import streamlit as st

from voogle import collection, models, routers, settings, tasks
from voogle.management import utils as m_utils


async def add_channel() -> None:
    st.header("Add new podcast")
    with st.form("my_form"):
        st.markdown(
            """Write below the RSS feed url from a podcast and click `ADD`
            to include it in the database. """
        )
        channel_url = st.text_input("Channel RSS feed url")
        if st.form_submit_button("Add channel", use_container_width=True):
            with st.spinner("⌛ Adding new channel... Please, wait."):
                _, ch = await collection.get_or_create_channel(channel_url)
                if ch:
                    settings.queue.enqueue(
                        collection.update_channel, ch, job_timeout="600m"
                    )
                    st.success(
                        f"""Channel "{ch.title}" correctly added to
                        the database.  Its episodes are being updated
                        in a background task. This process can take a
                        few minutes."""
                    )


async def add_local_channel() -> None:
    st.header("Add local channel")
    st.markdown(
        """For each local channel you want to include, create a folder within
   Voogle's `data/local/` folder and put there all the audio files
   (`mp3` or `wav`) you want to be indexed.


   Then, fill the following information for each channel."""
    )
    with st.form("local_channel_form_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("✏️ Channel name(*)")
        with col2:
            folder = st.text_input("📁 Local folder name(*)")
        description = st.text_input("✏️ Channel description")
        with col1:
            image = st.text_input("🔗 URL of channel image(*)")
        with col2:
            language = st.selectbox("🗺️ Episodes language (*)", ("es", "en"))
        data = {
            "name": name,
            "description": description,
            "folder": folder,
            "image": image,
            "language": language,
        }
        if st.form_submit_button("Add local channel", use_container_width=True):
            error = False
            for k in ["name", "folder", "image", "language"]:
                if data[k] is None or data[k] == "":
                    st.error(f"Missing field **{k}**")
                    error = True
            if not error:
                await collection.get_or_create_local_channel(data)
                settings.queue.enqueue(tasks.update_channels, job_timeout="1h")
                st.success(f"Channel **{data['name']}** created correctly")
                st.success("Episodes are being updated in a background task...")


async def podcasts_and_episodes() -> None:
    st.header("Podcasts and episodes")

    col1, col2, col3 = st.columns(3)
    col1.metric("Channels", await models.Channel.objects.count())
    col2.metric(
        "Transcribed episodes",
        await models.Episode.objects.filter(transcribed=True).count(),
    )
    col3.metric(
        "Indexed episodes",
        await models.Episode.objects.filter(embeddings=True).count(),
    )
    with st.spinner("⌛ Loading channels..."):
        for ch in (await routers.analytics._media()).channels:
            title = ch.title
            if ch.kind == models.ChannelKind.local.value:
                title = f"📁 **{title}**"
            with st.expander(
                f"{title}. Indexed {ch.available_episodes}/{ch.total_episodes}"
            ):
                st.image(ch.image)
                st.markdown(ch.description)


async def main() -> None:
    st.set_page_config(page_title="Voogle", page_icon="🎧")
    st.title("📻 Media")
    if m_utils.login_message(st.session_state):
        await add_channel()
        st.divider()
        await add_local_channel()
        st.divider()
        await podcasts_and_episodes()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
