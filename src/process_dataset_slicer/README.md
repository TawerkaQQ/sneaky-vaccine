# Dataset Generation and Visualization Module

This module is designed for generating and visualizing 2D image datasets with landmark annotations from 3D CT head scans with markup data. It consists of three scripts:

---

## Scripts

### process_dataset.py

- **Purpose:**
  Processes all patient markup folders, generates 2D images and corresponding annotation files, and saves them in a standardized dataset structure.
- **Usage:**
  Run inside 3D Slicer. Edit the `data_path` and `dataset_path` variables at the top of the script to match your data locations.

### visualize_markup.py

- **Purpose:**
  Quickly visualize all images and their landmark points for any patient in the dataset. Useful for fast quality control and dataset inspection.
- **Usage:**
  Run with standard Python. Edit the `dataset_path` variable to point to your dataset directory.

### visualize_sequence.py

- **Purpose:**
  Step-by-step visualization of the landmark sequence on each image. Useful for verifying the order and placement of keypoints.
- **Usage:**
  Run with standard Python. Edit the `images_path`, `labels_path`, and `output_path` variables as needed.

---

## Annotation Format

Each `.txt` annotation file contains:

```
<class-index> <x> <y> <width> <height>
<px1> <py1>
<px2> <py2>
<px3> <py3>
<px4> <py4>
```

- All coordinates are normalized (0-1, float).
- The keypoint order is: Left Infraorbital, Left Mental, Right Infraorbital, Right Mental.

---

## Notes

- For `process_dataset.py`, use 3D Slicer.
- For visualization scripts, use standard Python with OpenCV installed.
- Check and edit paths in the scripts before running.
