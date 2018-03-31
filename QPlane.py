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

def CreatePlane(self, context):
	"""create new obj"""
	if self.view:
		bpy.ops.mesh.primitive_plane_add(view_align=True)
	else:
		bpy.ops.mesh.primitive_plane_add()
	new = context.active_object
	new.scale = Vector((0.00001, 0.00001, 0.0001))
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	new.location = self.mouseLocation
	org = new.data.vertices[3].co.copy()
	new.data.transform(Matrix.Translation(-org))
	new.location += org
	
	return new

def MoveVerts(self, compress=False):
	"""Moving the first vertives to create an area"""
	if self.mouseLocation:
		self.direct1 = (self.new_obj.data.vertices[3].co.copy() - self.new_obj.data.vertices[1].co.copy()).normalized()
		self.direct2 = (self.new_obj.data.vertices[3].co.copy() - self.new_obj.data.vertices[2].co.copy()).normalized()
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


def DrawHelp(self, context, event):
	co = 'SpaceBar(On):Fix Graund, '
	cf = 'SpaceBar(Off):Fix Graund, '
	so = 'CTRL(On): Snaping, '
	sf = 'CTRL(Off): Snaping, '
	po = 'SHIFT(On): Proportional Shift'
	pf = 'SHIFT(Off): Proportional Shift'
	str = 'LMB: Create New Premetive, '
	
	
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

class SPlane(SObj):
	bl_idname = "objects.stream_plane"
	bl_label = "Stream Plane"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	def __init__(self):
		super(SPlane,self).__init__()
		self.stepCount = 2
		self.create = CreatePlane
		self.moveStep1 = MoveVerts
		self.moveStep2 = None
		self.useBool = False
		self.help = DrawHelp
		self.useOffset = None
		self.direct1 = None
		self.direct2 = None

