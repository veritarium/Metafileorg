#!/usr/bin/env python3
"""
Extend categories.yaml with missing extensions from info.txt.
"""
import yaml
import sys
from pathlib import Path

# Load existing categories
with open('config/categories.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

mapping = data.get('mapping', {})

# New mappings to add (extension -> (category, subcategory))
new_mappings = {
    # CAD & 3D
    'acr': ('CAD', 'AutoCAD'),
    'adsk': ('CAD', 'Autodesk'),
    'adsklib': ('CAD', 'Autodesk Library'),
    'ai': ('Images', 'Vector'),
    'blend': ('CAD', 'Blender'),
    'blend1': ('CAD', 'Blender Backup'),
    'bpmn': ('Documents', 'Business Process'),
    'bup': ('Miscellaneous', 'Backup'),
    'ctb': ('CAD', 'AutoCAD Plot Style'),
    'cuix': ('CAD', 'AutoCAD UI'),
    'dcl': ('CAD', 'AutoCAD Dialog'),
    'dgn': ('CAD', 'MicroStation'),
    'dvb': ('CAD', 'AutoCAD VBA'),
    'dwf': ('CAD', 'Design Web Format'),
    'dwl': ('CAD', 'AutoCAD Lock'),
    'dwl2': ('CAD', 'AutoCAD Lock'),
    'dwt': ('CAD', 'AutoCAD Template'),
    'dwt-alt': ('CAD', 'AutoCAD Template'),
    'emz': ('Images', 'Compressed EMF'),
    'exr': ('Images', 'OpenEXR'),
    'fbx': ('CAD', '3D Model'),
    'fdf': ('Documents', 'PDF Form'),
    'glb': ('CAD', '3D Model'),
    'glsl': ('Code', 'Shader'),
    'glslfx': ('Code', 'Shader Effect'),
    'hdr': ('Images', 'HDR'),
    'hipfb': ('CAD', 'Houdini'),
    'iam': ('CAD', 'Inventor Assembly'),
    'ics': ('Documents', 'Calendar'),
    'idw': ('CAD', 'Inventor Drawing'),
    'ifc': ('CAD', 'Industry Foundation Classes'),
    'ifo': ('Media', 'DVD Info'),
    'ipj': ('CAD', 'Inventor Project'),
    'ipn': ('CAD', 'Inventor Presentation'),
    'ipt': ('CAD', 'Inventor Part'),
    'iqy': ('Documents', 'Excel Query'),
    'jt': ('CAD', 'JT'),
    'key': ('Documents', 'Keynote'),
    'lin': ('CAD', 'AutoCAD Linetype'),
    'lng': ('Config', 'Language'),
    'lnk': ('System', 'Shortcut'),
    'lsp': ('Code', 'Lisp'),
    'manifest': ('System', 'Manifest'),
    'mat': ('Data', 'MATLAB'),
    'max': ('CAD', '3ds Max'),
    'mdl': ('CAD', 'Model'),
    'metal': ('Code', 'Metal Shader'),
    'mnl': ('CAD', 'AutoCAD Menu Lisp'),
    'mpp': ('Documents', 'Microsoft Project'),
    'msg': ('Documents', 'Outlook Message'),
    'mtlx': ('CAD', 'MaterialX'),
    'mus': ('Media', 'Music'),
    'npy': ('Data', 'NumPy'),
    'npz': ('Data', 'NumPy'),
    'nwc': ('CAD', 'Navisworks'),
    'nwd': ('CAD', 'Navisworks'),
    'nwf': ('CAD', 'Navisworks'),
    'ocio': ('Config', 'Color Management'),
    'old': ('Miscellaneous', 'Backup'),
    'osl': ('Code', 'Open Shading Language'),
    'oso': ('Code', 'OSL Compiled'),
    'p7s': ('System', 'Digital Signature'),
    'pak': ('Archives', 'Package'),
    'pc3': ('CAD', 'AutoCAD Plotter Config'),
    'pcp': ('CAD', 'AutoCAD Plotter Config'),
    'pdb': ('Data', 'Database'),
    'pem': ('System', 'Certificate'),
    'pep8': ('Config', 'Python Style'),
    'pickle': ('Data', 'Python Pickle'),
    'pkl': ('Data', 'Python Pickle'),
    'pkpass': ('Miscellaneous', 'Apple Wallet'),
    'pot': ('Documents', 'PowerPoint Template'),
    'potx': ('Documents', 'PowerPoint Template'),
    'pov': ('CAD', 'POV-Ray'),
    'ppsx': ('Documents', 'PowerPoint Show'),
    'pth': ('Config', 'Python Path'),
    'ptx': ('Code', 'CUDA PTX'),
    'pxd': ('Code', 'Cython'),
    'pyc': ('Code', 'Python Bytecode'),
    'pyd': ('Code', 'Python DLL'),
    'pyf': ('Code', 'Fortran Wrapper'),
    'pyi': ('Code', 'Python Stub'),
    'pyx': ('Code', 'Cython Source'),
    'qry': ('Data', 'Query'),
    'rdf': ('Data', 'Resource Description'),
    'rev': ('CAD', 'Revit'),
    'rfa': ('CAD', 'Revit Family'),
    'rst': ('Documents', 'reStructuredText'),
    'rvt': ('CAD', 'Revit Project'),
    'sat': ('CAD', 'ACIS SAT'),
    'scdoc': ('Documents', 'Scientific Document'),
    'scr': ('System', 'Screen Saver'),
    'sha256': ('Miscellaneous', 'Hash'),
    'shp': ('Data', 'Shapefile'),
    'shx': ('Data', 'Shapefile Index'),
    'skp': ('CAD', 'SketchUp'),
    'sl': ('Code', 'Scheme'),
    'slb': ('CAD', 'AutoCAD Slide Library'),
    'sld': ('CAD', 'SolidWorks Drawing'),
    'sldasm': ('CAD', 'SolidWorks Assembly'),
    'sldprt': ('CAD', 'SolidWorks Part'),
    'slnk': ('System', 'Shortcut'),
    'sph': ('Miscellaneous', 'Sphere'),
    'spi1d': ('Images', 'Lookup Table'),
    'spi3d': ('Images', 'Lookup Table'),
    'spimtx': ('Images', 'Lookup Table'),
    'styxml': ('Miscellaneous', 'Style XML'),
    'sxk': ('Miscellaneous', 'Unknown'),
    'template': ('Config', 'Template'),
    'thmx': ('Documents', 'Office Theme'),
    'tmpl': ('Config', 'Template'),
    'tr': ('Miscellaneous', 'Trace'),
    'ttf': ('System', 'TrueType Font'),
    'tus': ('Miscellaneous', 'Unknown'),
    'typed': ('Miscellaneous', 'Typed'),
    'url': ('System', 'Internet Shortcut'),
    'usda': ('CAD', 'Universal Scene Description'),
    'v': ('Code', 'Verilog'),
    'vob': ('Media', 'DVD Video'),
    'vxp': ('Miscellaneous', 'Unknown'),
    'wbk': ('Documents', 'Word Backup'),
    'whl': ('Archives', 'Python Wheel'),
    'wmf': ('Images', 'Windows Metafile'),
    'woff2': ('System', 'Web Font'),
    'x_t': ('CAD', 'Parasolid'),
    'xdb': ('Data', 'XML Database'),
    'xlf': ('Documents', 'Localization'),
    'xlt': ('Documents', 'Excel Template'),
    'xltx': ('Documents', 'Excel Template'),
    'xsl': ('Code', 'XSL'),
    'xslt': ('Code', 'XSLT'),
    'zst': ('Archives', 'Zstandard'),
}

# Add only if not already present
for ext, (cat, sub) in new_mappings.items():
    if ext not in mapping:
        mapping[ext] = {'category': cat, 'subcategory': sub}

# Sort mapping alphabetically for readability
sorted_mapping = dict(sorted(mapping.items()))

data['mapping'] = sorted_mapping

# Write back
with open('config/categories.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print(f"Added {len(new_mappings)} new extensions.")