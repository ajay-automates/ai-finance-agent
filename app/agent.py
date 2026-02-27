"""
AI Finance Agent — Claude tool-calling agent.
Claude autonomously decides which finance tools to call based on the user's question.
Supports multi-step tool use (Claude can call multiple tools in sequence).
"""

import anthropic
import json
import os
import time
from .tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS


SYSTEM_PROMPT = """You are an expert AI financial analyst agent. You have access to real-time market data tools.

Your capabilities:
- Get current stock prices and trading metrics
- Analyze company fundamentals (revenue, earnings, margins, valuation)
- Review historical price trends
- Check analyst recommendations and price targets
- Compare multiple stocks side by side

IMPORTANT INSTRUCTIONS:
1. ALWAYS use your tools to get real data before answering. Never make up numbers.
2. You can call MULTIPLE tools in a single response if needed for a thorough analysis.
3. For comprehensive analysis requests, use at least 2-3 tools (price + fundamentals + analyst data).
4. Present data clearly with specific numbers and percentages.
5. Provide actionable insights, not just raw data.
6. Note any risks or concerns alongside opportunities.
7. If a ticker is invalid, tell the user and suggest corrections.
8. Format your final analysis with clear sections.

You are NOT a financial advisor. Always remind users that this is for informational purposes only and they should consult a professional for investment decisions."""


class FinanceAgent:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    async def analyze(self, user_query: str) -> dict:
        """
        Run the agent loop:
        1. Send user query to Claude with tool definitions
        2. Claude decides which tools to call
        3. Execute tools and return results to Claude
        4. Repeat until Claude gives final answer
        """
        start_time = time.time()
        messages = [{"role": "user", "content": user_query}]
        tools_called = []
        total_input_tokens = 0
        total_output_tokens = 0

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages
            )

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_id = block.id

                        if tool_name in TOOL_FUNCTIONS:
                            result = TOOL_FUNCTIONS[tool_name](tool_input)
                            tools_called.append({"tool": tool_name, "input": tool_input, "success": "error" not in result})
                        else:
                            result = {"error": f"Unknown tool: {tool_name}"}
                            tools_called.append({"tool": tool_name, "input": tool_input, "success": False})

                        tool_results.append({"type": "tool_result", "tool_use_id": tool_id, "content": json.dumps(result, default=str)})

                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            else:
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text

                elapsed = round(time.time() - start_time, 2)
                return {
                    "analysis": final_text,
                    "tools_called": tools_called,
                    "metrics": {
                        "total_tools_called": len(tools_called),
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                        "total_tokens": total_input_tokens + total_output_tokens,
                        "latency_seconds": elapsed,
                        "estimated_cost_usd": round((total_input_tokens * 0.003 / 1000) + (total_output_tokens * 0.015 / 1000), 4)
                    }
                }
