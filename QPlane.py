import bpy
import bmesh
import bgl
from bgl import glVertex3f
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils
import numpy as np
from mathutils.geometry import intersect_line_plane
from mathutils.geometry import tessellate_polygon as tessellate
from .utilities import *

def CreatePlane(self, context):
	"""create new obj"""
	if self.view:
		bpy.ops.mesh.primitive_plane_add(view_align=True)
	else:
		bpy.ops.mesh.primitive_plane_add()
	new = context.active_object
	new.scale = Vector((0.00001, 0.00001, 0.0001))
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	org = new.data.vertices[3].co.copy()
	new.data.transform(Matrix.Translation(-org))
	new.location += org
	bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
	return new

def MoveVerts(self, compress=False):
	"""Moving the first vertives to create an area"""
	v1 =self.new_obj.matrix_world.inverted() * self.mouseLocation

	self.new_obj.data.vertices[0].co = v1
	
	if compress:
		dvec = v1-self.new_obj.data.vertices[1].co.copy()
		dnormal = np.dot(dvec, self.direct1)
		self.new_obj.data.vertices[1].co += Vector(dnormal*self.direct1)

		self.new_obj.data.vertices[2].co = self.new_obj.data.vertices[3].co.copy()

		dist = (self.new_obj.data.vertices[1].co.copy() - self.new_obj.data.vertices[3].co.copy()).length
		self.new_obj.data.vertices[2].co += self.direct2 * dist

		dvec = self.new_obj.data.vertices[1].co.copy()-self.new_obj.data.vertices[0].co.copy()
		dnormal = np.dot(dvec, self.direct1)
		self.new_obj.data.vertices[0].co += Vector(dnormal*self.direct1)

		dvec = self.new_obj.data.vertices[2].co.copy()-self.new_obj.data.vertices[0].co.copy()
		dnormal = np.dot(dvec, self.direct2)
		self.new_obj.data.vertices[0].co += Vector(dnormal*self.direct2)


	else:
		dvec = v1-self.new_obj.data.vertices[1].co.copy()
		dnormal = np.dot(dvec, self.direct1)
		self.new_obj.data.vertices[1].co += Vector(dnormal*self.direct1)

		dvec = v1-self.new_obj.data.vertices[2].co.copy()
		dnormal = np.dot(dvec, self.direct2)
		self.new_obj.data.vertices[2].co += Vector(dnormal*self.direct2)


def FirstState(self, context, event):
	if not self.faceComstrain:
		if event.ctrl:
			self.ray_faca, self.ray_obj, self.mouseLocation, self.dir_longest_edge = RayCast(self, context, event,
			                                                                                 ray_max=1000.0, snap=True)
		else:
			self.ray_faca, self.ray_obj, self.mouseLocation, self.dir_longest_edge = RayCast(self, context, event,
			                                                                                 ray_max=1000.0, snap=False)
		if self.ray_faca is None and self.ray_obj is None:
			self.panel_points = []
			self.mouseLocation = get_pos3d(self, context, event)
		else:
			self.global_norm = self.ray_obj.matrix_world.to_3x3() * self.mesh.polygons[self.ray_faca].normal.copy()
			self.global_loc = self.ray_obj.matrix_world * self.mesh.polygons[self.ray_faca].center.copy()
			self.matrix = Rotation(self.ray_faca, self.ray_obj, self.dir_longest_edge, self.mesh)
	
	elif self.faceComstrain:
		self.mouseLocation = get_pos3d(self, context, event, self.global_loc, self.global_norm)
		if not self.mouseLocation:
			self.faceComstrain = False
			FirstState(self, context, event)


def SecondState(self, context, event):
	if event.ctrl:
		self.mouseLocation = RayCast(self, context, event, ray_max=1000.0, snap=True)[2]
		if event.shift and not event.type == 'MIDDLEMOUSE':
			MoveVerts(self, compress=True)
		else:
			MoveVerts(self)
	else:
		self.mouseLocation = get_pos3d(self, context, event, self.global_loc, self.global_norm)
		
		if event.shift and not event.type == 'MIDDLEMOUSE':
			MoveVerts(self, compress=True)
		else:
			MoveVerts(self)


def LeftMouseClick(self, context, event):
	if self.mouseState == 0:
		if not self.ray_faca is None:
			self.global_norm = self.ray_obj.matrix_world.to_3x3() * self.mesh.polygons[self.ray_faca].normal.copy()
			self.global_loc = self.ray_obj.matrix_world * self.mesh.polygons[self.ray_faca].center.copy()
			
			self.new_obj = CreatePlane(self, context)
			self.new_obj.matrix_world = self.matrix
			self.new_obj.location = self.mouseLocation
		
		else:
			self.new_obj = CreatePlane(self, context)
			self.global_norm = Vector((0.0, 0.0, 1.0))
			self.global_loc = Vector((0.0, 0.0, 0.0))
		self.direct1 = (self.new_obj.data.vertices[3].co.copy() - self.new_obj.data.vertices[1].co.copy()).normalized()
		self.direct2 = (self.new_obj.data.vertices[3].co.copy() - self.new_obj.data.vertices[2].co.copy()).normalized()
	
	elif self.mouseState == 1:
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
		self.global_norm = getView(context, event)
		self.global_loc = self.new_obj.location
	self.mouseState += 1


