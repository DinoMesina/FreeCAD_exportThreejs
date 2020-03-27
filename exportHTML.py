# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (C) 2020 Dino del Favero <dino@delfavero.it>                *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 3 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD, Draft, Part

__title__   = "FreeCAD Javascript 3D library Three.js export"
__author__  = "Dino@mesina.net"
__version__ = "0.1.0"
__date__    = "26/03/2020"

TOLERANCE = 0.01;

if open.__module__ in ['__builtin__','io']:
    pyopen = open

def export(exportList, fileName):

    # extract macro path
    macroPath = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Macro").GetString("MacroPath")
    
    # read the template
    templateFile = pyopen(macroPath+"/TemplateExportThreejs.html", "r")
    template = str(templateFile.read())
    templateFile.close()
    
    # Scorro la selezione
    objectsList = Draft.getGroupContents(exportList, walls=True, addgroups=False)
    
    if (len(objectsList) < 1):
        FreeCAD.Console.PrintMessage("Selezionare almeno un oggetto da esportare\n")
    else:
        objs = []
        for o in objectsList:
            if (o.isDerivedFrom("Part::Feature") or o.isDerivedFrom("Mesh::Feature") or o.isDerivedFrom("Part::TopoShape")):
                if (o.Shape.Solids):
                    objs.append(o.Shape)
        if (len(objs) != 0):
            compound=Part.makeCompound(objs)
            template = template.replace("<!--InsertGeometryHere-->", obj2threejs(compound, TOLERANCE))
            # create html file
            htmlFile = pyopen(fileName, "w")
            htmlFile.write(template)
            htmlFile.close()
        else:
            FreeCAD.Console.PrintMessage("Selezionati solo oggetti non solidi, nulla da esportare\n")

def obj2threejs(obj, tolerance):
    """Converts a Shape to three.js javascript code"""
    
    # Part::Feature
    if (obj.isDerivedFrom("Part::Feature")):
        shape = obj.Shape
        mesh = shape.tessellate(tolerance)
        vertices = mesh[0]
        index = mesh[1]
    
    # Part::TopoShape
    if (obj.isDerivedFrom("Part::TopoShape")):
        mesh = obj.tessellate(tolerance)
        vertices = mesh[0]
        index = mesh[1]

    # Mesh::Feature 
    if (obj.isDerivedFrom("Mesh::Feature")):
        mesh = obj.Mesh
        vertices = []
        index = []
        for p in mesh.Points:
            vertices.append(p.Vector)
        for f in mesh.Facets:
            index.append(f.PointIndices)
                
    # creo lo script javascript
    str = "\t\tgeom = new THREE.Geometry();\n"
    str += "\t\tgeom.vertices.push(\n"
    # scrivo i vertici
    for v in vertices[:-1]:
        str += "\t\t\tnew THREE.Vector3({:f},{:f},{:f}),\n".format(v.x, v.y, v.z)
    str += "\t\t\tnew THREE.Vector3({:f},{:f},{:f})\n".format(vertices[-1].x, vertices[-1].y, vertices[-1].z)
    str += "\t\t);\n"
    
    # scrivo le facce
    str += "\t\tgeom.faces.push(\n"
    for i in index[:-1]:
        str += "\t\t\tnew THREE.Face3({:d},{:d},{:d}),\n".format(i[0], i[1], i[2])
    str += "\t\t\tnew THREE.Face3({:d},{:d},{:d})\n".format(index[-1][0], index[-1][1], index[-1][2])
    str += "\t\t);\n"
    str += "\t\tgeom.computeFaceNormals();\n"
    
    return(str)

