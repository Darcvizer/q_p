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
from .main import *



def faceMove(self, pasS = True):
	"""Sets the height of the boxing"""
	if self.mouseLocation:
		v1 = self.new_obj.matrix_world.inverted() * self.mouseLocation
		normal = None
		if self.segment <= 4:
			normal = self.new_obj.data.polygons[2].normal.copy()
			for i in self.new_obj.data.polygons[self.segment - 2].vertices:
				v2 = self.new_obj.data.vertices[i].co.copy()
				dvec = v1-v2
				dnormal = np.dot(dvec, normal)
				self.new_obj.data.vertices[i].co += Vector(dnormal*normal)
		else:
			normal = self.new_obj.data.polygons[self.segment - 2].normal.copy()
			for i in self.new_obj.data.polygons[self.segment - 2].vertices:
				v2 = self.new_obj.data.vertices[i].co.copy()
				dvec = v1-v2
				dnormal = np.dot(dvec, normal)
				self.new_obj.data.vertices[i].co += Vector(dnormal*normal)
	
		self.edglen = self.new_obj.dimensions.copy()

def CreateCilinder(self, pasS=True):
	if self.view:
		bpy.ops.mesh.primitive_cylinder_add(vertices=self.segment, radius=0.0001, depth=2, view_align=True)
	else:
		bpy.ops.mesh.primitive_cylinder_add(vertices=self.segment, radius=0.0001, depth=0.0001, view_align=False)
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	new = bpy.context.active_object
	org = new.data.polygons[self.segment+1].center.copy()
	new.data.transform(Matrix.Translation(-org))
	new.location = self.mouseLocation
	if not self.firstPosition is None:
		new.location = self.firstPosition
	else:
		new.location = self.mouseLocation

	self.firstPosition = new.location.copy()
	return new
	


def Scale(self, pasS=True):
	if self.mouseLocation:

		if self.mouseState == 1:
			loc = self.mouseLocation
			self.dist = (self.firstPosition - loc).length
		
		bpy.data.meshes.remove(self.new_obj.data)
		bpy.data.objects.remove(self.new_obj)
		if self.view:
			bpy.ops.mesh.primitive_cylinder_add(vertices=self.segment, radius=self.dist, depth=2, view_align=True)
			self.new_obj = bpy.context.active_object
			if self.segment <= 4:
				org = self.new_obj.data.polygons[4].center.copy()
			else:
				org = self.new_obj.data.polygons[self.segment + 1].center.copy()
				self.new_obj.data.transform(Matrix.Translation(-org))
				self.new_obj.location = self.firstPosition
		else:
			bpy.ops.mesh.primitive_cylinder_add(vertices=self.segment, radius=self.dist, depth=0.0001, view_align=False)
			self.new_obj = bpy.context.active_object
			if self.segment <= 4:
				org = self.new_obj.data.polygons[4].center.copy()
			else:
				org = self.new_obj.data.polygons[self.segment + 1].center.copy()
				self.new_obj.data.transform(Matrix.Translation(-org))
				self.new_obj.location = self.firstPosition
		
		
		if self.matrix is not None and not self.ray_faca is None:
			self.new_obj.matrix_world = self.matrix
		
		self.new_obj.location = self.firstPosition
		if self.mode:
			if not self.ray_obj is None and self.mode:
				n = self.new_obj.matrix_world.to_3x3().inverted() * self.mesh.polygons[self.ray_faca].normal.copy()
				for i in self.new_obj.data.polygons[self.useOffset].vertices:
					self.new_obj.data.vertices[i].co = n * 0.0001 + self.new_obj.data.vertices[i].co.copy()
			if len(self.ray_obj.modifiers)  == 0:
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
			else:
				self.new_obj.draw_type = 'WIRE'
				self.ray_obj.modifiers[-1].object = self.new_obj
		if self.mouseState > 1:
			faceMove(self, pasS=True)

	

def DrawHelp(self, context, event):
	bo = 'RMB(On): Boolean, '
	bf = 'RMB(Off): Boolean, '
	co = 'SpaceBar(On):Fix Graund, '
	cf = 'SpaceBar(Off):Fix Graund, '
	so = 'CTRL(On): Snaping, '
	sf = 'CTRL(Off): Snaping, '
	str = 'LMB: Create New Premetive, '
	
	if self.mode:
		str += bo
	else:
		str += bf
	
	if self.faceComstrain:
		str += co
	else:
		str += cf
	
	if event.ctrl:
		str += so
	else:
		str += sf
	
	return str + ', Segments(' + self.segment.__str__() + ')'
class SCylinder(SObj):
	bl_idname = "objects.stream_cylinder"
	bl_label = "Stream Cylinder"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	def __init__(self):
		super(SCylinder,self).__init__()
		self.stepCount = 3
		self.create = CreateCilinder
		self.moveStep1 = Scale
		self.moveStep2 = faceMove
		self.useBool = True
		self.help = DrawHelp
		self.segment = 32
		self.useOffset = self.segment + 1
		self.firstPosition = None
		self.dist = None
		self.edglen = None
