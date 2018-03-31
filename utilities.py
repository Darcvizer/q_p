import bpy
import bmesh
import bgl
#from bgl import glVertex3f
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils
from mathutils.bvhtree import BVHTree
import numpy as np
from mathutils.geometry import intersect_line_plane
from mathutils.geometry import tessellate_polygon as tessellate
from math import cos, sin, pi

# import time
#d_time = time.time()
#print("--- %s notM del mesh seconds ---" % (time.time() - d_time))

def draw_circle_2d(color, point, r, num_segments):
	bgl.glBegin(bgl.GL_POLYGON)
	bgl.glColor4f(*color)
	#bgl.glBegin(bgl.GL_LINE_LOOP)
	for i in range (num_segments):
		a = (pi * 2 / num_segments) * i
		point2 = Vector((point[0] + r * cos(a), point[1] + r * sin(a), 0.0))

		bgl.glVertex2f(point2[0], point2[1]) # output vertex
		# apply the rotation matrix
	bgl.glEnd()

def draw_callback_px(self, context):
	# draw poly
	
	if len(self.panel_points) == 0 or self.mouseState > 0:
		return 0
	if self.faceComstrain:
		bgl.glColor4f(0.0, 1.0, 0.2, 0.15)
	else:
		bgl.glColor4f(1.0, 0.085, 0.0, 0.3)

	bgl.glEnable(bgl.GL_BLEND)
	bgl.glBegin(bgl.GL_TRIANGLES)
	for i in range(len(self.panel_points)):
		vec = view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.region_data , self.panel_points[i])
		bgl.glVertex2f(vec[0], vec[1])
		#glVertex3f(*self.panel_points[i])
	
	bgl.glEnd()
	v3 = view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.region_data , self.mouseLocation)
	draw_circle_2d((0.0, 1.0, 0.0, 0.6), v3, 3, 12)
	
	# restore opengl defaults
	bgl.glLineWidth(1)
	bgl.glDisable(bgl.GL_BLEND)
	bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def draw_callback_pv(self, context):
	if not self.ray_faca is None:
		zoom = (self.ray_obj.matrix_world * self.mesh.polygons[
			self.ray_faca].center - bpy.context.region_data.view_location).length * 2
		mw = self.matrix
	else:
		mw = Matrix.Translation(self.mouseLocation)
		zoom = (bpy.context.region_data.view_location - self.mouseLocation).length * 2
		
	scale = 2.0
	zoom_scale = 3.0
	bgl.glEnable(bgl.GL_BLEND)
	if not self.faceComstrain:
		bgl.glColor4f(0.471938, 0.530946, 0.8, 0.06)
	else:
		bgl.glColor4f(0.365066, 0.819318, 0.906332,0.06)
	bgl.glBegin(bgl.GL_POLYGON)
	
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, -1.0, 0.0))))))
	bgl.glEnd()
	
	# bgl.glEnable(bgl.GL_BLEND)
	bgl.glLineWidth(1.0)
	bgl.glBegin(bgl.GL_LINES)
	bgl.glColor4f(1, 1, 1, 0.1)
	
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.8, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.8, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.6, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.6, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.4, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.4, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.2, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.2, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.0, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((0.0, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-0.2, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-0.2, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-0.4, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-0.4, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-0.6, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-0.6, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-0.8, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-0.8, -1.0, 0.0))))))
	bgl.glColor4f(1, 1, 1, 0.1)
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, 0.8, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, 0.8, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, 0.6, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, 0.6, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, 0.4, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, 0.4, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, 0.2, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, 0.2, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, 0.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, 0.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, -0.2, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, -0.2, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, -0.4, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, -0.4, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, -0.6, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, -0.6, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, -0.8, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, -0.8, 0.0))))))
	bgl.glEnd()
	bgl.glLineWidth(0.6)
	bgl.glBegin(bgl.GL_LINES)
	
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, -1.0, 0.0))))))
	
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, -1.0, 0.0))))))
	
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, 1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, 1.0, 0.0))))))
	
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((1.0, -1.0, 0.0))))))
	bgl.glVertex3f(*(mw * ((zoom / zoom_scale) * (scale * Vector((-1.0, -1.0, 0.0))))))
	
	bgl.glEnd()
	
	# bgl.glBegin(bgl.GL_POLYGON)
	# bgl.glColor3f(1.0, 0.0, 0.0)
	# steps= 40
	# for step in range(steps):
	#     a = (math.pi * 2 / steps) * step
	#     glVertex3f(*(mw * Vector((0 + radius * math.cos(a), 0 + radius * math.sin(a), 0.0))))
	# glEnd()
	
	bgl.glEnd()

	
	# restore opengl defaults
	bgl.glLineWidth(1)
	bgl.glDisable(bgl.GL_BLEND)
	bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

