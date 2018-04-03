## ______________ Begin Python Code example _____________ ##

bl_info = {
	"name": "q_p",
	"author": "Vladislav Kindushov, Alexander Nedovizin",
	"version": (0, 0, 9),
	"blender": (2, 79, 0),
	"description": "Interactive creation of primitives",
	"category": "Object" }

import bpy
from bpy.types import Menu
import rna_keymap_ui
from bpy.props import (
		EnumProperty,
		IntProperty
		)
from . import (
		QBox,
		QCylinder,
		QSphere,
		QPlane,
		QGSphere,
		QCircle,
		QEmpty,
		QRBox
		)
# Spawn an Nested Pie Menu selection

class VIEW3D_PIE_q_p(Menu):
	bl_label = "q_p"    
	bl_idname = "mesh.q_p"

	def draw(self, context):
		layout = self.layout

		pie = layout.menu_pie()
		pie.operator("objects.stream_box",      	text= "Box")
		pie.operator("objects.stream_cylinder", 	text= "Cylinder")
		pie.operator("objects.stream_sphere", 		text= "Sphere")
		pie.operator("objects.stream_plane",		text= "Plane")
		pie.operator("objects.stream_ico_sphere",	text= "Ico Sphere")
		pie.operator("objects.stream_circle",		text= "Circle")
		pie.operator("objects.stream_empty",        text= "Empty")
		try:
			pie.operator("objects.stream_round_box", text="Round Box")
		except:
			pass
		
		#pie.operator("objects.stream_empty",        text="DrawPoly (KTools)")
		
def use_cashes(self, context):
	self.caches_valid = True
	
class AddonPreferencesQP(bpy.types.AddonPreferences):
	bl_idname = __name__

	Mode = EnumProperty(
		items=[('blender', "Blender", "Blender Navigation "),
			   ('maya', "Maya", "Maya Navigation "),],
		name="Rotate View Settings",
		default='blender',
		update=use_cashes
	)
	
	Cylinder = IntProperty(
		name="Cylinder Default Sigments",
		default=32,
		min = 4
	)
	Circle = IntProperty(
		name="Circle Default Sigments",
		default=32,
		min=4,
	)
	Sphere = IntProperty(
		name="UV Sphere Default Sigments",
		default=32,
		min=4,
	)
	GSphere = IntProperty(
		name="Ico Sphere Default Sigments",
		default=4,
		min=3,
	)
	
	caches_valid = True
	def draw(self, context):
		layout = self.layout
		layout.prop(self, "Mode")
		layout.prop(self, "Cylinder")
		layout.prop(self, "Circle")
		layout.prop(self, "Sphere")
		layout.prop(self, "GSphere")

def register():
	bpy.utils.register_class(VIEW3D_PIE_q_p)
	bpy.utils.register_class(QBox.SBox)
	bpy.utils.register_class(QCylinder.SCylinder)
	bpy.utils.register_class(QSphere.SSphere)
	bpy.utils.register_class(QPlane.SPlane)
	bpy.utils.register_class(QGSphere.SGSphere)
	bpy.utils.register_class(QCircle.SCircle)
	bpy.utils.register_class(QEmpty.SEmpty)
	try:
		bpy.utils.register_class(QRBox.SRBox)
	except:
		pass
	bpy.utils.register_class(AddonPreferencesQP)
	wm = bpy.context.window_manager
	km = wm.keyconfigs.addon.keymaps.new(name="3D View Generic", space_type = "VIEW_3D")
	kmi = km.keymap_items.new("wm.call_menu_pie","RIGHTMOUSE","PRESS",ctrl=True).properties.name = "mesh.q_p"
	
def unregister():
	bpy.utils.unregister_class(VIEW3D_PIE_q_p)
	bpy.utils.unregister_class(QBox.SBox)
	bpy.utils.unregister_class(QCylinder.SCylinder)
	bpy.utils.unregister_class(QSphere.SSphere)
	bpy.utils.unregister_class(QPlane.SPlane)
	bpy.utils.unregister_class(QGSphere.SGSphere)
	bpy.utils.unregister_class(QCircle.SCircle)
	bpy.utils.unregister_class(QEmpty.SEmpty)
	try:
		bpy.utils.unregister_class(QRBox.SRBox)
	except:
		pass
	bpy.utils.unregister_class(AddonPreferencesQP)

if __name__ == "__main__":
	register()