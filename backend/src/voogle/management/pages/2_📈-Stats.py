# Copyright (c) 2022-2023 Pablo González Carrizo (unmonoqueteclea)
# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

import asyncio

import pandas as pd
import streamlit as st
from voogle.management import utils
from voogle.models import analytics


async def main():
    st.set_page_config(page_title="Voogle", page_icon="🎧")
    st.title("📈 Stats")
    if utils.login_message(st.session_state):
        tab_last, tab_graphs = st.tabs(["Last queries", "Queries per day"])
        with tab_last:
            st.write("Last 20 queries performed by Voogle users")
            qs = await analytics.Query.objects.order_by("-created_at").limit(20).all()
            markdown_queries = ""
            for query in qs:
                # created_at is a datetime object from the model
                created_at = query.created_at
                if created_at:
                    date = created_at.strftime("%Y-%m-%d, %H:%M:%S")  # type: ignore[attr-defined]
                    markdown_queries += f"\n - `{date}` {query.text}"
            if len(qs) == 0:
                st.write("⚠️ No queries yet!")
            st.markdown(markdown_queries)
        with tab_graphs:
            qs = await analytics.Query.objects.order_by("-created_at").values(
                fields=["created_at", "text"]
            )
            df = pd.DataFrame(qs)
            if df.shape[0] == 0:
                st.write("⚠️ No queries yet!")
            else:
                df["created_at"] = pd.to_datetime(df["created_at"]).dt.date
                st.bar_chart(data=df.created_at.value_counts())
        refresh = st.button("Refresh", use_container_width=True)
        if refresh:
            st.rerun()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
