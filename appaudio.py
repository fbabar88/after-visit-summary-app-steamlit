import streamlit as st
import streamlit.components.v1 as components
import openai
from fpdf import FPDF
from io import BytesIO

# --- Custom CSS for UI Style and Print ---
st.markdown(
    """
    <style>
    /* Main container background */
    .reportview-container {
        background: #f5f5f5;
    }
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f0f0f0;
        padding: 20px;
    }
    /* Custom button styling */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
    }
    /* Print styles: Only display the #printable div */
    @media print {
      body * {
        visibility: hidden;
      }
      #printable, #printable * {
        visibility: visible;
      }
      #printable {
        position: absolute;
        left: 0;
        top: 0;
      }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Set OpenAI API Key ---
openai.api_key = st.secrets["general"]["MY_API_KEY"]

# --- PDF Generation Function ---
def generate_pdf(text: str) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return BytesIO(pdf_bytes)

# --- Build Prompt from Structured Inputs (unchanged) ---
def build_prompt(inputs: dict) -> str:
    # [Your existing code for building the prompt from inputs]
    # ...
    return "\n".join([
        "Generate a concise, coherent AVS summary for the following patient details in 1–2 paragraphs. Do not repeat broad category headings; instead, integrate recommendations, next steps, and patient education points naturally into a unified narrative.",
        # ... add your details here ...
    ])

# --- Generate AVS Summary from OpenAI (unchanged) ---
def generate_avs_summary(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledgeable medical assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return ""

# --- Audio Recorder HTML (updated to include transcription display) ---
audio_recorder_html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Audio Recorder</title>
  </head>
  <body>
    <h3>Record Your Command</h3>
    <button id="startBtn">Start Recording</button>
    <button id="stopBtn" disabled>Stop Recording</button>
    <br><br>
    <audio id="audioPlayback" controls></audio>
    <div id="transcription" style="margin-top:20px; border: 1px solid #ccc; padding: 10px;"></div>
    <script>
      if (!navigator.mediaDevices || !window.MediaRecorder) {
        alert("Your browser does not support the MediaRecorder API.");
      }
      let mediaRecorder;
      let audioChunks = [];
      const startBtn = document.getElementById("startBtn");
      const stopBtn = document.getElementById("stopBtn");
      const audioPlayback = document.getElementById("audioPlayback");
      const transcriptionDiv = document.getElementById("transcription");

      startBtn.addEventListener("click", async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaRecorder = new MediaRecorder(stream);
          audioChunks = [];
          mediaRecorder.addEventListener("dataavailable", event => {
            if (event.data.size > 0) {
              audioChunks.push(event.data);
            }
          });
          mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;
            // Send the audio to the transcription backend.
            let formData = new FormData();
            formData.append('file', audioBlob, 'recording.wav');
            fetch("https://929f-35-243-236-56.ngrok-free.app/transcribe", {
              method: "POST",
              body: formData
            })
            .then(response => response.json())
            .then(data => {
              transcriptionDiv.innerHTML = "<strong>Transcription:</strong> " + data.transcription;
            })
            .catch(error => {
              transcriptionDiv.innerHTML = "Error transcribing audio.";
              console.error("Error:", error);
            });
          });
          mediaRecorder.start();
          startBtn.disabled = true;
          stopBtn.disabled = false;
        } catch (err) {
          console.error("Error starting recording:", err);
        }
      });

      stopBtn.addEventListener("click", () => {
        mediaRecorder.stop();
        startBtn.disabled = false;
        stopBtn.disabled = true;
      });
    </script>
  </body>
</html>
"""

# --- Main App Function ---
def main():
    st.title("AVS Summary Generator")
    st.write("Enter patient details using the sidebar to generate an AVS summary.")

    # Input mode selection in sidebar
    input_mode = st.sidebar.radio("Select Input Mode", ["Structured Input", "Free Text Command"])

    if input_mode == "Structured Input":
        # [Your existing structured input code here...]
        st.sidebar.markdown("Structured input mode is not shown here for brevity.")
    else:  # Free Text Command Mode
        st.sidebar.subheader("Free Text Command Mode")
        # Create two columns: left for free text and right for the audio recorder.
        col1, col2 = st.columns(2)
        with col1:
            free_text_command = st.text_area("Enter your free text command (or copy transcription from the recorder):", height=200)
            if st.button("Generate AVS Summary", key="free_text"):
                prompt = free_text_command
                st.info("Generating AVS summary from free text command, please wait...")
                summary_text = generate_avs_summary(prompt)
                if summary_text:
                    st.subheader("Generated AVS Summary")
                    st.text_area("", value=summary_text, height=300)
                    pdf_data = generate_pdf(summary_text)
                    st.download_button(
                        label="Download Summary as PDF",
                        data=pdf_data.getvalue(),
                        file_name="AVS_Summary.pdf",
                        mime="application/pdf"
                    )
                    st.markdown(
                        f"""
                        <div id="printable">
                        <h3>Generated AVS Summary</h3>
                        <p>{summary_text.replace("\n", "<br>")}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.markdown("### Printing Instructions")
                    st.write("To print only the AVS summary, use your browser's print function (Ctrl+P or Cmd+P).")
        with col2:
            st.header("Record Your Command")
            components.html(audio_recorder_html, height=450)
    
    st.sidebar.markdown("### Use the sidebar to input patient details or a free text command.")

if __name__ == "__main__":
    main()
