import bpy
import bmesh
from mathutils import Vector, kdtree, Matrix
from bpy_extras import view3d_utils
import numpy as np
from mathutils.geometry import intersect_line_plane

bl_info = {
	"name": "q_p :)",
	"location": "View3D > Add > Object > q_p,",
	"description": "Interactive creation of primitives.",
	"author": "Vladislav Kindushov, 1 more cool uncle, but I did not ask his nickname ",
	"version": (0, 0, 1),
	"blender": (2, 7, 9),
	"category": "Object",
}


def get_pos3d(context, event, point=False, normal=False, revers=False): 
	""" 
	convert mouse pos to 3d point over plane defined by origin and normal 
	""" 
	# get the context arguments
	region = bpy.context.region 
	rv3d = bpy.context.region_data 
	coord = event.mouse_region_x, event.mouse_region_y
	view_vector_mouse = view3d_utils.region_2d_to_vector_3d(region, rv3d,coord)
	ray_origin_mouse = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

	# get coord by plane
	if not point and not normal:
		pointLoc = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse, Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0)), False)
	else:
		if not revers:
			pointLoc = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse, point, normal, False)
		else:
			pointLoc = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse, point, normal, True)

	if not pointLoc is None:
		context.scene.cursor_location = pointLoc

def RayCast(self, context, event, ray_max=1000.0, snap=False):
	"""Run this function on left mouse, execute the ray cast"""
	# get the context arguments
	scene = context.scene
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y

	# get the ray from the viewport and mouse
	view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord).normalized()
	ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

	ray_target = ray_origin + view_vector

	def visible_objects_and_duplis():
		"""Loop over (object, matrix) pairs (mesh only)"""

		for obj in  reversed(context.visible_objects):
			if obj.type == 'MESH':
				yield (obj, obj.matrix_world.copy())

			if obj.dupli_type != 'NONE':
				obj.dupli_list_create(scene)
				for dob in obj.dupli_list:
					obj_dupli = dob.object
					if obj_dupli.type == 'MESH':
						yield (obj_dupli, dob.matrix.copy())

			obj.dupli_list_clear()


	def obj_ray_cast(obj, matrix):
		"""Wrapper for ray casting that moves the ray into object space"""

		# get the ray relative to the object
		matrix_inv = matrix.inverted()
		ray_origin_obj = matrix_inv * ray_origin
		ray_target_obj = matrix_inv * ray_target
		ray_direction_obj = ray_target_obj - ray_origin_obj
		d = ray_direction_obj.length

		ray_direction_obj.normalized()

		success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
		print("Face", face_index)
		if face_index != -1:
			return location, normal, face_index
		else:
			return None, None, None

	# cast rays and find the closest object
	best_length_squared = -1.0
	best_obj = None
	best_matrix = None
	best_face = None
	best_hit = None

	for obj, matrix in visible_objects_and_duplis():
		if obj.type == 'MESH':

			hit, normal, face_index = obj_ray_cast(obj, matrix)
			if hit is not None:
				hit_world = matrix * hit
				scene.cursor_location = hit_world
				length_squared = (hit_world - ray_origin).length
				if best_obj is None or length_squared < best_length_squared:
					best_length_squared = length_squared
					best_obj = obj
					best_matrix = matrix
					best_face = face_index
					best_hit = hit
					break
	if not snap:
		return best_face, best_obj

	def run(best_obj, best_matrix, best_face, best_hit):
		best_distance = float("inf")  # use float("inf") (infinity) to have unlimited search range
		print("Face", face_index)
		mesh = best_obj.data
		#best_matrix = best_obj.matrix_world
		for vert_index in mesh.polygons[best_face].vertices:
			vert_coord = mesh.vertices[vert_index].co
			distance = (vert_coord - best_hit).length
			if distance < best_distance:
				best_distance = distance
				scene.cursor_location = best_matrix * vert_coord

		for v0, v1 in mesh.polygons[best_face].edge_keys:
			p0 = mesh.vertices[v0].co
			p1 = mesh.vertices[v1].co
			p = (p0 + p1) / 2
			distance = (p - best_hit).length
			if distance < best_distance:
				best_distance = distance
				scene.cursor_location = best_matrix * p

		face_pos = Vector(mesh.polygons[best_face].center)
		distance = (face_pos - best_hit).length
		if distance < best_distance:
			best_distance = distance
			scene.cursor_location = best_matrix * face_pos


	if not best_face is None and not best_obj is None:
		run(best_obj, best_matrix, best_face, best_hit)
		return best_face, best_obj
	else:
		return None, None

