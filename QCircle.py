import bpy
import bmesh
from mathutils import Vector, kdtree, Matrix
from bpy_extras import view3d_utils
import numpy as np
from mathutils.geometry import intersect_line_plane
from math import sqrt

def Rotation(self, context, face, obj):
	bpy.context.scene.objects.active = obj
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='DESELECT')
	bm = bmesh.from_edit_mesh(obj.data)
	bm.faces.ensure_lookup_table()
	bm.faces[face].select = True
	bpy.ops.transform.create_orientation(name = 'sosok', use = False, overwrite = True)
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.context.scene.objects.active = self.new_obj
	self.new_obj.matrix_world  = context.scene.orientations['sosok'].matrix.to_4x4().copy()
	bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

def get_pos3d(context, event, point=False, normal=False): 
	""" 
	convert mouse pos to 3d point over plane defined by origin and normal 
	""" 
	region = bpy.context.region 
	rv3d = bpy.context.region_data 
	coord = event.mouse_region_x, event.mouse_region_y
	#rM = context.active_object.matrix_world.to_3x3() 
	view_vector_mouse = view3d_utils.region_2d_to_vector_3d(region, rv3d,coord)
	ray_origin_mouse = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
	if not point and not normal:
		pt = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse, Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0)), False)
	else:
		pt = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse, point, normal, False)
	if not pt is None:
		bpy.context.scene.cursor_location = pt

def SetCursor(context, event):
	scene = context.scene
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y
	view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
	scene.cursor_location = view3d_utils.region_2d_to_location_3d(region, rv3d, coord, view_vector)

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

		for obj in context.visible_objects:
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

		ray_direction_obj.normalize()

		success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

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
				length_squared = (hit_world - ray_origin).length_squared
				if best_obj is None or length_squared < best_length_squared:
					best_length_squared = length_squared
					best_obj = obj
					best_matrix = matrix
					best_face = face_index
					best_hit = hit
					break

	def run(best_obj, best_matrix, best_face, best_hit):
		best_distance = float("inf")  # use float("inf") (infinity) to have unlimited search range

		mesh = best_obj.data
		best_matrix = best_obj.matrix_world
		for vert_index in mesh.polygons[best_face].vertices:
			vert_coord = mesh.vertices[vert_index].co
			distance = (vert_coord - best_hit).magnitude
			if distance < best_distance:
				best_distance = distance
				scene.cursor_location = best_matrix * vert_coord

		for v0, v1 in mesh.polygons[best_face].edge_keys:
			p0 = mesh.vertices[v0].co
			p1 = mesh.vertices[v1].co
			p = (p0 + p1) / 2
			distance = (p - best_hit).magnitude
			if distance < best_distance:
				best_distance = distance
				scene.cursor_location = best_matrix * p

		face_pos = Vector(mesh.polygons[best_face].center)
		distance = (face_pos - best_hit).magnitude
		if distance < best_distance:
			best_distance = distance
			scene.cursor_location = best_matrix * face_pos

	if snap:
		run(best_obj, best_matrix, best_face, best_hit)

	return best_face, best_obj

def CreateCilinder(context):
	sv = context.scene.cursor_location
	ab = context.active_object
	bpy.ops.mesh.primitive_circle_add(vertices=32, fill_type='NGON')
	new = context.active_object
	new.scale = Vector((0.00001, 0.00001, 0.00001))
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	return new, context.scene.cursor_location.copy()

def Scale(self, context):
	mainPoint = self.new_obj.data.polygons[0].center.copy()
	loc = self.new_obj.matrix_world.inverted() * context.scene.cursor_location

	locx = loc[0] - mainPoint[0]
	locy = loc[1] - mainPoint[1]
	locz = loc[2] - mainPoint[2]
	# получаем радиус, между мышкой и центром
	distance = sqrt((locx)**2 + (locy)**2 + (locz)**2)
 
	bpy.data.objects.remove(self.new_obj)
	SC = context.scene.cursor_location.copy()
	context.scene.cursor_location = self.savePos.copy()
	bpy.ops.mesh.primitive_circle_add(vertices=self.segment,radius=distance, fill_type='NGON')
	self.new_obj = context.active_object
	if self.face is not None:
		Rotation(self, context, self.face, self.obj)
	context.scene.cursor_location = SC
	print(distance)
	
	#bpy.ops.transform.resize(value= loc * distance)
	#bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def Sub(self, context, mode):
	if mode:
		self.segment += 1
	else:
		self.segment -= 1
		if self.segment == 2:
			self.segment += 1

	mainPoint = self.new_obj.data.polygons[0].center.copy()
	loc = self.new_obj.matrix_world.inverted() * context.scene.cursor_location

	locx = loc[0] - mainPoint[0]
	locy = loc[1] - mainPoint[1]
	locz = loc[2] - mainPoint[2]
	# получаем радиус, между мышкой и центром
	distance = sqrt((locx)**2 + (locy)**2 + (locz)**2)

	bpy.data.objects.remove(self.new_obj)
	SC = context.scene.cursor_location.copy()
	context.scene.cursor_location = self.savePos.copy()
	bpy.ops.mesh.primitive_circle_add(vertices=self.segment,radius=distance, fill_type='NGON')
	self.new_obj = context.active_object
	if self.face is not None:
		Rotation(self, context, self.face, self.obj)

	context.scene.cursor_location = SC
	print(distance)
	self.new_obj = context.active_object
	#bpy.ops.transform.resize(value= loc * distance)
	#bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def StarPosMouse(self, context, event):
	scene = context.scene
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y
	view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
	loc = view3d_utils.region_2d_to_location_3d(region, rv3d, coord, view_vector)

	#normal = self.new_obj.matrix_local * self.new_obj.data.polygons[5].normal
	#loc = ((normal * -1) * (self.new_obj.matrix_local * loc))
	return loc

