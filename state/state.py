from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Optional, TypedDict
from langchain_core.messages import BaseMessage
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from uuid import uuid4
from langgraph.graph import StateGraph, END
import streamlit as st

load_dotenv()

llm = ChatGoogleGenerativeAI(model= "gemini-2.0-flash")

conn = sqlite3.connect(database="linkedin.sqlite", check_same_thread=False)

saver = SqliteSaver(conn= conn)

class AgentState(TypedDict):
    user_id: str
    topic: str
    tone: list[str]
    audience: list[str]
    drafts: Optional[List[str]] = []
    best_post: Optional[str] = None
    feedback: Optional[str] = None
    history: List[BaseMessage]
    current_step: Optional[str] = None
    validation: Optional[str] = None
    on: str
    analysis: str


def input_node(state: AgentState) -> AgentState:
    if state.get('history') is None:
        state['history'] = []
    # This node should only be used in CLI mode. In Streamlit, topic, tone, and audience are set by the UI.
    # Remove input() and print() calls.
    # Just return the state as is.
    return state

class Validator(BaseModel):
    response: str = Field("Topic, tone, target audience is valid for LinkedIn? if Yes then provide 'Valid', otherwise provide 'Invalid'", description="Response from the validator indicating if the post is suitable for LinkedIn.")

# --- CACHED LLM HELPERS ---
@st.cache_data(show_spinner="Validating topic, tone, and audience...")
def cached_validator_llm(topic, tone, audience):
    prompt = (
        f"You are a LinkedIn content expert. Review the following:\n"
        f"1. Topic: \"{topic}\"\n"
        f"2. Tone: \"{tone}\"\n"
        f"3. Target Audience: \"{audience}\"\n"
        "If the topic is professional, relevant, and the tone and audience are appropriate for LinkedIn, reply ONLY with 'Valid'. "
        "Reply with 'Invalid' ONLY if there is a clear reason the post would be inappropriate for LinkedIn. "
        "Do not provide any explanation, just reply with 'Valid' or 'Invalid'."
    )
    return llm.invoke([HumanMessage(content=prompt)]).content

@st.cache_data(show_spinner="Generating LinkedIn post...")
def cached_generate_post_llm(topic, tone, audience):
    prompt = f"""You are a LinkedIn post generator. Please create a post based on the following details:\n\n    - Topic: {topic}\n    - Tone: {tone}\n    - Audience: {audience}\n\n    Requirements:\n    - Start with a strong hook to grab attention.\n    - Write a clear, concise, and engaging body that provides value to these categories: {audience}.\n    - Maintain a {tone} tone throughout.\n    - End with a call-to-action or thought-provoking question.\n    - Include relevant and trending hashtags (3-7).\n    - Ensure the post follows LinkedIn best practices for formatting and engagement.\n    - Avoid clichés and keep the language authentic.\n    """
    return llm.invoke([HumanMessage(content=prompt)]).content

@st.cache_data(show_spinner="Validating generated post...")
def cached_post_validation_llm(topic, tone, audience, draft):
    prompt = f"""
You are a LinkedIn post validator. Please analyze the following details:
1. Topic: \"{topic}\"
2. Tone: \"{tone}\"
3. Target Audience: \"{audience}\"
4. Draft Post: \"{draft}\"
Your tasks:
- Determine if the post aligns with the topic and uses the specified tone.
- Ensure the post is appropriate for the target audience.
- Respond with 'Valid' if the post meets all criteria for LinkedIn suitability; otherwise, respond with 'Invalid'.
"""
    structured_llm = llm.with_structured_output(PostValidator)
    return structured_llm.invoke([HumanMessage(content=prompt)]).response

@st.cache_data(show_spinner="Analyzing feedback sentiment...")
def cached_feedback_sentiment_llm(feedback):
    prompt = (
        "You are a sentiment analysis expert. "
        "Categorize the following feedback as either positive or negative.\n"
        "If the feedback suggests or requests any improvements, changes, or modifications to the current post, categorize it as 'negative'.\n"
        "If the feedback indicates that the user does not want any improvements or changes, or is satisfied with the post as it is, categorize it as 'positive'.\n"
        f"Feedback: {feedback}\n"
        "Reply with only 'positive' or 'negative'."
    )
    structure_llm = llm.with_structured_output(FeedbackGrader)
    return structure_llm.invoke([HumanMessage(content=prompt)]).sentiment

@st.cache_data(show_spinner="Generating improved post based on feedback...")
def cached_collect_feedback_llm(feedback, last_draft, topic, tone, audience):
    prompt = f"""You are a LinkedIn post generator that generate posts based on user feedback.\n    Please analyze the feedback provided by the user and suggest improvements to the last draft post.\n\n    Feedback: {feedback}\n    Last Draft: {last_draft}\n\n    Your task:\n    - Analyze the feedback and the last draft.\n    - Generate new post content that incorporates the feedback.\n    - Ensure the new post maintains the original {topic}, {tone}, and {audience}.\n    """
    return llm.invoke([HumanMessage(content=prompt)]).content

# --- NODES (replace LLM calls with cached helpers) ---
def validator_node(state: AgentState) -> AgentState:
    topic = state['topic']
    tone = state['tone']
    audience = state['audience']
    audience_str = ', '.join(audience) if isinstance(audience, list) else str(audience)
    response_content = cached_validator_llm(topic, str(tone), audience_str)
    print(f"[DEBUG] LLM raw response: {response_content}")
    state['current_step'] = "validate_node"
    state['history'].append(AIMessage(content=f"Validation Node: Response - {response_content}"))
    result = response_content.strip().lower()
    if 'valid' in result:
        state['validation'] = 'Valid'
    else:
        print("[DEBUG] LLM did not return 'Valid', treating as 'Invalid'")
        state['validation'] = 'Invalid'
    print(f"[Current Step] {state['current_step']}")
    return state

