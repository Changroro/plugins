---
description: Launch blog-writer agent to create a technical blog post
---

Use the Task tool with subagent_type='blog-writer' to create a well-structured, human-like technical blog post.

User input: $ARGUMENTS

Expected input format: "[주제] [참고URL] [format: markdown|html] [optional: output_path]"

Examples:
- "MCP 프로토콜 https://modelcontextprotocol.io markdown"
- "FastAPI 시작하기 https://fastapi.tiangolo.com html"
- "Docker 입문 https://docs.docker.com markdown /home/user/my_blog/"

Output path:
- Default: Uses config.json settings ({obsidian_base}/{blog_path}/)
- Custom: Specify absolute path as last argument to override

The agent will:
1. Research the provided URLs
2. Structure the content logically
3. Write in natural Korean conversational tone (~한다/~된다 체)
4. Save to configured or specified path
