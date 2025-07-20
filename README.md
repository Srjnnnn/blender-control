# Blender Remote Control Advanced

A comprehensive Blender addon that enables external control through HTTP API, WebSocket connections, file watchers, and AI-powered features. Control Blender remotely for automation, pipeline integration, and advanced workflows.

## Features

### 🌐 Multiple Control Methods
- **HTTP REST API** - RESTful endpoints for all operations
- **WebSocket Server** - Real-time bidirectional communication
- **File Watcher** - Monitor directories for JSON command files
- **Batch Processing** - Execute multiple commands in sequence

### 🎨 Scene Manipulation
- Create, modify, and delete objects
- Transform operations (move, rotate, scale)
- Material creation and assignment
- Lighting setups (three-point, studio)
- Camera animations (orbit, dolly)
- Physics simulation setup

### 🔧 Advanced Features
- **Geometry Nodes** - Create and apply procedural node setups
- **Animation System** - Keyframe animations with easing
- **Procedural Generation** - Generate terrains, forests, cities
- **AI Assistant** - Scene analysis and optimization suggestions
- **Template System** - Save and apply scene templates
- **Python Execution** - Run Python code remotely

## Installation

1. Download `blender_remote_addon.py`
2. Open Blender
3. Go to Edit → Preferences → Add-ons
4. Click "Install..." and select the downloaded file
5. Enable "System: Blender Remote Control Advanced"

### Optional Dependencies

For WebSocket support:
```bash
# Ensure pip is installed in Blender's Python
# Navigate to Blender's Python directory
python -m pip install websockets
```

## Quick Start

### 1. Start the HTTP Server

1. Open the 3D Viewport sidebar (press N)
2. Navigate to the "Remote Control" tab
3. Click "Start" next to HTTP Server
4. The server will start on port 8080 (configurable in preferences)

### 2. Test the Connection

```bash
# Check server status
curl http://localhost:8080/status

# Get scene information
curl http://localhost:8080/scene
```

### 3. Send Your First Command

```bash
# Add a cube to the scene
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "command": "add_object",
    "params": {
      "type": "cube",
      "location": [0, 0, 1],
      "name": "MyCube"
    }
  }'
```

## API Reference

### HTTP Endpoints

#### GET Endpoints

| Endpoint | Description | Response |
|----------|-------------|----------|
| `/status` | Server and scene status | System info, object counts, server states |
| `/scene` | Complete scene data | Objects, materials, animations |
| `/templates` | Available templates | List of scene templates |
| `/presets` | Animation/geometry presets | Available presets |
| `/ai/context` | AI scene analysis | Complexity score, recommendations |
| `/ai/suggestions` | AI improvement suggestions | Suggested actions |
| `/batch/{id}` | Batch execution status | Status of batch operation |

#### POST Endpoints

All commands are sent to the root endpoint `/` with JSON body.

### Object Commands

#### add_object
Create a new object in the scene.

```json
{
  "command": "add_object",
  "params": {
    "type": "cube|sphere|cylinder|plane|torus|monkey|light|camera|empty",
    "name": "ObjectName",
    "location": [0, 0, 0],
    "rotation": [0, 0, 0],
    "scale": [1, 1, 1],
    "subdivisions": 0,
    "material": "MaterialName",
    "parent": "ParentObjectName",
    "collection": "CollectionName"
  }
}
```

#### delete_object
Remove an object from the scene.

```json
{
  "command": "delete_object",
  "params": {
    "name": "ObjectName",
    "delete_children": false,
    "delete_materials": false
  }
}
```

#### move_object
Change object location.

```json
{
  "command": "move_object",
  "params": {
    "name": "ObjectName",
    "location": [1, 2, 3],
    "relative": false,
    "interpolate": false,
    "duration": 1.0
  }
}
```

#### rotate_object
Rotate an object.

```json
{
  "command": "rotate_object",
  "params": {
    "name": "ObjectName",
    "rotation": [0, 0, 1.57],
    "relative": false,
    "mode": "euler|quaternion|axis_angle"
  }
}
```

#### scale_object
Scale an object.

```json
{
  "command": "scale_object",
  "params": {
    "name": "ObjectName",
    "scale": [2, 2, 2],
    "relative": false,
    "uniform": true
  }
}
```

### Material Commands

#### set_material
Create or modify materials.

