"""Prompt templates for content generation."""

STORY_GENERATION_PROMPT = """You are an expert AI educator and storyteller. Your task is to create an engaging LinkedIn post about an AI concept that reads like a captivating story.

## Today's Topic Information:
- **Day**: {day} of 90
- **Topic**: {topic}
- **Category**: {category}
- **Difficulty Level**: {difficulty}
- **Key Points to Cover**: {key_points}
- **Story Angle**: {story_angle}

## Previous Posts Summary (for continuity):
{previous_posts_summary}

## Guidelines:

1. **Story Format**: Start with a hook - a relatable scenario, question, or mini-story that draws readers in
2. **Educational Value**: Weave the technical concepts naturally into the narrative
3. **Progression**: Build on previous days' concepts when applicable
4. **Engagement**: Include a thought-provoking question or call-to-action at the end
5. **Accessibility**: Explain complex concepts using simple analogies
6. **Length**: Keep it between 500-2500 characters (LinkedIn optimal)
7. **Structure**: Use short paragraphs, emojis sparingly for visual breaks
8. **Voice**: Professional yet conversational, passionate about AI

## Format:
- Start with an attention-grabbing opening line
- Use 2-3 short paragraphs for the story/explanation
- Include 1-2 real-world examples or applications
- End with a reflection question or teaser for tomorrow
- Add a separator line before hashtags

## DO NOT:
- Use overly technical jargon without explanation
- Make it feel like a textbook
- Include code snippets
- Use more than 5 hashtags
- Exceed 3000 characters

Write the complete LinkedIn post now:
"""

HASHTAG_PROMPT = """Based on the following LinkedIn post about AI, generate exactly 5 relevant and popular hashtags.
The hashtags should be a mix of:
- Broad AI/Tech hashtags (for reach)
- Specific topic hashtags (for relevance)
- Community hashtags (for engagement)

Post content:
{post_content}

Return only the hashtags, space-separated, starting with #. Example: #AI #MachineLearning #TechEducation #DataScience #FutureOfWork
"""

CONTINUATION_PROMPT = """Based on your previous posts in this 90-day AI journey, here's a brief summary to maintain continuity:

{summary}

Today is Day {day}, and we're covering: {topic}

Make sure to:
1. Reference relevant concepts from previous days when applicable
2. Build upon the learning progression
3. Remind readers this is part of a 90-day journey
4. Create anticipation for what's coming next
"""

APPROVAL_MESSAGE_TEMPLATE = """
╔══════════════════════════════════════════════════════════════════╗
║                    📝 DAILY POST READY FOR REVIEW                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Day {day}/90 | Topic: {topic}
║  Category: {category} | Difficulty: {difficulty}
╠══════════════════════════════════════════════════════════════════╣

{content}

╠══════════════════════════════════════════════════════════════════╣
║  Character Count: {char_count}
║  Generated At: {timestamp}
╚══════════════════════════════════════════════════════════════════╝

Commands:
  [A]pprove - Post to LinkedIn
  [R]eject  - Regenerate content
  [E]dit    - Manually edit before posting
  [S]kip    - Skip today's post
  [Q]uit    - Exit without posting

Your choice: """
