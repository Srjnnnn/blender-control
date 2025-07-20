"""
Blender Remote Control Addon
A comprehensive addon for controlling Blender externally with WebSocket, file commands,
batch execution, templates, advanced animation, geometry nodes, and AI assistant features.

Author: Open Source Community
License: MIT
Version: 2.0.0
"""

bl_info = {
    "name": "Blender Remote Control Advanced",
    "author": "Eyüp Sercan UYGUR",
    "version": (2, 0, 0),
    "blender": (3, 3, 0),
    "location": "View3D > Sidebar > Remote Control",
    "description": "Advanced external control with WebSocket, AI features, templates, and geometry nodes",
    "category": "System",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/Srjnnnn/blender-control/blender-remote-control-advanced",
    "tracker_url": "https://github.com/Srjnnnn/blender-control/blender-remote-control-advanced/issues",
}

# ============================================================================
# IMPORTS
# ============================================================================

import bpy
import bmesh
import json
import threading
import time
import os
import queue
import uuid
import math
import random
import io
import sys
from pathlib import Path
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty, CollectionProperty
from bpy.types import Panel, Operator, PropertyGroup, AddonPreferences
from mathutils import Vector, Euler, Matrix, Quaternion
import mathutils.geometry
from bpy.app.handlers import persistent

# Try to import optional dependencies
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

try:
    import asyncio
    import websockets
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================

server_instance = None
server_thread = None
websocket_server = None
websocket_thread = None
file_watcher_thread = None
command_queue = queue.Queue()
batch_processor = None

# ============================================================================
# PROPERTY GROUPS
# ============================================================================

class SceneTemplate(PropertyGroup):
    """Scene template definition"""
    name: StringProperty(name="Template Name")
    description: StringProperty(name="Description")
    file_path: StringProperty(name="File Path", subtype='FILE_PATH')
    thumbnail: StringProperty(name="Thumbnail Path", subtype='FILE_PATH')
    category: StringProperty(name="Category", default="General")
    tags: StringProperty(name="Tags")

class AnimationPreset(PropertyGroup):
    """Animation preset definition"""
    name: StringProperty(name="Preset Name")
    description: StringProperty(name="Description")
    animation_type: EnumProperty(
        name="Animation Type",
        items=[
            ('LOCATION', 'Location', 'Location animation'),
            ('ROTATION', 'Rotation', 'Rotation animation'),
            ('SCALE', 'Scale', 'Scale animation'),
            ('CUSTOM', 'Custom', 'Custom property animation'),
        ]
    )
    duration: IntProperty(name="Duration (frames)", default=50)
    easing: EnumProperty(
        name="Easing",
        items=[
            ('LINEAR', 'Linear', 'Linear interpolation'),
            ('EASE_IN', 'Ease In', 'Ease in'),
            ('EASE_OUT', 'Ease Out', 'Ease out'),
            ('EASE_IN_OUT', 'Ease In/Out', 'Ease in and out'),
            ('BOUNCE', 'Bounce', 'Bounce effect'),
        ]
    )

class GeometryNodePreset(PropertyGroup):
    """Geometry node preset definition"""
    name: StringProperty(name="Preset Name")
    description: StringProperty(name="Description")
    node_group_name: StringProperty(name="Node Group")
    parameters: StringProperty(name="Parameters (JSON)")

class RemoteControlAdvancedProperties(PropertyGroup):
    """Main properties for the addon"""
    # Server status
    http_server_running: BoolProperty(name="HTTP Server Running", default=False)
    websocket_server_running: BoolProperty(name="WebSocket Server Running", default=False)
    file_watcher_running: BoolProperty(name="File Watcher Running", default=False)
    
    # Statistics
    command_count: IntProperty(name="Commands Executed", default=0)
    batch_count: IntProperty(name="Batches Executed", default=0)
    websocket_connections: IntProperty(name="WebSocket Connections", default=0)
    
    # Current state
    last_command: StringProperty(name="Last Command", default="")
    current_batch_id: StringProperty(name="Current Batch ID", default="")
    ai_context: StringProperty(name="AI Context", default="")

# ============================================================================
# ADDON PREFERENCES
# ============================================================================

class RemoteControlAdvancedPreferences(AddonPreferences):
    bl_idname = __name__
    
    # Server settings
    http_port: IntProperty(
        name="HTTP Port",
        description="Port for HTTP API server",
        default=8080,
        min=1024,
        max=65535
    )
    
    websocket_port: IntProperty(
        name="WebSocket Port",
        description="Port for WebSocket server",
        default=8081,
        min=1024,
        max=65535
    )
    
    # File system settings
    command_file_path: StringProperty(
        name="Command Directory",
        description="Directory to watch for command files",
        default="//remote_commands/",
        subtype='DIR_PATH'
    )
    
    template_path: StringProperty(
        name="Template Directory",
        description="Directory for scene templates",
        default="//templates/",
        subtype='DIR_PATH'
    )
    
    # Feature toggles
    enable_websocket: BoolProperty(
        name="Enable WebSocket",
        description="Enable WebSocket server for real-time communication",
        default=True
    )
    
    enable_file_watcher: BoolProperty(
        name="Enable File Watcher",
        description="Watch directory for command files",
        default=True
    )
    
    enable_batch_processing: BoolProperty(
        name="Enable Batch Processing",
        description="Enable batch command execution",
        default=True
    )
    
    enable_ai_features: BoolProperty(
        name="Enable AI Features",
        description="Enable advanced AI assistant features",
        default=True
    )
    
    # AI settings
    ai_context_frames: IntProperty(
        name="AI Context Frames",
        description="Number of frames to analyze for AI context",
        default=10,
        min=1,
        max=100
    )
    
    ai_suggestion_threshold: FloatProperty(
        name="AI Suggestion Threshold",
        description="Threshold for AI suggestions",
        default=0.7,
        min=0.0,
        max=1.0
    )
    
    # Templates
    scene_templates: CollectionProperty(type=SceneTemplate)
    animation_presets: CollectionProperty(type=AnimationPreset)
    geometry_presets: CollectionProperty(type=GeometryNodePreset)

    def draw(self, context):
        layout = self.layout
        
        # Server Settings
        box = layout.box()
        box.label(text="Server Settings", icon='NETWORK_DRIVE')
        row = box.row()
        row.prop(self, "http_port")
        row.prop(self, "websocket_port")
        
        # Paths
        box = layout.box()
        box.label(text="Paths", icon='FILE_FOLDER')
        box.prop(self, "command_file_path")
        box.prop(self, "template_path")
        
        # Features
        box = layout.box()
        box.label(text="Features", icon='PREFERENCES')
        box.prop(self, "enable_websocket")
        box.prop(self, "enable_file_watcher")
        box.prop(self, "enable_batch_processing")
        box.prop(self, "enable_ai_features")
        
        # AI Settings
        if self.enable_ai_features:
            box = layout.box()
            box.label(text="AI Settings", icon='EXPERIMENTAL')
            box.prop(self, "ai_context_frames")
            box.prop(self, "ai_suggestion_threshold")

# ============================================================================
# COMMAND HANDLER BASE CLASS
# ============================================================================

