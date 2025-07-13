import slicer
import math
import os
import time
import json
import numpy as np

try:
    from dotenv import load_dotenv
except ImportError:
    import sys
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv


class DatasetProcessor:
    """
    Processes 3D CT head scans with markup data to generate 2D image datasets for machine learning.

    This class handles the complete pipeline from loading 3D scenes to generating
    annotated 2D images with corresponding landmark coordinates.
    """

    def __init__(
        self,
        data_path,
        dataset_path,
        distance=450,
        pitch_range=(-15.0, 15.0),
        pitch_num=10,
        yaw_range=(-10.0, 10.0),
        yaw_num=10,
    ):
        """
        Initialize the dataset processor.

        Args:
            data_path (str): Path to the root data directory containing markup folders
            dataset_path (str): Path where the processed dataset will be saved
            distance (float): Camera distance from the center of the 3D scene
            pitch_range (tuple): Range of pitch angles in degrees (min, max)
            pitch_num (int): Number of pitch angle samples
            yaw_range (tuple): Range of yaw angles in degrees (min, max)
            yaw_num (int): Number of yaw angle samples
        """
        self.data_path = data_path
        self.dataset_path = dataset_path
        self.distance = distance
        self.pitch_range = pitch_range
        self.pitch_num = pitch_num
        self.yaw_range = yaw_range
        self.yaw_num = yaw_num

        # Create dataset directory if it doesn't exist
        if not os.path.exists(self.dataset_path):
            os.makedirs(self.dataset_path)

    def find_markup_folders(self):
        """
        Find all markup folders in the data directory.

        Returns:
            list: List of folder names that start with 'markups_'
        """
        markup_folders = []
        for item in os.listdir(self.data_path):
            item_path = os.path.join(self.data_path, item)
            if os.path.isdir(item_path) and item.startswith("markups_"):
                markup_folders.append(item)
        return markup_folders

    def get_patient_name(self, markup_folder):
        """
        Extract the original patient name from markup folder name.

        Args:
            markup_folder (str): Folder name with 'markups_' prefix

        Returns:
            str: Patient name without the 'markups_' prefix
        """
        if markup_folder.startswith("markups_"):
            return markup_folder[8:]  # Remove "markups_" prefix
        return markup_folder

    def hide_all_markups(self):
        """Hide all markup nodes in the 3D scene."""
        scene = slicer.mrmlScene
        for i in range(scene.GetNumberOfNodesByClass("vtkMRMLMarkupsNode")):
            markupsNode = scene.GetNthNodeByClass(i, "vtkMRMLMarkupsNode")
            markupsNode.SetDisplayVisibility(0)

    def hide_cube_and_axis(self):
        """Hide 3D cube and axis labels in the 3D view."""
        view = slicer.app.layoutManager().threeDWidget(0).threeDView()
        viewNode = view.mrmlViewNode()
        viewNode.SetBoxVisible(0)
        viewNode.SetAxisLabelsVisible(0)
        view.forceRender()

    def center_camera(self):
        """Center the camera at the specified distance from the scene origin."""
        view = slicer.app.layoutManager().threeDWidget(0).threeDView()
        cameraNode = view.cameraNode()
        cameraNode.SetPosition(0, self.distance, 0)
        cameraNode.SetFocalPoint(0, 0, 0)
        cameraNode.SetViewUp(0, 0, 1)
        cameraNode.Modified()

    def set_camera_pitch(self, pitch_deg):
        """
        Set camera position for a given pitch angle.

        Args:
            pitch_deg (float): Pitch angle in degrees
        """
        view = slicer.app.layoutManager().threeDWidget(0).threeDView()
        cameraNode = view.cameraNode()
        pitch = math.radians(pitch_deg)
        x = 0
        y = self.distance * math.cos(pitch)
        z = self.distance * math.sin(pitch)
        cameraNode.SetPosition(x, y, z)
        cameraNode.SetFocalPoint(0, 0, 0)
        cameraNode.SetViewUp(0, 0, 1)
        cameraNode.Modified()

    def set_camera_yaw(self, yaw_deg):
        """
        Set camera position for a given yaw angle.

        Args:
            yaw_deg (float): Yaw angle in degrees
        """
        view = slicer.app.layoutManager().threeDWidget(0).threeDView()
        cameraNode = view.cameraNode()
        yaw = math.radians(yaw_deg)
        x = self.distance * math.sin(yaw)
        y = self.distance * math.cos(yaw)
        z = 0
        cameraNode.SetPosition(x, y, z)
        cameraNode.SetFocalPoint(0, 0, 0)
        cameraNode.SetViewUp(0, 0, 1)
        cameraNode.Modified()

    def extract_soft_tissue_points(self, markup_folder):
        """
        Extract 3D coordinates of soft tissue points from markup JSON files.

        Args:
            markup_folder (str): Name of the markup folder

        Returns:
            list: List of 3D point coordinates on soft tissues
        """
        markup_path = os.path.join(self.data_path, markup_folder)
        json_files = [
            f
            for f in os.listdir(markup_path)
            if f.endswith(".json") and f.startswith("L_")
        ]
        soft_tissue_points = []

        for json_file in json_files:
            json_path = os.path.join(markup_path, json_file)
            with open(json_path, "r", encoding="utf-8") as f:
                markup_data = json.load(f)

            for markup in markup_data.get("markups", []):
                if (
                    markup.get("type") == "Line"
                    and len(markup.get("controlPoints", [])) >= 2
                ):
                    # Extract the second point (point2) - soft tissue point
                    soft_tissue_point = markup["controlPoints"][1]["position"]
                    soft_tissue_points.append(soft_tissue_point)

        print(f"Extracted {len(soft_tissue_points)} soft tissue points")
        return soft_tissue_points

    def project_3d_to_2d(self, point_3d, camera_info):
        """
        Project 3D point to 2D coordinates using LPS coordinate system correction.

        Args:
            point_3d (list): 3D point coordinates [x, y, z]
            camera_info (dict): Camera parameters including position, focal_point, etc.

        Returns:
            list or None: 2D pixel coordinates [x, y] or None if point is behind camera
        """
        # LPS: Left-Posterior-Superior -> RAS: Right-Anterior-Superior
        point_ras = np.array(point_3d)
        point_ras[0] = -point_ras[0]  # Left -> Right
        point_ras[1] = -point_ras[1]  # Posterior -> Anterior

        # Extract camera parameters
        camera_pos = np.array(camera_info["position"])
        focal_point = np.array(camera_info["focal_point"])
        view_up = np.array(camera_info["view_up"])
        fov = camera_info["fov"]
        image_width, image_height = camera_info["image_size"]

        # Calculate camera vectors
        forward = focal_point - camera_pos
        forward = forward / np.linalg.norm(forward)

        right = np.cross(forward, view_up)
        right = right / np.linalg.norm(right)

        up = np.cross(right, forward)

        # Transform point to camera coordinates
        point_cam = point_ras - camera_pos
        x_cam = np.dot(point_cam, right)
        y_cam = np.dot(point_cam, up)
        z_cam = np.dot(point_cam, forward)

        # Check if point is behind camera
        if z_cam <= 0:
            return None

        # Perspective projection
        fov_rad = math.radians(fov)
        aspect_ratio = image_width / image_height

        # Normalized coordinates (-1 to 1)
        x_norm = (x_cam / z_cam) / math.tan(fov_rad / 2) / aspect_ratio
        y_norm = (y_cam / z_cam) / math.tan(fov_rad / 2)

        # Convert to pixel coordinates
        x_pixel = (x_norm + 1) * image_width / 2
        y_pixel = (1 - y_norm) * image_height / 2  # Invert Y axis

        return [int(x_pixel), int(y_pixel)]

    def arrange_points_in_sequence(self, points):
        """
        Arrange points in the order:
        Left Mental, Left Infraorbital, Right Mental, Right Infraorbital
        (Ментальные — снизу, инфраорбитальные — сверху)
        Args:
            points (list): List of 3D points
        Returns:
            list: Points in the correct sequence
        """
        if len(points) < 4:
            return points
        points = points[:4]
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        x_median = np.median(x_coords)
        y_median = np.median(y_coords)
        left_lower = []  # Left Mental (снизу)
        left_upper = []  # Left Infraorbital (сверху)
        right_lower = []  # Right Mental (снизу)
        right_upper = []  # Right Infraorbital (сверху)
        for i, point in enumerate(points):
            x, y = point[0], point[1]
            if x < x_median and y > y_median:
                left_lower.append(point)  # Левое ментальное (снизу)
            elif x < x_median and y <= y_median:
                left_upper.append(point)  # Левое инфраорбитальное (сверху)
            elif x >= x_median and y > y_median:
                right_lower.append(point)  # Правое ментальное (снизу)
            else:  # x >= x_median and y <= y_median
                right_upper.append(point)  # Правое инфраорбитальное (сверху)
        sequence = []
        if left_upper:
            sequence.append(left_upper[0])  # 1. Левое инфраорбитальное
        if left_lower:
            sequence.append(left_lower[0])  # 2. Левое ментальное
        if right_upper:
            sequence.append(right_upper[0])  # 3. Правое инфраорбитальное
        if right_lower:
            sequence.append(right_lower[0])  # 4. Правое ментальное
        # Если не все квадранты заполнены, добавляем оставшиеся
        for group in [left_upper, left_lower, right_upper, right_lower]:
            for p in group[1:]:
                sequence.append(p)
        return sequence

    def process_markup_folder(self, markup_folder):
        """
        Process a single markup folder to generate images and annotations.

        Args:
            markup_folder (str): Name of the markup folder to process
        """
        print(f"\nProcessing {markup_folder}...")

        markup_path = os.path.join(self.data_path, markup_folder)

        # Get original patient name
        patient_name = self.get_patient_name(markup_folder)

        # Create dataset directory structure with original patient name
        dataset_patient_path = os.path.join(self.dataset_path, patient_name)
        images_path = os.path.join(dataset_patient_path, "images")
        labels_path = os.path.join(dataset_patient_path, "labels")

        os.makedirs(images_path, exist_ok=True)
        os.makedirs(labels_path, exist_ok=True)

        print(f"Creating directories for patient: {patient_name}")

        # Find .mrml file
        mrml_files = [f for f in os.listdir(markup_path) if f.endswith(".mrml")]
        if not mrml_files:
            print(f"❌ No .mrml file found in {markup_folder}")
            return

        mrml_path = os.path.join(markup_path, mrml_files[0])

        # Load scene
        slicer.mrmlScene.Clear()
        slicer.util.loadScene(mrml_path)

        # Extract soft tissue points
        soft_tissue_points = self.extract_soft_tissue_points(markup_folder)

        # Center camera
        self.center_camera()

        # Hide markups and cube
        self.hide_all_markups()
        self.hide_cube_and_axis()
        self.center_camera()

        # Pitch series
        for i in range(self.pitch_num):
            pitch = self.pitch_range[0] + (
                self.pitch_range[1] - self.pitch_range[0]
            ) * i / (self.pitch_num - 1)
            self.set_camera_pitch(pitch)
            slicer.app.processEvents()
            time.sleep(0.1)

            view = slicer.app.layoutManager().threeDWidget(0).threeDView()
            view.forceRender()
            cameraNode = view.cameraNode()

            # Save camera parameters
            camera_info = {
                "position": cameraNode.GetPosition(),
                "focal_point": cameraNode.GetFocalPoint(),
                "view_up": cameraNode.GetViewUp(),
                "fov": cameraNode.GetViewAngle(),
                "image_size": (
                    view.width() if callable(view.width) else view.width,
                    view.height() if callable(view.height) else view.height,
                ),
            }

            # Save image
            image_filename = f"image_pitch{i:02d}.png"
            image_path = os.path.join(images_path, image_filename)
            view.grab().save(image_path)

            # --- PITCH SERIES ---
            # Arrange points in correct sequence
            sequenced_points = self.arrange_points_in_sequence(soft_tissue_points)
            # Project points and save annotations
            projected_points = []
            for point_3d in sequenced_points:
                point_2d = self.project_3d_to_2d(point_3d, camera_info)
                if point_2d is not None:
                    projected_points.append(point_2d)
            # Save annotations in YOLO format
            label_filename = f"image_pitch{i:02d}.txt"
            label_path = os.path.join(labels_path, label_filename)
            with open(label_path, "w", encoding="utf-8") as f:
                if projected_points:
                    x_coords = [p[0] for p in projected_points]
                    y_coords = [p[1] for p in projected_points]
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    center_x = (x_min + x_max) / 2
                    center_y = (y_min + y_max) / 2
                    width = x_max - x_min
                    height = y_max - y_min
                    image_width, image_height = camera_info["image_size"]
                    center_x_norm = center_x / image_width
                    center_y_norm = center_y / image_height
                    width_norm = width / image_width
                    height_norm = height / image_height
                    f.write(
                        f"0 {center_x_norm:.6f} {center_y_norm:.6f} {width_norm:.6f} {height_norm:.6f}\n"
                    )
                    for point in projected_points:
                        px_norm = point[0] / image_width
                        py_norm = point[1] / image_height
                        f.write(f"{px_norm:.6f} {py_norm:.6f}\n")

        # Yaw series
        self.hide_all_markups()
        self.hide_cube_and_axis()

        for i in range(self.yaw_num):
            yaw = self.yaw_range[0] + (self.yaw_range[1] - self.yaw_range[0]) * i / (
                self.yaw_num - 1
            )
            self.set_camera_yaw(yaw)
            slicer.app.processEvents()
            time.sleep(0.1)

            view = slicer.app.layoutManager().threeDWidget(0).threeDView()
            view.forceRender()
            cameraNode = view.cameraNode()

            # Save camera parameters
            camera_info = {
                "position": cameraNode.GetPosition(),
                "focal_point": cameraNode.GetFocalPoint(),
                "view_up": cameraNode.GetViewUp(),
                "fov": cameraNode.GetViewAngle(),
                "image_size": (
                    view.width() if callable(view.width) else view.width,
                    view.height() if callable(view.height) else view.height,
                ),
            }

            # Save image
            image_filename = f"image_yaw{i:02d}.png"
            image_path = os.path.join(images_path, image_filename)
            view.grab().save(image_path)

            # --- YAW SERIES ---
            # Arrange points in correct sequence
            sequenced_points = self.arrange_points_in_sequence(soft_tissue_points)
            # Project points and save annotations
            projected_points = []
            for point_3d in sequenced_points:
                point_2d = self.project_3d_to_2d(point_3d, camera_info)
                if point_2d is not None:
                    projected_points.append(point_2d)
            # Save annotations in YOLO format
            label_filename = f"image_yaw{i:02d}.txt"
            label_path = os.path.join(labels_path, label_filename)
            with open(label_path, "w", encoding="utf-8") as f:
                if projected_points:
                    x_coords = [p[0] for p in projected_points]
                    y_coords = [p[1] for p in projected_points]
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    center_x = (x_min + x_max) / 2
                    center_y = (y_min + y_max) / 2
                    width = x_max - x_min
                    height = y_max - y_min
                    image_width, image_height = camera_info["image_size"]
                    center_x_norm = center_x / image_width
                    center_y_norm = center_y / image_height
                    width_norm = width / image_width
                    height_norm = height / image_height
                    f.write(
                        f"0 {center_x_norm:.6f} {center_y_norm:.6f} {width_norm:.6f} {height_norm:.6f}\n"
                    )
                    for point in projected_points:
                        px_norm = point[0] / image_width
                        py_norm = point[1] / image_height
                        f.write(f"{px_norm:.6f} {py_norm:.6f}\n")

        print(f"✅ Completed: {markup_folder} -> {patient_name}")

    def process_all(self):
        """Process all markup folders in the data directory."""
        markup_folders = self.find_markup_folders()

        if not markup_folders:
            print("❌ No markups_xxx folders found in the specified directory")
            return

        print(f"Found {len(markup_folders)} folders to process:")
        for folder in markup_folders:
            print(f"  - {folder}")

        for markup_folder in markup_folders:
            self.process_markup_folder(markup_folder)

        print(f"\n🎉 Processing completed! Results saved to {self.dataset_path}")


if __name__ == "__main__":
    # Paths to directories
    load_dotenv()
    data_path = os.getenv("INPUT_MARKUP_PATH")
    dataset_path = os.getenv("OUTPUT_DATASET_PATH")
    if not data_path or not dataset_path:
        raise ValueError(
            "INPUT_MARKUP_PATH and OUTPUT_DATASET_PATH must be set in .env"
        )

    processor = DatasetProcessor(
        data_path=data_path,
        dataset_path=dataset_path,
        distance=450,
        pitch_range=(-15.0, 15.0),
        pitch_num=10,
        yaw_range=(-10.0, 10.0),
        yaw_num=10,
    )
    processor.process_all()