def Rotation(self, context, face, obj):
	"""Rotation new object by source face"""
	mesh = self.ray_obj.to_mesh(context.scene, apply_modifiers=True, settings='PREVIEW')
	mw = self.ray_obj.matrix_world.copy()
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bm.faces.ensure_lookup_table()
	face = bm.faces[self.ray_faca]
	o = face.calc_center_median()
	def rot(face,o,obj, mw, axis_dst2):
	
		axis_src = face.normal
		axis_src2 = face.calc_tangent_edge()
		axis_dst = Vector((0, 0, 1))
		
		vec2 = axis_src * mw.inverted()
		matrix_rotate = axis_dst.rotation_difference(vec2).to_matrix().to_4x4()
		
		vec1 = axis_src2 * mw.inverted()
		axis_dst2 = axis_dst2 * matrix_rotate.inverted()
		mat_tmp = axis_dst2.rotation_difference(vec1).to_matrix().to_4x4()
		matrix_rotate = mat_tmp*matrix_rotate
		matrix_translation = Matrix.Translation(mw * o)
		
		self.new_obj.matrix_world = matrix_translation * matrix_rotate.to_4x4()

	rot(face,o,self.new_obj, self.ray_obj.matrix_world, Vector((1, 0, 0)))

	if self.ray_obj.matrix_world * self.new_obj.data.polygons[5].normal[1] != self.ray_obj.matrix_world * face.normal[1]:
		rot(face,o,self.new_obj, self.ray_obj.matrix_world, Vector((0, 1, 0)))

	bm.free
	bpy.data.meshes.remove(mesh)

	org = self.new_obj.data.vertices[3].co.copy()
	self.new_obj.data.transform(Matrix.Translation(-org))
	self.new_obj.location += org
	bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
	

def getView(context, event):
	"""Get Viewport Vector""" 
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y
	#view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
	print('popa',rv3d.view_rotation * Vector((0.0, 0.0, -1.0)))
	print('popa')
	return rv3d.view_rotation * Vector((0.0, 0.0, -1.0))

def PerspOrOrtot():
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			for space in area.spaces:
				if space.type == 'VIEW_3D':
					if space.region_3d.is_perspective:
						return False
					else:
						return True

def findView(self, context, event):
	"""Get Viewport State
	Use in def CreateBox()"""

	if PerspOrOrtot():
		view = getView(context, event)
		if view == Vector((0.0, -1.0, 0.0)):
			self.view = True
			return True
		elif view == Vector((0.0, 1.0, 0.0)):
			self.view = True
			return True
		elif view == Vector((1.0, 0.0, 0.0)):
			self.view = True
			return True
		elif view == Vector((-1.0, 0.0, 0.0)):
			self.view = True
			return True
		elif view == Vector((0.0, 0.0, 1.0)):
			self.view = True
			return True
		elif view == Vector((0.0, 0.0, -1.0)):
			self.view = True
			return True
		else:
			self.view = False
			return False
	else:
		self.view = False
		return False

def CreateBox(self, context, event, mode):
	"""create new obj"""
	bpy.ops.mesh.primitive_cube_add()
	new = context.active_object

	if findView(self, context, event):
		new.scale = Vector((0.00001, 0.00001, 1.0))
	else:
		if mode:
			new.scale = Vector((0.00001, 0.00001, 0.00001))
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			# org = new.data.vertices[3].co.copy()
			# new.data.transform(Matrix.Translation(-org))
			# new.location += org
			# bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
			

			normal = new.data.polygons[4].normal.copy()

			for i in new.data.polygons[4].vertices:
				new.data.vertices[i].co += (normal *-1) * 0.0001

		else:
			new.scale = Vector((0.00001, 0.00001, 0.00001))
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

			org = new.data.vertices[2].co.copy()
			new.data.transform(Matrix.Translation(-org))
			new.location += org
			bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)



	return new