def get_pos3d(self, context, event, point=False, normal=False, revers=False):
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
		if not self.view:
			pointLoc = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse, Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0)), False)
		else:
			pointLoc = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse, Vector((0.0, 0.0, 0.0)), getView(context, event), True)
	else:
		if not revers:
			pointLoc = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse, point, normal, False)
		else:
			pointLoc = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse, point, normal, True)
	
	if not pointLoc is None:
		return pointLoc

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

		for obj in  context.visible_objects:
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
		#d = ray_direction_obj.length

		ray_direction_obj.normalized()
		
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
	best_location = None
	edge_direction = None
	
	
	for obj, matrix in visible_objects_and_duplis():
		if obj.type == 'MESH':
			if not self.new_obj is None:
				if obj.name == self.new_obj.name:
					continue
			hit, normal, face_index = obj_ray_cast(obj, matrix)

			if hit is not None:
				hit_world = matrix * hit
				best_location = hit_world
				length_squared = (hit_world - ray_origin).length
				if best_obj is None or length_squared < best_length_squared:
					best_length_squared = length_squared
					best_obj = obj
					best_matrix = matrix
					best_face = face_index
					best_hit = hit
					if self.mesh is None:
						if len(best_obj.modifiers) == 0:
							self.mesh = best_obj.data
						else:
							name = best_obj.name + 'GegaSosok'
							self.mesh = best_obj.to_mesh(context.scene, apply_modifiers=True, settings='PREVIEW',calc_tessface=False, calc_undeformed=False)
							self.mesh.name = name
					elif self.mesh.name != best_obj.data.name + 'GegaSosok':
						if len(best_obj.modifiers) == 0:
							if len(self.ray_obj.modifiers)!=0:
								bpy.data.meshes.remove(self.mesh)
							self.mesh = best_obj.data
						else:
							if len(self.ray_obj.modifiers)!=0:
								bpy.data.meshes.remove(self.mesh)
							name = best_obj.name + 'GegaSosok'
							self.mesh = best_obj.to_mesh(context.scene, apply_modifiers=True, settings='PREVIEW',calc_tessface=False, calc_undeformed=False)
					break
								
					
	if not best_hit is None:
		best_distance = 0.0  # use float("inf") (infinity) to have unlimited search range
		mesh = self.mesh
		#edge_direction = None
		#best_matrix = best_obj.matrix_world
		
	
		#Coord for Darw
		if not self.faceComstrain and self.mouseState == 0:
			v = []
			for i in mesh.polygons[best_face].vertices:
				v.append(mesh.vertices[i].co.copy())
			self.panel_points = []
			for face in tessellate([v]):
				for vert in face:
					vec = best_matrix * v[vert].copy()
					self.panel_points.append(vec)
		
		# get the longest edge
		verts = None
		vector = None
		for i in mesh.polygons[best_face].edge_keys:
			distance = (mesh.vertices[i[0]].co.copy() - mesh.vertices[i[1]].co.copy()).length
			if best_distance <  distance:
				best_distance = distance
				v1 = mesh.vertices[i[0]].co.copy()
				v2 = mesh.vertices[i[1]].co.copy()
				vec = v1 - v2
				vec.normalize()
				edge_direction = vec
				
		#edge_direction = (mesh.vertices[verts[0]].co.copy() + mesh.vertices[verts[1]].co.copy()).normalize()

		
		# if used snapping
		best_distance = float("inf")
		
		if snap:
			for vert_index in mesh.polygons[best_face].vertices:
				vert_coord = mesh.vertices[vert_index].co
				distance = (vert_coord - best_hit).length
				if distance < best_distance:
					best_distance = distance
					best_location = best_matrix * vert_coord
	
			for v0, v1 in mesh.polygons[best_face].edge_keys:
				p0 = mesh.vertices[v0].co
				p1 = mesh.vertices[v1].co
				p = (p0 + p1) / 2
				distance = (p - best_hit).length
				if distance < best_distance:
					best_distance = distance
					best_location = best_matrix * p
	
			face_pos = Vector(mesh.polygons[best_face].center)
			distance = (face_pos - best_hit).length
			if distance < best_distance:
				best_distance = distance
				best_location = best_matrix * face_pos
	
	if not best_face is None and not best_obj is None:
		return best_face, best_obj, best_location, edge_direction
	else:
		return None, self.ray_obj, None, None

