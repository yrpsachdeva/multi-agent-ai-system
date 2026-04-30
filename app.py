import streamlit as st
import os
from dotenv import load_dotenv
from graph import app
import time
import boto3

# Initialize S3 client using environment variables
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name="ap-south-1"
)

BUCKET_NAME = "your-real-bucket-name"

BUCKET_NAME = "your-bucket-name"   # ⚠️ change this

load_dotenv()

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
def upload_to_s3(content, filename):
    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=content
        )
        return True
    except Exception as e:
        print("S3 Upload Error:", e)
        return False

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a, #111827, #1e293b);
    color: white;
}

.main-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    color: #cbd5e1;
    font-size: 1.1rem;
    margin-bottom: 35px;
}

.hero-box {
    background: rgba(30, 41, 59, 0.75);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    border-radius: 24px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.35);
}

.agent-card {
    background: rgba(30, 41, 59, 0.85);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0px 8px 20px rgba(0,0,0,0.25);
    transition: 0.3s ease;
    text-align: center;
    min-height: 160px;
}

.agent-card:hover {
    transform: translateY(-6px);
    border: 1px solid #38bdf8;
}

.metric-card {
    background: linear-gradient(145deg, #1e293b, #111827);
    border-radius: 20px;
    padding: 22px;
    text-align: center;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.06);
}

.metric-card h2 {
    color: #38bdf8;
    margin-bottom: 5px;
    font-size: 2rem;
}

.report-box {
    background: rgba(17, 24, 39, 0.88);
    border-radius: 18px;
    padding: 22px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0px 8px 20px rgba(0,0,0,0.35);
    margin-bottom: 20px;
}

.step-header {
    background: linear-gradient(90deg, #1e293b, #0f172a);
    border-left: 5px solid #38bdf8;
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.25);
}

.step-card {
    background: rgba(15, 23, 42, 0.95);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 20px;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.25);
}

.stButton > button {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px 24px;
    font-size: 17px;
    font-weight: 600;
    width: 100%;
    transition: 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.02);
    background: linear-gradient(90deg, #1d4ed8, #6d28d9);
}

div[data-baseweb="input"] input {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 14px !important;
    border: 1px solid #334155 !important;
}

section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid rgba(255,255,255,0.08);
}

hr {
    border: 1px solid rgba(255,255,255,0.08);
}

.small-label {
    color: #94a3b8;
    font-size: 0.9rem;
    margin-bottom: 8px;
}

