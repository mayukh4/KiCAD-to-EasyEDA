#!/usr/bin/env python3
"""
KiCad to EasyEDA Footprint Converter
Converts KiCad .kicad_mod files to EasyEDA JSON format
"""

import re
import json
import sys
from typing import Dict, List, Tuple, Any

def mm_to_easyeda(mm: float) -> float:
    """Convert millimeters to EasyEDA units (10 mil increments)
    1 mm = 39.3701 mil, EasyEDA units = mil/10
    """
    return round(mm * 39.3701 / 10, 2)

def parse_kicad_footprint(kicad_content: str) -> Dict[str, Any]:
    """Parse KiCad footprint file and extract relevant information"""
    
    footprint_data = {
        'name': '',
        'description': '',
        'pads': [],
        'circles': [],
        'texts': []
    }
    
    # Extract footprint name
    name_match = re.search(r'footprint\s+"([^"]+)"', kicad_content)
    if name_match:
        footprint_data['name'] = name_match.group(1)
    
    # Extract description
    desc_match = re.search(r'\(descr\s+"([^"]+)"\)', kicad_content)
    if desc_match:
        footprint_data['description'] = desc_match.group(1)
    
    # Extract pads - handle multi-line pad definitions
    pad_pattern = r'\(pad\s+"([^"]+)"\s+(\w+)\s+(\w+)\s*\n?\s*\(at\s+([-\d.]+)\s+([-\d.]+)[^)]*\)\s*\n?\s*\(size\s+([-\d.]+)\s+([-\d.]+)\)\s*\n?\s*\(drill\s+([-\d.]+)\)'
    for match in re.finditer(pad_pattern, kicad_content, re.MULTILINE):
        pad = {
            'number': match.group(1),
            'type': match.group(2),  # thru_hole, smd, connect
            'shape': match.group(3),  # circle, rect, oval
            'x': float(match.group(4)),
            'y': float(match.group(5)),
            'width': float(match.group(6)),
            'height': float(match.group(7)),
            'drill': float(match.group(8))
        }
        
        # Check for layers
        if 'F.Cu' in kicad_content[match.start():match.end()+200]:
            pad['layers'] = ['F.Cu']
        elif 'B.Cu' in kicad_content[match.start():match.end()+200]:
            pad['layers'] = ['B.Cu']
        elif '*.Cu' in kicad_content[match.start():match.end()+200]:
            pad['layers'] = ['*.Cu']
        
        footprint_data['pads'].append(pad)
    
    # Extract circles (for reference/documentation)
    circle_pattern = r'\(fp_circle\s*\n?\s*\(center\s+([-\d.]+)\s+([-\d.]+)\)\s*\n?\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)'
    for match in re.finditer(circle_pattern, kicad_content, re.MULTILINE):
        cx = float(match.group(1))
        cy = float(match.group(2))
        ex = float(match.group(3))
        ey = float(match.group(4))
        radius = ((ex - cx)**2 + (ey - cy)**2)**0.5
        
        circle = {
            'cx': cx,
            'cy': cy,
            'radius': radius,
            'layer': 'Cmts.User'  # Default, could be extracted
        }
        footprint_data['circles'].append(circle)
    
    return footprint_data