def transfor(self, context):
	"""set origin object"""
	org = self.new_obj.data.vertices[6].co.copy()
	self.new_obj.data.transform(Matrix.Translation(-org))
	self.new_obj.location += org
	bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

def Rotation(face, obj, longhtEdge, mesh):
	"""Rotation matrix by source face"""
	normal = mesh.polygons[face].normal.copy()

	matrix_rotate = Vector((1, 0, 0)).rotation_difference(longhtEdge * obj.matrix_world.copy().inverted()).to_matrix().to_4x4()
	
	mat_tmp = (Vector((0, 0, 1)) * matrix_rotate.inverted()).rotation_difference(normal * obj.matrix_world.copy().inverted()).to_matrix().to_4x4()
	
	matrix_rotate = mat_tmp * matrix_rotate
	matrix_translation = Matrix.Translation(obj.matrix_world.copy() * mesh.polygons[face].center.copy())
	
	return matrix_translation * matrix_rotate.to_4x4()

def SetupBool(self, context):
	"""Setup Object For Boolean"""
	self.new_obj.draw_type = 'WIRE'
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
	bpy.context.scene.objects.active = self.new_obj
	self.auto_merge = bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge
	bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = False
	self.ray_obj.show_wire = True
	self.ray_obj.show_all_edges = True
	
def ApplyBool(self, context):
	bpy.context.scene.objects.active = self.ray_obj
	bpy.ops.object.modifier_apply(modifier=self.ray_obj.modifiers[-1].name)

	for i in self.ray_obj.modifiers:
		if i in self.u_modifier:
			i.show_viewport = True

	self.ray_obj.show_wire = self.show_wire
	self.ray_obj.show_all_edges = self.show_all_edges
	bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = self.auto_merge
	bpy.data.meshes.remove(self.new_obj.data)
	#bpy.context.scene.objects.unlink(self.new_obj)
	bpy.data.objects.remove(self.new_obj)

	if self.edit_mode_obj:
		bpy.context.scene.objects.active = self.edit_mode_obj
		bpy.ops.object.mode_set(mode='EDIT')

def getView(context, event):
	"""Get Viewport Vector"""
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y
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

def findView(context, event):
	"""Get Viewport State"""
	viewState = False
	if PerspOrOrtot():
		view = getView(context, event)
		if view == Vector((0.0, -1.0, 0.0)):
			viewState = True
			return True
		elif view == Vector((0.0, 1.0, 0.0)):
			viewState = True
			return True
		elif view == Vector((1.0, 0.0, 0.0)):
			viewState = True
			return True
		elif view == Vector((-1.0, 0.0, 0.0)):
			viewState = True
			return True
		elif view == Vector((0.0, 0.0, 1.0)):
			viewState = True
			return True
		elif view == Vector((0.0, 0.0, -1.0)):
			viewState = True
			return True
		else:
			viewState = False
			return viewState
	else:
		viewState = False
		return viewState
	
def FindNormal(obj, face1, face2):
	n1 = obj.matrix_world.to_3x3() * obj.data.polygons[face1].normal
	n2 = obj.matrix_world.to_3x3() * obj.data.polygons[face2].normal
	c1 = obj.matrix_world * obj.data.polygons[face1].center
	c2 = obj.matrix_world * obj.data.polygons[face2].center
	
	line = (n1 * 3000) + c1
	
	hit = intersect_line_plane(c1, line, c2, n2, False)
	
	return hit

def FlipNormal():
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.normals_make_consistent(inside=False)
	bpy.ops.object.mode_set(mode='OBJECT')


