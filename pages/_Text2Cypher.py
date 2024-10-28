import streamlit as st
from tools.text2cypher import generate_cypher
from api.dao.general import GeneralDAO
from tools.rating import save_ratings
from api.neo4j import init_driver
from components.navigation_bar import navigation_bar


driver = init_driver()
state = st.session_state

# Page config and icon
st.set_page_config(layout="wide", page_title="Text2Cypher View", page_icon=":keyboard:")

# sidebar for navigation
navigation_bar()

def upvote_callback():
    save_ratings(state['user_input'], state['cypher_code'], "up")
    state.rated = True

def downvote_callback():
    save_ratings(state['user_input'], state['cypher_code'], "down")
    state.rated = True

def init_state(key, value):
    if key not in state:
        state[key] = value

def _set_state_cb(**kwargs):
    for state_key, widget_key in kwargs.items():
        val = state.get(widget_key, None)
        if val is not None or val == "":
            setattr(state, state_key, state[widget_key])
    
init_state('cypher_code', None)
init_state('query_result', None)
init_state('user_input', None)
init_state('rated', False)
init_state('run_query', False)

def _set_run_query_cb():
    state['run_query'] = True
    state['rated'] = False
    state['cypher_code'] = None
    state['query_result'] = None

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Text To Cypher Conversion</h1>", unsafe_allow_html=True)
st.subheader("Query the knowledge graph using natural language!")

tutorial_col, tips_col = st.columns([1,1])

with tutorial_col:
    with st.expander("How it works", expanded=False):
        st.write("""
        1. Enter your query in natural language.
        2. Click 'Generate' to create the corresponding Cypher query.
        3. The generated Cypher code will automatically run against our database.
        4. The generated Cypher code and query results will be returned.
        5. (Optional) Rate the response to help us improve! (Only the quality of the answer (thumbs up or down) is stored).
        """)
        st.write("**Example**: Return all Fields. For each field, return the name and the number of Experimental Units it has.")

with tips_col:
    with st.expander("Prompts Tips", expanded=False):
        st.write("""
        1. Be clear and specific in your query. Provide detailed descriptions of the data you want to retrieve, closely matching the node labels, relationships, and property values.
        2. Use declarative language sometime give better result than asking questions. Start with phrases like "Show me a list of..." or "Return all...".
        3. Ask precise questions. For example, instead of "Return all fields," try "Return all fields and their respective longitudes and latitudes."
        4. Avoid ambiguous questions that are not related to the database.
        """)


st.text_input(
    "Enter your query:", value=state.user_input, key='user_input',
    on_change=_set_state_cb, kwargs={'user_input': 'user_input'}
)

generate_col, _ = st.columns([1,4])
with generate_col:
    st.button(
        "🔄 Generate", type="primary", on_click=_set_run_query_cb, args=()
    )

if state['run_query']:
    with st.spinner("🔧 Generating Cypher..."):
        try:
            response = generate_cypher(state['user_input'])
            state['cypher_code'] = response['constructed_cypher']
            state['run_query'] = False
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            state['run_query'] = False

if state['cypher_code']:
    st.subheader("Generated Cypher Code")
    st.code(state['cypher_code'], language='cypher')
    
    st.subheader("Query Result")
    general_dao = GeneralDAO(driver)
    query_result = general_dao.run_query(state['cypher_code'])
    st.dataframe(data=query_result, hide_index=False, use_container_width=True)
    
    if not state['rated']:
        st.markdown("### Rate this response:")
        col1, col2, _ = st.columns([1,1,4])
        with col1:
            st.button("👍 Upvote", key="upvote", on_click=upvote_callback)
        with col2:
            st.button("👎 Downvote", key="downvote", on_click=downvote_callback)

    if state['rated']:
        st.success("✅ Thanks for your feedback!")