def MoveVerts(self, context, event):
	"""Moving the first vertives to create an area"""
	v1 =self.new_obj.matrix_world.inverted() * context.scene.cursor_location

	normal = self.new_obj.data.polygons[3].normal.copy()
	normal2 = self.new_obj.data.polygons[0].normal.copy()

	for i in self.new_obj.data.polygons[0].vertices:
			v2 = self.new_obj.data.vertices[i].co.copy()
			dvec = v1-v2
			dnormal = np.dot(dvec, normal2)
			self.new_obj.data.vertices[i].co += Vector(dnormal*normal2)
			
	for i in self.new_obj.data.polygons[3].vertices:
			v2 = self.new_obj.data.vertices[i].co.copy()
			dvec = v1-v2
			dnormal = np.dot(dvec, normal)
			self.new_obj.data.vertices[i].co += Vector(dnormal*normal)

def faceMove(self, context):
	"""Sets the height of the boxing"""
	v1 = self.new_obj.matrix_world.inverted() * context.scene.cursor_location

	normal = self.new_obj.data.polygons[5].normal.copy()

	for i in self.new_obj.data.polygons[5].vertices:
			v2 = self.new_obj.data.vertices[i].co.copy()
			dvec = v1-v2
			dnormal = np.dot(dvec, normal)
			self.new_obj.data.vertices[i].co += Vector(dnormal*normal)

def SetupBool(self, context):
	"""Setup Object For Boolean"""
	for i in self.ray_obj.modifiers:
		if i.show_viewport:
			self.u_modifier.append(i)
			i.show_viewport = False

	bpy.context.scene.objects.active = self.ray_obj
	bpy.ops.object.modifier_add(type='BOOLEAN')
	self.ray_obj.modifiers[-1].operation = 'DIFFERENCE'
	self.ray_obj.modifiers[-1].object = self.new_obj
	self.ray_obj.modifiers[-1].solver = 'CARVE'

	self.show_wire = self.ray_obj.show_wire
	self.show_all_edges = self.ray_obj.show_all_edges
	self.auto_merge = bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge
	bpy.context.scene.objects.active = self.new_obj
	bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = False
	self.ray_obj.show_wire = True
	self.ray_obj.show_all_edges = True

	self.new_obj.draw_type = 'WIRE'

def ApplyBool(self, context):
	bpy.context.scene.objects.active = self.ray_obj
	bpy.ops.object.modifier_apply(modifier=self.ray_obj.modifiers[-1].name)

	for i in self.ray_obj.modifiers:
		if i in self.u_modifier:
			i.show_viewport = True

	self.ray_obj.show_wire = self.show_wire
	self.ray_obj.show_all_edges = self.show_all_edges
	bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = self.auto_merge

	bpy.context.scene.objects.unlink(self.new_obj)
	bpy.data.objects.remove(self.new_obj)

	if self.edit_mode_obj:
		bpy.context.scene.objects.active = self.edit_mode_obj
		bpy.ops.object.mode_set(mode='EDIT')


def FlipNormal():
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.normals_make_consistent(inside=False)
	bpy.ops.object.mode_set(mode='OBJECT')



class QBox(bpy.types.Operator):
	bl_idname = "objects.stream_box"
	bl_label = "Stream Box"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}

			# Main Variable
######################################
	leftMS = 0 # Left Mouse State
	rightMS = 0 # Right Mouse State
	new_obj = None # New object
	ray_faca = None # Face for rotation
	ray_obj = None # sours object
	mode = False # Create object for new geometry of boolean "if True then boolean"
	view = None # vector viev
	
######################################
			#user setings
	show_wire = None
	show_all_edges = None
	u_modifier = [] # Save state, need for boolean mode
	auto_merge = None
	edit_mode_obj = None
