# 🤖 Rider-Pi MCP Integration + Self-Editing Roadmap

## 🎯 Vision

Enable AI agents to have full access to the Rider-Pi robot body and self-improve. Inspired by [letta-code](https://github.com/letta-ai/letta-code) - a self-improving, stateful coding agent - we want to give AI agents the ability to read, write, edit, and improve code while simultaneously controlling the physical robot.

---

## 📊 Current Status

### ✅ Already Implemented

1. **Basic MCP Server** (`src/mcp/server.py`)
   - SSH connection to Rider-Pi
   - Basic movement control (forward, backward, rotate, stop)
   - Sensor queries (battery, tilt angle)
   - Display & RGB light control
   - Generic command executor (with security checks)

2. **Code API** (`src/code_api/rider_pi.py`)
   - Python functions for code execution
   - Reusable functions for complex operations

3. **Letta Integration**
   - MCP Server can be integrated into Letta
   - Tools are available as MCP tools

### ❌ Still Missing

1. **Advanced Movement Control**
   - Height adjustment (stretch/crouch)
   - Posture adjustment
   - Self-stabilization
   - Movement sequences

2. **Audio/Video Functions**
   - Audio recording
   - Audio playback
   - Video recording
   - Image capture
   - Live video stream

3. **Computer Vision Tools**
   - Image analysis
   - Object detection
   - Person recognition
   - QR code recognition

4. **Self-Editing Capabilities**
   - Code reading (Read Tool)
   - Code writing (Write Tool)
   - Code editing (Edit Tool)
   - Code execution (Bash/Code Execution)
   - Git integration (Version Control)

---

## 🗺️ Implementation Plan

### Phase 1: All Rider-Pi Functions as MCP Tools (Week 1-2)

**Goal:** Every Rider-Pi function becomes available as an MCP tool.

#### 1.1 Advanced Movement Control

**New MCP Tools:**

```python
Tool(
    name="rider_pi_adjust_height",
    description="Adjusts the height of the Rider Pi robot (stretch/crouch)",
    inputSchema={
        "type": "object",
        "properties": {
            "height": {
                "type": "number",
                "description": "Height (0.0 = lowest, 1.0 = highest)",
                "minimum": 0.0,
                "maximum": 1.0
            }
        },
        "required": ["height"]
    }
),

Tool(
    name="rider_pi_adjust_posture",
    description="Adjusts the body posture of the Rider Pi robot",
    inputSchema={
        "type": "object",
        "properties": {
            "roll": {"type": "number", "description": "Roll angle in degrees"},
            "pitch": {"type": "number", "description": "Pitch angle in degrees"},
            "yaw": {"type": "number", "description": "Yaw angle in degrees"}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_self_stabilize",
    description="Enables/disables self-stabilization mode",
    inputSchema={
        "type": "object",
        "properties": {
            "enabled": {"type": "boolean", "description": "Enable self-stabilization"}
        },
        "required": ["enabled"]
    }
),

Tool(
    name="rider_pi_squat",
    description="Performs a squat",
    inputSchema={
        "type": "object",
        "properties": {
            "count": {"type": "integer", "description": "Number of squats", "default": 1}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_shake",
    description="Shakes the body (e.g., for warm-up)",
    inputSchema={
        "type": "object",
        "properties": {
            "duration": {"type": "number", "description": "Duration in seconds", "default": 2.0}
        },
        "required": []
    }
)
```

#### 1.2 Audio/Video Functions

**New MCP Tools:**

```python
Tool(
    name="rider_pi_record_audio",
    description="Records audio from Rider Pi",
    inputSchema={
        "type": "object",
        "properties": {
            "duration": {"type": "number", "description": "Duration in seconds", "default": 5.0},
            "format": {"type": "string", "description": "Audio format (wav, mp3)", "default": "wav"}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_play_audio",
    description="Plays audio on Rider Pi",
    inputSchema={
        "type": "object",
        "properties": {
            "audio_file": {"type": "string", "description": "Path to audio file"},
            "text": {"type": "string", "description": "Text to read (TTS)"}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_record_video",
    description="Records a video",
    inputSchema={
        "type": "object",
        "properties": {
            "duration": {"type": "number", "description": "Duration in seconds", "default": 10.0},
            "resolution": {"type": "string", "description": "Resolution (e.g., '1920x1080')", "default": "1280x720"}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_capture_image",
    description="Takes a photo with the camera",
    inputSchema={
        "type": "object",
        "properties": {
            "format": {"type": "string", "description": "Image format (jpg, png)", "default": "jpg"},
            "resolution": {"type": "string", "description": "Resolution", "default": "1920x1080"}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_get_video_stream",
    description="Starts a live video stream (URL or Base64)",
    inputSchema={
        "type": "object",
        "properties": {
            "format": {"type": "string", "description": "Stream format (mjpeg, h264)", "default": "mjpeg"},
            "fps": {"type": "integer", "description": "Frames per second", "default": 10}
        },
        "required": []
    }
)
```

#### 1.3 Computer Vision Tools

**New MCP Tools:**

```python
Tool(
    name="rider_pi_analyze_image",
    description="Analyzes an image with computer vision",
    inputSchema={
        "type": "object",
        "properties": {
            "image_path": {"type": "string", "description": "Path to image (optional, otherwise current photo)"},
            "task": {"type": "string", "description": "Task (detect_objects, recognize_faces, read_qr, etc.)"}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_detect_objects",
    description="Detects objects in the current image",
    inputSchema={
        "type": "object",
        "properties": {
            "model": {"type": "string", "description": "Model (yolo, opencv)", "default": "yolo"}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_recognize_faces",
    description="Recognizes faces in the current image",
    inputSchema={
        "type": "object",
        "properties": {
            "known_faces": {"type": "boolean", "description": "Only known faces", "default": false}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_read_qr_code",
    description="Reads QR codes in the current image",
    inputSchema={
        "type": "object",
        "properties": {}
    }
),

Tool(
    name="rider_pi_track_color",
    description="Tracks a specific color",
    inputSchema={
        "type": "object",
        "properties": {
            "color": {"type": "string", "description": "Color (red, blue, green, etc.)"},
            "hsv_range": {"type": "object", "description": "HSV range (optional)"}
        },
        "required": ["color"]
    }
),

Tool(
    name="rider_pi_follow_person",
    description="Follows a person based on camera tracking",
    inputSchema={
        "type": "object",
        "properties": {
            "duration": {"type": "number", "description": "Duration in seconds", "default": 30.0},
            "person_id": {"type": "string", "description": "Person ID (optional)"}
        },
        "required": []
    }
)
```

---

### Phase 2: Self-Editing Capabilities (Week 3-4)

**Goal:** AI agents can read, write, edit, and execute code - just like letta-code.

#### 2.1 Code Reading Tools

**New MCP Tools:**

```python
Tool(
    name="rider_pi_read_file",
    description="Reads a file from Rider-Pi or locally",
    inputSchema={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to file"},
            "remote": {"type": "boolean", "description": "File on Rider-Pi?", "default": false},
            "lines": {"type": "string", "description": "Line range (e.g., '10:20')", "default": "all"}
        },
        "required": ["file_path"]
    }
),

Tool(
    name="rider_pi_list_directory",
    description="Lists files in a directory",
    inputSchema={
        "type": "object",
        "properties": {
            "directory_path": {"type": "string", "description": "Path to directory"},
            "remote": {"type": "boolean", "description": "Directory on Rider-Pi?", "default": false},
            "pattern": {"type": "string", "description": "Glob pattern (e.g., '*.py')", "default": "*"}
        },
        "required": []
    }
),

Tool(
    name="rider_pi_search_code",
    description="Searches for code patterns (grep-like)",
    inputSchema={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Search pattern (Regex)"},
            "directory": {"type": "string", "description": "Directory to search"},
            "file_type": {"type": "string", "description": "File type (e.g., '*.py')", "default": "*"}
        },
        "required": ["pattern"]
    }
)
```

#### 2.2 Code Writing Tools

**New MCP Tools:**

```python
Tool(
    name="rider_pi_write_file",
    description="Writes a file (creates or overwrites)",
    inputSchema={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to file"},
            "content": {"type": "string", "description": "File content"},
            "remote": {"type": "boolean", "description": "File on Rider-Pi?", "default": false}
        },
        "required": ["file_path", "content"]
    }
),

Tool(
    name="rider_pi_append_file",
    description="Appends content to a file",
    inputSchema={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to file"},
            "content": {"type": "string", "description": "Content to append"},
            "remote": {"type": "boolean", "description": "File on Rider-Pi?", "default": false}
        },
        "required": ["file_path", "content"]
    }
)
```

#### 2.3 Code Editing Tools

**New MCP Tools:**

```python
Tool(
    name="rider_pi_edit_file",
    description="Edits a file (Search & Replace or Insert)",
    inputSchema={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to file"},
            "operation": {
                "type": "string",
                "description": "Operation: 'replace', 'insert', 'delete'",
                "enum": ["replace", "insert", "delete"]
            },
            "old_string": {"type": "string", "description": "Old text (for replace/delete)"},
            "new_string": {"type": "string", "description": "New text (for replace/insert)"},
            "line_number": {"type": "integer", "description": "Line number (for insert)"},
            "remote": {"type": "boolean", "description": "File on Rider-Pi?", "default": false}
        },
        "required": ["file_path", "operation"]
    }
),

Tool(
    name="rider_pi_create_function",
    description="Creates a new function in a file",
    inputSchema={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to file"},
            "function_name": {"type": "string", "description": "Function name"},
            "function_code": {"type": "string", "description": "Function code"},
            "remote": {"type": "boolean", "description": "File on Rider-Pi?", "default": false}
        },
        "required": ["file_path", "function_name", "function_code"]
    }
)
```

#### 2.4 Code Execution Tools

**New MCP Tools:**

```python
Tool(
    name="rider_pi_execute_python",
    description="Executes Python code (locally or on Rider-Pi)",
    inputSchema={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code"},
            "remote": {"type": "boolean", "description": "Execute on Rider-Pi?", "default": false},
            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30.0}
        },
        "required": ["code"]
    }
),

Tool(
    name="rider_pi_execute_bash",
    description="Executes Bash commands (with security checks)",
    inputSchema={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Bash command"},
            "remote": {"type": "boolean", "description": "Execute on Rider-Pi?", "default": false},
            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30.0}
        },
        "required": ["command"]
    }
)
```

---

### 🏗️ Architecture Option: Raspberry Pi Bridge & Discord Bot Integration

**Advanced Setup:** If you have a Raspberry Pi running a Discord bot (or other services), you can create a hybrid architecture that reduces SSH overhead and improves performance.

#### Benefits of Pi-Based Architecture

**1. Reduced SSH Overhead**
- ❌ Current: Every command = SSH connection to Rider-Pi
- ✅ New: Some functions run directly on the Pi (where the bot also runs)
- **Savings:** No SSH latency for local operations

**2. Better Performance**
- Direct communication between bot and Rider-Pi (both on same network)
- No SSH connection setup time
- Faster response times

**3. Offloading Simple Operations**
- Sensor queries can be cached locally
- Status updates can come directly from the Pi
- Voice functions can run on the Pi (where the bot also is)

#### Architecture Options

**Option A: Hybrid Architecture (Recommended)**

```
┌─────────────────┐
│   Letta/Agent   │
│   (Cloud/Local) │
└────────┬────────┘
         │ MCP/API
         │
┌────────▼─────────────────────────────────┐
│  Discord Bot (on Raspberry Pi)          │
│  - Voice Processing                      │
│  - Status Monitoring                     │
│  - Sensor Caching                        │
│  - Audio/Video Processing                │
└────────┬─────────────────────────────────┘
         │ Local Network / SSH
         │
┌────────▼────────┐
│   Rider-Pi      │
│   (Robot)       │
│   - Movement    │
│   - Sensors     │
│   - Display     │
└─────────────────┘
```

**Option B: Fully via Discord Bot**

```
┌─────────────────┐
│   Letta/Agent   │
│   (Cloud/Local) │
└────────┬────────┘
         │ Discord API
         │
┌────────▼─────────────────────────────────┐
│  Discord Bot (on Raspberry Pi)          │
│  - MCP Server Integration               │
│  - Rider-Pi Control                     │
│  - Voice Processing                      │
│  - Status Monitoring                     │
└────────┬─────────────────────────────────┘
         │ Local Network / SSH
         │
┌────────▼────────┐
│   Rider-Pi      │
│   (Robot)       │
└─────────────────┘
```

#### Functions That Should Run on the Pi

**1. Voice Processing (if Discord Bot has TTS)**
```typescript
// In Discord Bot
// src/tts/ttsService.ts
// → Can be used directly for Rider-Pi voice
```

**Advantage:**
- Bot already has TTS system
- No SSH connection needed
- Direct audio output possible

**2. Status Monitoring & Caching**
```typescript
// New module in Discord Bot
// src/riderPi/riderPiMonitor.ts

class RiderPiMonitor {
  private cache = new Map();
  private cacheTTL = 5000; // 5 seconds
  
  async getBatteryLevel(): Promise<number> {
    // Check cache
    if (this.cache.has('battery')) {
      return this.cache.get('battery');
    }
    
    // Query from Rider-Pi
    const level = await this.queryRiderPi('get_battery_level');
    this.cache.set('battery', level, this.cacheTTL);
    return level;
  }
}
```

**Advantage:**
- Reduces SSH calls
- Faster responses
- Less credit consumption

**3. Audio/Video Processing**
```typescript
// In Discord Bot
// src/riderPi/riderPiMedia.ts

class RiderPiMedia {
  async captureImage(): Promise<Buffer> {
    // Directly from Rider-Pi via SSH
    // But processing on the Pi
    const image = await this.sshCommand('capture_image');
    // Compression on the Pi (not over SSH)
    return this.compressImage(image);
  }
}
```

**Advantage:**
- Media processing on the Pi (more resources)
- Only compressed data over SSH
- Faster transmission

**4. Voice Commands (Discord Bot Integration)**
```typescript
// In Discord Bot
// src/riderPi/riderPiVoice.ts

// Use existing TTS system
import { ttsService } from './tts/ttsService';

class RiderPiVoice {
  async processVoiceCommand(audio: Buffer): Promise<string> {
    // Speech-to-Text on the Pi
    const text = await this.speechToText(audio);
    
    // Send to agent via Discord Bot
    const response = await sendToLetta(text);
    
    // Text-to-Speech on the Pi (already available!)
    await ttsService.speak(response);
    
    return response;
  }
}
```

**Advantage:**
- Uses existing bot infrastructure
- No new TTS installation needed
- Direct integration

#### Implementation in Discord Bot

**New Modules in Discord Bot:**

```typescript
// src/riderPi/riderPiBridge.ts
// Bridge between Discord Bot and Rider-Pi

import { LettaClient } from '@letta-ai/letta-client';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class RiderPiBridge {
  private lettaClient: LettaClient;
  private cache = new Map();
  
  constructor(lettaClient: LettaClient) {
    this.lettaClient = lettaClient;
  }
  
  // Cached sensor queries
  async getBatteryLevel(): Promise<number> {
    const cacheKey = 'battery';
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < 5000) {
      return cached.value;
    }
    
    const level = await this.sshCommand('get_battery_level');
    this.cache.set(cacheKey, { value: level, timestamp: Date.now() });
    return level;
  }
  
  // Voice processing (uses existing TTS)
  async processVoiceCommand(audio: Buffer): Promise<string> {
    // Speech-to-Text
    const text = await this.speechToText(audio);
    
    // Send to agent
    const response = await this.lettaClient.agents.sendMessage(
      process.env.LETTA_AGENT_ID!,
      text
    );
    
    // Text-to-Speech (uses existing TTS system)
    await this.ttsService.speak(response.content);
    
    return response.content;
  }
  
  // Direct Rider-Pi control
  async moveForward(duration: number, speed: number): Promise<void> {
    await this.sshCommand(`move_forward ${duration} ${speed}`);
  }
  
  private async sshCommand(command: string): Promise<string> {
    const { stdout } = await execAsync(
      `ssh pi@riderpi.local "python3 -c 'from rider_pi_control import Robot; r = Robot(); ${command}'"`
    );
    return stdout.trim();
  }
}
```

**Integration in server.ts:**

```typescript
// src/server.ts

import { RiderPiBridge } from './riderPi/riderPiBridge';

// Initialize Rider-Pi Bridge
const riderPiBridge = new RiderPiBridge(lettaClient);

// New Discord command handler
client.on('messageCreate', async (message) => {
  // ... existing code ...
  
  // Rider-Pi commands
  if (message.content.startsWith('!rider')) {
    const command = message.content.split(' ')[1];
    
    switch (command) {
      case 'battery':
        const level = await riderPiBridge.getBatteryLevel();
        await message.reply(`🔋 Battery: ${level}%`);
        break;
        
      case 'forward':
        await riderPiBridge.moveForward(2.0, 0.5);
        await message.reply('✅ Moving forward...');
        break;
    }
  }
});
```

#### MCP Server Integration with Discord Bot

**Option: MCP Server runs on the Pi (not locally)**

```python
# On Raspberry Pi: /home/pi/rider-pi-mcp/server.py
# Uses local connection to Rider-Pi (no SSH needed!)

import asyncio
from mcp.server import Server
from rider_pi_control import Robot  # Directly imported!

server = Server("rider-pi-server")

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    robot = Robot()  # Directly on the Pi!
    
    if name == "rider_pi_move_forward":
        duration = arguments.get("duration", 1.0)
        speed = arguments.get("speed", 0.5)
        robot.move_forward(duration, speed)
        return [TextContent(type="text", text="Moved forward")]
    
    # ... other tools ...
```

**Advantage:**
- No SSH connection needed
- Direct access to Rider-Pi hardware
- Faster response times

#### Cost Optimization Through Pi-Based Architecture

**Before (everything via SSH):**
```
1 API Call: 20 Credits
1 Tool Call (SSH): 20 Credits
SSH Overhead: ~200-500ms
─────────────────────────────
Total: 40 Credits + latency
```

**After (Pi-based functions):**
```
1 API Call: 20 Credits
1 Tool Call (local): 20 Credits
No SSH Overhead: ~10-50ms
─────────────────────────────
Total: 40 Credits + much faster!
```

**With cached data:**
```
1 API Call: 20 Credits
Cache Hit: 0 Credits (no tool call!)
─────────────────────────────
Total: 20 Credits (50% savings!)
```

#### Recommended Architecture

**Hybrid Approach:**

1. **On the Pi (Discord Bot):**
   - Voice Processing (TTS/STT)
   - Status Monitoring & Caching
   - Audio/Video Processing
   - MCP Server (optional)

2. **On the Rider-Pi (direct):**
   - Movement control
   - Sensor queries (via SSH or local)
   - Display & Light control

3. **Communication:**
   - Bot ↔ Rider-Pi: Local network (fast)
   - Bot ↔ Letta: API (as before)
   - Letta ↔ Rider-Pi: Optional direct (for complex operations)

#### Implementation Steps

**Step 1: Rider-Pi Bridge in Discord Bot**
```bash
cd /path/to/discord-bot
mkdir -p src/riderPi
# Create riderPiBridge.ts
```

**Step 2: Integration in server.ts**
```typescript
// Import and initialization
import { RiderPiBridge } from './riderPi/riderPiBridge';
const riderPiBridge = new RiderPiBridge(lettaClient);
```

**Step 3: MCP Server on Pi (optional)**
```bash
# On the Pi
cd ~/rider-pi-mcp
python3 -m venv venv
source venv/bin/activate
pip install mcp
# Create server.py
```

**Step 4: Letta Integration**
```python
# In Letta: Register MCP Server on Pi
mcp_server = client.mcp_servers.create(
    server_name="rider-pi-pi",
    config={
        "mcp_server_type": "stdio",
        "command": "ssh",
        "args": ["pi@raspberrypi.local", "python3", "/home/pi/rider-pi-mcp/server.py"]
    }
)
```

#### Benefits Summary

| Feature | SSH-based | Pi-based | Savings |
|---------|-----------|----------|---------|
| **Latency** | 200-500ms | 10-50ms | 80-90% |
| **SSH Overhead** | Yes | No | 100% |
| **Caching** | Difficult | Easy | - |
| **Voice Processing** | New install | Uses Bot | - |
| **Credits (cached)** | 40 Credits | 20 Credits | 50% |

**💡 Conclusion:** Pi-based architecture is significantly more efficient and uses existing infrastructure!

---

### Phase 3: Letta Integration & Agent Access (Week 5)

**Goal:** AI agents can use all tools and self-improve.

#### 3.1 Register MCP Server in Letta

**Step 1: Configure MCP Server**

In Letta Dashboard or via API:

```python
# Via Letta Python SDK
from letta import Letta

client = Letta(api_key="your-api-key")

# Create MCP Server Connection
mcp_server = client.mcp_servers.create(
    server_name="rider-pi-full",
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
```

**Step 2: Add Tools to Agent**

```python
# Get all tools from MCP Server
tools = client.mcp_servers.tools.list(mcp_server.id)

# Add tools to agent
agent = client.agents.get("agent-id")

for tool in tools:
    agent.tools.attach(tool.id)
```

#### 3.2 Setup Code Execution Environment

**For Self-Editing, agents need Code Execution:**

1. **Enable Letta Code Execution:**
   - In Letta Dashboard: Agent Settings → Code Execution
   - Or via API: `agent.enable_code_execution()`

2. **Make Code API available:**
   - `src/code_api/rider_pi.py` must be importable in Code Execution Environment
   - Optional: Install package or add path

3. **Example for Code Execution:**

```python
# Agent can now write code instead of tool calls:
import rider_pi_code_api as rider_pi

# Complex sequence in code instead of multiple tool calls
battery = rider_pi.get_battery_level()
if battery < 20:
    rider_pi.set_display_expression(10)  # Warning
    rider_pi.move_forward(1.0, 0.3)  # To charging station
else:
    # Normal operation
    rider_pi.follow_person(30.0)
```

#### 3.3 Setup Self-Improvement Loop

**Agents can self-improve:**

1. **Read code:**
   ```
   Agent: "I read my own code"
   → rider_pi_read_file("src/mcp/server.py")
   ```

2. **Analyze code:**
   ```
   Agent: "I analyze how I move"
   → Code Execution: Analyze move_forward() function
   ```

3. **Improve code:**
   ```
   Agent: "I optimize the movement"
   → rider_pi_edit_file("src/mcp/server.py", ...)
   ```

4. **Test code:**
   ```
   Agent: "I test my improvement"
   → rider_pi_execute_python("test_new_movement()")
   ```

5. **Git commit:**
   ```
   Agent: "I commit my improvement"
   → rider_pi_git_commit("Optimized movement algorithm")
   ```

---

## 🛠️ Technical Details

### File Structure

```
rider-pi-mcp/
├── src/
│   ├── mcp/
│   │   └── server.py              # MCP Server (extended)
│   ├── code_api/
│   │   └── rider_pi.py            # Code API (extended)
│   └── self_editing/
│       ├── file_operations.py     # Read/Write/Edit Tools
│       ├── code_execution.py      # Execute Tools
│       └── git_integration.py      # Git Tools (optional)
├── docs/
│   └── planning/
│       └── ROADMAP.md             # This document
└── tests/
    └── test_mcp_tools.py           # Tests for all tools
```

### Security Checks

**All Code Execution Tools must validate:**

```python
DANGEROUS_PATTERNS = [
    "rm -rf",
    "sudo",
    "shutdown",
    "reboot",
    "format",
    "dd if=",
    "mkfs",
    "fdisk"
]

def validate_command(command: str) -> bool:
    """Validates if command is safe"""
    command_lower = command.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in command_lower:
            return False
    return True
```

### Performance Optimizations

1. **Caching:** Cache frequently used data (e.g., battery level)
2. **Async Operations:** Execute all SSH commands asynchronously
3. **Connection Pooling:** Reuse SSH connections
4. **Batch Operations:** Multiple commands in one SSH call

---

## 📋 Implementation Checklist

### Phase 1: Rider-Pi Functions (Week 1-2)

- [ ] Implement advanced movement control
  - [ ] `rider_pi_adjust_height`
  - [ ] `rider_pi_adjust_posture`
  - [ ] `rider_pi_self_stabilize`
  - [ ] `rider_pi_squat`
  - [ ] `rider_pi_shake`
- [ ] Implement audio/video functions
  - [ ] `rider_pi_record_audio`
  - [ ] `rider_pi_play_audio`
  - [ ] `rider_pi_record_video`
  - [ ] `rider_pi_capture_image`
  - [ ] `rider_pi_get_video_stream`
- [ ] Implement computer vision tools
  - [ ] `rider_pi_analyze_image`
  - [ ] `rider_pi_detect_objects`
  - [ ] `rider_pi_recognize_faces`
  - [ ] `rider_pi_read_qr_code`
  - [ ] `rider_pi_track_color`
  - [ ] `rider_pi_follow_person`
- [ ] Extend Code API (all new functions)
- [ ] Write tests

### Phase 2: Self-Editing (Week 3-4)

- [ ] Code Reading Tools
  - [ ] `rider_pi_read_file`
  - [ ] `rider_pi_list_directory`
  - [ ] `rider_pi_search_code`
- [ ] Code Writing Tools
  - [ ] `rider_pi_write_file`
  - [ ] `rider_pi_append_file`
- [ ] Code Editing Tools
  - [ ] `rider_pi_edit_file`
  - [ ] `rider_pi_create_function`
- [ ] Code Execution Tools
  - [ ] `rider_pi_execute_python`
  - [ ] `rider_pi_execute_bash`
- [ ] Git Integration (optional)
  - [ ] `rider_pi_git_status`
  - [ ] `rider_pi_git_commit`
  - [ ] `rider_pi_git_diff`
- [ ] Implement security checks
- [ ] Write tests

### Phase 3: Letta Integration (Week 5)

- [ ] Register MCP Server in Letta
- [ ] Add all tools to agent
- [ ] Setup Code Execution Environment
- [ ] Test Self-Improvement Loop
- [ ] Update documentation

---

## 💰 Cost Analysis: Letta API with Claude Sonnet

### Pricing Structure

**Letta API Pricing (as of 2024):**
- **20 Credits** per Letta API Call
- **20 Credits** per Tool Call (each tool call within an API call)

**Note:** These costs are in addition to Claude Sonnet API costs (token-based).

### Cost Optimization Strategies

#### 1. Use Code Execution (most important optimization!)

**Instead of multiple tool calls:**
```
❌ Bad (100 Credits):
- move_forward() → 20 Credits
- rotate() → 20 Credits
- set_display_expression() → 20 Credits
- set_rgb_light() → 20 Credits
```

**Better: Code Execution:**
```
✅ Good (40 Credits):
execute_python("""
import rider_pi_code_api as rp
rp.move_forward(2.0, 0.5)
rp.rotate(90, 0.5)
rp.set_display_expression(5)
rp.set_rgb_light(255, 0, 0)
""")
```

**Savings: 60 Credits (60%)**

#### 2. Batch Operations

**Instead of multiple API calls:**
```
❌ Bad:
"Move forward" → 40 Credits
"Rotate 90°" → 40 Credits
"Show expression" → 40 Credits
Total: 120 Credits
```

**Better: One API call with multiple tools:**
```
✅ Good:
"Move forward, rotate 90°, show expression 5"
→ 1 API Call + 3 Tool Calls = 80 Credits
```

**Savings: 40 Credits (33%)**

#### 3. Use Caching

**Cache sensor data:**
```
❌ Bad: Query battery every time
→ 40 Credits per query

✅ Good: Cache battery value (5 min TTL)
→ Only 1x per 5 minutes = 40 Credits
```

---

## 📚 References

- **Letta Code:** https://github.com/letta-ai/letta-code
- **MCP Protocol:** https://modelcontextprotocol.io
- **Letta Documentation:** https://docs.letta.com
- **Rider-Pi Official Repository:** https://github.com/YahboomTechnology/Rider-Pi-Robot
- **Rider-Pi Documentation:** See [official repository](https://github.com/YahboomTechnology/Rider-Pi-Robot) for manufacturer documentation

---

## 💡 Best Practices

1. **Security first:** Validate all Code Execution tools
2. **Error Handling:** Robust error handling for all tools
3. **Logging:** Log all actions for debugging
4. **Version Control:** Use Git for all code changes
5. **Testing:** Test every new tool thoroughly
6. **Documentation:** Document all tools and their parameters

---

## 🎯 Success Criteria

### Phase 1
- ✅ All Rider-Pi functions available as MCP tools
- ✅ Code API complete
- ✅ All tests pass

### Phase 2
- ✅ Agents can read, write, edit code
- ✅ Self-Improvement Loop works
- ✅ Security checks work

### Phase 3
- ✅ Agents have access to all tools
- ✅ Code Execution works
- ✅ Agents can self-improve

---

**Last Updated:** 2025-01-XX  
**Status:** 🚧 In Planning  
**Next Steps:** Start Phase 1 - Implement advanced movement control

