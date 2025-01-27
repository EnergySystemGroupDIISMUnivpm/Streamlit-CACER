from streamlit.web.cli import _main_run_clExplicit

# This import path depends on your Streamlit version
if __name__ == "__main__":
    _main_run_clExplicit("main.py", args=["run"], is_hello=False)
    # We will CREATE this function inside our Streamlit framework