def FirstState(self, context, event):
	if not self.faceComstrain:
		if event.ctrl:
			self.ray_faca, self.ray_obj, self.mouseLocation, self.dir_longest_edge = RayCast(self, context, event,
			                                                                                 ray_max=1000.0, snap=True)
		else:
			self.ray_faca, self.ray_obj, self.mouseLocation, self.dir_longest_edge = RayCast(self, context, event,
			                                                                                 ray_max=1000.0, snap=False)
		if self.ray_faca is None:
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
			self.moveStep1(self, True)
		else:
			self.moveStep1(self)
	else:
		self.mouseLocation = get_pos3d(self, context, event, self.global_loc, self.global_norm)
		
		if event.shift and not event.type == 'MIDDLEMOUSE':
			self.moveStep1(self, True)
		else:
			self.moveStep1(self)


def ThirdState(self, context, event):
	if event.ctrl:
		self.mouseLocation = RayCast(self, context, event, ray_max=1000.0, snap=True)[2]
		if event.shift and not event.type == 'MIDDLEMOUSE':
			self.moveStep2(self, True)
		else:
			self.moveStep2(self)
	else:
		self.mouseLocation = get_pos3d(self, context, event, self.global_loc, self.global_norm, True)
		
		if event.shift and not event.type == 'MIDDLEMOUSE':
			self.moveStep2(self, True)
		else:
			self.moveStep2(self)
			
	hit = FindNormal(self.new_obj, 4, 5)
	if not hit is None:
		FlipNormal()

def LeftMouseClick(self, context, event):
	if self.mouseState == 0:
		if not self.ray_faca is None:
			self.global_norm = self.ray_obj.matrix_world.to_3x3() * self.mesh.polygons[self.ray_faca].normal.copy()
			self.global_loc = self.ray_obj.matrix_world * self.mesh.polygons[self.ray_faca].center.copy()
			
			self.new_obj = self.create(self, context)
			self.new_obj.matrix_world = self.matrix
			self.new_obj.location = self.mouseLocation
		
		else:
			self.new_obj = self.create(self, context)
			self.global_norm = Vector((0.0, 0.0, 1.0))
			self.global_loc = Vector((0.0, 0.0, 0.0))
	elif self.mouseState == 1:
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
		self.global_norm = getView(context, event)
		self.global_loc = self.new_obj.location
	self.mouseState += 1


def RightMouseClick(self, context, event):
	if ((not self.ray_faca is None) or self.faceComstrain) or (self.global_norm and self.global_loc):
		if self.mouseState == 0:
			self.mode = True
			
			self.global_norm = self.ray_obj.matrix_world.to_3x3() * self.mesh.polygons[self.ray_faca].normal.copy()
			self.global_loc = self.ray_obj.matrix_world * self.mesh.polygons[self.ray_faca].center.copy()
			
			self.new_obj = self.create(self, context)
			self.new_obj.matrix_world = self.matrix
			self.new_obj.location = self.mouseLocation
			if not self.useOffset is None:
				n = self.new_obj.matrix_world.to_3x3().inverted() * self.mesh.polygons[self.ray_faca].normal.copy()
				for i in self.new_obj.data.polygons[self.useOffset].vertices:
					self.new_obj.data.vertices[i].co = n * 0.0001 + self.new_obj.data.vertices[i].co.copy()
			if self.stepCount == 2:
				SetupBool(self, context)
		elif self.mouseState == 1:
			bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
			self.global_norm = getView(context, event)
			self.global_loc = self.new_obj.location
			if self.stepCount == 3:
				SetupBool(self, context)
		self.mouseState += 1

def Cansel(self, context):
	if not self.mesh is None:
		if len(self.ray_obj.modifiers) == 1 and self.mode == True:
			pass
		elif len(self.ray_obj.modifiers) != 0 and self.mode == False:
			bpy.data.meshes.remove(self.mesh)
	
	if self.mouseState > 0 and not self.mode:
		bpy.data.meshes.remove(self.new_obj.data)
		bpy.data.objects.remove(self.new_obj)
	
	
	
	elif self.mouseState > 0 and self.mode:
		bpy.data.meshes.remove(self.new_obj.data)
		bpy.data.objects.remove(self.new_obj)
		self.ray_obj.modifiers.remove(self.ray_obj.modifiers[-1])


def Finish(self, context):
	if not self.mesh is None:
		if len(self.ray_obj.modifiers) == 1 and self.mode == True:
			pass
		elif len(self.ray_obj.modifiers) != 0 and self.mode == False:
			bpy.data.meshes.remove(self.mesh)
	if self.mode:
		ApplyBool(self, context)
	
	else:
		pass
