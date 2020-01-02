# agrtoolset

Introduction:

The add-on "agrtoolset" is a temporary set of tools used for a quicker workflow with .agr files. It is based upon Dardhandrob's Source-AGR-Import-Export-FBX (AIOX) add-on for blender 2.8, but it has been changed so heavily i decided to put it up on GitHub.

Features:

- Merging recordInvisible 1 animation tracks
- Custom .fbx exporter

Installation:

1. Clone repo or download as .zip

2. Extract .zip into a folder

3. In Blender 2.8x go to Edit > Preferences > Add-ons > Install..., and choose the export.py file.

Usage:
- Name your players sequentially with this syntax:

  - player(number)_movement/ragdoll
  - eg. player0_movement
  
- Press shift + comma (,) on your keyboard to bring up the pie menu
- "Merge Anims" merges the previously named ragdoll and death anims
- "AGR (.fbx)" exports each player model with the filename for each .fbx using the name of each skeleton, and then replaces the actual skeleton name to a user set name.
