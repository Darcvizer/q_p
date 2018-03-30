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


def CreateBox(self, context, event):
	"""create new obj"""
	if self.viewState:
		bpy.ops.mesh.primitive_cube_add(view_align=True)
		new = context.active_object
		new.scale = Vector((0.00001, 0.00001, 0.00001))
	else:
		bpy.ops.mesh.primitive_cube_add(view_align=False)
		new = context.active_object
		new.scale = Vector((0.00001, 0.00001, 0.00001))
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		new.location = self.mouseLocation
		org = new.data.vertices[6].co.copy()
		new.data.transform(Matrix.Translation(-org))
		new.location += org
	return new

def MoveVerts(self, compress=False):
	"""Moving the first vertives to create an area"""
	v1 = self.new_obj.matrix_world.inverted() * self.mouseLocation

	normal = self.new_obj.data.polygons[3].normal.copy()
	normal2 = self.new_obj.data.polygons[0].normal.copy()

	for i in self.new_obj.data.polygons[0].vertices:
			v2 = self.new_obj.data.vertices[i].co.copy()
			dvec = v1-v2
			dnormal = np.dot(dvec, normal2)
			self.new_obj.data.vertices[i].co += Vector(dnormal*normal2)

	if compress:
			self.new_obj.data.vertices[1].co = self.new_obj.data.vertices[3].co.copy()
			self.new_obj.data.vertices[0].co = self.new_obj.data.vertices[2].co.copy()
			self.new_obj.data.vertices[5].co = self.new_obj.data.vertices[7].co.copy()
			self.new_obj.data.vertices[4].co = self.new_obj.data.vertices[6].co.copy()

			dist = (self.new_obj.data.vertices[2].co - self.new_obj.data.vertices[6].co).length

			for i in self.new_obj.data.polygons[3].vertices:
				self.new_obj.data.vertices[i].co += normal * dist


	else:
		for i in self.new_obj.data.polygons[3].vertices:
			v2 = self.new_obj.data.vertices[i].co.copy()
			dvec = v1-v2
			dnormal = np.dot(dvec, normal)
			self.new_obj.data.vertices[i].co += Vector(dnormal*normal)

def faceMove(self, compress=False):
	"""Sets the height of the boxing"""
	v1 = self.new_obj.matrix_world.inverted() * self.mouseLocation

	normal = self.new_obj.data.polygons[5].normal.copy()

	if compress:
		# Move on base position
		self.new_obj.data.vertices[1].co = self.new_obj.data.vertices[0].co.copy()
		self.new_obj.data.vertices[5].co = self.new_obj.data.vertices[4].co.copy()
		self.new_obj.data.vertices[3].co = self.new_obj.data.vertices[2].co.copy()
		self.new_obj.data.vertices[7].co = self.new_obj.data.vertices[6].co.copy()

		#Arithmetical mean
		v1 = (self.new_obj.data.vertices[3].co.copy() - self.new_obj.data.vertices[1].co.copy()).length
		v2 = (self.new_obj.data.vertices[1].co.copy() - self.new_obj.data.vertices[5].co.copy()).length
		v3 = (self.new_obj.data.vertices[7].co.copy() - self.new_obj.data.vertices[5].co.copy()).length
		v4 = (self.new_obj.data.vertices[7].co.copy() - self.new_obj.data.vertices[3].co.copy()).length

		dist = (v1 + v2 + v3 + v4) /4

		#Move face
		for i in self.new_obj.data.polygons[5].vertices:
			self.new_obj.data.vertices[i].co += normal * dist
	else:
		for i in self.new_obj.data.polygons[5].vertices:
			v2 = self.new_obj.data.vertices[i].co.copy()
			dvec = v1-v2
			dnormal = np.dot(dvec, normal)
			self.new_obj.data.vertices[i].co += Vector(dnormal*normal)



def FirstState(self, context, event):
	if not self.faceComstrain:
		if event.ctrl:
			self.ray_faca, self.ray_obj, self.mouseLocation, self.dir_longest_edge = RayCast(self, context, event, ray_max=1000.0, snap=True)
		else:
			self.ray_faca, self.ray_obj, self.mouseLocation, self.dir_longest_edge = RayCast(self, context, event, ray_max=1000.0, snap=False)
		if self.ray_faca is None :
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
		else: MoveVerts(self)
	else:
		self.mouseLocation = get_pos3d(self, context, event, self.global_loc, self.global_norm)
		
			
		if event.shift and not event.type == 'MIDDLEMOUSE':
			MoveVerts(self, compress=True)
		else: MoveVerts(self)

def ThirdState(self, context, event):
	if event.ctrl:
		self.mouseLocation = RayCast(self, context, event, ray_max=1000.0, snap=True)[2]
		if event.shift and not event.type == 'MIDDLEMOUSE':
			faceMove(self, True)
		else:
			faceMove(self)
	else:
		self.mouseLocation = get_pos3d(self, context, event, self.global_loc, self.global_norm)
		
		if event.shift and not event.type == 'MIDDLEMOUSE':
			faceMove(self, True)
		else:
			faceMove(self)
	hit = FindNormal(self.new_obj, 4, 5)
	if not hit is None:
		FlipNormal()
		
			
