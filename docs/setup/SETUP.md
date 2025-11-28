# 🚀 Rider-Pi MCP Setup Guide

Complete setup guide for integrating Rider-Pi robot with AI agents via MCP.

## Prerequisites

- Python 3.8 or higher
- SSH access to Rider-Pi robot
- MCP-compatible AI agent (e.g., Letta, Claude Desktop)
- Rider-Pi robot with network connectivity

## Step 1: Install Dependencies

```bash
# Install MCP SDK
pip install mcp

# Verify installation
python3 -c "import mcp; print('MCP installed successfully')"
```

## Step 2: Configure SSH Access

### 2.1 Generate SSH Key (if not already done)

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -f ~/.ssh/rider_pi_key

# Copy public key to Rider-Pi
ssh-copy-id -i ~/.ssh/rider_pi_key.pub pi@riderpi.local
```

### 2.2 Test SSH Connection

```bash
# Test connection
ssh -i ~/.ssh/rider_pi_key pi@riderpi.local "echo 'Connection successful'"
```

## Step 3: Configure Environment Variables

Create a `.env` file or set environment variables:

```bash
export RIDER_PI_HOST="riderpi.local"
export RIDER_PI_USER="pi"
export RIDER_PI_SSH_KEY="~/.ssh/rider_pi_key"
export RIDER_PI_TIMEOUT="10"
```

Or create a `.env` file:

```env
RIDER_PI_HOST=riderpi.local
RIDER_PI_USER=pi
RIDER_PI_SSH_KEY=~/.ssh/rider_pi_key
RIDER_PI_TIMEOUT=10
```

## Step 4: Test MCP Server

### 4.1 Run MCP Server Manually

```bash
# Navigate to project directory
cd rider-pi-mcp

# Run MCP server
python3 src/mcp/server.py
```

### 4.2 Test with MCP Client

```bash
# Install MCP client (if needed)
pip install mcp-client

# Test connection
mcp-client --server python3 --args src/mcp/server.py
```

## Step 5: Integrate with Letta

### 5.1 Via Letta Dashboard

1. Go to Letta Dashboard
2. Navigate to MCP Servers
3. Click "Add MCP Server"
4. Configure:
   - **Name:** `rider-pi-mcp`
   - **Type:** `stdio`
   - **Command:** `python3`
   - **Args:** `["/path/to/rider-pi-mcp/src/mcp/server.py"]`
   - **Environment Variables:**
     - `RIDER_PI_HOST=riderpi.local`
     - `RIDER_PI_USER=pi`
     - `RIDER_PI_SSH_KEY=~/.ssh/rider_pi_key`
     - `RIDER_PI_TIMEOUT=10`

### 5.2 Via Letta Python SDK

```python
from letta import Letta

client = Letta(api_key="your-api-key")

# Create MCP Server Connection
mcp_server = client.mcp_servers.create(
    server_name="rider-pi-mcp",
    config={
        "mcp_server_type": "stdio",
        "command": "python3",
        "args": ["/path/to/rider-pi-mcp/src/mcp/server.py"],
        "env": {
            "RIDER_PI_HOST": "riderpi.local",
            "RIDER_PI_USER": "pi",
            "RIDER_PI_SSH_KEY": "~/.ssh/rider_pi_key",
            "RIDER_PI_TIMEOUT": "10"
        }
    }
)

# Get all tools
tools = client.mcp_servers.tools.list(mcp_server.id)

# Attach tools to agent
agent = client.agents.get("your-agent-id")
for tool in tools:
    agent.tools.attach(tool.id)
```

## Step 6: Setup Code Execution API

### 6.1 Make Code API Available

For Code Execution, the `rider_pi_code_api` module must be importable:

```python
# Option 1: Add to Python path
import sys
sys.path.append('/path/to/rider-pi-mcp/src/code_api')

# Option 2: Install as package
cd rider-pi-mcp
pip install -e .
```

### 6.2 Enable Code Execution in Letta

1. Go to Agent Settings
2. Enable "Code Execution"
3. Configure execution environment
4. Add `rider_pi_code_api` to available modules

### 6.3 Test Code Execution

```python
# In Code Execution environment
import rider_pi_code_api as rp

# Test basic functions
rp.move_forward(1.0, 0.5)
battery = rp.get_battery_level()
print(f"Battery: {battery}%")
```

## Step 7: Verify Installation

### 7.1 Test Basic Movement

```python
# Via MCP Tool
# Ask your agent: "Move the robot forward for 2 seconds"

# Via Code Execution
import rider_pi_code_api as rp
rp.move_forward(2.0, 0.5)
```

### 7.2 Test Sensor Reading

```python
# Via MCP Tool
# Ask your agent: "What is the battery level?"

# Via Code Execution
import rider_pi_code_api as rp
battery = rp.get_battery_level()
print(f"Battery: {battery}%")
```

### 7.3 Test Image Capture

```python
# Via MCP Tool
# Ask your agent: "Take a photo"

# Via Code Execution
import rider_pi_code_api as rp
image_path = rp.capture_image()
print(f"Image saved to: {image_path}")
```

## Troubleshooting

### SSH Connection Issues

```bash
# Test SSH connection
ssh -v -i ~/.ssh/rider_pi_key pi@riderpi.local

# Check SSH key permissions
chmod 600 ~/.ssh/rider_pi_key

# Verify hostname resolution
ping riderpi.local
```

### MCP Server Not Starting

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check MCP installation
pip show mcp

# Run with verbose output
python3 -v src/mcp/server.py
```

### Code Execution Not Working

```bash
# Verify Code API is importable
python3 -c "import sys; sys.path.append('src/code_api'); import rider_pi; print('OK')"

# Check file permissions
ls -la src/code_api/rider_pi.py
```

### Letta Integration Issues

1. Check MCP Server is registered correctly
2. Verify environment variables are set
3. Check Letta logs for errors
4. Test MCP Server manually first

## Next Steps

- Read the [Roadmap](planning/ROADMAP.md) for planned features
- Check [Architecture](architecture/) documentation
- Explore [Examples](../examples/) for usage patterns

## Resources

- **Official Rider-Pi Repository:** [YahboomTechnology/Rider-Pi-Robot](https://github.com/YahboomTechnology/Rider-Pi-Robot)
- **Rider-Pi Documentation:** See the [official repository](https://github.com/YahboomTechnology/Rider-Pi-Robot) for manufacturer documentation, tutorials, and examples
- **Product Page:** [Yahboom Rider-Pi](https://category.yahboom.net/products/rider-pi)

## Support

- **Issues:** [GitHub Issues](https://github.com/Duzafizzl/rider-pi-publicproject/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Duzafizzl/rider-pi-publicproject/discussions)

---

**Last Updated:** 2025-01-XX

