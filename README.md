# LinkedIn AI Concepts Agent 🤖

A LangGraph-based agent that posts daily AI concepts on LinkedIn as engaging stories, progressing from basics to advanced topics over 90 days.

## Features

- 📚 **90-Day AI Curriculum**: Structured learning path from fundamentals to advanced AI
- 📖 **Story-Style Posts**: Engaging narrative format for each concept
- ✅ **Daily Approval Flow**: Asks permission before posting at 10 AM
- 🔄 **No Duplicates**: Tracks all posted content to avoid repetition
- 📊 **Progress Tracking**: Maintains history and current day status

## Project Structure

```
post_agent/
├── src/
│   ├── __init__.py
│   ├── agent.py              # Main LangGraph agent
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── content_generator.py
│   │   ├── approval_handler.py
│   │   └── linkedin_poster.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── linkedin_api.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── templates.py
│   └── utils/
│       ├── __init__.py
│       ├── scheduler.py
│       └── storage.py
├── data/
│   ├── curriculum.json       # 90-day AI topics
│   └── posted_history.json   # Track posted content
├── config/
│   └── settings.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `LINKEDIN_ACCESS_TOKEN`: LinkedIn OAuth access token
- `LINKEDIN_PERSON_ID`: Your LinkedIn person URN

### 3. LinkedIn API Setup

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Create an application
3. Request access to "Share on LinkedIn" and "Sign In with LinkedIn"
4. Generate an access token with `w_member_social` scope

## Usage

### Run the Agent

```bash
python main.py
```

### Commands

- `start` - Start the 90-day posting schedule
- `generate` - Generate today's post for preview
- `approve` - Approve and post today's content
- `reject` - Reject and regenerate content
- `status` - View current progress
- `history` - View posting history
- `quit` - Exit the agent

## How It Works

1. **Scheduler**: Triggers at 10 AM daily
2. **Content Generator**: Creates story-style post based on curriculum
3. **Approval Handler**: Presents content for user approval
4. **LinkedIn Poster**: Posts approved content to LinkedIn
5. **Storage**: Records posted content to prevent duplicates

## Curriculum Topics (90 Days)

### Week 1-2: AI Fundamentals
- What is AI?, History, Types of AI, ML basics...

### Week 3-4: Machine Learning Core
- Supervised/Unsupervised learning, Neural Networks...

### Week 5-6: Deep Learning
- CNNs, RNNs, Transformers...

### Week 7-8: NLP & Computer Vision
- Text processing, Image recognition...

### Week 9-10: Advanced Topics
- Reinforcement Learning, GANs, Diffusion Models...

### Week 11-12: Cutting Edge
- LLMs, RAG, Agents, Multimodal AI...

### Week 13: Future & Ethics
- AI Safety, Regulations, Future trends...

## License

MIT License
