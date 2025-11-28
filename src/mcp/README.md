# MCP Server

This directory contains the MCP (Model Context Protocol) server implementation.

## Files

- `server.py` - Main MCP server implementation with all Rider-Pi tools

## Usage

```bash
# Run MCP server
python3 src/mcp/server.py

# Or via stdio for MCP clients
python3 src/mcp/server.py < input.json > output.json
```

## Configuration

Set environment variables:

```bash
export RIDER_PI_HOST="riderpi.local"
export RIDER_PI_USER="pi"
export RIDER_PI_SSH_KEY="~/.ssh/rider_pi_key"
export RIDER_PI_TIMEOUT="10"
```

## Integration

See [Setup Guide](../../docs/setup/SETUP.md) for integration with Letta or other MCP clients.