class CommandHandler:
    """Base class for command handling functionality"""
    
    def __init__(self):
        self.command_handlers = {
            'add_object': self.add_object,
            'delete_object': self.delete_object,
            'move_object': self.move_object,
            'rotate_object': self.rotate_object,
            'scale_object': self.scale_object,
            'set_material': self.set_material,
            'render': self.render_scene,
            'animate': self.animate_object,
            'animate_advanced': self.animate_advanced,
            'python': self.execute_python,
            'geometry_nodes': self.apply_geometry_nodes,
            'create_node_group': self.create_geometry_node_group,
            'camera_animation': self.animate_camera,
            'lighting_setup': self.setup_lighting,
            'physics_simulation': self.setup_physics,
            'procedural_generation': self.procedural_generation,
            'ai_optimize_scene': self.ai_optimize_scene,
            'ai_suggest_improvements': self.ai_suggest_improvements,
        }
    
    def execute_command(self, command_data):
        """Execute a single command"""
        command = command_data.get('command', '')
        params = command_data.get('params', {})
        
        # Update statistics
        props = bpy.context.scene.remote_control_advanced_props
        props.command_count += 1
        props.last_command = command
        
        # Get handler
        handler = self.command_handlers.get(command)
        if handler:
            return handler(params)
        else:
            return {'success': False, 'error': f'Unknown command: {command}'}
    
    def execute_batch(self, batch_commands):
        """Execute a batch of commands"""
        batch_id = str(uuid.uuid4())
        results = []
        success_count = 0
        
        props = bpy.context.scene.remote_control_advanced_props
        props.current_batch_id = batch_id
        props.batch_count += 1
        
        for i, cmd_data in enumerate(batch_commands):
            try:
                result = self.execute_command(cmd_data)
                result['batch_index'] = i
                results.append(result)
                if result.get('success', False):
                    success_count += 1
            except Exception as e:
                results.append({
                    'batch_index': i,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'batch_id': batch_id,
            'total_commands': len(batch_commands),
            'successful': success_count,
            'failed': len(batch_commands) - success_count,
            'results': results
        }
    
    # ========================================================================
    # OBJECT MANIPULATION COMMANDS
    # ========================================================================
    
    def add_object(self, params):
        """Enhanced object creation with more options"""
        obj_type = params.get('type', 'cube')
        location = Vector(params.get('location', [0, 0, 0]))
        rotation = Euler(params.get('rotation', [0, 0, 0]))
        scale = Vector(params.get('scale', [1, 1, 1]))
        name = params.get('name', f'RemoteObject_{int(time.time())}')
        
        # Advanced parameters
        subdivisions = params.get('subdivisions', 0)
        apply_material = params.get('material')
        parent_to = params.get('parent')
        collection = params.get('collection', 'Collection')
        
        try:
            # Create object based on type
            if obj_type == 'cube':
                bpy.ops.mesh.primitive_cube_add(location=location)
            elif obj_type == 'sphere':
                bpy.ops.mesh.primitive_uv_sphere_add(location=location, segments=32, ring_count=16)
            elif obj_type == 'cylinder':
                bpy.ops.mesh.primitive_cylinder_add(location=location)
            elif obj_type == 'plane':
                bpy.ops.mesh.primitive_plane_add(location=location)
            elif obj_type == 'torus':
                bpy.ops.mesh.primitive_torus_add(location=location)
            elif obj_type == 'monkey':
                bpy.ops.mesh.primitive_monkey_add(location=location)
            elif obj_type == 'light':
                light_type = params.get('light_type', 'POINT')
                energy = params.get('energy', 10)
                bpy.ops.object.light_add(type=light_type, location=location)
                bpy.context.active_object.data.energy = energy
            elif obj_type == 'camera':
                bpy.ops.object.camera_add(location=location)
            elif obj_type == 'empty':
                bpy.ops.object.empty_add(location=location)
            else:
                return {'success': False, 'error': f'Unsupported object type: {obj_type}'}
            
            obj = bpy.context.active_object
            if obj:
                obj.name = name
                obj.rotation_euler = rotation
                obj.scale = scale
                
                # Apply subdivisions if specified
                if subdivisions > 0 and obj.type == 'MESH':
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.subdivide(number_cuts=subdivisions)
                    bpy.ops.object.mode_set(mode='OBJECT')
                
                # Set parent
                if parent_to:
                    parent_obj = bpy.data.objects.get(parent_to)
                    if parent_obj:
                        obj.parent = parent_obj
                
                # Move to collection
                if collection != 'Collection':
                    col = bpy.data.collections.get(collection)
                    if not col:
                        col = bpy.data.collections.new(collection)
                        bpy.context.scene.collection.children.link(col)
                    
                    # Remove from default collection
                    for col_remove in obj.users_collection:
                        col_remove.objects.unlink(obj)
                    col.objects.link(obj)
                
                # Apply material
                if apply_material:
                    self.set_material({'object': name, 'material': apply_material})
            
            return {
                'success': True, 
                'object_name': name, 
                'location': list(location),
                'type': obj_type
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_object(self, params):
        """Enhanced object deletion"""
        obj_name = params.get('name', '')
        delete_children = params.get('delete_children', False)
        delete_materials = params.get('delete_materials', False)
        
        try:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {'success': False, 'error': f'Object not found: {obj_name}'}
            
            deleted_objects = [obj_name]
            
            # Delete children if requested
            if delete_children:
                for child in obj.children:
                    deleted_objects.append(child.name)
                    bpy.data.objects.remove(child, do_unlink=True)
            
            # Store materials before deletion
            materials_to_delete = []
            if delete_materials and obj.type == 'MESH' and obj.data:
                materials_to_delete = [mat for mat in obj.data.materials if mat and mat.users == 1]
            
            # Delete the object
            bpy.data.objects.remove(obj, do_unlink=True)
            
            # Delete unused materials
            for mat in materials_to_delete:
                bpy.data.materials.remove(mat)
            
            return {
                'success': True, 
                'deleted': deleted_objects,
                'deleted_materials': [mat.name for mat in materials_to_delete]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def move_object(self, params):
        """Enhanced object movement with interpolation options"""
        obj_name = params.get('name', '')
        location = Vector(params.get('location', [0, 0, 0]))
        relative = params.get('relative', False)
        interpolate = params.get('interpolate', False)
        duration = params.get('duration', 1.0)
        
        try:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {'success': False, 'error': f'Object not found: {obj_name}'}
            
            original_location = obj.location.copy()
            
            if interpolate:
                # Create smooth interpolated movement
                start_frame = bpy.context.scene.frame_current
                end_frame = start_frame + int(duration * bpy.context.scene.render.fps)
                
                if relative:
                    target_location = original_location + location
                else:
                    target_location = location
                
                # Set keyframes
                obj.location = original_location
                obj.keyframe_insert(data_path="location", frame=start_frame)
                
                obj.location = target_location
                obj.keyframe_insert(data_path="location", frame=end_frame)
                
                return {
                    'success': True, 
                    'object': obj_name, 
                    'animated_from': list(original_location),
                    'animated_to': list(target_location),
                    'duration_frames': end_frame - start_frame
                }
            else:
                # Immediate movement
                if relative:
                    obj.location += location
                else:
                    obj.location = location
                
                return {
                    'success': True, 
                    'object': obj_name, 
                    'new_location': list(obj.location)
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rotate_object(self, params):
        """Enhanced object rotation"""
        obj_name = params.get('name', '')
        rotation = params.get('rotation', [0, 0, 0])
        relative = params.get('relative', False)
        rotation_mode = params.get('mode', 'euler')  # euler, quaternion, axis_angle
        
        try:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {'success': False, 'error': f'Object not found: {obj_name}'}
            
            if rotation_mode == 'euler':
                rot = Euler(rotation)
                if relative:
                    obj.rotation_euler.rotate(rot)
                else:
                    obj.rotation_euler = rot
                result_rotation = list(obj.rotation_euler)
                
            elif rotation_mode == 'quaternion':
                rot = Quaternion(rotation)
                if relative:
                    obj.rotation_quaternion @= rot
                else:
                    obj.rotation_quaternion = rot
                result_rotation = list(obj.rotation_quaternion)
                
            elif rotation_mode == 'axis_angle':
                # rotation should be [angle, axis_x, axis_y, axis_z]
                angle = rotation[0]
                axis = Vector(rotation[1:4])
                rot = Matrix.Rotation(angle, 4, axis)
                if relative:
                    obj.matrix_world @= rot
                else:
                    obj.matrix_world = rot
                result_rotation = list(obj.rotation_euler)
            
            return {
                'success': True, 
                'object': obj_name, 
                'new_rotation': result_rotation,
                'rotation_mode': rotation_mode
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scale_object(self, params):
        """Enhanced object scaling"""
        obj_name = params.get('name', '')
        scale = Vector(params.get('scale', [1, 1, 1]))
        relative = params.get('relative', False)
        uniform = params.get('uniform', False)
        
        try:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {'success': False, 'error': f'Object not found: {obj_name}'}
            
            if uniform:
                # Use only the first scale value for uniform scaling
                scale = Vector([scale[0]] * 3)
            
            if relative:
                obj.scale = Vector([obj.scale[i] * scale[i] for i in range(3)])
            else:
                obj.scale = scale
                
            return {
                'success': True, 
                'object': obj_name, 
                'new_scale': list(obj.scale)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # MATERIAL AND RENDERING COMMANDS
    # ========================================================================
    
    def set_material(self, params):
        """Enhanced material creation and assignment"""
        obj_name = params.get('object', '')
        mat_name = params.get('material', 'RemoteMaterial')
        color = params.get('color', [0.8, 0.8, 0.8, 1.0])
        metallic = params.get('metallic', 0.0)
        roughness = params.get('roughness', 0.5)
        emission = params.get('emission', [0, 0, 0])
        emission_strength = params.get('emission_strength', 1.0)
        
        try:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {'success': False, 'error': f'Object not found: {obj_name}'}
            
            # Create or get material
            material = bpy.data.materials.get(mat_name)
            if not material:
                material = bpy.data.materials.new(name=mat_name)
                material.use_nodes = True
                
            # Configure material nodes
            nodes = material.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            
            if bsdf:
                # Ensure color has 4 components
                if len(color) == 3:
                    color = color + [1.0]
                elif len(color) < 3:
                    color = [0.8, 0.8, 0.8, 1.0]
                    
                bsdf.inputs['Base Color'].default_value = color[:4]
                bsdf.inputs['Metallic'].default_value = metallic
                bsdf.inputs['Roughness'].default_value = roughness
                
                # Handle emission
                if len(emission) == 3:
                    emission_color = emission + [1.0]
                else:
                    emission_color = [0, 0, 0, 1.0]
                    
                bsdf.inputs['Emission'].default_value = emission_color[:4]
                
                # Check if Emission Strength exists (Blender 3.0+)
                if 'Emission Strength' in bsdf.inputs:
                    bsdf.inputs['Emission Strength'].default_value = emission_strength
            
            # Assign material to object
            if obj.data and hasattr(obj.data, 'materials'):
                if obj.data.materials:
                    obj.data.materials[0] = material
                else:
                    obj.data.materials.append(material)
            
            return {
                'success': True, 
                'object': obj_name, 
                'material': mat_name,
                'properties': {
                    'color': color,
                    'metallic': metallic,
                    'roughness': roughness,
                    'emission': emission
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def render_scene(self, params):
        """Enhanced rendering with more options"""
        output_path = params.get('output', '//render_output')
        file_format = params.get('format', 'PNG')
        resolution = params.get('resolution', [1920, 1080])
        samples = params.get('samples', 128)
        engine = params.get('engine', 'CYCLES')
        
        try:
            scene = bpy.context.scene
            
            # Set render settings
            scene.render.filepath = output_path
            scene.render.image_settings.file_format = file_format
            scene.render.resolution_x = resolution[0]
            scene.render.resolution_y = resolution[1]
            scene.render.engine = engine
            
            if engine == 'CYCLES':
                scene.cycles.samples = samples
                scene.cycles.use_denoising = True
            elif engine == 'EEVEE':
                scene.eevee.taa_render_samples = samples
                scene.eevee.use_bloom = True
                scene.eevee.use_ssr = True
            
            # Render
            bpy.ops.render.render(write_still=True)
            
            return {
                'success': True,
                'output_path': output_path,
                'format': file_format,
                'resolution': resolution,
                'engine': engine,
                'samples': samples
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # ANIMATION COMMANDS
    # ========================================================================
    
    def animate_object(self, params):
        """Basic animation function"""
        obj_name = params.get('object', '')
        property_name = params.get('property', 'location')
        start_frame = params.get('start_frame', 1)
        end_frame = params.get('end_frame', 50)
        start_value = params.get('start_value')
        end_value = params.get('end_value')
        
        try:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {'success': False, 'error': f'Object not found: {obj_name}'}
            
            # Set start keyframe
            bpy.context.scene.frame_set(start_frame)
            if property_name == 'location':
                obj.location = Vector(start_value)
            elif property_name == 'rotation':
                obj.rotation_euler = Euler(start_value)
            elif property_name == 'scale':
                obj.scale = Vector(start_value)
            obj.keyframe_insert(data_path=property_name)
            
            # Set end keyframe
            bpy.context.scene.frame_set(end_frame)
            if property_name == 'location':
                obj.location = Vector(end_value)
            elif property_name == 'rotation':
                obj.rotation_euler = Euler(end_value)
            elif property_name == 'scale':
                obj.scale = Vector(end_value)
            obj.keyframe_insert(data_path=property_name)
            
            return {
                'success': True,
                'object': obj_name,
                'property': property_name,
                'frames': [start_frame, end_frame]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def animate_advanced(self, params):
        """Advanced animation with easing and multiple properties"""
        obj_name = params.get('object', '')
        animations = params.get('animations', [])
        easing_type = params.get('easing', 'LINEAR')
        
        try:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {'success': False, 'error': f'Object not found: {obj_name}'}
            
            animated_properties = []
            
            for anim in animations:
                property_name = anim.get('property', 'location')
                start_frame = anim.get('start_frame', 1)
                end_frame = anim.get('end_frame', 50)
                start_value = anim.get('start_value')
                end_value = anim.get('end_value')
                
                if start_value is None or end_value is None:
                    continue
                
                # Convert values to appropriate types
                if property_name == 'location':
                    start_value = Vector(start_value)
                    end_value = Vector(end_value)
                elif property_name == 'rotation_euler':
                    start_value = Euler(start_value)
                    end_value = Euler(end_value)
                elif property_name == 'scale':
                    start_value = Vector(start_value)
                    end_value = Vector(end_value)
                
                # Set start keyframe
                bpy.context.scene.frame_set(start_frame)
                setattr(obj, property_name, start_value)
                obj.keyframe_insert(data_path=property_name)
                
                # Set end keyframe
                bpy.context.scene.frame_set(end_frame)
                setattr(obj, property_name, end_value)
                obj.keyframe_insert(data_path=property_name)
                
                # Apply easing
                if obj.animation_data and obj.animation_data.action:
                    for fcurve in obj.animation_data.action.fcurves:
                        if property_name in fcurve.data_path:
                            for keyframe in fcurve.keyframe_points:
                                if easing_type == 'EASE_IN':
                                    keyframe.interpolation = 'BEZIER'
                                    keyframe.handle_left_type = 'AUTO'
                                    keyframe.handle_right_type = 'AUTO'
                                elif easing_type == 'EASE_OUT':
                                    keyframe.interpolation = 'BEZIER'
                                    keyframe.handle_left_type = 'AUTO'
                                    keyframe.handle_right_type = 'VECTOR'
                                elif easing_type == 'EASE_IN_OUT':
                                    keyframe.interpolation = 'BEZIER'
                                    keyframe.handle_left_type = 'AUTO'
                                    keyframe.handle_right_type = 'AUTO'
                                elif easing_type == 'BOUNCE':
                                    keyframe.interpolation = 'BACK'
                                else:  # LINEAR
                                    keyframe.interpolation = 'LINEAR'
                
                animated_properties.append({
                    'property': property_name,
                    'start_frame': start_frame,
                    'end_frame': end_frame,
                    'easing': easing_type
                })
            
            return {
                'success': True,
                'object': obj_name,
                'animated_properties': animated_properties
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def animate_camera(self, params):
        """Create camera animations"""
        camera_name = params.get('camera', 'Camera')
        animation_type = params.get('type', 'orbit')
        target = params.get('target', [0, 0, 0])
        duration = params.get('duration', 100)
        
        try:
            camera = bpy.data.objects.get(camera_name)
            if not camera or camera.type != 'CAMERA':
                return {'success': False, 'error': f'Camera not found: {camera_name}'}
            
            target_vec = Vector(target)
            start_frame = bpy.context.scene.frame_current
            end_frame = start_frame + duration
            
            if animation_type == 'orbit':
                radius = params.get('radius', 10)
                height = params.get('height', 5)
                
                for frame in range(start_frame, end_frame + 1):
                    bpy.context.scene.frame_set(frame)
                    
                    # Calculate orbit position
                    angle = (frame - start_frame) / duration * 2 * math.pi
                    x = target_vec.x + radius * math.cos(angle)
                    y = target_vec.y + radius * math.sin(angle)
                    z = target_vec.z + height
                    
                    camera.location = (x, y, z)
                    
                    # Look at target
                    direction = target_vec - camera.location
                    rot_quat = direction.to_track_quat('-Z', 'Y')
                    camera.rotation_euler = rot_quat.to_euler()
                    
                    # Insert keyframes
                    camera.keyframe_insert(data_path="location")
                    camera.keyframe_insert(data_path="rotation_euler")
            
            elif animation_type == 'dolly':
                start_pos = Vector(params.get('start_position', camera.location))
                end_pos = Vector(params.get('end_position', target))
                
                # Animate position
                bpy.context.scene.frame_set(start_frame)
                camera.location = start_pos
                camera.keyframe_insert(data_path="location")
                
                bpy.context.scene.frame_set(end_frame)
                camera.location = end_pos
                camera.keyframe_insert(data_path="location")
            
            return {
                'success': True,
                'camera': camera_name,
                'animation_type': animation_type,
                'duration': duration
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # GEOMETRY NODES COMMANDS
    # ========================================================================
    
    def apply_geometry_nodes(self, params):
        """Apply geometry nodes to an object"""
        obj_name = params.get('object', '')
        node_group_name = params.get('node_group', '')
        node_params = params.get('parameters', {})
        
        try:
            obj = bpy.data.objects.get(obj_name)
            if not obj or obj.type != 'MESH':
                return {'success': False, 'error': f'Mesh object not found: {obj_name}'}
            
            node_group = bpy.data.node_groups.get(node_group_name)
            if not node_group:
                return {'success': False, 'error': f'Node group not found: {node_group_name}'}
            
            # Add geometry nodes modifier
            modifier = obj.modifiers.new(name="GeometryNodes", type='NODES')
            modifier.node_group = node_group
            
            # Set parameters
            for param_name, value in node_params.items():
                if param_name in modifier:
                    modifier[param_name] = value
            
            return {
                'success': True,
                'object': obj_name,
                'node_group': node_group_name,
                'parameters': node_params
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_geometry_node_group(self, params):
        """Create a new geometry node group"""
        group_name = params.get('name', 'CustomNodeGroup')
        node_setup = params.get('setup', 'basic')
        
        try:
            # Create new node group
            node_group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
            
            # Add input and output nodes
            input_node = node_group.nodes.new('NodeGroupInput')
            output_node = node_group.nodes.new('NodeGroupOutput')
            
            input_node.location = (-300, 0)
            output_node.location = (300, 0)
            
            # Add geometry input/output - Updated for newer Blender versions
            if hasattr(node_group, 'interface'):
                # Blender 4.0+ interface
                node_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
                node_group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
            else:
                # Older Blender versions
                node_group.inputs.new('NodeSocketGeometry', 'Geometry')
                node_group.outputs.new('NodeSocketGeometry', 'Geometry')
            
            if node_setup == 'subdivide':
                # Create subdivision setup
                subdiv_node = node_group.nodes.new('GeometryNodeSubdivisionSurface')
                subdiv_node.location = (0, 0)
                
                # Add level input
                if hasattr(node_group, 'interface'):
                    node_group.interface.new_socket('Level', in_out='INPUT', socket_type='NodeSocketInt')
                else:
                    node_group.inputs.new('NodeSocketInt', 'Level')
                
                # Connect nodes
                node_group.links.new(input_node.outputs['Geometry'], subdiv_node.inputs['Mesh'])
                node_group.links.new(input_node.outputs['Level'], subdiv_node.inputs['Level'])
                node_group.links.new(subdiv_node.outputs['Mesh'], output_node.inputs['Geometry'])
                
            elif node_setup == 'array':
                # Create array setup
                array_node = node_group.nodes.new('GeometryNodeMeshToPoints')
                instance_node = node_group.nodes.new('GeometryNodeInstanceOnPoints')
                
                array_node.location = (-100, 0)
                instance_node.location = (100, 0)
                
                # Add count input
                if hasattr(node_group, 'interface'):
                    node_group.interface.new_socket('Count', in_out='INPUT', socket_type='NodeSocketInt')
                else:
                    node_group.inputs.new('NodeSocketInt', 'Count')
                
                # Connect nodes
                node_group.links.new(input_node.outputs['Geometry'], array_node.inputs['Mesh'])
                node_group.links.new(array_node.outputs['Points'], instance_node.inputs['Points'])
                node_group.links.new(input_node.outputs['Geometry'], instance_node.inputs['Instance'])
                node_group.links.new(instance_node.outputs['Instances'], output_node.inputs['Geometry'])
            
            else:  # basic
                # Simple pass-through
                node_group.links.new(input_node.outputs['Geometry'], output_node.inputs['Geometry'])
            
            return {
                'success': True,
                'node_group': group_name,
                'setup': node_setup,
                'nodes': len(node_group.nodes)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # SCENE SETUP COMMANDS
    # ========================================================================
    
    def setup_lighting(self, params):
        """Setup advanced lighting rigs"""
        setup_type = params.get('type', 'three_point')
        target = Vector(params.get('target', [0, 0, 0]))
        intensity = params.get('intensity', 10)
        
        try:
            lights_created = []
            
            if setup_type == 'three_point':
                # Key light
                bpy.ops.object.light_add(type='SUN', location=target + Vector([5, -5, 8]))
                key_light = bpy.context.active_object
                key_light.name = "KeyLight"
                key_light.data.energy = intensity
                key_light.data.color = (1, 0.95, 0.8)
                lights_created.append("KeyLight")
                
                # Fill light
                bpy.ops.object.light_add(type='AREA', location=target + Vector([-3, -3, 4]))
                fill_light = bpy.context.active_object
                fill_light.name = "FillLight"
                fill_light.data.energy = intensity * 0.3
                fill_light.data.color = (0.8, 0.9, 1)
                lights_created.append("FillLight")
                
                # Rim light
                bpy.ops.object.light_add(type='SPOT', location=target + Vector([0, 5, 6]))
                rim_light = bpy.context.active_object
                rim_light.name = "RimLight"
                rim_light.data.energy = intensity * 0.5
                rim_light.data.color = (1, 1, 0.9)
                lights_created.append("RimLight")
            
            elif setup_type == 'studio':
                # Main key light
                bpy.ops.object.light_add(type='AREA', location=target + Vector([3, -3, 5]))
                main_light = bpy.context.active_object
                main_light.name = "StudioMain"
                main_light.data.energy = intensity
                main_light.data.size = 3
                lights_created.append("StudioMain")
                
                # Side lights
                for i, pos in enumerate([Vector([-4, 0, 3]), Vector([4, 0, 3])]):
                    bpy.ops.object.light_add(type='AREA', location=target + pos)
                    side_light = bpy.context.active_object
                    side_light.name = f"StudioSide{i+1}"
                    side_light.data.energy = intensity * 0.4
                    side_light.data.size = 2
                    lights_created.append(f"StudioSide{i+1}")
                
                # Top light
                bpy.ops.object.light_add(type='AREA', location=target + Vector([0, 0, 8]))
                top_light = bpy.context.active_object
                top_light.name = "StudioTop"
                top_light.data.energy = intensity * 0.2
                top_light.data.size = 4
                lights_created.append("StudioTop")
            
            return {
                'success': True,
                'setup_type': setup_type,
                'lights_created': lights_created,
                'target': list(target)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def setup_physics(self, params):
        """Setup physics simulation"""
        obj_name = params.get('object', '')
        physics_type = params.get('type', 'rigid_body')
        properties = params.get('properties', {})
        
        try:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {'success': False, 'error': f'Object not found: {obj_name}'}
            
            if physics_type == 'rigid_body':
                # Add rigid body physics
                bpy.context.view_layer.objects.active = obj
                bpy.ops.rigidbody.object_add()
                
                # Set properties
                rb = obj.rigid_body
                rb.type = properties.get('type', 'ACTIVE')
                rb.mass = properties.get('mass', 1.0)
                rb.friction = properties.get('friction', 0.5)
                rb.restitution = properties.get('restitution', 0.5)
                
            elif physics_type == 'soft_body':
                # Add soft body physics
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_add(type='SOFT_BODY')
                
                # Set properties
                sb = obj.modifiers["Softbody"].settings
                sb.mass = properties.get('mass', 1.0)
                sb.friction = properties.get('friction', 5.0)
                sb.spring_length = properties.get('spring_length', 0.2)
                
            elif physics_type == 'cloth':
                # Add cloth physics
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_add(type='CLOTH')
                
                # Set properties
                cloth = obj.modifiers["Cloth"].settings
                cloth.mass = properties.get('mass', 0.3)
                cloth.air_damping = properties.get('air_damping', 1.0)
                cloth.quality = properties.get('quality', 5)
            
            return {
                'success': True,
                'object': obj_name,
                'physics_type': physics_type,
                'properties': properties
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # PROCEDURAL GENERATION COMMANDS
    # ========================================================================
    
    def procedural_generation(self, params):
        """Generate procedural content"""
        generation_type = params.get('type', 'terrain')
        seed = params.get('seed', 42)
        size = params.get('size', 10)
        detail = params.get('detail', 5)
        
        try:
            random.seed(seed)
            
            if generation_type == 'terrain':
                # Create terrain mesh
                bpy.ops.mesh.primitive_plane_add(size=size, location=[0, 0, 0])
                terrain = bpy.context.active_object
                terrain.name = "ProceduralTerrain"
                
                # Enter edit mode and subdivide
                bpy.ops.object.mode_set(mode='EDIT')
                for _ in range(detail):
                    bpy.ops.mesh.subdivide()
                
                # Apply displacement
                bpy.ops.object.mode_set(mode='OBJECT')
                mesh = terrain.data
                
                for vertex in mesh.vertices:
                    noise_val = random.uniform(-1, 1) * 2
                    vertex.co.z += noise_val
                
                mesh.update()
                
            elif generation_type == 'forest':
                trees_created = []
                tree_count = params.get('count', 20)
                
                for i in range(tree_count):
                    # Random position
                    x = random.uniform(-size, size)
                    y = random.uniform(-size, size)
                    
                    # Create tree trunk
                    bpy.ops.mesh.primitive_cylinder_add(
                        radius=random.uniform(0.1, 0.3),
                        depth=random.uniform(2, 5),
                        location=[x, y, 0]
                    )
                    trunk = bpy.context.active_object
                    trunk.name = f"TreeTrunk_{i}"
                    
                    # Create tree crown
                    bpy.ops.mesh.primitive_ico_sphere_add(
                        radius=random.uniform(1, 2),
                        location=[x, y, trunk.dimensions.z]
                    )
                    crown = bpy.context.active_object
                    crown.name = f"TreeCrown_{i}"
                    crown.parent = trunk
                    
                    trees_created.extend([trunk.name, crown.name])
                
                return {
                    'success': True,
                    'generation_type': generation_type,
                    'objects_created': trees_created,
                    'count': tree_count
                }
            
            elif generation_type == 'city':
                buildings_created = []
                building_count = params.get('count', 15)
                
                for i in range(building_count):
                    # Random position and size
                    x = random.uniform(-size, size)
                    y = random.uniform(-size, size)
                    height = random.uniform(3, 15)
                    width = random.uniform(1, 3)
                    
                    bpy.ops.mesh.primitive_cube_add(
                        size=2,
                        location=[x, y, height/2]
                    )
                    building = bpy.context.active_object
                    building.name = f"Building_{i}"
                    building.scale = [width, width, height/2]
                    
                    buildings_created.append(building.name)
                
                return {
                    'success': True,
                    'generation_type': generation_type,
                    'objects_created': buildings_created,
                    'count': building_count
                }
            
            return {
                'success': True,
                'generation_type': generation_type,
                'seed': seed,
                'size': size,
                'detail': detail
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # AI COMMANDS
    # ========================================================================
    
    def ai_optimize_scene(self, params):
        """AI-powered scene optimization"""
        optimization_type = params.get('type', 'performance')
        target_fps = params.get('target_fps', 60)
        
        try:
            optimizations_applied = []
            
            if optimization_type == 'performance':
                # Analyze scene complexity
                total_vertices = sum(len(obj.data.vertices) for obj in bpy.context.scene.objects 
                                   if obj.type == 'MESH' and obj.data)
                
                if total_vertices > 100000:
                    # Apply LOD to high-poly objects
                    for obj in bpy.context.scene.objects:
                        if obj.type == 'MESH' and obj.data and len(obj.data.vertices) > 10000:
                            # Add decimation modifier
                            decimate_mod = obj.modifiers.new(name="AI_Decimate", type='DECIMATE')
                            decimate_mod.ratio = 0.5
                            optimizations_applied.append(f"Decimated {obj.name}")
                
                # Optimize materials
                for mat in bpy.data.materials:
                    if mat.use_nodes:
                        nodes = mat.node_tree.nodes
                        # Simplify complex node setups
                        if len(nodes) > 10:
                            # Keep only essential nodes
                            essential_nodes = ['Principled BSDF', 'Material Output']
                            for node in list(nodes):
                                if node.bl_idname not in essential_nodes and node.name not in essential_nodes:
                                    nodes.remove(node)
                            optimizations_applied.append(f"Simplified material {mat.name}")
            
            elif optimization_type == 'lighting':
                # Optimize lighting setup
                lights = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
                light_count = len(lights)
                
                if light_count > 5:
                    # Remove weakest lights
                    lights.sort(key=lambda x: x.data.energy)
                    
                    for light in lights[:max(0, light_count-3)]:  # Keep only 3 strongest
                        bpy.data.objects.remove(light, do_unlink=True)
                        optimizations_applied.append(f"Removed weak light {light.name}")
            
            return {
                'success': True,
                'optimization_type': optimization_type,
                'optimizations_applied': optimizations_applied,
                'scene_stats': {
                    'objects': len(bpy.context.scene.objects),
                    'materials': len(bpy.data.materials),
                    'lights': len([obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT'])
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def ai_suggest_improvements(self, params):
        """Generate AI-powered suggestions for scene improvement"""
        analysis_type = params.get('analysis', 'composition')
        
        try:
            suggestions = []
            
            if analysis_type == 'composition':
                # Analyze object distribution
                objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
                
                if len(objects) == 0:
                    suggestions.append({
                        'type': 'content',
                        'priority': 'high',
                        'suggestion': 'Scene is empty. Consider adding some objects.',
                        'action': 'add_object'
                    })
                
                # Check for clustering
                positions = [obj.location for obj in objects]
                if len(positions) > 1:
                    center = Vector([sum(p[i] for p in positions)/len(positions) for i in range(3)])
                    distances = [(pos - center).length for pos in positions]
                    avg_distance = sum(distances) / len(distances)
                    
                    if avg_distance < 2:
                        suggestions.append({
                            'type': 'composition',
                            'priority': 'medium',
                            'suggestion': 'Objects are clustered together. Consider spreading them out.',
                            'action': 'redistribute_objects'
                        })
            
            elif analysis_type == 'lighting':
                lights = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
                
                if len(lights) == 0:
                    suggestions.append({
                        'type': 'lighting',
                        'priority': 'high',
                        'suggestion': 'No lights in scene. Add lighting for better visibility.',
                        'action': 'add_lighting'
                    })
                elif len(lights) == 1:
                    suggestions.append({
                        'type': 'lighting',
                        'priority': 'medium',
                        'suggestion': 'Single light source creates harsh shadows. Add fill lighting.',
                        'action': 'add_fill_light'
                    })
            
            elif analysis_type == 'materials':
                objects_without_materials = [obj for obj in bpy.context.scene.objects 
                                           if obj.type == 'MESH' and obj.data and not obj.data.materials]
                
                if objects_without_materials:
                    suggestions.append({
                        'type': 'materials',
                        'priority': 'medium',
                        'suggestion': f'{len(objects_without_materials)} objects have no materials.',
                        'action': 'assign_materials',
                        'objects': [obj.name for obj in objects_without_materials]
                    })
            
            return {
                'success': True,
                'analysis_type': analysis_type,
                'suggestions': suggestions,
                'suggestion_count': len(suggestions)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========================================================================
    # UTILITY COMMANDS
    # ========================================================================
    
    def execute_python(self, params):
        """Enhanced Python execution with more safety"""
        code = params.get('code', '')
        context = params.get('context', 'safe')  # safe, full, restricted
        
        if not code:
            return {'success': False, 'error': 'No code provided'}
        
        try:
            if context == 'safe':
                # Restricted environment
                safe_globals = {
                    'bpy': bpy,
                    'bmesh': bmesh,
                    'Vector': Vector,
                    'Euler': Euler,
                    'Matrix': Matrix,
                    'Quaternion': Quaternion,
                    'mathutils': mathutils,
                    'math': math,
                    'random': random,
                    '__builtins__': {}
                }
            elif context == 'full':
                # Full Python environment
                safe_globals = globals().copy()
            else:  # restricted
                # Very limited environment
                safe_globals = {
                    'bpy': bpy,
                    'Vector': Vector,
                    '__builtins__': {}
                }
            
            # Capture output
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            try:
                exec(code, safe_globals)
                output = captured_output.getvalue()
            finally:
                sys.stdout = old_stdout
            
            return {
                'success': True,
                'message': 'Code executed successfully',
                'output': output,
                'context': context
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'context': context}

# ============================================================================
# HTTP HANDLER
# ============================================================================

class AdvancedBlenderHTTPHandler(BaseHTTPRequestHandler, CommandHandler):
    """Enhanced HTTP handler with advanced features"""
    
    def __init__(self, *args, **kwargs):
        CommandHandler.__init__(self)
        if args:  # Only call parent init if we have args
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to suppress console logging"""
        pass
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        params = parse_qs(parsed_path.query)
        
        try:
            if path == '/status':
                response_data = self.get_status()
                self.send_json_response(response_data)
            elif path == '/scene':
                response_data = self.get_scene_data()
                self.send_json_response(response_data)
            elif path == '/templates':
                response_data = self.get_templates()
                self.send_json_response(response_data)
            elif path == '/presets':
                response_data = self.get_presets()
                self.send_json_response(response_data)
            elif path == '/ai/context':
                response_data = self.get_ai_context()
                self.send_json_response(response_data)
            elif path == '/ai/suggestions':
                response_data = self.get_ai_suggestions()
                self.send_json_response(response_data)
            elif path.startswith('/batch/'):
                batch_id = path.split('/')[-1]
                response_data = self.get_batch_status(batch_id)
                self.send_json_response(response_data)
            else:
                self.send_error(404, 'Endpoint not found')
        except Exception as e:
            self.send_error(500, f'Server error: {str(e)}')
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
            
            if 'batch' in data:
                result = self.execute_batch(data['batch'])
            elif 'template' in data:
                result = self.apply_template(data)
            elif 'ai_query' in data:
                result = self.process_ai_query(data)
            else:
                result = self.execute_command(data)
            
            self.send_json_response(result)
            
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
        except Exception as e:
            self.send_error(500, f'Error: {str(e)}')
    
    def send_json_response(self, data):
        """Send JSON response with proper headers"""
        response_data = json.dumps(data, indent=2).encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(response_data)
    
    # ========================================================================
    # STATUS AND INFO METHODS
    # ========================================================================
    
    def get_status(self):
        """Get current status information"""
        try:
            props = bpy.context.scene.remote_control_advanced_props
            prefs = bpy.context.preferences.addons[__name__].preferences
            
            status_data = {
                'blender_version': bpy.app.version_string,
                'addon_version': '.'.join(map(str, bl_info['version'])),
                'scene_objects': len(bpy.context.scene.objects),
                'render_engine': bpy.context.scene.render.engine,
                'websocket_connections': props.websocket_connections,
                'commands_executed': props.command_count,
                'batches_executed': props.batch_count,
                'ai_features_enabled': prefs.enable_ai_features,
                'servers': {
                    'http': props.http_server_running,
                    'websocket': props.websocket_server_running,
                    'file_watcher': props.file_watcher_running
                }
            }
            
            return status_data
            
        except Exception as e:
            return {'error': f'Failed to get status: {str(e)}'}
    
    def get_scene_data(self):
        """Enhanced scene data with geometry nodes and materials info"""
        try:
            objects_data = []
            
            for obj in bpy.context.scene.objects:
                obj_data = {
                    'name': obj.name,
                    'type': obj.type,
                    'location': list(obj.location),
                    'rotation': list(obj.rotation_euler),
                    'scale': list(obj.scale),
                    'visible': obj.visible_get(),
                    'selected': obj.select_get(),
                    'parent': obj.parent.name if obj.parent else None,
                    'children': [child.name for child in obj.children],
                    'collections': [col.name for col in obj.users_collection]
                }
                
                if obj.type == 'MESH' and obj.data:
                    obj_data.update({
                        'vertices': len(obj.data.vertices),
                        'faces': len(obj.data.polygons),
                        'materials': [mat.name for mat in obj.data.materials if mat],
                        'has_geometry_nodes': bool(obj.modifiers and any(mod.type == 'NODES' for mod in obj.modifiers))
                    })
                    
                    # Geometry nodes info
                    for mod in obj.modifiers:
                        if mod.type == 'NODES' and mod.node_group:
                            obj_data['geometry_node_groups'] = obj_data.get('geometry_node_groups', [])
                            obj_data['geometry_node_groups'].append({
                                'name': mod.node_group.name,
                                'inputs': []  # Simplified for compatibility
                            })
                
                objects_data.append(obj_data)
            
            return {
                'frame_current': bpy.context.scene.frame_current,
                'frame_start': bpy.context.scene.frame_start,
                'frame_end': bpy.context.scene.frame_end,
                'objects': objects_data,
                'materials': [{'name': mat.name, 'users': mat.users} for mat in bpy.data.materials],
                'collections': [{'name': col.name, 'objects': len(col.objects)} for col in bpy.data.collections],
                'geometry_node_groups': [{'name': ng.name, 'type': ng.type} for ng in bpy.data.node_groups if ng.type == 'GEOMETRY'],
                'animation_data': self.get_animation_summary()
            }
            
        except Exception as e:
            return {'error': f'Failed to get scene data: {str(e)}'}
    
    def get_animation_summary(self):
        """Get summary of animations in the scene"""
        animated_objects = []
        for obj in bpy.context.scene.objects:
            if obj.animation_data and obj.animation_data.action:
                animated_objects.append({
                    'object': obj.name,
                    'action': obj.animation_data.action.name,
                    'frame_range': list(obj.animation_data.action.frame_range),
                    'fcurves': len(obj.animation_data.action.fcurves)
                })
        return animated_objects
    
    def get_templates(self):
        """Get available scene templates"""
        prefs = bpy.context.preferences.addons[__name__].preferences
        templates = []
        
        for template in prefs.scene_templates:
            templates.append({
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'tags': template.tags.split(',') if template.tags else []
            })
        
        return {'templates': templates}
    
    def get_presets(self):
        """Get available presets"""
        prefs = bpy.context.preferences.addons[__name__].preferences
        
        animation_presets = []
        for preset in prefs.animation_presets:
            animation_presets.append({
                'name': preset.name,
                'description': preset.description,
                'type': preset.animation_type,
                'duration': preset.duration,
                'easing': preset.easing
            })
        
        geometry_presets = []
        for preset in prefs.geometry_presets:
            geometry_presets.append({
                'name': preset.name,
                'description': preset.description,
                'node_group': preset.node_group_name
            })
        
        return {
            'animation_presets': animation_presets,
            'geometry_presets': geometry_presets
        }
    
    def get_batch_status(self, batch_id):
        """Get status of a batch execution"""
        props = bpy.context.scene.remote_control_advanced_props
        
        if props.current_batch_id == batch_id:
            return {
                'batch_id': batch_id,
                'status': 'current',
                'message': 'This is the current batch'
            }
        else:
            return {
                'batch_id': batch_id,
                'status': 'completed',
                'message': 'Batch execution completed'
            }
    
    # ========================================================================
    # TEMPLATE AND AI METHODS
    # ========================================================================
    
    def apply_template(self, data):
        """Apply a scene template"""
        template_name = data.get('template', '')
        parameters = data.get('parameters', {})
        
        try:
            prefs = bpy.context.preferences.addons[__name__].preferences
            template = None
            
            for t in prefs.scene_templates:
                if t.name == template_name:
                    template = t
                    break
            
            if not template:
                return {'success': False, 'error': f'Template not found: {template_name}'}
            
            # Load template file if it exists
            if template.file_path and os.path.exists(template.file_path):
                bpy.ops.wm.open_mainfile(filepath=template.file_path)
            
            # Apply parameters
            for param, value in parameters.items():
                if param == 'scale_all':
                    for obj in bpy.context.scene.objects:
                        if obj.type == 'MESH':
                            obj.scale *= value
                elif param == 'material_color':
                    for mat in bpy.data.materials:
                        if mat.use_nodes:
                            bsdf = mat.node_tree.nodes.get("Principled BSDF")
                            if bsdf:
                                bsdf.inputs['Base Color'].default_value = value + [1.0]
            
            return {
                'success': True,
                'template': template_name,
                'parameters': parameters
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_ai_context(self):
        """Get AI context about current scene"""
        try:
            context = {
                'scene_analysis': {
                    'object_count': len(bpy.context.scene.objects),
                    'mesh_objects': len([obj for obj in bpy.context.scene.objects if obj.type == 'MESH']),
                    'light_count': len([obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']),
                    'camera_count': len([obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']),
                    'total_vertices': sum(len(obj.data.vertices) for obj in bpy.context.scene.objects 
                                        if obj.type == 'MESH' and obj.data),
                    'materials_count': len(bpy.data.materials),
                    'has_animation': any(obj.animation_data for obj in bpy.context.scene.objects),
                    'render_engine': bpy.context.scene.render.engine,
                    'frame_range': [bpy.context.scene.frame_start, bpy.context.scene.frame_end]
                },
                'recommendations': [],
                'complexity_score': 0
            }
            
            # Calculate complexity score
            complexity = 0
            complexity += len(bpy.context.scene.objects) * 0.1
            complexity += sum(len(obj.data.vertices) for obj in bpy.context.scene.objects 
                            if obj.type == 'MESH' and obj.data) * 0.0001
            complexity += len(bpy.data.materials) * 0.05
            
            context['complexity_score'] = min(complexity, 10)  # Cap at 10
            
            # Generate recommendations based on analysis
            if context['scene_analysis']['mesh_objects'] == 0:
                context['recommendations'].append("Consider adding some mesh objects to populate the scene")
            
            if context['scene_analysis']['light_count'] == 0:
                context['recommendations'].append("Add lighting to improve scene visibility and mood")
            
            if context['scene_analysis']['materials_count'] == 0:
                context['recommendations'].append("Apply materials to objects for better visual appeal")
            
            return context
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_ai_suggestions(self):
        """Get AI suggestions for scene improvement"""
        return self.ai_suggest_improvements({'analysis': 'composition'})
    
    def process_ai_query(self, data):
        """Process AI-specific queries"""
        query_type = data.get('ai_query', '')
        parameters = data.get('parameters', {})
        
        try:
            if query_type == 'scene_summary':
                return self.get_ai_context()
            
            elif query_type == 'suggest_next_action':
                suggestions = self.ai_suggest_improvements({'analysis': 'composition'})
                return suggestions
            
            elif query_type == 'auto_improve':
                improvement_type = parameters.get('type', 'lighting')
                return self.ai_optimize_scene({'type': improvement_type})
            
            elif query_type == 'generate_content':
                content_type = parameters.get('content_type', 'basic_scene')
                
                if content_type == 'basic_scene':
                    # Create a basic scene automatically
                    commands = [
                        {'command': 'add_object', 'params': {'type': 'plane', 'location': [0, 0, 0], 'name': 'Ground', 'scale': [10, 10, 1]}},
                        {'command': 'add_object', 'params': {'type': 'cube', 'location': [0, 0, 1], 'name': 'MainObject'}},
                        {'command': 'setup_lighting', 'params': {'type': 'three_point', 'target': [0, 0, 1]}},
                        {'command': 'add_object', 'params': {'type': 'camera', 'location': [7, -7, 5], 'name': 'MainCamera'}},
                    ]
                    
                    results = []
                    for cmd in commands:
                        result = self.execute_command(cmd)
                        results.append(result)
                    
                    return {
                        'success': True,
                        'content_type': content_type,
                        'actions_performed': len(commands),
                        'results': results
                    }
            
            return {'success': False, 'error': f'Unknown AI query: {query_type}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# ============================================================================
# WEBSOCKET SERVER
# ============================================================================

class WebSocketServer:
    def __init__(self, host='localhost', port=8081):
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None
        
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        props = bpy.context.scene.remote_control_advanced_props
        props.websocket_connections = len(self.clients)
        
        try:
            await websocket.send(json.dumps({
                'type': 'connection',
                'status': 'connected',
                'message': 'Welcome to Blender Remote Control WebSocket'
            }))
            
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            props.websocket_connections = len(self.clients)
    
    async def handle_message(self, websocket, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            command_type = data.get('type', 'command')
            
            if command_type == 'command':
                # Execute Blender command
                handler = AdvancedBlenderHTTPHandler()
                result = handler.execute_command(data)
                
                response = {
                    'type': 'command_result',
                    'id': data.get('id'),
                    'result': result
                }
                
            elif command_type == 'subscribe':
                # Subscribe to scene updates
                response = {
                    'type': 'subscription',
                    'status': 'subscribed',
                    'events': data.get('events', ['scene_update'])
                }
                
            elif command_type == 'ping':
                response = {
                    'type': 'pong',
                    'timestamp': time.time()
                }
            
            else:
                response = {
                    'type': 'error',
                    'message': f'Unknown message type: {command_type}'
                }
            
            await websocket.send(json.dumps(response))
            
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def broadcast_scene_update(self):
        """Broadcast scene updates to all connected clients"""
        if not self.clients:
            return
        
        handler = AdvancedBlenderHTTPHandler()
        scene_data = handler.get_scene_data()
        
        message = json.dumps({
            'type': 'scene_update',
            'timestamp': time.time(),
            'scene': scene_data
        })
        
        # Send to all connected clients
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected
    
    def start_server(self):
        """Start the WebSocket server"""
        if WEBSOCKET_AVAILABLE:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.server = websockets.serve(
                self.register_client,
                self.host,
                self.port
            )
            
            loop.run_until_complete(self.server)
            loop.run_forever()

# ============================================================================
# FILE WATCHER
# ============================================================================

class FileWatcher:
    def __init__(self, watch_dir):
        self.watch_dir = Path(watch_dir).expanduser().resolve()
        self.watch_dir.mkdir(exist_ok=True)
        self.running = False
        
    def start_watching(self):
        """Start watching for command files"""
        self.running = True
        while self.running:
            try:
                # Look for .json command files
                for file_path in self.watch_dir.glob('*.json'):
                    if file_path.is_file():
                        self.process_command_file(file_path)
                        
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"File watcher error: {e}")
                time.sleep(5)
    
    def process_command_file(self, file_path):
        """Process a command file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Execute the command
            handler = AdvancedBlenderHTTPHandler()
            
            if 'batch' in data:
                result = handler.execute_batch(data['batch'])
            else:
                result = handler.execute_command(data)
            
            # Write result file
            result_file = file_path.with_suffix('.result.json')
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            # Remove original command file
            file_path.unlink()
            
        except Exception as e:
            error_file = file_path.with_suffix('.error.json')
            with open(error_file, 'w') as f:
                json.dump({'error': str(e), 'timestamp': time.time()}, f, indent=2)
            
            file_path.unlink()
    
    def stop_watching(self):
        """Stop watching files"""
        self.running = False

# ============================================================================
# HANDLERS
# ============================================================================

@persistent
def scene_update_handler(scene):
    """Handle scene updates for WebSocket broadcasting"""
    global websocket_server
    if websocket_server and websocket_server.clients:
        # Schedule broadcast in a thread-safe way
        def broadcast():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(websocket_server.broadcast_scene_update())
                loop.close()
            except:
                pass
        
        threading.Thread(target=broadcast, daemon=True).start()

# ============================================================================
# OPERATORS
# ============================================================================

class REMOTE_CONTROL_OT_start_http_server(Operator):
    bl_idname = "remote_control.start_http_server"
    bl_label = "Start HTTP Server"
    bl_description = "Start the HTTP API server"
    
    def execute(self, context):
        global server_instance, server_thread
        
        if not HTTP_AVAILABLE:
            self.report({'ERROR'}, "HTTP server not available")
            return {'CANCELLED'}
        
        props = context.scene.remote_control_advanced_props
        prefs = context.preferences.addons[__name__].preferences
        
        if server_instance:
            self.report({'WARNING'}, "HTTP server already running")
            return {'CANCELLED'}
        
        try:
            server_instance = HTTPServer(('localhost', prefs.http_port), AdvancedBlenderHTTPHandler)
            server_thread = threading.Thread(target=server_instance.serve_forever, daemon=True)
            server_thread.start()
            
            props.http_server_running = True
            self.report({'INFO'}, f"HTTP server started on port {prefs.http_port}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start HTTP server: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class REMOTE_CONTROL_OT_stop_http_server(Operator):
    bl_idname = "remote_control.stop_http_server"
    bl_label = "Stop HTTP Server"
    bl_description = "Stop the HTTP API server"
    
    def execute(self, context):
        global server_instance, server_thread
        
        props = context.scene.remote_control_advanced_props
        
        if server_instance:
            server_instance.shutdown()
            server_instance = None
            server_thread = None
            props.http_server_running = False
            self.report({'INFO'}, "HTTP server stopped")
        else:
            self.report({'WARNING'}, "HTTP server not running")
        
        return {'FINISHED'}

class REMOTE_CONTROL_OT_start_websocket_server(Operator):
    bl_idname = "remote_control.start_websocket_server"
    bl_label = "Start WebSocket Server"
    bl_description = "Start the WebSocket server for real-time communication"
    
    def execute(self, context):
        global websocket_server, websocket_thread
        
        if not WEBSOCKET_AVAILABLE:
            self.report({'ERROR'}, "WebSocket not available. Install websockets library.")
            return {'CANCELLED'}
        
        props = context.scene.remote_control_advanced_props
        prefs = context.preferences.addons[__name__].preferences
        
        if websocket_server:
            self.report({'WARNING'}, "WebSocket server already running")
            return {'CANCELLED'}
        
        try:
            websocket_server = WebSocketServer('localhost', prefs.websocket_port)
            websocket_thread = threading.Thread(target=websocket_server.start_server, daemon=True)
            websocket_thread.start()
            
            props.websocket_server_running = True
            self.report({'INFO'}, f"WebSocket server started on port {prefs.websocket_port}")
            
            # Add scene update handler
            if scene_update_handler not in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.append(scene_update_handler)
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start WebSocket server: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class REMOTE_CONTROL_OT_stop_websocket_server(Operator):
    bl_idname = "remote_control.stop_websocket_server"
    bl_label = "Stop WebSocket Server"
    bl_description = "Stop the WebSocket server"
    
    def execute(self, context):
        global websocket_server, websocket_thread
        
        props = context.scene.remote_control_advanced_props
        
        if websocket_server:
            websocket_server = None
            websocket_thread = None
            props.websocket_server_running = False
            props.websocket_connections = 0
            self.report({'INFO'}, "WebSocket server stopped")
            
            # Remove scene update handler
            if scene_update_handler in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.remove(scene_update_handler)
        else:
            self.report({'WARNING'}, "WebSocket server not running")
        
        return {'FINISHED'}

class REMOTE_CONTROL_OT_start_file_watcher(Operator):
    bl_idname = "remote_control.start_file_watcher"
    bl_label = "Start File Watcher"
    bl_description = "Start watching for command files"
    
    def execute(self, context):
        global file_watcher_thread
        
        props = context.scene.remote_control_advanced_props
        prefs = context.preferences.addons[__name__].preferences
        
        if file_watcher_thread and file_watcher_thread.is_alive():
            self.report({'WARNING'}, "File watcher already running")
            return {'CANCELLED'}
        
        try:
            watcher = FileWatcher(prefs.command_file_path)
            file_watcher_thread = threading.Thread(target=watcher.start_watching, daemon=True)
            file_watcher_thread.start()
            
            props.file_watcher_running = True
            self.report({'INFO'}, f"File watcher started for {prefs.command_file_path}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start file watcher: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class REMOTE_CONTROL_OT_test_ai_features(Operator):
    bl_idname = "remote_control.test_ai_features"
    bl_label = "Test AI Features"
    bl_description = "Test AI-powered features"
    
    def execute(self, context):
        try:
            handler = AdvancedBlenderHTTPHandler()
            
            # Test AI context
            context_result = handler.get_ai_context()
            self.report({'INFO'}, f"AI Context: {context_result['complexity_score']:.1f} complexity")
            
            # Test suggestions
            suggestions = handler.ai_suggest_improvements({'analysis': 'composition'})
            suggestion_count = suggestions.get('suggestion_count', 0)
            self.report({'INFO'}, f"Generated {suggestion_count} AI suggestions")
            
        except Exception as e:
            self.report({'ERROR'}, f"AI test failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class REMOTE_CONTROL_OT_create_sample_template(Operator):
    bl_idname = "remote_control.create_sample_template"
    bl_label = "Create Sample Template"
    bl_description = "Create a sample scene template"
    
    def execute(self, context):
        try:
            # Clear scene
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            
            # Create sample scene
            commands = [
                {'command': 'add_object', 'params': {'type': 'plane', 'location': [0, 0, 0], 'name': 'Ground', 'scale': [5, 5, 1]}},
                {'command': 'add_object', 'params': {'type': 'cube', 'location': [-2, 0, 1], 'name': 'Cube1'}},
                {'command': 'add_object', 'params': {'type': 'sphere', 'location': [2, 0, 1], 'name': 'Sphere1'}},
                {'command': 'add_object', 'params': {'type': 'cylinder', 'location': [0, 2, 1], 'name': 'Cylinder1'}},
                {'command': 'setup_lighting', 'params': {'type': 'three_point', 'target': [0, 0, 1]}},
                {'command': 'add_object', 'params': {'type': 'camera', 'location': [7, -7, 5], 'name': 'MainCamera'}},
            ]
            
            handler = AdvancedBlenderHTTPHandler()
            for cmd in commands:
                handler.execute_command(cmd)
            
            # Add to templates
            prefs = context.preferences.addons[__name__].preferences
            template = prefs.scene_templates.add()
            template.name = "Basic Scene"
            template.description = "A basic scene with objects and lighting"
            template.category = "Sample"
            template.tags = "basic,sample,beginner"
            
            self.report({'INFO'}, "Sample template created successfully")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create template: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

# ============================================================================
# UI PANEL
# ============================================================================

class REMOTE_CONTROL_PT_advanced_panel(Panel):
    bl_label = "Remote Control Advanced"
    bl_idname = "REMOTE_CONTROL_PT_advanced_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Remote Control"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.remote_control_advanced_props
        prefs = context.preferences.addons[__name__].preferences
        
        # Server Controls
        box = layout.box()
        box.label(text="Servers", icon='NETWORK_DRIVE')
        
        # HTTP Server
        row = box.row()
        if props.http_server_running:
            row.label(text="HTTP: Running", icon='CHECKMARK')
            row.operator("remote_control.stop_http_server", text="Stop", icon='CANCEL')
        else:
            row.label(text="HTTP: Stopped", icon='CANCEL')
            row.operator("remote_control.start_http_server", text="Start", icon='PLAY')
        
        # WebSocket Server
        if prefs.enable_websocket:
            row = box.row()
            if props.websocket_server_running:
                row.label(text=f"WebSocket: {props.websocket_connections} clients", icon='CHECKMARK')
                row.operator("remote_control.stop_websocket_server", text="Stop", icon='CANCEL')
            else:
                row.label(text="WebSocket: Stopped", icon='CANCEL')
                row.operator("remote_control.start_websocket_server", text="Start", icon='PLAY')
        
        # File Watcher
        if prefs.enable_file_watcher:
            row = box.row()
            if props.file_watcher_running:
                row.label(text="File Watcher: Running", icon='CHECKMARK')
            else:
                row.label(text="File Watcher: Stopped", icon='CANCEL')
                row.operator("remote_control.start_file_watcher", text="Start", icon='PLAY')
        
        # Statistics
        box = layout.box()
        box.label(text="Statistics", icon='INFO')
        box.label(text=f"Commands: {props.command_count}")
        box.label(text=f"Batches: {props.batch_count}")
        if props.last_command:
            box.label(text=f"Last: {props.last_command}")
        
        # AI Features
        if prefs.enable_ai_features:
            box = layout.box()
            box.label(text="AI Features", icon='EXPERIMENTAL')
            box.operator("remote_control.test_ai_features", icon='PLAY')
            
            if props.ai_context:
                box.label(text=f"Context: {props.ai_context}")
        
        # Templates & Presets
        box = layout.box()
        box.label(text="Templates & Presets", icon='PRESET')
        box.operator("remote_control.create_sample_template", icon='ADD')
        
        # Connection info
        if props.http_server_running:
            box = layout.box()
            box.label(text="Connection Info", icon='URL')
            box.label(text=f"HTTP: localhost:{prefs.http_port}")
            if props.websocket_server_running:
                box.label(text=f"WebSocket: localhost:{prefs.websocket_port}")

# ============================================================================
# REGISTRATION
# ============================================================================

classes = [
    # Property Groups
    SceneTemplate,
    AnimationPreset,
    GeometryNodePreset,
    RemoteControlAdvancedProperties,
    RemoteControlAdvancedPreferences,
    
    # Operators
    REMOTE_CONTROL_OT_start_http_server,
    REMOTE_CONTROL_OT_stop_http_server,
    REMOTE_CONTROL_OT_start_websocket_server,
    REMOTE_CONTROL_OT_stop_websocket_server,
    REMOTE_CONTROL_OT_start_file_watcher,
    REMOTE_CONTROL_OT_test_ai_features,
    REMOTE_CONTROL_OT_create_sample_template,
    
    # UI
    REMOTE_CONTROL_PT_advanced_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.remote_control_advanced_props = bpy.props.PointerProperty(type=RemoteControlAdvancedProperties)

def unregister():
    global server_instance, websocket_server, file_watcher_thread
    
    # Stop all servers
    if server_instance:
        server_instance.shutdown()
        server_instance = None
    
    if websocket_server:
        websocket_server = None
    
    # Remove scene handler
    if scene_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(scene_update_handler)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.remote_control_advanced_props

if __name__ == "__main__":
    register()
                
    