```json
{
  "command": "set_material",
  "params": {
    "object": "ObjectName",
    "material": "MaterialName",
    "color": [0.8, 0.2, 0.2, 1.0],
    "metallic": 0.0,
    "roughness": 0.5,
    "emission": [0, 0, 0],
    "emission_strength": 1.0
  }
}
```

### Animation Commands

#### animate
Basic keyframe animation.

```json
{
  "command": "animate",
  "params": {
    "object": "ObjectName",
    "property": "location|rotation|scale",
    "start_frame": 1,
    "end_frame": 50,
    "start_value": [0, 0, 0],
    "end_value": [5, 0, 0]
  }
}
```

#### animate_advanced
Advanced animation with multiple properties and easing.

```json
{
  "command": "animate_advanced",
  "params": {
    "object": "ObjectName",
    "easing": "LINEAR|EASE_IN|EASE_OUT|EASE_IN_OUT|BOUNCE",
    "animations": [
      {
        "property": "location",
        "start_frame": 1,
        "end_frame": 50,
        "start_value": [0, 0, 0],
        "end_value": [5, 0, 0]
      }
    ]
  }
}
```

#### camera_animation
Animate cameras with presets.

```json
{
  "command": "camera_animation",
  "params": {
    "camera": "Camera",
    "type": "orbit|dolly",
    "target": [0, 0, 0],
    "duration": 100,
    "radius": 10,
    "height": 5
  }
}
```

### Scene Setup Commands

#### lighting_setup
Create professional lighting setups.

```json
{
  "command": "lighting_setup",
  "params": {
    "type": "three_point|studio",
    "target": [0, 0, 0],
    "intensity": 10
  }
}
```

#### physics_simulation
Add physics to objects.

```json
{
  "command": "physics_simulation",
  "params": {
    "object": "ObjectName",
    "type": "rigid_body|soft_body|cloth",
    "properties": {
      "mass": 1.0,
      "friction": 0.5,
      "restitution": 0.5
    }
  }
}
```

### Procedural Generation

#### procedural_generation
Generate procedural content.

```json
{
  "command": "procedural_generation",
  "params": {
    "type": "terrain|forest|city",
    "seed": 42,
    "size": 10,
    "detail": 5,
    "count": 20
  }
}
```

### Geometry Nodes

#### create_node_group
Create a geometry node group.

```json
{
  "command": "create_node_group",
  "params": {
    "name": "MyNodeGroup",
    "setup": "basic|subdivide|array"
  }
}
```

#### geometry_nodes
Apply geometry nodes to an object.

```json
{
  "command": "geometry_nodes",
  "params": {
    "object": "ObjectName",
    "node_group": "NodeGroupName",
    "parameters": {
      "Level": 2,
      "Count": 5
    }
  }
}
```

### AI Features

#### AI Query
Query the AI assistant.

```json
{
  "ai_query": "scene_summary|suggest_next_action|auto_improve|generate_content",
  "parameters": {
    "type": "lighting|performance",
    "content_type": "basic_scene"
  }
}
```

### Rendering

#### render
Render the current scene.

```json
{
  "command": "render",
  "params": {
    "output": "//render_output",
    "format": "PNG|JPEG|EXR",
    "resolution": [1920, 1080],
    "samples": 128,
    "engine": "CYCLES|EEVEE"
  }
}
```

### Utility Commands

#### python
Execute Python code in Blender.

```json
{
  "command": "python",
  "params": {
    "code": "import bpy\nprint(len(bpy.data.objects))",
    "context": "safe|full|restricted"
  }
}
```

### Batch Processing

Execute multiple commands in sequence.

```json
{
  "batch": [
    {
      "command": "add_object",
      "params": {"type": "cube", "name": "Cube1"}
    },
    {
      "command": "move_object",
      "params": {"name": "Cube1", "location": [2, 0, 0]}
    }
  ]
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8081');

ws.onopen = () => {
  console.log('Connected to Blender');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Commands
```javascript
// Execute command
ws.send(JSON.stringify({
  type: 'command',
  command: 'add_object',
  params: { type: 'cube' }
}));

// Subscribe to updates
ws.send(JSON.stringify({
  type: 'subscribe',
  events: ['scene_update']
}));

