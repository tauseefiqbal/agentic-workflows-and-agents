import streamlit as st
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.media import Image, Video
from agno.models.google import Gemini
import google.generativeai as genai
import fitz  # PyMuPDF
from youtube_transcript_api import YouTubeTranscriptApi
import re
import tempfile
import os
from pathlib import Path


YOUTUBE_TRANSCRIPT_MAX_CHARS = 80_000

def extract_youtube_id(url: str) -> str | None:
    match = re.search(r"(?:v=|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def get_youtube_transcript(url: str, max_chars: int = YOUTUBE_TRANSCRIPT_MAX_CHARS) -> tuple[str, bool]:
    """Fetch YouTube transcript text. Returns (text, was_truncated)."""
    video_id = extract_youtube_id(url)
    if not video_id:
        raise ValueError("Could not extract a valid YouTube video ID from the URL.")

    # youtube-transcript-api >=1.0 uses an instance method `fetch`; older versions
    # exposed the classmethod `get_transcript`. Support both.
    if hasattr(YouTubeTranscriptApi, "get_transcript"):
        entries = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join(line["text"] for line in entries)
    else:
        fetched = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join(snippet.text for snippet in fetched)

    if len(text) > max_chars:
        return text[:max_chars], True
    return text, False


st.set_page_config(
    page_title="Multimodal Reasoning AI Agent",
    page_icon="🧠",
    layout="wide",
)


@st.cache_resource
def initialize_agent(api_key: str) -> Agent:
    return Agent(
        name="Multimodal Analyst",
        model=Gemini(id="gemini-2.5-flash", api_key=api_key),
        markdown=True,
    )


def _get_extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


IMAGE_EXTS = {"jpg", "jpeg", "png"}
VIDEO_EXTS = {"mp4", "mov", "avi"}
PDF_EXTS = {"pdf"}

# Cap PDF text passed to the model to avoid huge prompts.
PDF_MAX_CHARS = 80_000


def extract_pdf_text(pdf_path: str, max_chars: int = PDF_MAX_CHARS) -> tuple[str, int, bool]:
    """Extract text from a PDF. Returns (text, page_count, was_truncated)."""
    parts: list[str] = []
    total = 0
    truncated = False
    with fitz.open(pdf_path) as doc:
        page_count = len(doc)
        for i, page in enumerate(doc, start=1):
            page_text = page.get_text()
            header = f"\n\n--- Page {i} ---\n"
            if total + len(header) + len(page_text) > max_chars:
                remaining = max_chars - total - len(header)
                if remaining > 0:
                    parts.append(header + page_text[:remaining])
                truncated = True
                break
            parts.append(header + page_text)
            total += len(header) + len(page_text)
    return "".join(parts).strip(), page_count, truncated


def media_tab(agent: Agent) -> None:
    st.write(
        "Provide a **YouTube URL** _or_ upload an **image**, **video**, or **PDF**, "
        "then ask a reasoning-based question. The AI Agent will analyze the input "
        "and respond — for videos it can also combine the analysis with web research."
    )

    yt_col, btn_col = st.columns([5, 1], vertical_alignment="bottom")
    with yt_col:
        youtube_url_input = st.text_input(
            "YouTube URL (optional)",
            placeholder="https://www.youtube.com/watch?v=...",
            key="media_youtube_url",
        )
    with btn_col:
        submitted = st.button(
            "Submit URL",
            key="submit_youtube_url",
            use_container_width=True,
        )

    youtube_url = (youtube_url_input or "").strip()
    if submitted and youtube_url:
        st.session_state["media_youtube_url_submitted"] = youtube_url
        st.session_state["media_active"] = "youtube"
    elif submitted and not youtube_url:
        st.warning("Please enter a YouTube URL before clicking Submit.")

    uploaded_file = st.file_uploader(
        "Upload Image, Video, or PDF",
        type=sorted(IMAGE_EXTS | VIDEO_EXTS | PDF_EXTS),
        key="media_uploader",
    )

    # Detect a newly-uploaded (or changed/cleared) file vs. previous run.
    prev_file_id = st.session_state.get("media_uploaded_file_id")
    current_file_id = uploaded_file.file_id if uploaded_file is not None else None
    if current_file_id != prev_file_id:
        st.session_state["media_uploaded_file_id"] = current_file_id
        if uploaded_file is not None:
            st.session_state["media_active"] = "file"
        elif st.session_state.get("media_active") == "file":
            # File was cleared — fall back to YouTube if a URL exists, else nothing.
            st.session_state["media_active"] = (
                "youtube" if youtube_url else None
            )

    active = st.session_state.get("media_active")

    # If nothing was ever submitted explicitly, pick whatever is available.
    if active is None:
        if uploaded_file is not None:
            active = "file"
        elif youtube_url:
            active = "youtube"

    is_youtube = active == "youtube" and bool(youtube_url)
    use_file = active == "file" and uploaded_file is not None

    if not is_youtube and not use_file:
        st.info("Please enter a YouTube URL or upload an image, video, or PDF to begin.")
        return

    # ----- YouTube branch -----
    if is_youtube:
        try:
            st.video(youtube_url)
        except Exception:
            video_id = extract_youtube_id(youtube_url)
            if video_id:
                st.image(
                    f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    caption="YouTube video",
                    use_container_width=True,
                )

        task_input = st.text_area(
            "Ask a question about this YouTube video:",
            placeholder="e.g. Summarize the main points, or list the speakers' key arguments.",
            key="media_task",
        )
        if st.button("Analyze YouTube Video", key="analyze_media_btn"):
            if not task_input:
                st.warning("Please enter your question.")
                return
            try:
                with st.spinner("Fetching transcript..."):
                    transcript, truncated = get_youtube_transcript(youtube_url)
            except Exception as e:
                st.error(f"Could not fetch transcript: {str(e)}")
                return
            st.success(f"Transcript loaded ({len(transcript):,} characters).")
            if truncated:
                st.warning(
                    f"Transcript truncated to {YOUTUBE_TRANSCRIPT_MAX_CHARS:,} characters "
                    "to fit the model context."
                )
            with st.expander("Preview transcript"):
                st.text(transcript[:3000] + ("\n..." if len(transcript) > 3000 else ""))
            with st.spinner("Analyzing transcript..."):
                try:
                    prompt = (
                        "You are an expert video analyst. Use the YouTube transcript below "
                        "to answer the user's question. If the answer isn't in the transcript, "
                        "say so.\n\n"
                        f"--- TRANSCRIPT ---\n{transcript}\n--- END TRANSCRIPT ---\n\n"
                        f"Question: {task_input}"
                    )
                    response: RunOutput = agent.run(prompt)
                    st.markdown("### AI Response:")
                    st.markdown(response.content)
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
        return

    # ----- File branch -----
    ext = _get_extension(uploaded_file.name)
    is_image = ext in IMAGE_EXTS
    is_video = ext in VIDEO_EXTS
    is_pdf = ext in PDF_EXTS

    if not (is_image or is_video or is_pdf):
        st.error(f"Unsupported file type: .{ext}")
        return

    temp_path = None
    try:
        suffix = f".{ext}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        pdf_text = ""
        if is_image:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            task_input = st.text_area(
                "Enter your task/question for the AI Agent:", key="media_task"
            )
            button_label = "Analyze Image"
        elif is_video:
            st.video(temp_path)
            task_input = st.text_area(
                "What would you like to know?",
                placeholder=(
                    "Ask any question related to the video - the AI Agent will analyze it "
                    "and search the web if needed"
                ),
                help=(
                    "You can ask questions about the video content and get relevant "
                    "information from the web"
                ),
                key="media_task",
            )
            button_label = "Analyze & Research"
        else:  # PDF
            with st.spinner("Extracting PDF text..."):
                pdf_text, page_count, truncated = extract_pdf_text(temp_path)
            st.success(f"Loaded PDF with {page_count} page(s).")
            if truncated:
                st.warning(
                    f"PDF text was truncated to {PDF_MAX_CHARS:,} characters to fit "
                    "the model context."
                )
            with st.expander("Preview extracted text"):
                st.text(pdf_text[:3000] + ("\n..." if len(pdf_text) > 3000 else ""))
            task_input = st.text_area(
                "Ask a question about this PDF:",
                placeholder="e.g. Summarize the key findings, or extract all dates mentioned.",
                key="media_task",
            )
            button_label = "Analyze PDF"

        if st.button(button_label, key="analyze_media_btn"):
            if not task_input:
                st.warning("Please enter your task/question.")
            else:
                if is_image:
                    spinner_msg = "AI is thinking... 🤖"
                elif is_video:
                    spinner_msg = "Processing video and researching..."
                else:
                    spinner_msg = "Reading PDF and reasoning..."
                with st.spinner(spinner_msg):
                    try:
                        if is_image:
                            response: RunOutput = agent.run(
                                task_input, images=[Image(filepath=temp_path)]
                            )
                        elif is_video:
                            prompt = f"""
                            First analyze this video and then answer the following question using both
                            the video analysis and web research: {task_input}

                            Provide a comprehensive response focusing on practical, actionable information.
                            """
                            response = agent.run(
                                prompt, videos=[Video(filepath=temp_path)]
                            )
                        else:  # PDF
                            prompt = (
                                "You are an expert document analyst. Use the PDF text below "
                                "to answer the user's question. Cite page numbers when "
                                "relevant. If the answer isn't in the document, say so.\n\n"
                                f"--- PDF CONTENT ---\n{pdf_text}\n--- END PDF ---\n\n"
                                f"Question: {task_input}"
                            )
                            response = agent.run(prompt)
                        st.markdown("### AI Response:")
                        st.markdown(response.content)
                    except Exception as e:
                        st.error(f"An error occurred during analysis: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


def main() -> None:
    st.title("Multimodal Reasoning AI Agent 🧠")

    with st.sidebar:
        st.header("🔑 Configuration")
        gemini_api_key = st.text_input("Enter your Gemini API Key", type="password")
        st.caption(
            "Get your API key from [Google AI Studio]"
            "(https://aistudio.google.com/apikey) 🔑"
        )

    if not gemini_api_key:
        st.warning("Please enter your Gemini API key in the sidebar to continue.")
        return

    # Configure the global google-generativeai client so File API uploads
    # (used by agno for Video) authenticate with the same key.
    os.environ["GOOGLE_API_KEY"] = gemini_api_key
    genai.configure(api_key=gemini_api_key)

    agent = initialize_agent(gemini_api_key)

    media_tab(agent)

    st.markdown(
        """
        <style>       
            .stTextArea textarea {
                height: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()