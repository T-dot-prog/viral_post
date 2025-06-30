# 💬 Viral-LinkedIn Post Agent

**Generate, review, and perfect LinkedIn posts with AI-powered feedback.**

![LinkedIn Logo](https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/linkedin.svg)

---

## 🚀 Overview

Viral-LinkedIn Post Agent is a modern Streamlit app that helps you craft, validate, and iterate on LinkedIn posts using a LangGraph-powered agent and LLMs. The app features a professional, ChatGPT-like chat interface, a beautiful dark theme, and a built-in FAQ tab with viral LinkedIn post hacks.

---

## ✨ Features

- **Modern Chat UI:** ChatGPT-style, with persistent, scrollable history and clear speaker labeling.
- **Bluish-Black Theme:** Stylish, professional, and easy on the eyes.
- **Custom Glossy Spinner:** Beautiful loading animation for a premium feel.
- **Category Badges:** Color-coded labels for original posts, feedback, validation, and more.
- **Multi-Select Inputs:** Choose multiple tones and audiences for nuanced post generation.
- **FAQ Tab:** Practical Q&A and hacks for going viral on LinkedIn.
- **Large LinkedIn Watermark:** Subtle, animated background logo for branding.
- **Responsive & Fast:** Caching for LLM calls, seamless reruns, and smooth transitions.

---

## 🛠️ How It Works

### 1. **User Input (Hybrid UI)**
- **Step 1:** Select your post topic, audience(s) (multi-select), and tone(s) (multi-select) using dropdowns.
- **Step 2:** Click “Generate LinkedIn Post” to start the agent.

### 2. **Validation Node**
- The agent validates your topic, tone, and audience for LinkedIn suitability using an LLM.
- If valid, the chain continues; if not, you’re prompted to revise.

### 3. **Post Generation Node**
- The agent generates a LinkedIn post draft based on your selections.
- The draft is displayed in the chat with a blue “Original Post” badge.

### 4. **Post Validation Node**
- The generated post is checked for alignment with your topic, tone, and audience.
- If valid, you’re prompted for feedback; if not, the agent regenerates.

### 5. **Human Feedback Node**
- You review the post and provide feedback in the chat.
- The agent analyzes your feedback sentiment (positive/negative).

### 6. **Feedback-Based Regeneration**
- If feedback is negative, the agent generates an improved post based on your comments.
- The new draft is shown with a green “Generated Post Based on Feedback” badge.
- The cycle repeats until you’re satisfied.

### 7. **Post Finalization**
- When you give positive feedback, the agent marks the post as ready for LinkedIn.

---

## 🧩 Chain Architecture

The backend is built with [LangGraph](https://github.com/langchain-ai/langgraph) and consists of these nodes:

- **input_node:** Receives initial user config.
- **validator_node:** Checks if the topic, tone, and audience are LinkedIn-appropriate.
- **generate_post_node:** Generates the first post draft.
- **post_validation_node:** Validates the generated post.
- **human_feedback_node:** Accepts and analyzes user feedback.
- **collect_feedback_node:** Regenerates the post based on feedback.
- **post:** Simulates posting to LinkedIn.

State is managed via a TypedDict (`AgentState`) and persisted with SQLite for checkpointing.

---

## 🖥️ User Interface

- **Tabs:**  
  - 🤖 Viral LinkedIn Agent: The main chat interface.
  - 📈 FAQ: Viral LinkedIn Posts & Hacks: Q&A and tips for LinkedIn virality.
- **Headers:**  
  - Bebas Neue font for a bold, modern look.
- **LinkedIn Branding:**  
  - Large, semi-transparent LinkedIn logo watermark.
  - Centered, clickable LinkedIn logo under the main header.
- **Chat Bubbles:**  
  - User and assistant messages are clearly separated.
  - Category badges for post types and feedback.
- **Custom Spinner:**  
  - Glossy, animated loader for all LLM operations.

---

## 🏁 How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Add your LLM API keys and any other secrets to a `.env` file.

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

4. **Interact:**
   - Use the dropdowns to start, then chat to review and improve your post.
   - Explore the FAQ tab for viral LinkedIn tips.

---

## 📚 FAQ & Viral Hacks

Check out the **FAQ** tab in the app for:
- What makes a LinkedIn post go viral?
- Hashtag strategies
- Best posting times
- Media usage tips
- Engagement hacks

---

## 🧑‍💻 Tech Stack

- **Frontend:** Streamlit (custom CSS, tabs, chat UI)
- **Backend:** LangGraph, LangChain, Google Generative AI, SQLite
- **State Management:** TypedDict, Streamlit session state, SQLite checkpointing

---

## 🤝 Contributing

Pull requests and suggestions are welcome! Please open an issue or PR for improvements.

---

## 📄 License

MIT License

---

## 🙏 Acknowledgements

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Streamlit](https://streamlit.io/)
- [Google Generative AI](https://ai.google/)
- [Simple Icons](https://simpleicons.org/)
