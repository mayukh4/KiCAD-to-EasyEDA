# KiCad to EasyEDA Footprint Converter

A Python script to convert KiCad footprint files (.kicad_mod) to EasyEDA JSON format for seamless PCB design workflow migration.

## Overview

This converter enables PCB designers to migrate their custom KiCad footprints to EasyEDA Standard Edition. The script automatically handles coordinate conversion, layer mapping, pad types, and origin positioning to create fully compatible EasyEDA footprint files.

## Features

- Converts KiCad .kicad_mod footprint files to EasyEDA JSON format
- Automatic unit conversion from millimeters to EasyEDA units (10 mil increments)
- Supports multiple pad types: through-hole, SMD, and connect pads
- Handles various pad shapes: circle, rectangle, and oval
- Preserves drill hole information for mounting holes and through-hole components
- Converts reference circles to documentation layer
- Automatic origin point calculation and positioning
- Complete layer mapping between KiCad and EasyEDA
- Validates output format to prevent import errors

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses only Python standard library)

## Installation

### Method 1: Direct Download

Download the script directly:

```bash
wget https://raw.githubusercontent.com/yourusername/kicad-to-easyeda-converter/main/kicad_to_easyeda_footprint_converter.py
```

Or clone the repository:

```bash
git clone https://github.com/yourusername/kicad-to-easyeda-converter.git
cd kicad-to-easyeda-converter
```

### Method 2: Manual Download

1. Download `kicad_to_easyeda_footprint_converter.py` from this repository
2. Save it to your working directory
3. Ensure it has execute permissions (Linux/Mac): `chmod +x kicad_to_easyeda_footprint_converter.py`

## Usage

### Basic Usage

Convert a single KiCad footprint file:

```bash
python kicad_to_easyeda_footprint_converter.py input_footprint.kicad_mod
```

The script will automatically create an output file named `input_footprint_easyeda.json` in the same directory.

### Specify Output File

To specify a custom output filename:

```bash
python kicad_to_easyeda_footprint_converter.py input_footprint.kicad_mod output_footprint.json
```

### Example

Converting a mounting hole footprint:

```bash
python kicad_to_easyeda_footprint_converter.py MountingHole_2.5mm_Pad_TopBottom.kicad_mod
```

Output:
```
Parsing KiCad footprint: MountingHole_2.5mm_Pad_TopBottom.kicad_mod
Found: 3 pads, 2 circles
  Pad 1: num=1, type=thru_hole, shape=circle, drill=2.5mm
  Pad 2: num=1, type=connect, shape=circle, drill=0.0mm
  Pad 3: num=1, type=connect, shape=circle, drill=0.0mm
Converting to EasyEDA format...
Generated 5 shape elements
Origin set to: (4000, 3000)
Successfully converted to: MountingHole_2.5mm_Pad_TopBottom_easyeda.json
```

## Importing to EasyEDA

After converting your footprint:

1. Open EasyEDA Standard Edition (web or desktop version)
2. Go to **File > Open > EasyEDA...**
3. Select your generated JSON file
4. The footprint will load in the editor
5. Save the footprint to your personal library: **File > Save As**
6. The footprint is now available in your library for use in PCB designs

## Supported KiCad Features

### Pad Types
- Through-hole pads with drill holes
- SMD pads on top and bottom layers
- Connect pads (mounting pads without electrical connection)
- Multi-layer pads

### Pad Shapes
- Circle (ELLIPSE in EasyEDA)
- Rectangle (RECT in EasyEDA)
- Oval (OVAL in EasyEDA)

### Layers
- Top Copper Layer (F.Cu)
- Bottom Copper Layer (B.Cu)
- Multi-Layer (*.Cu)
- Top Silkscreen (F.SilkS)
- Comments/User layer (Cmts.User) - converted to Document layer

### Graphics
- Footprint reference circles
- Drill holes with accurate dimensions
- Pad numbering preservation

## Technical Details

### Coordinate System

KiCad uses millimeters as the primary unit, while EasyEDA stores dimensions in units of 10 mils (0.01 inches). The converter automatically performs this transformation:

```
EasyEDA units = millimeters × 39.3701 / 10
```

### Layer Mapping

| KiCad Layer | EasyEDA Layer ID | EasyEDA Layer Name |
|-------------|------------------|-------------------|
| F.Cu        | 1                | TopLayer          |
| B.Cu        | 2                | BottomLayer       |
| *.Cu        | 11               | Multi-Layer       |
| F.SilkS     | 3                | TopSilkLayer      |
| Cmts.User   | 12               | Document          |

### Origin Point Calculation

The script automatically calculates the footprint's bounding box and sets the origin point at its center. This ensures:
- Proper rotation behavior when placing the footprint
- Compatibility with SMT pick-and-place machines
- Alignment with EasyEDA's origin requirements

## Limitations

Current limitations of the converter:

- Text and reference designators are not converted (can be added manually in EasyEDA)
- Custom pad shapes beyond circle, rectangle, and oval are not supported
- Footprint attributes and 3D models are not transferred
- Courtyard layers are not converted
- Complex graphics (arcs, polygons) on silkscreen are not supported

These elements can be added manually in the EasyEDA editor after import.

## Troubleshooting

### "decompress failed" Error

This error indicates an invalid JSON structure. Update to the latest version of the script, which generates properly formatted EasyEDA JSON.

### Blank Footprint After Import

Ensure you're using the latest version. Earlier versions had issues with the LIB wrapper format that has been resolved.

### "Origin not in graphics" Error When Saving

The latest version automatically calculates and sets the origin point. If you encounter this error with an older script version, update to the latest release.

### Pads Missing or Incorrect Size

Verify that your KiCad footprint uses standard pad definitions. Complex or custom pad definitions may require manual adjustment in EasyEDA.

## Use Cases

This converter is ideal for:

- Migrating existing KiCad projects to EasyEDA
- Sharing footprints between KiCad and EasyEDA users
- Creating EasyEDA libraries from KiCad footprint collections
- Prototyping in KiCad and manufacturing with EasyEDA/JLCPCB integration
- Converting legacy footprints for cloud-based PCB design
- Educational purposes when teaching both EDA tools

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug fixes
- New feature implementations
- Documentation improvements
- Test cases and examples
- Support for additional KiCad footprint features

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Related Projects

- KiCad EDA: https://www.kicad.org/
- EasyEDA Standard Edition: https://easyeda.com/
- EasyEDA to KiCad Converter: https://github.com/yaybee/easyeda2kicad6

## Keywords

KiCad to EasyEDA converter, footprint converter, PCB design migration, KiCad footprint export, EasyEDA JSON import, PCB library conversion, electronic design automation, KiCad .kicad_mod converter, EasyEDA Standard Edition, PCB footprint format conversion, open source PCB tools, hardware design workflow

## Changelog

### Version 1.0.0
- Initial release
- Support for basic pad types and shapes
- Automatic coordinate conversion
- Origin point calculation
- Layer mapping implementation
- Support for through-hole and SMD pads
- Documentation layer conversion for reference graphics

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Refer to EasyEDA documentation: https://docs.easyeda.com/
- Refer to KiCad documentation: https://docs.kicad.org/

## Author

Created to facilitate seamless workflow between KiCad and EasyEDA for PCB designers worldwide.

## Acknowledgments

- KiCad development team for excellent open-source EDA software
- EasyEDA team for providing documentation on their JSON format
- PCB design community for feedback and testing
