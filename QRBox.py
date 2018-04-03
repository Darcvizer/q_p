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
		bpy.ops.mesh.primitive_round_cube_add(view_align=True, radius=0.0001, arc_div=4, lin_div=0, div_type='CORNERS')
	else:
		bpy.ops.mesh.primitive_round_cube_add(view_align=False, radius=0.0001, arc_div=4, lin_div=0, div_type='CORNERS')
	new = context.active_object
	new.scale = Vector((0.00001, 0.00001, 0.00001))
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	
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
		# bpy.data.objects.remove(self.new_obj)
		bpy.ops.object.delete(use_global=True)
		if self.view:
			bpy.ops.mesh.primitive_round_cube_add(view_align=True, radius=dist, arc_div=4, lin_div=0, div_type='CORNERS')
		
		else:
			bpy.ops.mesh.primitive_round_cube_add(view_align=False, radius=dist, arc_div=4, lin_div=0,div_type='CORNERS')
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		self.new_obj = bpy.context.active_object
		
		if self.matrix is not None and not self.ray_faca is None:
			self.new_obj.matrix_world = self.matrix
		
		self.new_obj.location = self.firstPosition
		
		#self.new_obj.dimensions[0] = dist
		#self.new_obj.dimensions[1] = dist
		#self.new_obj.dimensions[2] = dist
		
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
	
	return str + 'Wheel: Add and Sub Segment' + '(' + self.segment.__str__() + ')'


class SRBox(SObj):
	bl_idname = "objects.stream_round_box"
	bl_label = "Stream Round Box"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	def __init__(self):
		super(SRBox,self).__init__()
		self.stepCount = 2
		self.create = CreateBox
		self.moveStep1 = Scale
		self.useBool = True
		self.help = DrawHelp
		self.segment = 4
		self.firstPosition = None


