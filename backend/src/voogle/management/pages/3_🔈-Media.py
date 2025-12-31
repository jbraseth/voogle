# Copyright (c) 2022-2024 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import asyncio

import streamlit as st

from voogle import collection, models, routers, settings, tasks
from voogle.collection import url_health
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
                if ch.image:
                    st.image(ch.image)
                st.markdown(ch.description)


async def url_health_section() -> None:
    st.header("URL Health")
    st.markdown(
        """Detect and fix broken episode media URLs.
        This helps recover episodes when podcast hosts change their CDN or file locations."""
    )

    # Metrics
    col1, _col2 = st.columns(2)
    total_episodes = await models.Episode.objects.count()
    col1.metric("Total Episodes", total_episodes)

    # Initialize session state for results
    if "broken_urls" not in st.session_state:
        st.session_state.broken_urls = None
    if "refresh_preview" not in st.session_state:
        st.session_state.refresh_preview = None

    # Section 1: Detect broken URLs
    st.subheader("1. Detect Broken URLs")
    st.info("This will check all episode URLs via HEAD requests. May take several minutes.")

    if st.button("Scan All Episode URLs", use_container_width=True):
        progress_bar = st.progress(0, text="Checking URLs...")

        def update_progress(checked: int, total: int) -> None:
            progress_bar.progress(checked / total, text=f"Checking URL {checked}/{total}...")

        with st.spinner("Checking URLs... This may take several minutes."):
            broken = await url_health.check_all_broken_urls(on_progress=update_progress)
            st.session_state.broken_urls = broken

        progress_bar.empty()

        if not broken:
            st.success("All episode URLs are accessible!")
        else:
            st.warning(f"Found {len(broken)} broken URLs")

    # Display broken URLs if we have results
    if st.session_state.broken_urls:
        broken = st.session_state.broken_urls
        st.markdown(f"**{len(broken)} broken URLs found:**")
        for result in broken:
            with st.expander(f"{result.episode_title}"):
                st.code(result.url)
                st.error(f"Status: {result.status.value} - {result.error_message}")

    st.divider()

    # Section 2: Preview URL refresh
    st.subheader("2. Preview URL Refresh")
    st.markdown("Select a channel to check for updated URLs in its RSS feed.")

    channels = await models.Channel.objects.filter(
        kind=models.ChannelKind.podcast.value
    ).all()

    if not channels:
        st.info("No podcast channels found. Add a channel first.")
    else:
        channel_options = {ch.title: ch for ch in channels}
        selected_channel_name = st.selectbox(
            "Select channel to preview",
            options=list(channel_options.keys()),
            key="preview_channel_select",
        )

        col1, _col2 = st.columns(2)
        with col1:
            broken_only = st.checkbox("Check broken URLs only", value=True)

        if st.button("Preview Changes", use_container_width=True):
            channel = channel_options[selected_channel_name]
            with st.spinner("Fetching RSS and comparing URLs..."):
                results = await url_health.preview_channel_refresh(
                    channel, broken_only=broken_only
                )
                st.session_state.refresh_preview = results

            if not results:
                st.success("No URL changes found")
            else:
                st.info(f"Found {len(results)} potential URL updates")

        # Display preview results
        if st.session_state.refresh_preview:
            results = st.session_state.refresh_preview
            for result in results:
                with st.expander(f"{result.episode_title}"):
                    st.markdown(f"**Old URL:** `{result.old_url}`")
                    st.markdown(f"**New URL:** `{result.new_url}`")
                    st.markdown(f"**Match method:** {result.match_method}")
                    if result.new_url_valid:
                        st.success("New URL is accessible")
                    else:
                        st.error(f"New URL not accessible: {result.error_message}")

    st.divider()

    # Section 3: Apply URL refresh
    st.subheader("3. Apply URL Refresh")
    st.warning("This will update episode URLs in the database. Preview first!")

    if channels:
        selected_apply_channel_name = st.selectbox(
            "Select channel to refresh",
            options=list(channel_options.keys()),
            key="apply_channel_select",
        )

        if st.button("Apply Refresh for Selected Channel", use_container_width=True):
            channel = channel_options[selected_apply_channel_name]
            with st.spinner("Applying URL refreshes..."):
                results = await url_health.refresh_broken_urls(channel, dry_run=False)

            applied = [r for r in results if r.new_url and r.new_url_valid]
            failed = [r for r in results if r.error_message and not r.new_url_valid]

            if applied:
                st.success(f"Updated {len(applied)} episode URLs")
                for r in applied:
                    st.markdown(f"- **{r.episode_title}**: URL updated")

            if failed:
                st.error(f"Failed to update {len(failed)} episodes")
                for r in failed:
                    st.markdown(f"- **{r.episode_title}**: {r.error_message}")

            if not applied and not failed:
                st.info("No URLs needed updating")

            # Clear preview cache after applying
            st.session_state.refresh_preview = None


async def main() -> None:
    st.set_page_config(page_title="Voogle", page_icon="🎧")
    st.title("📻 Media")
    if m_utils.login_message(st.session_state):  # type: ignore[arg-type]
        await add_channel()
        st.divider()
        await add_local_channel()
        st.divider()
        await podcasts_and_episodes()
        st.divider()
        await url_health_section()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