def SetSolidify(self, context):
	self.new_obj.modifiers.new('Solidify', 'SOLIDIFY')
	self.new_obj.modifiers[0].use_even_offset = True
	self.new_obj.modifiers[0].use_quality_normals = True
	self.new_obj.modifiers[0].thickness = 0.1

def StarPosMouse(self, context, event):
		scene = context.scene
		region = context.region
		rv3d = context.region_data
		coord = event.mouse_region_x, event.mouse_region_y
		view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
		loc = view3d_utils.region_2d_to_location_3d(region, rv3d, coord, view_vector)

		global_loc = self.new_obj.matrix_world * self.new_obj.data.polygons[0].center.copy()
		normal = self.new_obj.matrix_world * (self.new_obj.data.polygons[0].center.copy() + self.new_obj.data.polygons[0].normal.copy()) - global_loc
					
		#normal = self.new_obj.matrix_world * self.new_obj.data.polygons[0].normal
		loc = ((normal *-1) * (self.new_obj.matrix_world * loc))
		return loc

def Zoom(self, context):
	ar = None
	for i in bpy.context.window.screen.areas:
		if i.type == 'VIEW_3D': ar = i
	ar = ar.spaces[0].region_3d.view_distance
	return ar

class QuickCir(bpy.types.Operator):
	bl_idname = "mesh.q_p"
	bl_label = "q_p"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	right = 0
	segment = 16
	savePos = None
	obj = None
	face = None
	leftCount = 0
	normal = None
	new_obj = None
	scale = True
	starMouse = None
	t= True
	n = False
	@classmethod
	def poll(cls, context):
		return (context.mode == "EDIT_MESH") or (context.mode == "OBJECT")
	
	def modal(self, context, event):


		if event.type == 'Q':
			return {'FINISHED'}

		if event.type == 'WHEELUPMOUSE':
			if self.leftCount != 2:
				Sub(self, context, mode=True)
			else:
				dist = self.new_obj.modifiers[0].thickness
				Sub(self, context, mode=True)
				SetSolidify(self, context)
				self.new_obj.modifiers[0].thickness = dist

		if event.type == 'WHEELDOWNMOUSE':
			if self.leftCount != 2:
				Sub(self, context, mode=False)
			else: 
				dist = self.new_obj.modifiers[0].thickness
				Sub(self, context, mode=False)
				SetSolidify(self, context)
				self.new_obj.modifiers[0].thickness = dist


		if event.type == 'MOUSEMOVE':
			if self.leftCount == 0:
				self.face, self.obj = RayCast(self, context, event, ray_max=1000.0)
				if isinstance(self.face,type(None)):
					get_pos3d(context, event)
		elif self.leftCount == 1:
			#if not isinstance(self.face,type(None)):
			#if self.scale:
				#self.scale = False
			get_pos3d(context, event)
			Scale(self, context)
		elif self.leftCount == 2:
			dis = (StarPosMouse(self, context, event) - self.starMouse) / Zoom(self, context)
			self.new_obj.modifiers[0].thickness = dis * 2

		if event.type == 'LEFTMOUSE':
			if self.leftCount == 0 and self.face:
				self.new_obj, self.savePos = CreateCilinder(context)
				Rotation(self, context, self.face, self.obj)
			elif self.leftCount == 0 and not self.face:
				self.new_obj, self.savePos = CreateCilinder(context)
			elif self.leftCount == 2:
				bpy.ops.object.modifier_apply(modifier=self.new_obj.modifiers[0].name)
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.normals_make_consistent(inside=False)
				bpy.ops.object.mode_set(mode='OBJECT')
				if self.right != 0:
					bpy.context.scene.objects.active = self.obj
					bpy.ops.object.modifier_apply(modifier=self.obj.modifiers[0].name)
					bpy.context.scene.objects.unlink(self.new_obj)
					bpy.data.objects.remove(self.new_obj)



				return {'FINISHED'}

			self.leftCount += 1
			if self.leftCount == 2:
				SetSolidify(self, context)
				self.starMouse = StarPosMouse(self, context, event)

		return {'RUNNING_MODAL'}

	def invoke(self, context, event):
		if context.space_data.type == 'VIEW_3D':
			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "is't 3dview")
			return {'CANCELLED'}

def register():
	bpy.utils.register_class(QuickCir)


def unregister():
	bpy.utils.unregister_class(QuickCir)


if __name__ == "__main__":
	register()
