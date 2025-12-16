# Perplexity MCP (OpenRouter)

Model Context Protocol (MCP) tools for web search using Perplexity models via OpenRouter.

## Motivation

[Perplexity models](https://openrouter.ai/perplexity) excel at finding information online, but they present several challenges:

- **Output formatting**: These models are extremely difficult to prompt for specific formats and desired outputs
- **Metadata preservation**: Many environments like Claude, OpenCode, or n8n can't be easily configured to preserve additional outputs like source URLs
- **Yet another one credentials**: Managing dozens of separate credentials across different services is cumbersome

This wrapper solves these problems by providing access through the universal OpenRouter provider, with the ability to preserve all output information. The server is designed for remote use and easy connection to most of [MCP clients](https://modelcontextprotocol.io/clients). 

## Features

- Remote MCP server with simple authentication
- Tool naming compatible with the [official Perplexity MCP](https://docs.perplexity.ai/guides/mcp-server#available-tools)

## Installation and Usage

This system was designed to run remotely, making Docker the ideal standard for packaging the project without worrying about dependencies. Docker also enables easy horizontal scaling by running multiple container instances.

### Quick Start (Remote Build)

Build directly from GitHub on your remote server:

```bash
docker build -t perplexity-mcp https://github.com/undiabler/perplexity-openrouter-mcp.git
```

### Local Build

Alternatively, clone the repository and build locally:

```bash
git clone https://github.com/undiabler/perplexity-openrouter-mcp.git
cd perplexity-openrouter-mcp
docker build -t perplexity-mcp .
```

### Running the Server

Once the Docker image is built, run the container:

```bash
docker run -d -p 8001:8001 --name perplexity-mcp-app \
  -e OPENROUTER_API_KEY=<your api key> \
  -e MCP_BEARER_TOKEN=<your generated key to secure> \
  perplexity-mcp
```

That's it! Your MCP server is now running and accessible at `http://your-server-ip:8001` as an endpoint for MCP clients.

### Environment Variables

- `OPENROUTER_API_KEY` - Your OpenRouter API key (required)
- `MCP_BEARER_TOKEN` - Bearer token for securing your MCP endpoint (required, can be any string)

