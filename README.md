# Cartoon Short

Production tools for the "Cartoon Short" style (analysis: `ANALYSIS.md`, brief: `PROMPT.md`).

## Install (Linux, no graphics card needed)
```bash
sudo apt-get install -y ffmpeg libegl1 libegl-mesa0 libgl1-mesa-dri
python3 -m venv /opt/cartoon-venv
/opt/cartoon-venv/bin/pip install bpy==5.3.0 pillow numpy fonttools
```
Blender is used as a Python module (`bpy`), Eevee renderer, software OpenGL (Mesa).

## Make the still
```bash
python3 scripts/build/fetch_polyhaven.py modular_urban_apartments_facade modular_fire_escape street_lamp_01 metal_trash_can fire_hydrant rollershutter_door exterior_aircon_unit utility_box_01 concrete_road_barrier modular_metal_gutter water_manhole_cover cardboard_box_01 asphalt_02 concrete_pavement_02
python3 scripts/build/fetch_polyhaven.py --res 2k industrial_sunset_02_puresky
/opt/cartoon-venv/bin/python scripts/build/character.py assets/characters
/opt/cartoon-venv/bin/python scripts/build/scene_alley.py renders/still_raw.png 1.0 24
python3 scripts/build/finish.py still renders/still_raw.png renders/still_01.png "Nobody"
/opt/cartoon-venv/bin/python scripts/build/measure.py renders/still_01.png
```

## Files
- `scripts/build/character.py` - the flat character (drawn, never rendered), one PNG per expression
- `scripts/build/scene_alley.py` - the alley set from Poly Haven CC0 assets, light, camera, render
- `scripts/build/finish.py` - bloom, vignette, burned-in caption (ASS + libass)
- `scripts/build/measure.py` - palette and luma measured like ANALYSIS.md section 4
- `CREDITS.md` - every asset that is not ours; `assets/fonts/` - Montserrat Black (OFL)
