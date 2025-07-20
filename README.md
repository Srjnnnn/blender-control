# Blender Remote Control v4.0 - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Quick Start Guide](#quick-start-guide)
4. [API Reference](#api-reference)
5. [WebSocket Protocol](#websocket-protocol)
6. [File-Based Commands](#file-based-commands)
7. [Batch Processing](#batch-processing)
8. [Advanced Animation System](#advanced-animation-system)
9. [Geometry Nodes Integration](#geometry-nodes-integration)
10. [AI Features](#ai-features)
11. [Templates & Presets](#templates--presets)
12. [Performance Optimization](#performance-optimization)
13. [Security & Best Practices](#security--best-practices)
14. [Troubleshooting](#troubleshooting)
15. [Development Guide](#development-guide)

---

## Overview

Blender Remote Control v4.0 is a comprehensive addon that enables external control of Blender through multiple communication channels. It's designed for AI assistants, automation pipelines, real-time collaboration, and procedural content generation.

### Key Features

- **Multi-Protocol Support**: HTTP REST API, WebSocket real-time communication, file-based commands
- **AI Integration**: Scene analysis, optimization suggestions, automated content generation
- **Advanced Animation**: Multi-property animations with professional easing curves
- **Geometry Nodes**: Full integration with procedural modeling workflows
- **Template System**: Reusable scene templates and animation presets
- **Batch Processing**: Execute multiple commands atomically
- **Real-time Collaboration**: Live scene updates via WebSocket
- **Performance Analytics**: Scene complexity analysis and optimization

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HTTP Client   │    │  WebSocket Client│    │  File Commands  │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          ▼                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Blender Remote Control                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ HTTP Server │  │ WS Server   │  │     File Watcher        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Command Processing Engine                      │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │    AI Engine   │  Animation  │  Geometry  │   Templates     │ │
│  │                │   System    │   Nodes    │   & Presets     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      Blender Scene      │
                    └─────────────────────────┘
```

---

## Installation & Setup

### Prerequisites

- **Blender 3.3+** (Blender 4.0+ recommended)
- **Python 3.9+** (included with Blender)
- **Optional**: `websockets` library for WebSocket support

### Installation Steps

1. **Download the Addon**
   ```bash
   # Clone from repository
   git clone https://github.com/your-repo/blender-remote-control-v4
   
   # Or download the addon file directly
   wget https://github.com/your-repo/blender-remote-control-v4/releases/latest/blender_remote_control_v4.py
   ```

2. **Install in Blender**
   - Open Blender
   - Go to `Edit > Preferences > Add-ons`
   - Click `Install...` and select the addon file
   - Enable "Blender Remote Control Advanced"

3. **Install Optional Dependencies** (for WebSocket support)
   ```bash
   # Using Blender's Python
   /path/to/blender/python -m pip install websockets
   
   # Or using system Python (if Blender uses system Python)
   pip install websockets
   ```

4. **Configure Addon Preferences**
   - In Blender preferences, find "Blender Remote Control Advanced"
   - Set ports (default: HTTP 8080, WebSocket 8081)
   - Configure file paths
   - Enable desired features

### Initial Configuration

```python
# Addon Preferences Configuration
{
    "http_port": 8080,
    "websocket_port": 8081,
    "command_file_path": "//remote_commands/",
    "template_path": "//templates/",
    "enable_websocket": True,
    "enable_file_watcher": True,
    "enable_batch_processing": True,
    "enable_ai_features": True,
    "ai_context_frames": 10,
    "ai_suggestion_threshold": 0.7
}
```

---

## Quick Start Guide

### 1. Start the Servers

```python
# In Blender, go to 3D Viewport > Sidebar > Remote Control tab
# Click "Start" for HTTP Server
# Click "Start" for WebSocket Server (if enabled)
```

### 2. Test Connection

```bash
# Test HTTP connection
curl http://localhost:8080/status

# Expected response:
{
  "blender_version": "4.0.0",
  "addon_version": [4, 0, 0],
  "scene_objects": 3,
  "websocket_connections": 0,
  "ai_features_enabled": true
}
```

### 3. First Commands

```python
import requests

BASE_URL = "http://localhost:8080"

# Add a cube
response = requests.post(BASE_URL, json={
    "command": "add_object",
    "params": {
        "type": "cube",
        "location": [2, 0, 2],
        "name": "MyCube"
    }
})

# Set material
requests.post(BASE_URL, json={
    "command": "set_material",
    "params": {
        "object": "MyCube",
        "material": "RedMaterial",
        "color": [1, 0, 0, 1],
        "metallic": 0.2,
        "roughness": 0.3
    }
})

# Animate
requests.post(BASE_URL, json={
    "command": "animate_advanced",
    "params": {
        "object": "MyCube",
        "animations": [{
            "property": "rotation_euler",
            "start_frame": 1,
            "end_frame": 100,
            "start_value": [0, 0, 0],
            "end_value": [0, 0, 6.28]
        }],
        "easing": "EASE_IN_OUT"
    }
})
```

### 4. AI-Powered Scene Creation

```python
# Let AI create a basic scene
response = requests.post(BASE_URL, json={
    "ai_query": "generate_content",
    "parameters": {
        "content_type": "basic_scene"
    }
})

# Get AI suggestions
suggestions = requests.get(f"{BASE_URL}/ai/suggestions").json()
print(f"AI generated {len(suggestions['suggestions'])} suggestions")
```

---

## API Reference

### Base URL and Authentication

```
Base URL: http://localhost:8080
WebSocket URL: ws://localhost:8081
Authentication: None (localhost only by default)
```

### HTTP Endpoints

#### GET /status
Returns server and Blender status.

**Response:**
```json
{
  "blender_version": "4.0.0",
  "addon_version": [4, 0, 0],
  "scene_objects": 5,
  "active_object": "Cube",
  "render_engine": "CYCLES",
  "websocket_connections": 2,
  "commands_executed": 157,
  "batches_executed": 12,
  "ai_features_enabled": true
}
```

#### GET /scene
Returns comprehensive scene information.

**Response:**
```json
{
  "frame_current": 1,
  "frame_start": 1,
  "frame_end": 250,
  "objects": [
    {
      "name": "Cube",
      "type": "MESH",
      "location": [0, 0, 0],
      "rotation": [0, 0, 0],
      "scale": [1, 1, 1],
      "visible": true,
      "selected": false,
      "parent": null,
      "children": [],
      "collections": ["Collection"],
      "vertices": 8,
      "faces": 6,
      "materials": ["Material"],
      "has_geometry_nodes": false,
      "geometry_node_groups": []
    }
  ],
  "materials": [
    {"name": "Material", "users": 1}
  ],
  "collections": [
    {"name": "Collection", "objects": 3}
  ],
  "geometry_node_groups": [],
  "animation_data": []
}
```

#### GET /templates
Returns available scene templates.

**Response:**
```json
{
  "templates": [
    {
      "name": "Basic Scene",
      "description": "A basic scene with objects and lighting",
      "category": "Sample",
      "tags": ["basic", "sample", "beginner"]
    }
  ]
}
```

#### GET /presets
Returns available animation and geometry presets.

**Response:**
```json
{
  "animation_presets": [
    {
      "name": "Bounce In",
      "description": "Bouncy entrance animation",
      "type": "LOCATION",
      "duration": 30,
      "easing": "BOUNCE"
    }
  ],
  "geometry_presets": [
    {
      "name": "Subdivision Surface",
      "description": "Smooth subdivision modifier",
      "node_group": "SubdivisionSetup"
    }
  ]
}
```

#### GET /ai/context
Returns AI analysis of current scene.

**Response:**
```json
{
  "scene_analysis": {
    "object_count": 5,
    "mesh_objects": 3,
    "light_count": 2,
    "camera_count": 1,
    "total_vertices": 1024,
    "materials_count": 3,
    "has_animation": true,
    "render_engine": "CYCLES",
    "frame_range": [1, 250]
  },
  "recommendations": [
    "Consider adding some mesh objects to populate the scene",
    "Add lighting to improve scene visibility and mood"
  ],
  "complexity_score": 3.2
}
```

#### GET /ai/suggestions
Returns AI-generated improvement suggestions.

**Response:**
```json
{
  "analysis_type": "composition",
  "suggestions": [
    {
      "type": "lighting",
      "priority": "high",
      "suggestion": "No lights in scene. Add lighting for better visibility.",
      "action": "add_lighting"
    }
  ],
  "suggestion_count": 1
}
```

#### GET /batch/{batch_id}
Returns status of a specific batch execution.

**Response:**
```json
{
  "batch_id": "uuid-string",
  "status": "completed",
  "total_commands": 5,
  "successful": 4,
  "failed": 1,
  "results": [...]
}
```

#### POST /
Main command execution endpoint.

**Request Body:**
```json
{
  "command": "command_name",
  "params": {
    "parameter1": "value1",
    "parameter2": "value2"
  }
}
```

### Command Reference

#### Object Management

##### add_object
Create a new object in the scene.

**Parameters:**
- `type` (string): Object type - "cube", "sphere", "cylinder", "plane", "torus", "monkey", "light", "camera", "empty"
- `location` (array): [x, y, z] coordinates
- `rotation` (array): [x, y, z] rotation in radians
- `scale` (array): [x, y, z] scale factors
- `name` (string): Object name
- `subdivisions` (int): Subdivision level for mesh objects
- `material` (string): Material to apply
- `parent` (string): Parent object name
- `collection` (string): Collection to add object to

**Example:**
```json
{
  "command": "add_object",
  "params": {
    "type": "sphere",
    "location": [0, 0, 3],
    "rotation": [0, 0, 0.5],
    "scale": [1.5, 1.5, 1.5],
    "name": "MySphere",
    "subdivisions": 3,
    "material": "GlowMaterial",
    "collection": "MainObjects"
  }
}
```

##### delete_object
Remove an object from the scene.

**Parameters:**
- `name` (string): Object name to delete
- `delete_children` (bool): Whether to delete child objects
- `delete_materials` (bool): Whether to delete unused materials

**Example:**
```json
{
  "command": "delete_object",
  "params": {
    "name": "OldObject",
    "delete_children": true,
    "delete_materials": true
  }
}
```

##### move_object
Move an object to a new position.

**Parameters:**
- `name` (string): Object name
- `location` (array): [x, y, z] coordinates
- `relative` (bool): Whether movement is relative
- `interpolate` (bool): Whether to create smooth animation
- `duration` (float): Animation duration in seconds

**Example:**
```json
{
  "command": "move_object",
  "params": {
    "name": "Cube",
    "location": [5, 0, 0],
    "relative": false,
    "interpolate": true,
    "duration": 2.0
  }
}
```

##### rotate_object
Rotate an object.

**Parameters:**
- `name` (string): Object name
- `rotation` (array): Rotation values
- `relative` (bool): Whether rotation is relative
- `mode` (string): "euler", "quaternion", "axis_angle"

**Example:**
```json
{
  "command": "rotate_object",
  "params": {
    "name": "Propeller",
    "rotation": [0, 0, 1.57],
    "relative": true,
    "mode": "euler"
  }
}
```

##### scale_object
Scale an object.

**Parameters:**
- `name` (string): Object name
- `scale` (array): [x, y, z] scale factors
- `relative` (bool): Whether scaling is relative
- `uniform` (bool): Use only first scale value for all axes

**Example:**
```json
{
  "command": "scale_object",
  "params": {
    "name": "Building",
    "scale": [1, 1, 2],
    "relative": false,
    "uniform": false
  }
}
```

#### Materials

##### set_material
Create and assign a material.

**Parameters:**
- `object` (string): Object name
- `material` (string): Material name
- `color` (array): [r, g, b, a] base color (0-1)
- `metallic` (float): Metallic value (0-1)
- `roughness` (float): Roughness value (0-1)
- `emission` (array): [r, g, b] emission color
- `emission_strength` (float): Emission strength

**Example:**
```json
{
  "command": "set_material",
  "params": {
    "object": "Sphere",
    "material": "MetalMaterial",
    "color": [0.8, 0.8, 0.9, 1.0],
    "metallic": 0.9,
    "roughness": 0.1,
    "emission": [0, 0, 0],
    "emission_strength": 0
  }
}
```

#### Advanced Animation

##### animate_advanced
Create complex animations with multiple properties and easing.

**Parameters:**
- `object` (string): Object name
- `animations` (array): Array of animation definitions
- `easing` (string): "LINEAR", "EASE_IN", "EASE_OUT", "EASE_IN_OUT", "BOUNCE"

**Animation Definition:**
- `property` (string): Property to animate ("location", "rotation_euler", "scale")
- `start_frame` (int): Starting frame
- `end_frame` (int): Ending frame
- `start_value` (array): Starting value
- `end_value` (array): Ending value

**Example:**
```json
{
  "command": "animate_advanced",
  "params": {
    "object": "FlyingCube",
    "animations": [
      {
        "property": "location",
        "start_frame": 1,
        "end_frame": 50,
        "start_value": [0, 0, 0],
        "end_value": [10, 0, 5]
      },
      {
        "property": "rotation_euler",
        "start_frame": 1,
        "end_frame": 50,
        "start_value": [0, 0, 0],
        "end_value": [0, 0, 6.28]
      }
    ],
    "easing": "EASE_IN_OUT"
  }
}
```

##### camera_animation
Create camera animations.

**Parameters:**
- `camera` (string): Camera name
- `type` (string): "orbit", "dolly"
- `target` (array): [x, y, z] target point
- `duration` (int): Duration in frames

**Orbit Parameters:**
- `radius` (float): Orbit radius
- `height` (float): Camera height

**Dolly Parameters:**
- `start_position` (array): Starting position
- `end_position` (array): Ending position

**Example:**
```json
{
  "command": "camera_animation",
  "params": {
    "camera": "MainCamera",
    "type": "orbit",
    "target": [0, 0, 1],
    "radius": 8,
    "height": 5,
    "duration": 120
  }
}
```

#### Geometry Nodes

##### apply_geometry_nodes
Apply geometry nodes to an object.

**Parameters:**
- `object` (string): Object name
- `node_group` (string): Node group name
- `parameters` (object): Node parameters

**Example:**
```json
{
  "command": "apply_geometry_nodes",
  "params": {
    "object": "Plane",
    "node_group": "SubdivisionSetup",
    "parameters": {
      "Level": 3,
      "Smooth": true
    }
  }
}
```

##### create_geometry_node_group
Create a new geometry node group.

**Parameters:**
- `name` (string): Node group name
- `setup` (string): "basic", "subdivide", "array"

**Example:**
```json
{
  "command": "create_geometry_node_group",
  "params": {
    "name": "CustomArraySetup",
    "setup": "array"
  }
}
```

#### Lighting & Environment

##### lighting_setup
Create professional lighting setups.

**Parameters:**
- `type` (string): "three_point", "studio"
- `target` (array): [x, y, z] target point
- `intensity` (float): Light intensity

**Example:**
```json
{
  "command": "lighting_setup",
  "params": {
    "type": "three_point",
    "target": [0, 0, 1],
    "intensity": 15
  }
}
```

#### Physics

##### setup_physics
Add physics simulation to objects.

**Parameters:**
- `object` (string): Object name
- `type` (string): "rigid_body", "soft_body", "cloth"
- `properties` (object): Physics properties

**Rigid Body Properties:**
- `type` (string): "ACTIVE", "PASSIVE"
- `mass` (float): Object mass
- `friction` (float): Friction coefficient
- `restitution` (float): Bounce factor

**Example:**
```json
{
  "command": "setup_physics",
  "params": {
    "object": "Ball",
    "type": "rigid_body",
    "properties": {
      "type": "ACTIVE",
      "mass": 2.0,
      "friction": 0.8,
      "restitution": 0.9
    }
  }
}
```

#### Procedural Generation

##### procedural_generation
Generate procedural content.

**Parameters:**
- `type` (string): "terrain", "forest", "city"
- `seed` (int): Random seed
- `size` (float): Generation area size
- `detail` (int): Detail level
- `count` (int): Number of objects (for forest/city)

**Example:**
```json
{
  "command": "procedural_generation",
  "params": {
    "type": "forest",
    "seed": 42,
    "size": 20,
    "count": 50
  }
}
```

#### AI Commands

##### ai_optimize_scene
AI-powered scene optimization.

**Parameters:**
- `type` (string): "performance", "lighting"
- `target_fps` (int): Target FPS for performance optimization

**Example:**
```json
{
  "command": "ai_optimize_scene",
  "params": {
    "type": "performance",
    "target_fps": 60
  }
}
```

##### ai_suggest_improvements
Generate AI improvement suggestions.

**Parameters:**
- `analysis` (string): "composition", "lighting", "materials"

**Example:**
```json
{
  "command": "ai_suggest_improvements",
  "params": {
    "analysis": "composition"
  }
}
```

#### Rendering

##### render
Render the scene with advanced settings.

**Parameters:**
- `output` (string): Output file path
- `format` (string): "PNG", "JPEG", "EXR", "TIFF"
- `resolution` (array): [width, height]
- `samples` (int): Render samples
- `engine` (string): "CYCLES", "EEVEE"

**Example:**
```json
{
  "command": "render",
  "params": {
    "output": "//renders/final_render.png",
    "format": "PNG",
    "resolution": [1920, 1080],
    "samples": 256,
    "engine": "CYCLES"
  }
}
```

#### Python Execution

##### python
Execute Python code in Blender.

**Parameters:**
- `code` (string): Python code to execute
- `context` (string): "safe", "full", "restricted"

**Example:**
```json
{
  "command": "python",
  "params": {
    "code": "import bmesh\nbm = bmesh.new()\nbmesh.ops.create_cube(bm, size=2)\nmesh = bpy.data.meshes.new('CustomCube')\nbm.to_mesh(mesh)\nbm.free()",
    "context": "safe"
  }
}
```

---

## WebSocket Protocol

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8081');

ws.onopen = function(event) {
    console.log('Connected to Blender WebSocket');
};
```

### Message Format

All WebSocket messages use JSON format:

```json
{
  "type": "message_type",
  "id": "optional_unique_id",
  "data": {...}
}
```

### Message Types

#### Client to Server

##### command
Execute a Blender command.

```json
{
  "type": "command",
  "id": "cmd_001",
  "command": "add_object",
  "params": {
    "type": "cube",
    "location": [2, 0, 2]
  }
}
```

##### subscribe
Subscribe to scene updates.

```json
{
  "type": "subscribe",
  "events": ["scene_update", "object_change"]
}
```

##### ping
Ping the server.

```json
{
  "type": "ping"
}
```

#### Server to Client

##### connection
Connection acknowledgment.

```json
{
  "type": "connection",
  "status": "connected",
  "message": "Welcome to Blender Remote Control WebSocket"
}
```

##### command_result
Result of command execution.

```json
{
  "type": "command_result",
  "id": "cmd_001",
  "result": {
    "success": true,
    "object_name": "Cube.001"
  }
}
```

##### scene_update
Live scene updates.

```json
{
  "type": "scene_update",
  "timestamp": 1645123456.789,
  "scene": {
    "objects": [...],
    "frame_current": 50
  }
}
```

##### pong
Ping response.

```json
{
  "type": "pong",
  "timestamp": 1645123456.789
}
```

### WebSocket Client Example

```javascript
class BlenderWebSocketClient {
    constructor(url = 'ws://localhost:8081') {
        this.ws = new WebSocket(url);
        this.commandId = 0;
        this.pendingCommands = new Map();
        
        this.ws.onopen = this.onOpen.bind(this);
        this.ws.onmessage = this.onMessage.bind(this);
        this.ws.onclose = this.onClose.bind(this);
        this.ws.onerror = this.onError.bind(this);
    }
    
    onOpen(event) {
        console.log('Connected to Blender');
        this.subscribe(['scene_update']);
    }
    
    onMessage(event) {
        const message = JSON.parse(event.data);
        
        switch(message.type) {
            case 'command_result':
                this.handleCommandResult(message);
                break;
            case 'scene_update':
                this.handleSceneUpdate(message);
                break;
        }
    }
    
    executeCommand(command, params) {
        const id = `cmd_${++this.commandId}`;
        
        return new Promise((resolve, reject) => {
            this.pendingCommands.set(id, { resolve, reject });
            
            this.ws.send(JSON.stringify({
                type: 'command',
                id: id,
                command: command,
                params: params
            }));
            
            // Timeout after 30 seconds
            setTimeout(() => {
                if (this.pendingCommands.has(id)) {
                    this.pendingCommands.delete(id);
                    reject(new Error('Command timeout'));
                }
            }, 30000);
        });
    }
    
    handleCommandResult(message) {
        const pending = this.pendingCommands.get(message.id);
        if (pending) {
            this.pendingCommands.delete(message.id);
            if (message.result.success) {
                pending.resolve(message.result);
            } else {
                pending.reject(new Error(message.result.error));
            }
        }
    }
    
    subscribe(events) {
        this.ws.send(JSON.stringify({
            type: 'subscribe',
            events: events
        }));
    }
    
    handleSceneUpdate(message) {
        console.log('Scene updated:', message.scene);
        // Handle scene updates
    }
}

// Usage
const client = new BlenderWebSocketClient();

// Add object
client.executeCommand('add_object', {
    type: 'sphere',
    location: [0, 0, 3],
    name: 'WebSocketSphere'
}).then(result => {
    console.log('Object created:', result.object_name);
});

// Animate object
client.executeCommand('animate_advanced', {
    object: 'WebSocketSphere',
    animations: [{
        property: 'location',
        start_frame: 1,
        end_frame: 100,
        start_value: [0, 0, 3],
        end_value: [10, 0, 3]
    }],
    easing: 'EASE_IN_OUT'
});
```

---

## File-Based Commands

### Directory Structure

```
remote_commands/
├── command_001.json          # Command file
├── command_001.result.json   # Result file (auto-generated)
├── command_002.json
├── command_002.error.json    # Error file (if command failed)
└── batch_001.json           # Batch command file
```

### Command File Format

```json
{
  "command": "add_object",
  "params": {
    "type": "cube",
    "location": [1, 2, 3],
    "name": "FileCube"
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "source": "external_tool",
    "priority": "normal"
  }
}
```

### Batch File Format

```json
{
  "batch": [
    {
      "command": "add_object",
      "params": {"type": "sphere", "name": "Sphere1", "location": [3, 0, 0]}
    },
    {
      "command": "set_material",
      "params": {"object": "Cube1", "material": "BlueMat", "color": [0, 0, 1, 1]}
    },
    {
      "command": "set_material",
      "params": {"object": "Sphere1", "material": "RedMat", "color": [1, 0, 0, 1]}
    },
    {
      "command": "lighting_setup",
      "params": {"type": "three_point", "target": [1.5, 0, 0]}
    }
  ]
}
```

### Batch Response Format

```json
{
  "batch_id": "batch_1234567890",
  "total_commands": 5,
  "successful": 4,
  "failed": 1,
  "execution_time": 1.23,
  "results": [
    {
      "batch_index": 0,
      "success": true,
      "result": {"object_name": "Cube1", "location": [0, 0, 0]}
    },
    {
      "batch_index": 1,
      "success": true,
      "result": {"object_name": "Sphere1", "location": [3, 0, 0]}
    },
    {
      "batch_index": 2,
      "success": false,
      "error": "Object 'NonExistent' not found"
    }
  ]
}
```

### Conditional Batch Execution

```json
{
  "batch": [
    {
      "command": "add_object",
      "params": {"type": "cube", "name": "TestCube"},
      "condition": {"always": true}
    },
    {
      "command": "set_material",
      "params": {"object": "TestCube", "material": "TestMat"},
      "condition": {"depends_on": 0, "success_required": true}
    },
    {
      "command": "animate_advanced",
      "params": {"object": "TestCube", "animations": [...]},
      "condition": {"depends_on": [0, 1], "all_success_required": true}
    }
  ],
  "options": {
    "stop_on_error": false,
    "rollback_on_failure": true
  }
}
```

### Batch Status Monitoring

```python
import requests

# Execute batch
response = requests.post("http://localhost:8080/", json={"batch": [...]})
batch_id = response.json()["batch_id"]

# Check status
status = requests.get(f"http://localhost:8080/batch/{batch_id}")
print(f"Batch {batch_id}: {status.json()['successful']}/{status.json()['total_commands']} completed")
```

---

## Advanced Animation System

### Multi-Property Animations

Create complex animations affecting multiple properties:

```json
{
  "command": "animate_advanced",
  "params": {
    "object": "FlyingCar",
    "animations": [
      {
        "property": "location",
        "start_frame": 1,
        "end_frame": 100,
        "start_value": [0, 0, 0],
        "end_value": [20, 0, 5],
        "easing": "EASE_OUT"
      },
      {
        "property": "rotation_euler",
        "start_frame": 1,
        "end_frame": 100,
        "start_value": [0, 0, 0],
        "end_value": [0, 0, 1.57],
        "easing": "LINEAR"
      },
      {
        "property": "scale",
        "start_frame": 80,
        "end_frame": 100,
        "start_value": [1, 1, 1],
        "end_value": [0.5, 0.5, 0.5],
        "easing": "EASE_IN"
      }
    ],
    "global_easing": "EASE_IN_OUT"
  }
}
```

### Easing Types

| Easing Type | Description | Use Case |
|-------------|-------------|----------|
| `LINEAR` | Constant speed | Mechanical movements |
| `EASE_IN` | Slow start, fast end | Falling objects |
| `EASE_OUT` | Fast start, slow end | Coming to rest |
| `EASE_IN_OUT` | Slow start/end, fast middle | Natural movements |
| `BOUNCE` | Bouncing effect | Playful animations |
| `ELASTIC` | Elastic overshoot | UI transitions |
| `BACK` | Overshoot and settle | Anticipation |

### Custom Animation Curves

```json
{
  "command": "animate_advanced",
  "params": {
    "object": "Pendulum",
    "animations": [
      {
        "property": "rotation_euler",
        "keyframes": [
          {"frame": 1, "value": [-0.5, 0, 0], "interpolation": "BEZIER"},
          {"frame": 25, "value": [0.5, 0, 0], "interpolation": "BEZIER"},
          {"frame": 50, "value": [-0.5, 0, 0], "interpolation": "BEZIER"}
        ],
        "handles": "AUTO"
      }
    ]
  }
}
```

### Animation Presets

```json
{
  "command": "apply_animation_preset",
  "params": {
    "object": "Logo",
    "preset": "bounce_in",
    "duration": 60,
    "delay": 10,
    "scale_factor": 1.5
  }
}
```

### Camera Animation Patterns

#### Orbit Animation
```json
{
  "command": "camera_animation",
  "params": {
    "camera": "MainCamera",
    "type": "orbit",
    "target": [0, 0, 1],
    "radius": 8,
    "height": 5,
    "duration": 240,
    "start_angle": 0,
    "end_angle": 6.28,
    "vertical_oscillation": 0.5
  }
}
```

#### Dolly Zoom
```json
{
  "command": "camera_animation",
  "params": {
    "camera": "MainCamera",
    "type": "dolly_zoom",
    "start_position": [10, -10, 5],
    "end_position": [5, -5, 3],
    "target": [0, 0, 1],
    "focal_length_compensation": true,
    "duration": 120
  }
}
```

#### Handheld Shake
```json
{
  "command": "camera_animation",
  "params": {
    "camera": "MainCamera",
    "type": "handheld_shake",
    "intensity": 0.1,
    "frequency": 12,
    "duration": 100,
    "noise_scale": 0.5
  }
}
```

---

## Geometry Nodes Integration

### Node Group Creation

#### Basic Subdivision Setup
```json
{
  "command": "create_geometry_node_group",
  "params": {
    "name": "SubdivisionSetup",
    "setup": "subdivide",
    "parameters": {
      "level_input": true,
      "smooth_output": true
    }
  }
}
```

#### Procedural Array
```json
{
  "command": "create_geometry_node_group",
  "params": {
    "name": "CircularArray",
    "setup": "array",
    "array_type": "circular",
    "parameters": {
      "count": 8,
      "radius": 5,
      "rotation_offset": 0.785
    }
  }
}
```

#### Advanced Scatter
```json
{
  "command": "create_geometry_node_group",
  "params": {
    "name": "ScatterSystem",
    "setup": "scatter",
    "parameters": {
      "density": 100,
      "scale_variation": 0.3,
      "rotation_randomness": 1.0,
      "distribution": "random"
    }
  }
}
```

### Applying Geometry Nodes

```json
{
  "command": "apply_geometry_nodes",
  "params": {
    "object": "TerrainPlane",
    "node_group": "TerrainGenerator",
    "parameters": {
      "Subdivision_Level": 4,
      "Noise_Scale": 2.5,
      "Height_Multiplier": 3.0,
      "Seed": 42
    },
    "apply_modifier": false
  }
}
```

### Custom Node Setups

#### Displacement Modifier
```json
{
  "command": "create_custom_node_setup",
  "params": {
    "name": "DisplacementSetup",
    "nodes": [
      {
        "type": "GeometryNodeInputPosition",
        "location": [-400, 0]
      },
      {
        "type": "ShaderNodeTexNoise",
        "location": [-200, 0],
        "settings": {"noise_scale": 5.0}
      },
      {
        "type": "GeometryNodeSetPosition",
        "location": [0, 0]
      }
    ],
    "connections": [
      {"from": "Position.Position", "to": "Noise.Vector"},
      {"from": "Noise.Fac", "to": "SetPosition.Offset"}
    ]
  }
}
```

### Geometry Node Presets Library

```json
{
  "command": "get_geometry_presets",
  "params": {
    "category": "procedural"
  }
}
```

**Response:**
```json
{
  "presets": [
    {
      "name": "Rock Generator",
      "description": "Generates realistic rock formations",
      "node_group": "RockGen_v2",
      "parameters": {
        "Size": {"type": "float", "default": 1.0, "range": [0.1, 5.0]},
        "Roughness": {"type": "float", "default": 0.8, "range": [0.0, 1.0]},
        "Seed": {"type": "int", "default": 1, "range": [1, 1000]}
      },
      "category": "nature",
      "tags": ["rock", "stone", "geology"]
    }
  ]
}
```

---

## AI Features

### Scene Analysis

#### Comprehensive Scene Analysis
```python
import requests

# Get detailed AI analysis
response = requests.get("http://localhost:8080/ai/context")
analysis = response.json()

print(f"Scene Complexity: {analysis['complexity_score']}/10")
print(f"Recommendations: {len(analysis['recommendations'])}")

for rec in analysis['recommendations']:
    print(f"- {rec}")
```

#### Custom Analysis Parameters
```json
{
  "ai_query": "analyze_scene",
  "parameters": {
    "focus": "lighting",
    "depth": "detailed",
    "include_performance": true,
    "suggest_optimizations": true
  }
}
```

### AI-Powered Optimization

#### Performance Optimization
```json
{
  "command": "ai_optimize_scene",
  "params": {
    "type": "performance",
    "target_fps": 60,
    "quality_threshold": 0.8,
    "optimization_level": "aggressive",
    "preserve_animation": true
  }
}
```

#### Lighting Optimization
```json
{
  "command": "ai_optimize_scene",
  "params": {
    "type": "lighting",
    "mood": "dramatic",
    "color_temperature": "warm",
    "shadow_quality": "high",
    "energy_efficiency": true
  }
}
```

### Content Generation

#### AI Scene Generation
```json
{
  "ai_query": "generate_content",
  "parameters": {
    "content_type": "architectural_scene",
    "style": "modern",
    "complexity": "medium",
    "elements": ["building", "landscape", "lighting"],
    "color_palette": ["#2E4057", "#048A81", "#F1C453"]
  }
}
```

#### AI Material Generation
```json
{
  "ai_query": "generate_materials",
  "parameters": {
    "material_type": "pbr",
    "surface": "metal",
    "finish": "brushed",
    "color_base": [0.7, 0.7, 0.8],
    "procedural": true
  }
}
```

### Smart Suggestions

#### Composition Improvements
```json
{
  "command": "ai_suggest_improvements",
  "params": {
    "analysis": "composition",
    "reference_style": "rule_of_thirds",
    "subject_focus": "center_object",
    "depth_of_field": true
  }
}
```

#### Animation Enhancements
```json
{
  "command": "ai_suggest_improvements",
  "params": {
    "analysis": "animation",
    "animation_style": "cartoon",
    "timing_analysis": true,
    "secondary_motion": true
  }
}
```

### Learning System

The AI system learns from user preferences and project patterns:

```json
{
  "command": "ai_learn_preferences",
  "params": {
    "session_data": {
      "preferred_lighting": "three_point",
      "material_complexity": "medium",
      "animation_style": "smooth",
      "color_preferences": ["blue", "warm"]
    },
    "project_type": "product_visualization"
  }
}
```

---

## Templates & Presets

### Scene Templates

#### Creating Templates
```json
{
  "command": "create_template",
  "params": {
    "name": "Product Showcase",
    "description": "Template for product visualization",
    "category": "commercial",
    "elements": {
      "ground_plane": true,
      "lighting_rig": "studio",
      "camera_setup": "product",
      "materials": ["metal", "glass", "plastic"]
    },
    "parameters": {
      "product_scale": {"type": "float", "default": 1.0},
      "lighting_intensity": {"type": "float", "default": 10.0},
      "background_color": {"type": "color", "default": [0.8, 0.8, 0.8]}
    }
  }
}
```

#### Applying Templates
```json
{
  "template": "Product Showcase",
  "parameters": {
    "product_scale": 1.5,
    "lighting_intensity": 15.0,
    "background_color": [0.9, 0.95, 1.0]
  }
}
```

### Animation Presets

#### Preset Definition
```json
{
  "command": "create_animation_preset",
  "params": {
    "name": "Bounce In",
    "description": "Bouncy entrance animation",
    "animation_type": "LOCATION",
    "duration": 30,
    "easing": "BOUNCE",
    "keyframes": [
      {"frame": 0, "scale": [0, 0, 0]},
      {"frame": 20, "scale": [1.2, 1.2, 1.2]},
      {"frame": 30, "scale": [1, 1, 1]}
    ]
  }
}
```

#### Applying Presets
```json
{
  "command": "apply_animation_preset",
  "params": {
    "object": "Logo",
    "preset": "Bounce In",
    "start_frame": 10,
    "speed_multiplier": 1.5
  }
}
```

### Template Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `architectural` | Building and environment templates | Office, house, landscape |
| `product` | Product visualization setups | Studio, catalog, hero shot |
| `character` | Character animation rigs | Dialogue, action, emotion |
| `abstract` | Abstract and motion graphics | Particle systems, fractals |
| `scientific` | Scientific visualization | Molecular, anatomical, data |

### Template Marketplace

```json
{
  "command": "browse_template_marketplace",
  "params": {
    "category": "product",
    "sort_by": "popularity",
    "filter": {
      "complexity": "beginner",
      "render_engine": "CYCLES",
      "animated": false
    }
  }
}
```

---

## Performance Optimization

### Scene Analysis

#### Performance Metrics
```python
# Get performance analysis
response = requests.get("http://localhost:8080/ai/context")
metrics = response.json()['scene_analysis']

print(f"Total vertices: {metrics['total_vertices']}")
print(f"Object count: {metrics['object_count']}")
print(f"Material count: {metrics['materials_count']}")
print(f"Complexity score: {metrics['complexity_score']}")
```

#### Optimization Recommendations
```json
{
  "command": "ai_optimize_scene",
  "params": {
    "type": "performance",
    "analysis": {
      "vertex_budget": 50000,
      "draw_call_budget": 20,
      "texture_memory_budget": "512MB"
    },
    "optimizations": {
      "lod_generation": true,
      "texture_compression": true,
      "material_merging": true,
      "instance_optimization": true
    }
  }
}
```

### Automatic Optimizations

#### Level of Detail (LOD) Generation
```json
{
  "command": "generate_lod",
  "params": {
    "object": "ComplexModel",
    "levels": [
      {"distance": 10, "reduction": 0.1},
      {"distance": 50, "reduction": 0.5},
      {"distance": 100, "reduction": 0.8}
    ],
    "algorithm": "quadric_decimation"
  }
}
```

#### Texture Optimization
```json
{
  "command": "optimize_textures",
  "params": {
    "target_size": 1024,
    "compression": "DXT5",
    "mipmap_generation": true,
    "quality": 0.8
  }
}
```

#### Material Merging
```json
{
  "command": "merge_materials",
  "params": {
    "similarity_threshold": 0.9,
    "preserve_uv_layout": true,
    "atlas_size": 2048
  }
}
```

### Render Optimization

#### Adaptive Quality
```json
{
  "command": "render",
  "params": {
    "adaptive_quality": {
      "enabled": true,
      "target_time": 30,
      "min_samples": 64,
      "max_samples": 512,
      "noise_threshold": 0.05
    }
  }
}
```

#### Denoising Configuration
```json
{
  "command": "configure_denoising",
  "params": {
    "denoiser": "OPTIX",
    "passes": ["diffuse", "glossy", "transmission"],
    "prefilter": true,
    "strength": 1.0
  }
}
```

---

## Security & Best Practices

### Security Configuration

#### Network Security
```python
# Restrict to localhost only (default)
server_config = {
    "bind_address": "127.0.0.1",
    "allowed_origins": ["localhost", "127.0.0.1"],
    "max_connections": 10,
    "rate_limiting": {
        "requests_per_minute": 100,
        "burst_size": 20
    }
}
```

#### Command Validation
```python
# Safe command execution
{
  "command": "python",
  "params": {
    "code": "print('Hello World')",
    "context": "safe",  # restricted, safe, full
    "timeout": 10,
    "memory_limit": "100MB"
  }
}
```

#### Authentication (Optional)
```python
# Enable API key authentication
{
  "headers": {
    "Authorization": "Bearer your-api-key-here",
    "X-Client-ID": "your-client-id"
  }
}
```

### Best Practices

#### Error Handling
```python
import requests

try:
    response = requests.post("http://localhost:8080/", 
                           json={"command": "add_object", "params": {...}},
                           timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"Success: {result}")
        else:
            print(f"Command failed: {result.get('error')}")
    else:
        print(f"HTTP Error: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.ConnectionError:
    print("Connection failed")
except Exception as e:
    print(f"Unexpected error: {e}")
```

#### Resource Management
```python
# Monitor resource usage
response = requests.get("http://localhost:8080/status")
status = response.json()

if status['scene_objects'] > 1000:
    print("Warning: High object count")
    
if status['complexity_score'] > 8:
    print("Warning: Scene complexity is high")
    # Consider optimization
```

#### Batch Size Optimization
```python
# Optimal batch sizes
OPTIMAL_BATCH_SIZES = {
    "object_creation": 50,
    "material_assignment": 100,
    "animation_keyframes": 20,
    "geometry_operations": 10
}

def create_optimal_batches(commands, command_type):
    batch_size = OPTIMAL_BATCH_SIZES.get(command_type, 25)
    return [commands[i:i+batch_size] for i in range(0, len(commands), batch_size)]
```

#### Connection Pooling
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure connection pooling
session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=5,
    pool_maxsize=10,
    max_retries=Retry(total=3, backoff_factor=0.3)
)
session.mount("http://", adapter)

# Use session for all requests
response = session.post("http://localhost:8080/", json={...})
```

---

## Troubleshooting

### Common Issues

#### Server Won't Start

**Problem**: HTTP server fails to start
```
Error: [Errno 98] Address already in use
```

**Solutions**:
1. Check if port is in use: `netstat -an | grep 8080`
2. Change port in addon preferences
3. Kill process using port: `sudo lsof -ti:8080 | xargs kill -9`
4. Restart Blender

#### WebSocket Connection Issues

**Problem**: WebSocket connection fails
```
WebSocket connection failed: Connection refused
```

**Solutions**:
1. Ensure WebSocket server is started
2. Check firewall settings
3. Verify websockets library is installed
4. Check browser console for CORS issues

#### Command Execution Errors

**Problem**: Commands fail with errors
```json
{"success": false, "error": "Object not found: InvalidName"}
```

**Solutions**:
1. Verify object names exist
2. Check parameter types and ranges
3. Use scene endpoint to inspect current state
4. Enable debug logging

#### Performance Issues

**Problem**: Slow command execution
```
Commands taking >5 seconds to execute
```

**Solutions**:
1. Reduce scene complexity
2. Use batch commands
3. Optimize geometry and materials
4. Check system resources

### Debugging Tools

#### Enable Debug Logging
```python
# In Blender console
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via command
{
  "command": "set_debug_level",
  "params": {"level": "DEBUG"}
}
```

#### Scene State Inspection
```python
# Get detailed scene state
response = requests.get("http://localhost:8080/scene")
scene = response.json()

# Print object hierarchy
for obj in scene['objects']:
    print(f"{obj['name']} ({obj['type']}) - Parent: {obj['parent']}")
    print(f"  Location: {obj['location']}")
    print(f"  Materials: {obj.get('materials', [])}")
```

#### Performance Profiling
```python
# Profile command execution
import time

start_time = time.time()
response = requests.post("http://localhost:8080/", json={...})
execution_time = time.time() - start_time

print(f"Command executed in {execution_time:.3f} seconds")
```

### Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| `OBJECT_NOT_FOUND` | Object name doesn't exist | Check object names with /scene |
| `INVALID_PARAMETER` | Parameter type/value invalid | Verify parameter format |
| `GEOMETRY_ERROR` | Geometry operation failed | Check mesh validity |
| `MATERIAL_ERROR` | Material operation failed | Verify material properties |
| `ANIMATION_ERROR` | Animation setup failed | Check frame ranges and properties |
| `PHYSICS_ERROR` | Physics setup failed | Verify object type and properties |
| `RENDER_ERROR` | Render operation failed | Check render settings |
| `WEBSOCKET_ERROR` | WebSocket communication failed | Check connection and message format |
| `BATCH_ERROR` | Batch execution failed | Check individual command validity |
| `AI_ERROR` | AI operation failed | Verify AI features are enabled |

---

## Development Guide

### Extending the Addon

#### Adding New Commands

1. **Create Command Handler**
```python
def my_custom_command(self, params):
    """Custom command implementation"""
    try:
        # Your command logic here
        parameter1 = params.get('parameter1', 'default_value')
        parameter2 = params.get('parameter2', 0)
        
        # Perform Blender operations
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        obj.name = parameter1
        
        return {
            'success': True,
            'result': 'Custom command executed',
            'object_created': obj.name
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

2. **Register Command**
```python
# In AdvancedBlenderHTTPHandler.execute_command()
command_handlers = {
    # ... existing commands
    'my_custom_command': self.my_custom_command,
}
```

3. **Add Documentation**
```python
"""
my_custom_command

Creates a custom object with specific parameters.

Parameters:
- parameter1 (string): Object name
- parameter2 (int): Object count

Example:
{
  "command": "my_custom_command",
  "params": {
    "parameter1": "CustomObject",
    "parameter2": 5
  }
}
"""
```

#### Creating Custom AI Features

```python
def custom_ai_analysis(self, params):
    """Custom AI analysis implementation"""
    analysis_type = params.get('type', 'custom')
    
    # Analyze scene
    scene_data = self.get_scene_data()
    objects = scene_data['objects']
    
    # Custom analysis logic
    analysis_result = {
        'object_distribution': analyze_distribution(objects),
        'color_harmony': analyze_colors(objects),
        'composition_score': calculate_composition_score(objects)
    }
    
    # Generate suggestions
    suggestions = []
    if analysis_result['composition_score'] < 0.5:
        suggestions.append({
            'type': 'composition',
            'priority': 'medium',
            'suggestion': 'Consider redistributing objects for better composition'
        })
    
    return {
        'success': True,
        'analysis': analysis_result,
        'suggestions': suggestions
    }
```

#### Custom WebSocket Messages

```python
async def handle_custom_message(self, websocket, data):
    """Handle custom WebSocket message"""
    if data.get('type') == 'custom_request':
        # Process custom request
        result = self.process_custom_request(data)
        
        response = {
            'type': 'custom_response',
            'id': data.get('id'),
            'result': result
        }
        
        await websocket.send(json.dumps(response))
```

### Testing Framework

#### Unit Tests
```python
import unittest
import requests

class TestCustomCommands(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8080"
    
    def test_custom_command(self):
        response = requests.post(self.base_url, json={
            "command": "my_custom_command",
            "params": {
                "parameter1": "TestObject",
                "parameter2": 3
            }
        })
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertEqual(result['object_created'], 'TestObject')

if __name__ == '__main__':
    unittest.main()
```

#### Integration Tests
```python
def test_workflow():
    """Test complete workflow"""
    commands = [
        {"command": "add_object", "params": {"type": "cube", "name": "TestCube"}},
        {"command": "set_material", "params": {"object": "TestCube", "material": "TestMat"}},
        {"command": "animate_advanced", "params": {"object": "TestCube", "animations": [...]}}
    ]
    
    # Execute batch
    response = requests.post("http://localhost:8080/", json={"batch": commands})
    batch_result = response.json()
    
    assert batch_result['successful'] == len(commands)
    assert batch_result['failed'] == 0
```

### Performance Considerations

#### Optimization Guidelines

1. **Batch Operations**: Group related commands
2. **Async Processing**: Use WebSocket for real-time updates
3. **Resource Pooling**: Reuse objects and materials
4. **Lazy Loading**: Load complex data only when needed
5. **Caching**: Cache frequently accessed scene data

#### Memory Management
```python
def cleanup_scene():
    """Clean up unused resources"""
    # Remove unused materials
    for material in bpy.data.materials:
        if material.users == 0:
            bpy.data.materials.remove(material)
    
    # Remove unused meshes
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    
    # Garbage collection
    import gc
    gc.collect()
```

### Deployment

#### Production Configuration
```python
PRODUCTION_CONFIG = {
    "security": {
        "enable_authentication": True,
        "rate_limiting": True,
        "command_validation": "strict",
        "python_execution": "disabled"
    },
    "performance": {
        "max_batch_size": 50,
        "command_timeout": 30,
        "websocket_max_connections": 20,
        "enable_caching": True
    },
    "logging": {
        "level": "INFO",
        "log_file": "/var/log/blender-remote-control.log",
        "rotate_logs": True
    }
}
```

#### Docker Deployment
```dockerfile
FROM blender:latest

# Install dependencies
RUN",
      "params": {
        "type": "plane",
        "name": "Ground",
        "scale": [10, 10, 1]
      }
    },
    {
      "command": "lighting_setup",
      "params": {
        "type": "three_point",
        "target": [0, 0, 1]
      }
    }
  ],
  "metadata": {
    "batch_name": "scene_setup",
    "atomic": true
  }
}
```

### Result File Format

```json
{
  "success": true,
  "result": {
    "object_name": "FileCube",
    "location": [1, 2, 3]
  },
  "execution_time": 0.045,
  "timestamp": "2024-01-15T10:30:01Z"
}
```

### Error File Format

```json
{
  "error": "Object type 'invalid_type' not supported",
  "timestamp": "2024-01-15T10:30:01Z",
  "command": {
    "command": "add_object",
    "params": {
      "type": "invalid_type"
    }
  }
}
```

### File Watcher Configuration

```python
# Enable file watcher in preferences
prefs.enable_file_watcher = True
prefs.command_file_path = "//remote_commands/"

# Start file watcher
bpy.ops.remote_control.start_file_watcher()
```

---

## Batch Processing

### Batch Execution

Execute multiple commands atomically:

```json
{
  "batch": [
    {
      "command": "add_object",
      "params": {"type": "cube", "name": "Cube1", "location": [0, 0, 0]}
    },
    {
      "command": "add_object