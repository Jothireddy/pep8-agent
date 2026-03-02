import streamlit as st
import os
import zipfile
from io import BytesIO
from agent import PEP8Agent
from datetime import datetime
import time

st.cache_data.clear()
st.cache_resource.clear()

# Page config
st.set_page_config(
    page_title="PEP 8 Code Review Agent",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .clean-badge {
        color: #27ae60;
        font-weight: bold;
        background-color: #d5f4e6;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'files_dict' not in st.session_state:
    st.session_state.files_dict = {}

# Header
st.markdown('<h1 class="main-header">🤖 PEP 8 Code Review Agent</h1>', unsafe_allow_html=True)
st.markdown("### Watch AI add comments to your code LIVE!")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("ℹ️ How it works")
    st.write("""
    **Comments appear line-by-line WITHOUT touching your code!**
    
    ✅ Original code stays visible  
    ✅ Comments insert above violations  
    ✅ Watch it happen LIVE  
    ✅ Safe - zero code modification  
    """)
    
    st.markdown("---")
    st.caption("Powered by GPT-4o-mini")

# Initialize agent
if st.session_state.agent is None:
    with st.spinner("🔧 Initializing agent..."):
        try:
            st.session_state.agent = PEP8Agent()
            st.success("✅ Ready!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.stop()

# Main content
st.markdown("## 📁 Upload Python Files")

upload_method = st.radio(
    "Choose upload method:",
    ["Upload .py files", "Upload .zip folder"],
    horizontal=True
)

if upload_method == "Upload .py files":
    uploaded_files = st.file_uploader(
        "Select Python files",
        type=['py'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.session_state.files_dict = {}
        for file in uploaded_files:
            content = file.read().decode('utf-8')
            st.session_state.files_dict[file.name] = content
        
        st.success(f"✅ Loaded {len(uploaded_files)} file(s)")

else:
    uploaded_zip = st.file_uploader(
        "Upload .zip folder",
        type=['zip']
    )
    
    if uploaded_zip:
        st.session_state.files_dict = {}
        
        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('.py') and not file_info.is_dir():
                    with zip_ref.open(file_info) as file:
                        content = file.read().decode('utf-8')
                        filename = os.path.basename(file_info.filename)
                        st.session_state.files_dict[filename] = content
        
        if st.session_state.files_dict:
            st.success(f"✅ Extracted {len(st.session_state.files_dict)} Python file(s)")
        else:
            st.warning("⚠️ No Python files found in zip")

# Process button
if st.session_state.files_dict:
    st.markdown("---")
    
    if st.button("🚀 Start Review & Add Comments", type="primary", use_container_width=True):
        st.markdown("## 🔍 Live Processing")
        
        results = {}
        total_files = len(st.session_state.files_dict)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (filename, code) in enumerate(st.session_state.files_dict.items(), 1):
            progress = i / total_files
            progress_bar.progress(progress)
            status_text.markdown(f"**Processing file {i}/{total_files}: {filename}**")
            
            with st.expander(f"📄 {filename}", expanded=True):
                st.markdown("### 📝 Original Code (stays unchanged)")
                
                # Show original code
                code_lines = code.split('\n')
                
                # Create placeholder for live updates
                code_display = st.empty()
                
                # Initially show just original code
                display_lines = code_lines.copy()
                code_display.code('\n'.join(display_lines), language='python', line_numbers=True)
                
                st.markdown("### ✍️ AI adding comments live...")
                status = st.empty()
                
                # Track comments to insert
                comments_by_line = {}  # {line_number: [comments]}
                violation_count = 0
                
                # Stream comments
                for chunk in st.session_state.agent.add_inline_comments_streaming(code, filename):
                    if chunk['type'] == 'comment':
                        line_num = chunk['line_number']
                        comment = chunk['comment']
                        
                        # Track comment
                        if line_num not in comments_by_line:
                            comments_by_line[line_num] = []
                        comments_by_line[line_num].append(comment)
                        violation_count += 1
                        
                        # Rebuild display with comments inserted
                        display_lines = []
                        for i, line in enumerate(code_lines, 1):
                            # Insert comments before this line
                            if i in comments_by_line:
                                for comment in comments_by_line[i]:
                                    display_lines.append(comment)
                            # Add original line
                            display_lines.append(line)
                        
                        # Update display LIVE
                        code_display.code('\n'.join(display_lines), language='python', line_numbers=True)
                        status.markdown(f"✍️ Added comment for line {line_num}...")
                        time.sleep(0.1)  # Small delay for visual effect
                
                # Store result
                final_code = '\n'.join(display_lines)
                results[filename] = {
                    'original_code': code,
                    'commented_code': final_code,
                    'violation_count': violation_count,
                    'is_clean': violation_count == 0,
                    'filename': filename
                }
                
                if violation_count == 0:
                    status.markdown('<div class="clean-badge">✅ Clean! No violations</div>', unsafe_allow_html=True)
                else:
                    status.markdown(f"**✅ Added {violation_count} comments**")
        
        # Store results
        st.session_state.results = results
        
        progress_bar.progress(1.0)
        status_text.markdown("**✅ All files processed!**")
        st.balloons()
        
        # Summary
        st.markdown("---")
        st.markdown("## 📊 Summary Report")
        
        summary = st.session_state.agent.generate_summary(results)
        st.code(summary, language='text')
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        
        clean_count = sum(1 for r in results.values() if r['is_clean'])
        total_violations = sum(r['violation_count'] for r in results.values())
        
        with col1:
            st.metric("📁 Total Files", total_files)
        with col2:
            st.metric("✅ Clean Files", clean_count)
        with col3:
            st.metric("⚠️ Total Violations", total_violations)
        
        # Download section
        st.markdown("---")
        st.markdown("## 📥 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 Download Summary",
                data=summary,
                file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr("SUMMARY.txt", summary)
                for filename, result in results.items():
                    zip_file.writestr(f"commented_{filename}", result['commented_code'])
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="📦 Download All (ZIP)",
                data=zip_buffer,
                file_name=f"pep8_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )

else:
    st.info("👆 Please upload Python files above to begin")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🤖 PEP 8 Agent | Comments insert live - Code never changes!</p>
</div>
""", unsafe_allow_html=True)