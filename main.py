import bpy
from .utilities import *

class SObj(bpy.types.Operator):
	bl_idname = "objects.stream_obj"
	bl_label = "Stream Obj"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	def __init__(self):
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
		########################
		self.stepCount = None
		self.create = None
		self.moveStep1 = None
		self.moveStep2 = None
		
		self.useBool = None
		self.help = None
		self.useOffset = None
		self.useBool = None
		
		self.fill = None
		self.segment = None
		
		######################################
		# user setings
		self.show_wire = None
		self.show_all_edges = None
		self.u_modifier = []  # Save state, need for boolean mode
		self.auto_merge = None
		self.edit_mode_obj = None
	
	######################################


	@classmethod
	def poll(cls, context):
		return (context.mode == "EDIT_MESH") or (context.mode == "OBJECT")
	
	def modal(self, context, event):
		context.area.header_text_set(self.help(self, context, event))

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
					self.faceComstrain = True
				else:
					self.faceComstrain = False
					
		if event.type == 'WHEELUPMOUSE' and not self.segment is None :
				self.segment += 1
				Scale(self, context)


		if event.type == 'WHEELDOWNMOUSE' and not self.segment is None :
			if not self.segment >= 3:
				self.segment -= 1
				Scale(self, context)
				
				
		if event.type == 'LEFTMOUSE' and ((self.mode == False or self.mouseState == 0) or (self.mode == True and self.mouseState == 2)):
			if self.mouseState == 2 and self.mode:
				RightMouseClick(self, context, event)
			LeftMouseClick(self, context, event)
			
			
		if self.useBool and event.type == 'RIGHTMOUSE':
			if self.mode == True or self.mouseState == 0:
				RightMouseClick(self, context, event)
		elif event.type == 'RIGHTMOUSE' and not self.useBool and self.fill is None:
			LeftMouseClick(self, context, event)
			
		if event.type == 'RIGHTMOUSE' and event.value == 'RELEASE' and not self.fill is None:
			if self.fill:
				self.fill = False
			else:
				self.fill = True
				self.moveStep1(self, context)

		if self.mouseState >= self.stepCount:
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

		if event.type == 'MOUSEMOVE':
			bpy.context.area.tag_redraw()
			if self.mouseState == 0:
				FirstState(self, context, event)
			if self.mouseState == 1:
				SecondState(self, context, event)
			if self.mouseState == 2 :
				ThirdState(self, context, event)
			
		
				
		return {'RUNNING_MODAL'}



	def invoke(self, context, event):
		if context.space_data.type == 'VIEW_3D':
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