def convert_to_easyeda(footprint_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert parsed KiCad footprint data to EasyEDA JSON format"""
    
    # EasyEDA layer mapping
    layer_map = {
        'F.Cu': '1',      # Top Layer
        'B.Cu': '2',      # Bottom Layer
        '*.Cu': '11',     # Multi-Layer (through hole)
        'F.SilkS': '3',   # Top Silk
        'Cmts.User': '12' # Document layer
    }
    
    shapes = []
    gge_counter = 1
    
    # Track min/max coordinates to calculate bounding box
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    
    # Convert pads
    for pad in footprint_data['pads']:
        x = mm_to_easyeda(pad['x'])
        y = mm_to_easyeda(pad['y'])
        width = mm_to_easyeda(pad['width'])
        height = mm_to_easyeda(pad['height'])
        drill = mm_to_easyeda(pad['drill'])
        
        # Update bounding box
        min_x = min(min_x, x - width/2)
        max_x = max(max_x, x + width/2)
        min_y = min(min_y, y - height/2)
        max_y = max(max_y, y + height/2)
        
        # Determine pad shape
        if pad['shape'] == 'circle':
            shape_type = 'ELLIPSE'
        elif pad['shape'] == 'rect':
            shape_type = 'RECT'
        elif pad['shape'] == 'oval':
            shape_type = 'OVAL'
        else:
            shape_type = 'ELLIPSE'
        
        # Determine layer
        if pad['type'] == 'thru_hole':
            layer_id = '11'  # Multi-layer
            plated = 'Y'
        elif pad['type'] == 'connect':
            # SMD pads on specific layers
            if 'F.Cu' in pad.get('layers', []):
                layer_id = '1'
            elif 'B.Cu' in pad.get('layers', []):
                layer_id = '2'
            else:
                layer_id = '1'
            plated = 'N'
            drill = 0  # No drill for SMD
        else:
            layer_id = '11'
            plated = 'Y'
        
        # For mounting holes (drill only), we can use HOLE type or PAD with drill
        if drill > 0 and pad['type'] == 'thru_hole':
            # Create PAD with hole
            # PAD format: PAD~shape~x~y~width~height~layer~net~number~holeradius~points~rotation~id~holelength~holepoints~plated~locked
            pad_str = f"PAD~{shape_type}~{x}~{y}~{width}~{height}~{layer_id}~~{pad['number']}~{drill/2}~~0~gge{gge_counter}~~~{plated}~0"
            shapes.append(pad_str)
            gge_counter += 1
        
        # Add separate SMD pads if this is a connect type
        if pad['type'] == 'connect':
            for layer_name in pad.get('layers', []):
                if layer_name in ['F.Cu', 'B.Cu']:
                    layer_id = layer_map.get(layer_name, '1')
                    pad_str = f"PAD~{shape_type}~{x}~{y}~{width}~{height}~{layer_id}~~{pad['number']}~0~~0~gge{gge_counter}~~~N~0"
                    shapes.append(pad_str)
                    gge_counter += 1
    
    # Convert circles to documentation layer
    for circle in footprint_data['circles']:
        cx = mm_to_easyeda(circle['cx'])
        cy = mm_to_easyeda(circle['cy'])
        r = mm_to_easyeda(circle['radius'])
        layer_id = '12'  # Document layer
        stroke_width = 0.15 * 3.937  # Convert 0.15mm to mil/10
        
        # Update bounding box
        min_x = min(min_x, cx - r)
        max_x = max(max_x, cx + r)
        min_y = min(min_y, cy - r)
        max_y = max(max_y, cy + r)
        
        # CIRCLE format: CIRCLE~cx~cy~r~strokewidth~layerid~id~locked
        circle_str = f"CIRCLE~{cx}~{cy}~{r}~{stroke_width}~{layer_id}~gge{gge_counter}~0"
        shapes.append(circle_str)
        gge_counter += 1
    
    # Calculate center point for origin
    # If no shapes were found, default to canvas center
    if min_x == float('inf'):
        origin_x = 4000
        origin_y = 3000
    else:
        # Center of bounding box, with reasonable canvas positioning
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        # Place origin at the footprint center, offsetting by canvas position
        origin_x = 4000 + center_x
        origin_y = 3000 + center_y
    
    # Create complete EasyEDA JSON structure with proper format
    easyeda_json = {
        "head": {
            "docType": "4",
            "editorVersion": "6.5.0",
            "newgId": True,
            "c_para": {
                "package": footprint_data['name'],
                "pre": "FP?",
                "Contributor": "KiCad Converter"
            },
            "hasIdFlag": True,
            "x": int(origin_x),
            "y": int(origin_y)
        },
        "canvas": f"CA~2000~2000~#000000~yes~#FFFFFF~10~1000~1000~line~0.5~mil~1~45~visible~0.5~{int(origin_x)}~{int(origin_y)}",
        "shape": shapes,  # Direct array of shape strings, no LIB wrapper for footprint files
        "layers": [
            "1~TopLayer~#FF0000~true~true~true~",
            "2~BottomLayer~#0000FF~true~false~true~",
            "3~TopSilkLayer~#FFCC00~true~false~true~",
            "4~BottomSilkLayer~#66CC33~true~false~true~",
            "5~TopPasteMaskLayer~#808080~true~false~true~",
            "6~BottomPasteMaskLayer~#800000~true~false~true~",
            "7~TopSolderMaskLayer~#800080~true~false~true~0.3",
            "8~BottomSolderMaskLayer~#AA00FF~true~false~true~0.3",
            "9~Ratlines~#6464FF~false~false~true~",
            "10~BoardOutLine~#FF00FF~true~true~true~",
            "11~Multi-Layer~#C0C0C0~true~false~true~",
            "12~Document~#FFFFFF~true~false~true~",
            "13~TopAssembly~#33CC99~false~false~false~",
            "14~BottomAssembly~#5555FF~false~false~false~",
            "15~Mechanical~#33CC99~false~false~false~"
        ],
        "objects": [
            "All~true~false",
            "Component~true~true",
            "Prefix~true~true",
            "Name~true~false",
            "Track~true~true",
            "Pad~true~true",
            "Via~true~true",
            "Hole~true~true",
            "Copper_Area~true~true",
            "Circle~true~true",
            "Arc~true~true",
            "Solid_Region~true~true",
            "Text~true~true",
            "Dimension~true~true",
            "Rect~true~true"
        ]
    }
    
    return easyeda_json

def main():
    if len(sys.argv) < 2:
        print("Usage: python kicad_to_easyeda.py <input.kicad_mod> [output.json]")
        print("\nExample: python kicad_to_easyeda.py MountingHole_2.5mm_Pad_TopBottom.kicad_mod")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.kicad_mod', '_easyeda.json')
    
    # Read KiCad file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            kicad_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    # Parse and convert
    print(f"Parsing KiCad footprint: {input_file}")
    footprint_data = parse_kicad_footprint(kicad_content)
    print(f"Found: {len(footprint_data['pads'])} pads, {len(footprint_data['circles'])} circles")
    
    # Debug: show pad details
    for i, pad in enumerate(footprint_data['pads']):
        print(f"  Pad {i+1}: num={pad['number']}, type={pad['type']}, shape={pad['shape']}, drill={pad['drill']}mm")
    
    print("Converting to EasyEDA format...")
    easyeda_data = convert_to_easyeda(footprint_data)
    
    print(f"Generated {len(easyeda_data['shape'])} shape elements")
    print(f"Origin set to: ({easyeda_data['head']['x']}, {easyeda_data['head']['y']})")
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(easyeda_data, f, indent=2)
    
    print(f"Successfully converted to: {output_file}")
    print(f"\nTo import in EasyEDA:")
    print("1. Go to File > Open > EasyEDA...")
    print("2. Select the generated JSON file")
    print("3. The footprint will be imported into your library")

if __name__ == "__main__":
    main()
