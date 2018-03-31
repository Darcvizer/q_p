import bpy
import bmesh
import bgl
from bgl import glVertex3f
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils
from mathutils import bvhtree
import numpy as np
from mathutils.geometry import intersect_line_plane
from mathutils.geometry import tessellate_polygon as tessellate
from .utilities import *
from .main import *


def CreateSphere(self, context):
	if self.view:
		bpy.ops.mesh.primitive_ico_sphere_add(view_align=True, subdivisions=4, size=0.0001)
	else:
		bpy.ops.mesh.primitive_ico_sphere_add(view_align=False, subdivisions=4, size=0.0001)
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	new = context.active_object
	if not self.firstPosition is None:
		new.location = self.firstPosition
	else:
		new.location = self.mouseLocation
	self.firstPosition = new.location.copy()
	return new


def Scale(self, pasS=True):
	if self.mouseLocation:
		loc = self.mouseLocation
		dist = (self.firstPosition - loc).length
		
		bpy.data.meshes.remove(self.new_obj.data)
		bpy.data.objects.remove(self.new_obj)
		if self.view:
			bpy.ops.mesh.primitive_ico_sphere_add(view_align=True, subdivisions=self.segment)#, size=0.0001)
		else:
			bpy.ops.mesh.primitive_ico_sphere_add(view_align=True, subdivisions=self.segment)#, size=0.0001)
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		self.new_obj = bpy.context.active_object
		
		if self.matrix is not None and not self.ray_faca is None:
			self.new_obj.matrix_world = self.matrix
		
		self.new_obj.location = self.firstPosition
		
		self.new_obj.scale[0] = dist
		self.new_obj.scale[1] = dist
		self.new_obj.scale[2] = dist
		
		if self.mode:
			self.new_obj.draw_type = 'WIRE'
			self.ray_obj.modifiers[-1].object = self.new_obj


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


class SGSphere(SObj):
	bl_idname = "objects.stream_ico_sphere"
	bl_label = "Stream Ico Sphere"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	
	def __init__(self):
		super(SGSphere, self).__init__()
		self.stepCount = 2
		self.create = CreateSphere
		self.moveStep1 = Scale
		self.useBool = True
		self.help = DrawHelp
		self.segment = 4
		self.firstPosition = None




