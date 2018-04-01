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

def CreateEmpty(self, context):
	"""create new obj"""
	bpy.ops.object.empty_add(type='ARROWS')
	
	new = context.active_object
	new.location = self.mouseLocation

	
	return new

def MoveEmpty(self, compress=False):
	"""Moving the first vertives to create an area"""
	if self.mouseLocation:
		self.new_obj.location = self.mouseLocation
		

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

class SEmpty(SObj):
	bl_idname = "objects.stream_empty"
	bl_label = "Stream Empty"
	bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
	def __init__(self):
		super(SEmpty,self).__init__()
		self.stepCount = 2
		self.create = CreateEmpty
		self.moveStep1 = MoveEmpty
		self.moveStep2 = None
		self.help = DrawHelp