def Cansel(self, context):
	if not self.mesh is None:
		bpy.data.meshes.remove(self.mesh)
	
	if self.mouseState == 0:
		
		pass
	
	elif self.mouseState > 0 and not self.mode:
		bpy.data.meshes.remove(self.new_obj.data)
		bpy.data.objects.remove(self.new_obj)
	
	
	
	elif self.mouseState > 0 and self.mode:
		bpy.data.meshes.remove(self.new_obj.data)
		bpy.data.objects.remove(self.new_obj)
		self.ray_obj.modifiers.remove(self.ray_obj.modifiers[-1])


def Finish(self, context):
	if not self.mesh is None:
		bpy.data.meshes.remove(self.mesh)
	if self.mode:
		ApplyBool(self, context)
	
	else:
		pass


class SPlane(bpy.types.Operator):
	bl_idname = "objects.stream_plane"
	bl_label = "Stream Plane"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	
	@classmethod
	def poll(cls, context):
		return (context.mode == "EDIT_MESH") or (context.mode == "OBJECT")
	
	def modal(self, context, event):
		if event.ctrl:
			context.area.header_text_set(
				"LMB: Create New Premetive, SpaceBar:Fix Face, CTRL(True): Snaping, SHIFT: Proportional Shift")
		else:
			context.area.header_text_set(
				"LMB: Create New Premetive, SpaceBar:Fix Face, CTRL(False): Snaping, SHIFT: Proportional Shift")
			
		if self.addonPref == 'blender':
			if event.type == 'MIDDLEMOUSE':
				return {'PASS_THROUGH'}
		else:
			if event.alt:
				return {'PASS_THROUGH'}
		
		if event.type == 'ESC':
			Cansel(self, context)
			if self.edit_mode_obj:
				bpy.context.scene.objects.active = self.edit_mode_obj
				self.edit_mode_obj.select = True
				bpy.ops.object.mode_set(mode='EDIT')
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			bpy.types.SpaceView3D.draw_handler_remove(self._handle_1, 'WINDOW')
			context.area.header_text_set()
			bpy.context.area.tag_redraw()
			return {'CANCELLED'}
		
		if event.type == 'SPACE' and self.mouseState == 0:
			if not self.ray_faca is None:
				if not self.faceComstrain:
					self.ray_faca, self.ray_obj, self.mouseLocation, self.dir_longest_edge = RayCast(self, context, event, ray_max=1000.0)
					self.global_loc = self.ray_obj.matrix_world * self.mesh.polygons[self.ray_faca].center.copy()
					self.global_norm = self.ray_obj.matrix_world.to_3x3() * self.mesh.polygons[self.ray_faca].normal.copy()
					self.faceComstrain = True
				else:
					self.faceComstrain = False
			else:
				if not self.faceComstrain:
					self.global_norm = Vector((0.0, 0.0, 1.0))
					self.global_loc = Vector((0.0, 0.0, 0.0))
				else:
					self.faceComstrain = False
		
		if event.type == 'LEFTMOUSE':
			LeftMouseClick(self, context, event)
		if event.type == 'RIGHTMOUSE':
			LeftMouseClick(self, context, event)
		
		if event.type == 'MOUSEMOVE':
			bpy.context.area.tag_redraw()
			if self.mouseState == 0:
				FirstState(self, context, event)
			elif self.mouseState == 1:
				SecondState(self, context, event)
			else:
				Finish(self, context)
				if self.edit_mode_obj:
					bpy.context.scene.objects.active = self.edit_mode_obj
					self.edit_mode_obj.select = True
					if not self.mode:
						bpy.ops.object.join()
					bpy.ops.object.mode_set(mode='EDIT')
				bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
				bpy.types.SpaceView3D.draw_handler_remove(self._handle_1, 'WINDOW')
				context.area.header_text_set()
				bpy.context.area.tag_redraw()
				return {'FINISHED'}
		
		return {'RUNNING_MODAL'}
	
	def invoke(self, context, event):
		if context.space_data.type == 'VIEW_3D':
			# Main Variable
			######################################
			self.viewState = None
			self.mouseState = 0  # Mouse State
			# self.rightMS = 0 # Right Mouse State
			self.midMS = False  # Middle mouse State
			self.faceComstrain = False
			self.new_obj = None  # created object
			self.ray_faca = None  # Ray cast face
			self.ray_obj = None  # Ray cast object
			self.mode = False  # Create object for new geometry of boolean "if True then boolean"
			self.view = None  # vector viev
			self.global_loc = None  # use if faceComstrain = True for intersect_line_plane
			self.global_norm = None  # use if faceComstrain = True for intersect_line_plane
			# self.GLFACE = None
			self.panel_points = []
			self.mesh = [None, None]  # 0 - mesh , 1 name obj;
			# self.hit = None
			# self.normal= None
			self.addonPref = None  # Addon Preferences
			self.dir_longest_edge = None  # direction the longest edge
			self.mouseLocation = None
			self.matrix = None
			self.mesh = None
			self.direct1 = None
			self.direct2 = None
			
			######################################
			# user setings
			self.show_wire = None
			self.show_all_edges = None
			self.u_modifier = []  # Save state, need for boolean mode
			self.auto_merge = None
			self.edit_mode_obj = None
			######################################
			
			if context.mode == "EDIT_MESH":
				self.edit_mode_obj = context.active_object
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')
			
			self.addonPref = bpy.context.user_preferences.addons.get("q_p").preferences.Mode
			if self.addonPref == 'blender':
				self.passR = 'MIDDLEMOUSE'
			else:
				self.addonPref = 'LEFT_ALT'
			self.viewState = findView(context, event)
			args = (self, context)
			self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
			self._handle_1 = bpy.types.SpaceView3D.draw_handler_add(draw_callback_pv, args, 'WINDOW', 'POST_VIEW')
			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "is't 3dview")
			return {'CANCELLED'}

