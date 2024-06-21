import streamlit as st
from fuzzywuzzy import process
from os import listdir
import logging
from uuid import uuid4

logging.basicConfig(level=logging.DEBUG)


# Constants
media_path = "./media/"
search_limit = 8
score_cutoff = 50

# Global Variables
if "current_song" not in st.session_state:
    st.session_state["current_song"] = ""
if "song_queue" not in st.session_state:
    st.session_state["song_queue"] = []


# Helper Functions
def get_matched_songs(pattern: str, path: str) -> list[str]:
    logging.info("get_matched_songs() called")
    song_list = listdir(path)
    fuzzy_matches = process.extractBests(
        pattern, song_list, limit=search_limit, score_cutoff=score_cutoff
    )
    logging.debug(fuzzy_matches)
    matched_songs = [x[0] for x in fuzzy_matches]
    logging.debug(matched_songs)

    return matched_songs


def get_song_title(filename: str) -> str:
    return filename[: filename.index("[")]


def create_video(filename: str):
    path = f"{media_path}/{filename}"
    st.video(path, autoplay=True)


def next_song():
    if st.session_state["song_queue"]:
        st.session_state["current_song"] = st.session_state["song_queue"].pop(0)
    else:
        st.session_state["current_song"] = ""


def add_song_to_queue(filename: str):
    logging.info(f"Adding song with the following filename to queue: {filename}")
    st.session_state["song_queue"].append(filename)
    logging.info(st.session_state["song_queue"])


def display_song(filename: str):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(get_song_title(filename))
    with col2:
        st.button(
            "RES",
            key=f"reserve-{filename}-{uuid4()}",
            type="primary",
            on_click=add_song_to_queue,
            args=(filename,),
        )


# Main Content
with st.container() as main:
    if st.session_state["current_song"] == "" and st.session_state["song_queue"]:
        next_song()

    if st.session_state["current_song"]:
        create_video(st.session_state["current_song"])
        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(f'## {get_song_title(st.session_state["current_song"])}')

        with col2:
            st.text("\n\n\n")
            st.button(
                "Next Song", key=f"next-{uuid4()}", type="primary", on_click=next_song
            )
    else:
        st.write("# Nothing playing!")

# Sidebar Content
with st.sidebar:
    # Search
    current_search = st.text_input(
        "current_search",
        placeholder="Insert song title / artist here!",
        label_visibility="collapsed",
    )

    # Results Expander
    with st.expander("Results", expanded=True):
        if current_search:
            matched_songs = get_matched_songs(current_search, media_path)
            if matched_songs:
                for song_filename in matched_songs:
                    display_song(song_filename)
            else:
                st.write(f"No songs match '{current_search}'!")
        else:
            st.write("Nothing searched yet!")

    # Queue Expander
    with st.expander(f"Queue ({len(st.session_state['song_queue'])})", expanded=True):
        if st.session_state["song_queue"]:
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                for i in range(len(st.session_state["song_queue"])):
                    st.write(f"[{i+1}]")

            with col2:
                for i in range(len(st.session_state["song_queue"])):
                    st.write(f"{get_song_title(st.session_state['song_queue'][i])}")

            with col3:
                for i in range(len(st.session_state["song_queue"])):
                    st.button(
                        "x",
                        key=f"queue-{i}-{uuid4()}",
                        type="secondary",
                        on_click=st.session_state["song_queue"].pop,
                        args=(i,),
                    )
        else:
            st.write("No songs queued!")
