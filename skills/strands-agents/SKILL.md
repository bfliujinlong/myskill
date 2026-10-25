---
name: strands-agents
description: Build AI agents with Strands Agents SDK.
license: MIT
metadata:
  version: "1.0"
  author: jinlongliu
---

# Strands Agents SDK

Open-source AI Agent SDK by AWS. Library-level integration — runs inside your own process.

## Installation

```bash
pip install strands-agents
npm install @strands-agents/sdk
```

## Core Patterns

### Agent
```python
from strands import Agent, tool

@tool
def search_logs(query: str, hours: int = 24) -> list:
    return log_api.search(query, hours)

agent = Agent(system_prompt="...", tools=[search_logs])
result = agent("Find timeout errors")
```

```typescript
import { Agent, tool } from '@strands-agents/sdk'
import z from 'zod'

const searchLogs = tool({
  name: 'search_logs',
  description: 'Search logs.',
  inputSchema: z.object({ query: z.string(), hours: z.number().default(24) }),
  callback: ({ query, hours }) => logApi.search(query, hours),
})
const agent = new Agent({ systemPrompt: '...', tools: [searchLogs] })
const result = await agent.invoke('Find timeout errors')
```

### Hooks
```python
from strands.hooks import BeforeToolCallEvent

def require_sources(event: BeforeToolCallEvent):
    if event.tool_use["name"] == "save_report" and "[source]" not in str(event.tool_use["input"]):
        event.cancel_tool = "Add citations."

agent = Agent(tools=[save_report], hooks=[require_sources])
```

### Structured Output
```python
from pydantic import BaseModel, Field
class Briefing(BaseModel):
    headline: str = Field(description="Summary")
    developments: list[str] = Field(description="Key events")
agent = Agent(system_prompt="...", tools=[http_request])
result = agent("What happened?", structured_output_model=Briefing)
```

### Conversation Management
```python
from strands.agent import SummarizingConversationManager, SlidingWindowConversationManager
agent = Agent(tools=[...], conversation_manager=SummarizingConversationManager())
```

### Multi-Agent
```python
from strands.multi_agent import Swarm, Graph, Workflow
swarm = Swarm([agent_a, agent_b])
result = swarm("Collaborate")
```

### Model Providers
```python
# Bedrock (default), OpenAI, Anthropic, Google, Ollama, LiteLLM
from strands.models.openai import OpenAIModel
agent = Agent(model=OpenAIModel(model_id="gpt-4o"))
```

### Observability
```python
from strands.telemetry import StrandsTelemetry
telemetry = StrandsTelemetry()
telemetry.setup()
```

### MCP
```bash
claude mcp add strands uvx strands-agents-mcp-server
```

## Resources
- Docs: https://strandsagents.com/docs/
- GitHub: https://github.com/strands-agents/harness-sdk