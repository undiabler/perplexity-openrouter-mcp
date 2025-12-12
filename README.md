# Perplexity MCP (OpenRouter)

Model Context Protocol (MCP) tools for web search using Perplexity models via OpenRouter.

## Motivation

Perplexity models excel at finding information online, but they present several challenges:

- **Output formatting**: These models are extremely difficult to prompt for specific formats and desired outputs
- **Metadata preservation**: Many environments like Claude, OpenCode, or n8n can't be easily configured to preserve additional outputs like source URLs
- **Credential management**: Managing dozens of separate credentials across different services is cumbersome

This wrapper solves these problems by providing access through the universal OpenRouter provider, with the ability to customize and preserve all output information. It integrates seamlessly as a remote MCP tool for any LLM agent.

## Features

- Remote MCP server with simple authentication
- Tool naming compatible with the [official Perplexity MCP](https://docs.perplexity.ai/guides/mcp-server#available-tools)