######################################

	@classmethod
	def poll(cls, context):
		return (context.mode == "EDIT_MESH") or (context.mode == "OBJECT")

	def modal(self, context, event):
		context.area.header_text_set("Left Mouse Bootom: Create New Premetive, Right Mouse Bootom: Boolean, Press CTRL For Snap")
		if event.type == 'LEFTMOUSE':
			if self.leftMS == 0 and not self.ray_faca is None:
				self.new_obj = CreateBox(self, context, event, self.mode)
				Rotation(self, context, self.ray_faca, self.ray_obj)

			elif self.leftMS == 0 and self.ray_faca is None:
				self.new_obj = CreateBox(self, context, event, self.mode)

			elif self.leftMS == 2:
				FlipNormal()
				if self.mode:
					ApplyBool(self, context)
				elif self.edit_mode_obj:
						bpy.context.scene.objects.active = self.edit_mode_obj
						self.edit_mode_obj.select = True
						bpy.ops.object.join()
						bpy.ops.object.mode_set(mode='EDIT')
				context.area.header_text_set()
				return {'FINISHED'}

			self.leftMS  += 1
			self.rightMS += 1
			if self.leftMS == 2:
				bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
				FlipNormal()
				if self.view:
					if self.mode:
						ApplyBool(self, context)
					elif self.edit_mode_obj:
						bpy.context.scene.objects.active = self.edit_mode_obj
						self.edit_mode_obj.select = True
						bpy.ops.object.join()
						bpy.ops.object.mode_set(mode='EDIT')
					context.area.header_text_set()
					return {'FINISHED'}



		if event.type == 'RIGHTMOUSE' and not self.ray_faca is None:
			print('zah')
			self.mode = True
			if self.rightMS == 0 and not self.ray_faca is None:
				self.new_obj = CreateBox(self, context, event, self.mode)
				Rotation(self, context, self.ray_faca, self.ray_obj)
				SetupBool(self, context)

			elif self.rightMS == 0 and self.ray_faca is None:
				self.new_obj = CreateBox(self, context, event, self.mode)

			elif self.rightMS == 2:
				FlipNormal()
				ApplyBool(self, context)
				context.area.header_text_set()
				return {'FINISHED'}

			self.leftMS  += 1
			self.rightMS += 1
			if self.rightMS == 2:
				FlipNormal()
				if self.view:
					ApplyBool(self, context)
					context.area.header_text_set()
					return {'FINISHED'}


		if event.type == 'MOUSEMOVE':
			if self.rightMS > 0:
				FlipNormal()
			if self.leftMS == 0 and self.rightMS == 0:
				if event.ctrl:
					self.ray_faca, self.ray_obj = RayCast(self, context, event, ray_max=1000.0, snap=True)
				else:
					self.ray_faca, self.ray_obj = RayCast(self, context, event, ray_max=1000.0,snap=False)
				print(self.ray_faca)
				print(self.ray_obj)
				if isinstance(self.ray_faca,type(None)):
					get_pos3d(context, event)
					self.ray_obj = None
					self.ray_faca = None

			elif self.leftMS == 1 or self.rightMS == 1:
				if event.ctrl:
				   RayCast(self, context, event, ray_max=1000.0, snap=True)
				   MoveVerts(self, context, event)
				   return {'RUNNING_MODAL'}

				if not isinstance(self.ray_faca,type(None)):
					global_loc = self.ray_obj.matrix_world * self.ray_obj.data.polygons[self.ray_faca].center
					global_norm = self.ray_obj.matrix_world * (self.ray_obj.data.polygons[self.ray_faca].center + self.ray_obj.data.polygons[self.ray_faca].normal) - global_loc
					point = self.ray_obj.data.vertices[self.ray_obj.data.polygons[self.ray_faca].vertices[0]].co.copy()
					get_pos3d(context, event, global_loc, global_norm)
				else:
					get_pos3d(context, event)

				MoveVerts(self, context, event)

			elif self.leftMS == 2 or self.rightMS == 2:
				if event.ctrl:
					RayCast(self, context, event, ray_max=1000.0, snap=True)
					faceMove(self, context,)
					return {'RUNNING_MODAL'}
				get_pos3d(context, event, self.new_obj.location , getView(context, event), True)
				faceMove(self, context,)


		return {'RUNNING_MODAL'}



	def invoke(self, context, event):
		if context.space_data.type == 'VIEW_3D':
			if context.mode == "EDIT_MESH":
				self.edit_mode_obj = context.active_object
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')
			
			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "is't 3dview")
			return {'CANCELLED'}


def register():
	bpy.utils.register_class(QBox)


def unregister():
	bpy.utils.unregister_class(QBox)


if __name__ == "__main__":
	register()

