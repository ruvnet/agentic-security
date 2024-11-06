import streamlit as st
import subprocess
from typing import Optional, List, Tuple
from string import Template
import shlex
from .git_handler import SimpleGitHandler
from .prompt_handler import PromptHandler

class GUI:
    def __init__(self):
        try:
            # Initialize core components
            self.coder = SimpleGitHandler()
            self.prompt_handler = PromptHandler()
            self.state = self.initialize_state()
        except Exception as e:
            st.error(f"Error initializing GUI: {str(e)}")
            return

        self.do_sidebar()
        self.render_prompt_input()

    def initialize_state(self):
        """Initialize session state variables."""
        if 'previous_branch' not in st.session_state:
            st.session_state['previous_branch'] = self.coder.get_current_branch()
        if 'previous_status' not in st.session_state:
            st.session_state['previous_status'] = self.coder.get_status()
        if 'previous_commits' not in st.session_state:
            st.session_state['previous_commits'] = self.coder.get_recent_commits(3)
        return st.session_state

    def monitor_git_changes(self) -> bool:
        """Monitor for changes in the Git repository."""
        current_branch = self.coder.get_current_branch()
        current_status = self.coder.get_status()
        current_commits = self.coder.get_recent_commits(3)

        # Compare current state with previous state
        branch_changed = current_branch != st.session_state['previous_branch']
        status_changed = current_status != st.session_state['previous_status']
        commits_changed = current_commits != st.session_state['previous_commits']

        if branch_changed or status_changed or commits_changed:
            st.session_state['previous_branch'] = current_branch
            st.session_state['previous_status'] = current_status
            st.session_state['previous_commits'] = current_commits
            return True  # Indicates that there has been a change
        return False  # No changes detected

    def process_user_input(self, user_input: str):
        """Process user input and generate an appropriate response."""
        if self.monitor_git_changes():
            st.info("Detected changes in the Git repository. Updating context...")

        prompt = self.prompt_handler.generate_prompt(self.coder, user_input)
        response = self.get_ai_response(prompt)  # Implement this method to interface with AI
        st.write(response)

    def get_ai_response(self, prompt: str) -> str:
        """Placeholder for AI model integration."""
        # Implement AI model API calls here
        # For demonstration, returning a mock response
        return f"AI Response based on the prompt:\n{prompt}"

    def render_prompt_input(self):
        """Render the user input section for prompts."""
        with st.expander("📩 Enter Your Query", expanded=True):
            user_input = st.text_input("Your Query:", placeholder="Ask me about your Git repository...")
            if st.button("Submit"):
                if user_input.strip() == "":
                    st.warning("Please enter a valid query.")
                else:
                    self.process_user_input(user_input)

    def do_sidebar(self):
        with st.sidebar:
            # Title
            st.markdown("""
            <h1 style='
                font-family: "Courier New", monospace;
                color: #00ff00;
                text-shadow: 2px 2px 4px #003300;
                border: 1px solid #00ff00;
                padding: 30px;
                background: linear-gradient(45deg, #050505, #0a0a0a);
                text-align: center;
                letter-spacing: 3px;
                margin-bottom: 20px;
            '>
            S.P.A.R.C.
            </h1>            
            """, unsafe_allow_html=True)
            
            # Chat-Related Expanders
            with st.expander("💬 Chat Options", expanded=True):
                self.do_add_files()
                self.do_add_web_page()
                self.do_recent_msgs()
                self.do_clear_chat_history()
            
            # Tools and Settings Expanders
            with st.expander("🤖 Model Settings", expanded=False):
                self.do_model_settings()
            
            with st.expander("🛠️ Shell Commands", expanded=False):
                self.do_shell_commands()
            
            with st.expander("🔄 GitHub Actions", expanded=False):
                self.do_github_actions()
            
            with st.expander("🔒 Security Tools", expanded=False):
                self.do_security_tools()
            
            with st.expander("⚙️ Developer Tools", expanded=False):
                self.do_dev_tools()
            
            with st.expander("📝 Prompt Engineering", expanded=False):
                # Add tabs for better organization
                tab1, tab2, tab3 = st.tabs(["✏️ Templates", "⚙️ Settings", "🔧 Advanced"])
                
                with tab1:
                    # Template search and management
                    search_term = st.text_input("🔍 Search Templates", "")
                    template_category = st.selectbox(
                        "Category",
                        ["All", "Git", "Code Review", "Documentation", "Custom"]
                    )
                    
                    # Filter templates based on search and category
                    filtered_templates = self.prompt_handler.get_filtered_templates(
                        search_term, 
                        template_category
                    )
                    
                    # Template selection and editing
                    selected_template = st.selectbox(
                        "Select Template",
                        options=list(filtered_templates.keys()),
                        key="selected_template"
                    )
                    
                    # Template editor with description
                    with st.expander("Edit Template", expanded=True):
                        st.text_area(
                            "Template Description",
                            value=filtered_templates[selected_template].get('description', ''),
                            height=50,
                            key="template_description"
                        )
                        st.text_area(
                            "Template Content",
                            value=filtered_templates[selected_template]['template'],
                            height=150,
                            key="template_editor"
                        )
                        
                        # Quick insert variables
                        st.markdown("#### Quick Insert Variables")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.button("${git_context}")
                        with col2:
                            st.button("${user_query}")
                        with col3:
                            st.button("${branch}")
                
                with tab2:
                    # Context settings with presets
                    preset = st.selectbox(
                        "Presets",
                        ["Custom", "Minimal", "Standard", "Detailed"],
                        key="context_preset"
                    )
                    
                    if preset != "Custom":
                        self.prompt_handler.apply_preset(preset)
                    
                    with st.expander("Git Context", expanded=True):
                        num_commits = st.slider(
                            "Number of commits",
                            1, 10,
                            st.session_state.context_settings['num_commits'],
                            help="Number of recent commits to include"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            include_status = st.checkbox(
                                "Git status",
                                value=st.session_state.context_settings['include_status'],
                                help="Include git status"
                            )
                        with col2:
                            include_branch = st.checkbox(
                                "Branch info",
                                value=st.session_state.context_settings['include_branch'],
                                help="Include branch info"
                            )
                
                with tab3:
                    # Template testing
                    with st.expander("Template Testing", expanded=True):
                        test_input = st.text_input(
                            "Test User Query",
                            "What's the latest commit?"
                        )
                        if st.button("Test Template"):
                            with st.spinner("Testing template..."):
                                preview = self.prompt_handler.generate_preview(
                                    self.coder,
                                    st.session_state.template_editor
                                )
                                st.markdown(preview)
                    
                    # Template version history
                    with st.expander("Version History", expanded=False):
                        if st.button("Save Version"):
                            self.prompt_handler.save_template_version()
                        
                        versions = self.prompt_handler.get_template_versions()
                        if versions:
                            version = st.selectbox(
                                "Previous Versions",
                                options=list(versions.keys()),
                                format_func=self.prompt_handler.format_version_timestamp
                            )
                            if st.button("Restore Version"):
                                self.prompt_handler.restore_template_version(version)
            
            # Footer
            st.markdown("---")
            st.warning(
                "Created by rUv, because he could, with help from aider."
            )

    # Placeholder methods for sidebar functionalities
    def do_add_files(self):
        st.write("Add files functionality goes here.")
    
    def do_add_web_page(self):
        st.write("Add web page functionality goes here.")
    
    def do_recent_msgs(self):
        st.write("Recent messages functionality goes here.")
    
    def do_clear_chat_history(self):
        st.write("Clear chat history functionality goes here.")
    
    def do_model_settings(self):
        st.write("Model settings functionality goes here.")
    
    def do_shell_commands(self):
        st.write("Shell commands functionality goes here.")
    
    def do_github_actions(self):
        st.write("GitHub Actions functionality goes here.")
    
    def do_security_tools(self):
        st.write("Security tools functionality goes here.")
    
    def do_dev_tools(self):
        st.write("Developer tools functionality goes here.")

def gui_main():
    try:
        # Set page configuration
        st.set_page_config(
            layout="wide",
            page_title="Aider",
            page_icon="🛠️",
            menu_items={
                "Get Help": "https://your-help-url.com",
                "Report a bug": "https://your-bug-report-url.com",
                "About": "# Aider\nAI pair programming in your browser.",
            },
            initial_sidebar_state="expanded",
        )

        # Initialize GUI
        gui_instance = GUI()
    except Exception as e:
        st.error(f"Error running GUI: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    status = gui_main()
    import sys
    sys.exit(status)
