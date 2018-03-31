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


def CreateBox(self, context):
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
	if self.mouseLocation:
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
			
			print('sosok')
		
		else:
			for i in self.new_obj.data.polygons[3].vertices:
				v2 = self.new_obj.data.vertices[i].co.copy()
				dvec = v1-v2
				dnormal = np.dot(dvec, normal)
				self.new_obj.data.vertices[i].co += Vector(dnormal*normal)
		m = -1

def faceMove(self, compress=False):
	"""Sets the height of the boxing"""
	if self.mouseLocation:
		v1 = self.new_obj.matrix_world.inverted() * self.mouseLocation
		
		normal = self.new_obj.data.polygons[5].normal.copy()
		
		if compress:
			# Move on base position
			self.new_obj.data.vertices[1].co = self.new_obj.data.vertices[0].co.copy()
			self.new_obj.data.vertices[5].co = self.new_obj.data.vertices[4].co.copy()
			self.new_obj.data.vertices[3].co = self.new_obj.data.vertices[2].co.copy()
			self.new_obj.data.vertices[7].co = self.new_obj.data.vertices[6].co.copy()
			
			# Arithmetical mean
			v1 = (self.new_obj.data.vertices[3].co.copy() - self.new_obj.data.vertices[1].co.copy()).length
			v2 = (self.new_obj.data.vertices[1].co.copy() - self.new_obj.data.vertices[5].co.copy()).length
			v3 = (self.new_obj.data.vertices[7].co.copy() - self.new_obj.data.vertices[5].co.copy()).length
			v4 = (self.new_obj.data.vertices[7].co.copy() - self.new_obj.data.vertices[3].co.copy()).length
			
			dist = (v1 + v2 + v3 + v4) / 4
			
			# Move face
			for i in self.new_obj.data.polygons[5].vertices:
				self.new_obj.data.vertices[i].co += normal * dist
		else:
			for i in self.new_obj.data.polygons[5].vertices:
				v2 = self.new_obj.data.vertices[i].co.copy()
				dvec = v1 - v2
				dnormal = np.dot(dvec, normal)
				self.new_obj.data.vertices[i].co += Vector(dnormal * normal)

		
def DrawHelp(self, context, event):
	bo = 'RMB(On): Boolean, '
	bf = 'RMB(Off): Boolean, '
	co = 'SpaceBar(On):Fix Graund, '
	cf = 'SpaceBar(Off):Fix Graund, '
	so = 'CTRL(On): Snaping, '
	sf = 'CTRL(Off): Snaping, '
	po = 'SHIFT(On): Proportional Shift'
	pf = 'SHIFT(Off): Proportional Shift'
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
		
	if event.shift:
		str += po
	else:
		str += pf
	
	
	return str

class SBox(SObj):
	bl_idname = "objects.stream_box"
	bl_label = "Stream Box"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	def __init__(self):
		super(SBox,self).__init__()
		self.stepCount = 3
		self.create = CreateBox
		self.moveStep1 = MoveVerts
		self.moveStep2 = faceMove
		self.useBool = True
		self.help = DrawHelp
		self.useOffset = 4