// Ping
ws.send(JSON.stringify({
  type: 'ping'
}));
```

## File Watcher

Place JSON command files in the watched directory:

```json
{
  "command": "add_object",
  "params": {
    "type": "sphere",
    "location": [0, 0, 2]
  }
}
```

The file will be processed and a `.result.json` file will be created with the execution result.

## Configuration

Access addon preferences via Edit → Preferences → Add-ons → Blender Remote Control Advanced

### Server Settings
- **HTTP Port**: Default 8080
- **WebSocket Port**: Default 8081

### Paths
- **Command Directory**: Directory for file watcher
- **Template Directory**: Scene template storage

### Features
Toggle individual features:
- Enable WebSocket
- Enable File Watcher
- Enable Batch Processing
- Enable AI Features

### AI Settings
- **Context Frames**: Frames to analyze (1-100)
- **Suggestion Threshold**: AI suggestion sensitivity (0.0-1.0)

## Examples

### Example 1: Create a Simple Scene
```python
import requests
import json

base_url = "http://localhost:8080"

# Create ground plane
requests.post(base_url, json={
    "command": "add_object",
    "params": {
        "type": "plane",
        "name": "Ground",
        "scale": [10, 10, 1]
    }
})

# Add a cube
requests.post(base_url, json={
    "command": "add_object",
    "params": {
        "type": "cube",
        "name": "MainCube",
        "location": [0, 0, 1]
    }
})

# Set material
requests.post(base_url, json={
    "command": "set_material",
    "params": {
        "object": "MainCube",
        "material": "RedMetal",
        "color": [0.8, 0.1, 0.1, 1.0],
        "metallic": 0.9,
        "roughness": 0.1
    }
})

# Setup lighting
requests.post(base_url, json={
    "command": "lighting_setup",
    "params": {
        "type": "three_point",
        "target": [0, 0, 1]
    }
})
```

### Example 2: Animated Scene
```python
# Create animated spheres
for i in range(5):
    # Create sphere
    requests.post(base_url, json={
        "command": "add_object",
        "params": {
            "type": "sphere",
            "name": f"Sphere{i}",
            "location": [i * 2, 0, 1]
        }
    })
    
    # Animate up and down
    requests.post(base_url, json={
        "command": "animate_advanced",
        "params": {
            "object": f"Sphere{i}",
            "easing": "EASE_IN_OUT",
            "animations": [{
                "property": "location",
                "start_frame": 1,
                "end_frame": 50 + i * 10,
                "start_value": [i * 2, 0, 1],
                "end_value": [i * 2, 0, 3]
            }]
        }
    })
```

### Example 3: Procedural City
```python
# Generate city
requests.post(base_url, json={
    "command": "procedural_generation",
    "params": {
        "type": "city",
        "seed": 12345,
        "size": 20,
        "count": 30
    }
})

# Add fog (using Python execution)
requests.post(base_url, json={
    "command": "python",
    "params": {
        "code": """
import bpy
bpy.context.scene.world.use_nodes = True
nodes = bpy.context.scene.world.node_tree.nodes
links = bpy.context.scene.world.node_tree.links

# Add Volume Scatter
volume = nodes.new('ShaderNodeVolumeScatter')
volume.inputs['Density'].default_value = 0.01

# Connect to output
output = nodes['World Output']
links.new(volume.outputs['Volume'], output.inputs['Volume'])
""",
        "context": "safe"
    }
})
```

## Troubleshooting

### Server won't start
- Check if port is already in use
- Ensure Blender has network permissions
- Try a different port in preferences

### Empty responses
- Verify server is running (check status in UI panel)
- Ensure proper JSON formatting in requests
- Check Blender's console for error messages

### WebSocket issues
- Install websockets module: `pip install websockets`
- Check firewall settings
- Verify port is not blocked

### Command failures
- Verify object names exist in scene
- Check parameter types match expected format
- Review returned error messages

## Security Considerations

- The addon allows remote code execution - use only on trusted networks
- Consider implementing authentication for production use
- Restrict Python execution context based on security needs
- Monitor file watcher directory permissions

## Performance Tips

- Use batch commands for multiple operations
- Enable AI optimization for complex scenes
- Implement scene complexity limits
- Use WebSocket for real-time updates instead of polling

## Contributing

This is an open-source project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See LICENSE file for details

## Support

- Report issues on GitHub
- Check documentation for updates
- Join the community Discord
- Review example scripts

---

**Version**: 2.0.0  
**Blender Compatibility**: 3.3.0+  
**Author**: Open Source Community