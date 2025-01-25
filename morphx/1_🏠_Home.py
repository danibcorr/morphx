import streamlit as st


# Set the page configuration for Streamlit
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
st.title("🏠 MorphX")
st.sidebar.image("./images/logo.png")


def text_home() -> None:
    """
    Display the home page content with an overview of the application's features.
    """

    # Project Overview
    st.markdown("# 🏛️ Overview")
    st.markdown(
        """
    Welcome to MorphX, your go-to solution for simplifying and enhancing document management. 
    This application provides a range of tools, including metadata editing, file conversion, audio transcription, 
    and more—all within an intuitive, easy-to-use interface.
    """
    )

    col1, col2 = st.columns(2)

    with col1:

        # Metadata Section
        st.markdown("# 📑 Metadata editing")
        st.markdown(
            """
        Use the Metadata page to effortlessly modify document metadata and add custom cover pages.
        """
        )

        # PDF to Markdown Section
        st.markdown("# 📄 File to Markdown")
        st.markdown(
            """
        The PDF to Markdown page lets you convert PDF files into Markdown format, making content extraction 
        and editing a breeze. This feature is especially useful for extracting text and using a language model 
        (Large Language Model, LLM) to generate key points, summaries, and more.
        """
        )

    with col2:

        # Audio Transcription Section
        st.markdown("# 🎙️ Audio transcription")
        st.markdown(
            """
        The Audio Transcription feature allows you to transcribe audio files directly within the app. 
        Whether you're converting YouTube videos, recorded lectures, or other audio content, 
        this tool simplifies the process of generating text transcripts for analysis or documentation. 
        Additionally, you can use a language model to extract key points, summaries, and more from the transcribed text.
        """
        )


def main() -> None:
    """
    Main entry point of the application.
    """

    text_home()


if __name__ == "__main__":

    main()