.preview-box {
    background: #0f172a;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #334155;
    color: #e2e8f0;
    line-height: 1.7;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

def check_api_keys():
    together_key = os.environ.get("TOGETHER_API_KEY") or os.environ.get("GROQ_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")

    if not together_key or not tavily_key:
        st.error("🚨 API keys not found! Please set GROQ_API_KEY / TOGETHER_API_KEY and TAVILY_API_KEY.")
        return False

    return True

st.markdown("<div class='main-title'>🤖 Multi-Agent Research Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your AI-powered research platform where multiple intelligent agents collaborate to generate high-quality reports.</div>", unsafe_allow_html=True)

if not check_api_keys():
    st.stop()

with st.sidebar:
    st.title("⚙️ Control Panel")
    st.success("API Keys Loaded Successfully")
    st.info("Powered by Groq / Together + Tavily")

    st.markdown("### Workflow Settings")
    max_iterations = st.slider(
        "Max Workflow Iterations",
        min_value=5,
        max_value=25,
        value=15
    )

    st.markdown("---")
    st.markdown("### Agent Team")
    st.markdown("🎯 Supervisor")
    st.markdown("🔍 Researcher")
    st.markdown("✍️ Writer")
    st.markdown("🔎 Critiquer")

st.markdown("<div class='hero-box'>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='agent-card'>
        <h2>🎯</h2>
        <h4>Supervisor</h4>
        <p>Manages workflow, makes decisions, and coordinates all agents.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='agent-card'>
        <h2>🔍</h2>
        <h4>Researcher</h4>
        <p>Searches for information and collects useful findings.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='agent-card'>
        <h2>✍️</h2>
        <h4>Writer</h4>
        <p>Creates a detailed and structured report from findings.</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='agent-card'>
        <h2>🔎</h2>
        <h4>Critiquer</h4>
        <p>Reviews report quality and suggests improvements.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("## 🚀 Start Your Research")

topic = st.text_input(
    "Enter your research topic",
    placeholder="e.g. Impact of quantum computing on cybersecurity"
)

if st.button("🚀 Generate Research Report"):
    if not topic:
        st.warning("Please enter a topic first.")
    else:
        initial_state = {
            "main_task": topic,
            "research_findings": [],
            "draft": "",
            "critique_notes": "",
            "revision_number": 0,
            "next_step": "",
            "current_sub_task": ""
        }

        config = {"recursion_limit": max_iterations}

        st.info("🤖 Agents are starting their work...")
        progress_bar = st.progress(0)

        final_state = None
        all_states = []
        step_count = 0

        try:
            st.markdown("## 🔄 Live Agent Workflow")

            for step in app.stream(initial_state, config=config):
                step_count += 1
                progress_bar.progress(min(step_count / max_iterations, 1.0))

                node_name = list(step.keys())[0]
                node_output = step[node_name]

                all_states.append((node_name, node_output))
                final_state = node_output

                st.markdown(f"""
                <div class='step-header'>
                    <h3>🤖 {node_name.upper()} - Step {step_count}</h3>
                </div>
                """, unsafe_allow_html=True)

                with st.container():
                    st.markdown("<div class='step-card'>", unsafe_allow_html=True)

                    if node_name == "supervisor":
                        st.markdown(f"""
                        <div class='small-label'>Supervisor Decision</div>
                        <h4 style='color:#38bdf8;'>🎯 Next Step: {node_output.get('next_step', 'N/A')}</h4>
                        <div class='preview-box'>
                            <b>Current Task:</b><br>
                            {node_output.get('current_sub_task', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)

                    elif node_name == "researcher":
                        findings = node_output.get("research_findings", [])

                        if findings:
                            latest = findings[-1]

                            st.markdown("""
                            <div class='small-label'>Research Summary</div>
                            <h4 style='color:#38bdf8;'>🔍 Research Findings</h4>
                            """, unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class='preview-box'>
                                {latest[:700]}...
                            </div>
                            """, unsafe_allow_html=True)

                            with st.expander("📖 View Full Research"):
                                st.write(latest)

                    elif node_name == "writer":
                        draft = node_output.get("draft", "")

                        st.markdown("""
                        <div class='small-label'>Generated Report Draft</div>
                        <h4 style='color:#38bdf8;'>✍️ Draft Generated</h4>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class='preview-box'>
                            {draft[:700]}...
                        </div>
                        """, unsafe_allow_html=True)

                        with st.expander("📄 View Full Draft"):
                            st.write(draft)

                    elif node_name == "critiquer":
                        critique = node_output.get("critique_notes", "")

                        st.markdown("""
                        <div class='small-label'>Critique Result</div>
                        <h4 style='color:#38bdf8;'>🔎 Critique Feedback</h4>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class='preview-box'>
                            {critique if critique else "No critique available"}
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                time.sleep(0.3)

            progress_bar.progress(1.0)
            st.success("✅ Research Complete!")

        except Exception as e:
            st.error(f"Error: {str(e)}")

        final_draft = None

        if final_state and isinstance(final_state, dict):
            final_draft = final_state.get("draft", "")

        if not final_draft:
            for node_name, state in reversed(all_states):
                if isinstance(state, dict) and state.get("draft"):
                    final_draft = state.get("draft", "")
                    final_state = state
                    break

        if final_draft:
            st.markdown("## 📄 Final Research Report")

            st.markdown(f"""
                <div class='report-box'>
                    {final_draft.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

            # 🔥 UPLOAD TO S3 HERE
            filename = f"reports/{topic.replace(' ', '_')}.txt"

            uploaded = upload_to_s3(final_draft, filename)

            if uploaded:
                st.success("☁️ Report saved to AWS S3 successfully!")
            else:
                st.error("❌ Failed to upload to S3")

    st.markdown("## 📊 Report Statistics")

    col1, col2, col3, col4 = st.columns(4)

    stats = [
        ("Revisions", final_state.get("revision_number", 0)),
        ("Research Sources", len(final_state.get("research_findings", []))),
        ("Word Count", len(final_draft.split())),
        ("Characters", len(final_draft))
    ]

    for col, (label, value) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <h2>{value}</h2>
                <p>{label}</p>
            </div>
            """, unsafe_allow_html=True)

    st.download_button(
        label="📥 Download Report",
        data=final_draft,
        file_name=f"research_report_{topic.replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=True
    )

st.markdown("""
<hr>
<div style='text-align:center; color:#94a3b8; padding:15px;'>
Built with ❤️ using Streamlit, LangGraph, Groq, Together AI and Tavily
</div>
""", unsafe_allow_html=True)