def LeftMouseClick(self, context, event):
	if self.mouseState == 0:
		if not self.ray_faca is None:
			self.global_norm = self.ray_obj.matrix_world.to_3x3() * self.mesh.polygons[self.ray_faca].normal.copy()
			self.global_loc = self.ray_obj.matrix_world * self.mesh.polygons[self.ray_faca].center.copy()
			
			
			self.new_obj = CreateBox(self, context, event)
			self.new_obj.matrix_world = self.matrix
			self.new_obj.location = self.mouseLocation
			
		else:
			self.new_obj = CreateBox(self, context, event)
			self.global_norm = Vector((0.0, 0.0, 1.0))
			self.global_loc = Vector((0.0, 0.0, 0.0))
	elif self.mouseState == 1:
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
		self.global_norm = getView(context, event)
		self.global_loc = self.new_obj.location
	self.mouseState += 1
	
def RightMouseClick(self, context, event):
	if ((not self.ray_faca is None) or self.faceComstrain) or (self.global_norm and  self.global_loc ):
		if self.mouseState == 0:
			self.mode = True
			
			self.global_norm = self.ray_obj.matrix_world.to_3x3() * self.mesh.polygons[self.ray_faca].normal.copy()
			self.global_loc = self.ray_obj.matrix_world * self.mesh.polygons[self.ray_faca].center.copy()
			
			
			self.new_obj = CreateBox(self, context, event)
			self.new_obj.matrix_world = self.matrix
			self.new_obj.location = self.mouseLocation
			
			n = self.new_obj.matrix_world.to_3x3().inverted() * self.mesh.polygons[self.ray_faca].normal.copy()
			for i in self.new_obj.data.polygons[4].vertices:
				self.new_obj.data.vertices[i].co = n * 0.001 + self.new_obj.data.vertices[i].co.copy()
				
		elif self.mouseState == 1:
			bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
			self.global_norm = getView(context, event)
			self.global_loc = self.new_obj.location
			SetupBool(self, context)
		self.mouseState += 1

def Cansel(self, context):
	if not self.mesh is None :
		if  len(self.ray_obj.modifiers) == 1 and self.mode == True :
			pass
		elif len(self.ray_obj.modifiers) != 0 and self.mode == False:
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
	if not self.mesh is None :
		if  len(self.ray_obj.modifiers) == 1 and self.mode == True :
			pass
		elif len(self.ray_obj.modifiers) != 0 and self.mode == False:
			bpy.data.meshes.remove(self.mesh)
	if self.mode:
		ApplyBool(self, context)

	else:
		pass

		
	
	

class SBox(bpy.types.Operator):
	bl_idname = "objects.stream_box"
	bl_label = "Stream Box"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}


	@classmethod
	def poll(cls, context):
		return (context.mode == "EDIT_MESH") or (context.mode == "OBJECT")
	
	def modal(self, context, event):
		if event.ctrl:
			context.area.header_text_set("LMB: Create New Premetive, RMB: Boolean, SpaceBar:Fix Face, CTRL(True): Snaping, SHIFT: Proportional Shift")
		else:
			context.area.header_text_set("LMB: Create New Premetive, RMB: Boolean, SpaceBar:Fix Face, CTRL(False): Snaping, SHIFT: Proportional Shift")

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
		
		
		if (event.type == 'SPACE' and event.value == "RELEASE") and self.mouseState == 0:
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
				
		
		if event.type == 'LEFTMOUSE' and ((self.mode == False or self.mouseState == 0) or (self.mode == True and self.mouseState == 2)):
			if self.mouseState == 2 and self.mode:
				RightMouseClick(self, context, event)
			LeftMouseClick(self, context, event)
		if event.type == 'RIGHTMOUSE' and (self.mode == True or self.mouseState == 0):
			RightMouseClick(self, context, event)
		


		if event.type == 'MOUSEMOVE':
			bpy.context.area.tag_redraw()
			if self.mouseState == 0:
				FirstState(self, context, event)
			elif self.mouseState == 1:
				SecondState(self, context, event)
			elif self.mouseState == 2:
				ThirdState(self, context, event)
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
			self.mouseState = 0 # Mouse State
			#self.rightMS = 0 # Right Mouse State
			self.midMS = False # Middle mouse State
			self.faceComstrain = False
			self.new_obj = None # created object
			self.ray_faca = None # Ray cast face
			self.ray_obj = None # Ray cast object
			self.mode = False # Create object for new geometry of boolean "if True then boolean"
			self.view = None # vector viev
			self.global_loc = None # use if faceComstrain = True for intersect_line_plane
			self.global_norm = None # use if faceComstrain = True for intersect_line_plane
			#self.GLFACE = None
			self.panel_points = []
			self.mesh = [None, None] # 0 - mesh , 1 name obj;
			#self.hit = None
			#self.normal= None
			self.addonPref = None # Addon Preferences
			self.dir_longest_edge = None # direction the longest edge
			self.mouseLocation = None
			self.matrix = None
			self.mesh = None
			#self.stepCount = 3
			#self.create =
			#self.firstMove =
			
		######################################
					#user setings
			self.show_wire = None
			self.show_all_edges = None
			self.u_modifier = [] # Save state, need for boolean mode
			self.auto_merge = None
			self.edit_mode_obj = None
		######################################

			if context.mode == "EDIT_MESH":
				self.edit_mode_obj = context.active_object
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')
				
			self.addonPref = bpy.context.user_preferences.addons.get("q_p").preferences.Mode
			if self.addonPref == 'blender':
				self.passR ='MIDDLEMOUSE'
			else:
				self.addonPref = 'LEFT_ALT'
			self.viewState = findView(context, event)
			args = (self, context)
			self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL' )
			self._handle_1 = bpy.types.SpaceView3D.draw_handler_add(draw_callback_pv, args, 'WINDOW', 'POST_VIEW')
			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "is't 3dview")
			return {'CANCELLED'}

