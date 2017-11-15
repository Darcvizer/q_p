## ______________ Begin Python Code example _____________ ##

bl_info = {
	"name": "q_p",
	"author": "Vladislav Kindushov, Alexander Nedovizin",
	"version": (0, 0, 3),
	"blender": (2, 79, 0),
	"description": "Interactive creation of primitives",
	"category": "Object" }

import bpy
from bpy.types import Menu
from . import (
		QBox,
		QCylinder,
		QSphere,
		QPlane,
		QGSphere,
		QCircle
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

	  

def register():
	bpy.utils.register_class(VIEW3D_PIE_q_p)
	bpy.utils.register_class(QBox.SBox)
	bpy.utils.register_class(QCylinder.SCylinder)
	bpy.utils.register_class(QSphere.SSphere)
	bpy.utils.register_class(QPlane.SPlane)
	bpy.utils.register_class(QGSphere.SGSphere)
	bpy.utils.register_class(QCircle.SCircle)
	wm = bpy.context.window_manager
	km = wm.keyconfigs.addon.keymaps.new(name="3D View Generic", space_type = "VIEW_3D")
	kmi = km.keymap_items.new("wm.call_menu_pie","RIGHTMOUSE","PRESS",ctrl=True).properties.name = "mesh.q_p"
	
def unregister():
	bpy.utils.unregister_class(VIEW3D_PIE_q_p)
	bpy.utils.unregister_class(QBox.SBox)
	bpy.utils.unregister_class(QCylinder.SCylinder)
	bpy.utils.unregister_class(QSphere.SSphere)
	bpy.utils.unregister_class(QPlane.SPlane)
	bpy.utils.register_class(QGSphere.SGSphere)
	bpy.utils.register_class(QCircle.SCircle)
	SCircle

if __name__ == "__main__":
	register()