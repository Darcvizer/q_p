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


def CreateCircle(self, context):
	if self.view:
		if self.fill:
			bpy.ops.mesh.primitive_circle_add(vertices=self.segment,fill_type='NGON', radius=0.00001,view_align=True)
		else:
			bpy.ops.mesh.primitive_circle_add(vertices=self.segment,fill_type='NOTHING', radius=0.00001,view_align=True)
	else:
		if self.fill:
			bpy.ops.mesh.primitive_circle_add(vertices=self.segment,fill_type='NGON', radius=0.00001,view_align=False)
		else:
			bpy.ops.mesh.primitive_circle_add(vertices=self.segment,fill_type='NOTHING', radius=0.00001,view_align=False)
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
		dist = (self.firstPosition-loc).length
		
		bpy.data.meshes.remove(self.new_obj.data)
		bpy.data.objects.remove(self.new_obj)
	
		if self.view:
			if self.fill:
				bpy.ops.mesh.primitive_circle_add(vertices=self.segment,fill_type='NGON', radius=dist,view_align=True)
			else:
				bpy.ops.mesh.primitive_circle_add(vertices=self.segment,fill_type='NOTHING', radius=dist,view_align=True)
		else:
			if self.fill:
				bpy.ops.mesh.primitive_circle_add(vertices=self.segment,fill_type='NGON', radius=dist,view_align=False)
			else:
				bpy.ops.mesh.primitive_circle_add(vertices=self.segment,fill_type='NOTHING', radius=dist,view_align=False)
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
	bo = 'RMB(On): Fill, '
	bf = 'RMB(Off): Fill, '
	co = 'SpaceBar(On):Fix Graund, '
	cf = 'SpaceBar(Off):Fix Graund, '
	so = 'CTRL(On): Snaping, '
	sf = 'CTRL(Off): Snaping, '
	po = 'SHIFT(On): Proportional Shift'
	pf = 'SHIFT(Off): Proportional Shift'
	str = 'LMB: Create New Premetive, '
	
	if self.fill:
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
	
	return str + 'segments (' + self.segment.__str__() + ')'


class SCircle(SObj):
	bl_idname = "objects.stream_circle"
	bl_label = "Stream Circle"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	def __init__(self):
		super(SCircle,self).__init__()
		self.stepCount = 2
		self.create = CreateCircle
		self.moveStep1 = Scale
		self.moveStep2 = None
		self.help = DrawHelp
		self.useOffset = None
		self.fill = True
		self.segment = bpy.context.user_preferences.addons.get("q_p").preferences.Circle
		self.firstPosition = None