def validation_router(state: AgentState) -> str:
    print(f"[DEBUG] validation_router: validation status is {state['validation']}")
    if state['validation'] == 'Valid':
        return "generate_post_node"
    return END

def generate_post_node(state: AgentState) -> AgentState:
    if state.get('drafts') is None:
        state['drafts'] = []
    if state.get('history') is None:
        state['history'] = []
    topic = state['topic']
    tone = state['tone']
    audience = state['audience']
    audience_str = ', '.join(audience) if isinstance(audience, list) else str(audience)
    post_content = cached_generate_post_llm(topic, str(tone), audience_str)
    user_id = str(uuid4())
    state['drafts'].append(post_content)
    state['user_id'] = user_id
    state['current_step'] = "Generating Post"
    state['history'].append(AIMessage(content=f"Generated Post: {post_content}"))
    return state

class PostValidator(BaseModel):
    response: str = Field(
        "Carefully review the provided topic, tone, target audience, and generated LinkedIn post. Assess if the post aligns with the topic, uses the specified tone, and is appropriate for the target audience. Respond only with 'Valid' if all criteria are met for LinkedIn suitability; otherwise, respond with 'Invalid'.",
        description="Response from the validator indicating if the post is suitable for LinkedIn."
    )

def post_validation_node(state: AgentState) -> AgentState:
    if state.get('history') is None:
        state['history'] = []
    topic = state.get('topic')
    tone = state.get('tone')
    audience = state.get('audience')
    drafts = state.get('drafts')
    if not all([topic, tone, audience, drafts]):
        raise ValueError("Missing user information for post validation!")
    audience_str = ', '.join(audience) if isinstance(audience, list) else str(audience)
    response = cached_post_validation_llm(topic, str(tone), audience_str, drafts[-1])
    state['current_step'] = "post_validation"
    print(f"Validating Post: {state['current_step']}")
    state['on'] = response
    state['history'].append(AIMessage(content=f"Post Validation Node: Validation result - {response}"))
    return state

def on_validation_router(state: AgentState) -> str:
    print(f"[DEBUG] on_validation_router: on = {state['on']}")
    if state['on'] == "Valid":
        return "human_feedback_node"
    return "generate_post_node"


class FeedbackGrader(BaseModel):
    sentiment: str = Field(..., description="The sentiment category of the feedback (positive, negative).")
def human_feedback_node(state: AgentState) -> AgentState:
    if state.get('history') is None:
        state['history'] = []
    drafts = state['drafts']
    user_id = state['user_id']
    if not drafts:
        raise ValueError("No drafts found for user!")
    human_feedback = state.get('feedback', '')
    sentiment = cached_feedback_sentiment_llm(human_feedback)
    state['feedback'] = human_feedback
    state['analysis'] = sentiment
    if sentiment == "positive" and human_feedback:
        state['history'].append(
            AIMessage(content=f"Positive feedback received: {human_feedback}")
        )
    elif sentiment == "negative" and human_feedback:
        state['history'].append(
            AIMessage(content=f"Negative feedback received: {human_feedback}")
        )
    else:
        state['history'].append(
            AIMessage(content=f"Feedback received: {human_feedback}")
        )
    return state

def sentiment_routing(state: AgentState) -> str:
    print(f"[DEBUG] sentiment_routing: analysis = {state['analysis']}")
    if state['analysis'] == 'positive':
        return END
    return "collect_feedback_node"

def collect_feedback_node(state: AgentState) -> AgentState:
    if state.get('history') is None:
        state['history'] = []
    feedback = state['feedback']
    draft = state['drafts']
    topic = state.get('topic')
    tone = state.get('tone')
    audience = state.get('audience')
    last_draft = draft[-1]
    audience_str = ', '.join(audience) if isinstance(audience, list) else str(audience)
    improved_post = cached_collect_feedback_llm(feedback, last_draft, topic, str(tone), audience_str)
    state['current_step'] = "Collecting feedback from human"
    state['history'].append(
        AIMessage(content=f"Generated post based on feedback: {improved_post}")
    )
    state['best_post'] = improved_post
    return state

def post(state: AgentState) -> None:
    best_post  = state['best_post']
    # Instead of print, append to history
    state['history'].append(AIMessage(content="Post sent to LinkedIn (simulated). PING ==> PONG"))
    return None
# --------------------------------------

graph = StateGraph(AgentState)

# Add nodes
graph.add_node("input_node", input_node)
graph.add_node("validator_node", validator_node)
graph.add_node("generate_post_node", generate_post_node)
graph.add_node("post_validation_node", post_validation_node)
graph.add_node("human_feedback_node", human_feedback_node)
graph.add_node("collect_feedback_node", collect_feedback_node)
graph.add_node("post", post)

# Set entry point
graph.set_entry_point("input_node")

# Add edges between nodes
graph.add_edge("input_node", "validator_node")
graph.add_conditional_edges("validator_node", validation_router, {
    "generate_post_node": "generate_post_node",
    END: END
})  # validation_router returns next node name
graph.add_edge("generate_post_node", "post_validation_node")
graph.add_conditional_edges("post_validation_node", on_validation_router, {
    "human_feedback_node": "human_feedback_node",
    "generate_post_node": "generate_post_node"
})  # post_validation_router returns next node name
graph.add_conditional_edges("human_feedback_node", sentiment_routing, {
    END: END,
    "collect_feedback_node": "collect_feedback_node"
})
graph.add_edge("collect_feedback_node", "post")
graph.add_edge("post", END)  # After collecting feedback, go to post


app = graph.compile(checkpointer= saver)