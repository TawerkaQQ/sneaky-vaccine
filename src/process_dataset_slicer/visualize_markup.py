import cv2
import os
import numpy as np
from typing import List, Tuple, Optional
from dotenv import load_dotenv


class DatasetVisualizer:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.current_patient_index = 0
        self.current_image_index = 0

        # Cache for current patient data
        self.current_patient_name = None
        self.current_patient_images = []
        self.current_patient_labels = []

        # Get all patient folders
        self.patient_folders = self._get_patient_folders()

        if not self.patient_folders:
            print(f"❌ No patient folders found in: {self.dataset_path}")
            return

        print(f"✅ Found {len(self.patient_folders)} patient folders")
        for folder in self.patient_folders:
            print(f"  - {folder}")

        # Load first patient
        self._load_current_patient()

    def _get_patient_folders(self) -> List[str]:
        if not os.path.exists(self.dataset_path):
            return []

        patient_folders = []
        for item in os.listdir(self.dataset_path):
            item_path = os.path.join(self.dataset_path, item)
            if os.path.isdir(item_path):
                # Check if it has images subfolder
                images_path = os.path.join(item_path, "images")
                if os.path.exists(images_path):
                    patient_folders.append(item)

        return sorted(patient_folders)

    def _load_current_patient(self):
        """Load images and labels for the current patient."""
        if not self.patient_folders:
            return

        patient_name = self.patient_folders[self.current_patient_index]
        images_dir = os.path.join(self.dataset_path, patient_name, "images")
        labels_dir = os.path.join(self.dataset_path, patient_name, "labels")

        # Get all PNG files
        png_files = [f for f in os.listdir(images_dir) if f.endswith(".png")]
        png_files.sort()

        self.current_patient_name = patient_name
        self.current_patient_images = png_files
        self.current_patient_labels = []

        # Pre-load label file paths for quick access
        for png_file in png_files:
            txt_file = png_file.replace(".png", ".txt")
            txt_path = os.path.join(labels_dir, txt_file)
            self.current_patient_labels.append(txt_path)

        print(f"📁 Loaded patient: {patient_name} ({len(png_files)} images)")

    def _load_image_and_points(
        self, patient_index: int, image_index: int
    ) -> Tuple[Optional[np.ndarray], List[List[int]]]:
        """
        Load a specific image and its corresponding landmark points.

        Args:
            patient_index (int): Index of the patient
            image_index (int): Index of the image within the patient

        Returns:
            Tuple[Optional[np.ndarray], List[List[int]]]: (image, points) or (None, []) if failed
        """
        if patient_index >= len(self.patient_folders):
            return None, []

        patient_name = self.patient_folders[patient_index]
        images_dir = os.path.join(self.dataset_path, patient_name, "images")
        labels_dir = os.path.join(self.dataset_path, patient_name, "labels")

        # Get image files for this patient
        png_files = [f for f in os.listdir(images_dir) if f.endswith(".png")]
        png_files.sort()

        if image_index >= len(png_files):
            return None, []

        # Load image
        image_path = os.path.join(images_dir, png_files[image_index])
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Failed to load image: {image_path}")
            return None, []

        # Load points from YOLO-style annotation format
        txt_file = png_files[image_index].replace(".png", ".txt")
        txt_path = os.path.join(labels_dir, txt_file)
        points = []

        if os.path.exists(txt_path):
            try:
                with open(txt_path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                    if len(lines) >= 5:
                        # First line: class_index x_center y_center width height (bounding box)
                        # Next 4 lines: keypoint coordinates (normalized 0-1)
                        h, w = image.shape[:2]
                        for kp_line in lines[1:5]:  # Skip bounding box line
                            x_str, y_str = kp_line.split()
                            x_norm, y_norm = float(x_str), float(y_str)
                            # Convert normalized coordinates to pixel coordinates
                            x = int(x_norm * w)
                            y = int(y_norm * h)
                            points.append([x, y])
            except Exception as e:
                print(f"⚠️ Error reading label file {txt_path}: {e}")

        return image, points

    def draw_points(self, image: np.ndarray, points: List[List[int]], radius: int = 5):
        """
        Draw landmark points on the image with anatomical color coding.

        Args:
            image: OpenCV image to draw on
            points: List of [x, y] coordinates
            radius: Radius of the point circles
        """
        # Anatomical keypoint colors (BGR format)
        # Order: Left Infraorbital, Left Mental, Right Infraorbital, Right Mental
        colors = [
            (0, 255, 0),  # Green - Left Infraorbital
            (255, 0, 0),  # Blue - Left Mental
            (0, 0, 255),  # Red - Right Infraorbital
            (0, 255, 255),  # Yellow - Right Mental
        ]

        keypoint_names = [
            "Left Infraorbital",
            "Left Mental",
            "Right Infraorbital",
            "Right Mental",
        ]

        for i, point in enumerate(points):
            if i < len(colors):
                x, y = point
                color = colors[i]
                # Draw circle
                cv2.circle(image, (x, y), radius, color, -1)
                # Draw point number and name
                label = f"{i + 1}: {keypoint_names[i]}"
                cv2.putText(
                    image,
                    label,
                    (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

    def show_current_image(self):
        """Display the current image with overlaid markup points."""
        if not self.patient_folders:
            print("❌ No patients to display")
            return

        # Load current image and points
        image, points = self._load_image_and_points(
            self.current_patient_index, self.current_image_index
        )

        if image is None:
            print("❌ Failed to load current image")
            return

        # Copy image for display
        display_image = image.copy()

        # Draw points
        self.draw_points(display_image, points)

        # Add information overlay
        patient_name = self.patient_folders[self.current_patient_index]
        png_files = [
            f
            for f in os.listdir(os.path.join(self.dataset_path, patient_name, "images"))
            if f.endswith(".png")
        ]
        png_files.sort()
        current_file = png_files[self.current_image_index]

        info_text = (
            f"Patient: {patient_name} | Image: {current_file} | Points: {len(points)}"
        )
        cv2.putText(
            display_image,
            info_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        # Add navigation info
        nav_text = f"Patient {self.current_patient_index + 1}/{len(self.patient_folders)} | Image {self.current_image_index + 1}/{len(png_files)}"
        cv2.putText(
            display_image,
            nav_text,
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (200, 200, 200),
            2,
        )

        # Show image
        cv2.imshow("Dataset Visualization", display_image)

        # Print point coordinates to console
        keypoint_names = [
            "Left Infraorbital",
            "Left Mental",
            "Right Infraorbital",
            "Right Mental",
        ]
        print(f"\n📸 {patient_name}/{current_file}:")
        for i, point in enumerate(points):
            if i < len(keypoint_names):
                print(f"  {keypoint_names[i]}: ({point[0]}, {point[1]})")
            else:
                print(f"  Point_{i+1}: ({point[0]}, {point[1]})")

    def next_image(self):
        """Move to the next image."""
        if not self.patient_folders:
            return

        patient_name = self.patient_folders[self.current_patient_index]
        images_dir = os.path.join(self.dataset_path, patient_name, "images")
        png_files = [f for f in os.listdir(images_dir) if f.endswith(".png")]
        png_files.sort()

        self.current_image_index += 1
        if self.current_image_index >= len(png_files):
            # Move to next patient
            self.current_image_index = 0
            self.current_patient_index += 1
            if self.current_patient_index >= len(self.patient_folders):
                # Loop back to first patient
                self.current_patient_index = 0
            self._load_current_patient()

    def previous_image(self):
        """Move to the previous image."""
        if not self.patient_folders:
            return

        self.current_image_index -= 1
        if self.current_image_index < 0:
            # Move to previous patient
            self.current_patient_index -= 1
            if self.current_patient_index < 0:
                # Loop to last patient
                self.current_patient_index = len(self.patient_folders) - 1
            self._load_current_patient()

            # Set to last image of previous patient
            patient_name = self.patient_folders[self.current_patient_index]
            images_dir = os.path.join(self.dataset_path, patient_name, "images")
            png_files = [f for f in os.listdir(images_dir) if f.endswith(".png")]
            png_files.sort()
            self.current_image_index = len(png_files) - 1

    def next_patient(self):
        """Move to the next patient."""
        if not self.patient_folders:
            return

        self.current_patient_index += 1
        if self.current_patient_index >= len(self.patient_folders):
            self.current_patient_index = 0
        self.current_image_index = 0
        self._load_current_patient()

    def previous_patient(self):
        """Move to the previous patient."""
        if not self.patient_folders:
            return

        self.current_patient_index -= 1
        if self.current_patient_index < 0:
            self.current_patient_index = len(self.patient_folders) - 1
        self.current_image_index = 0
        self._load_current_patient()

    def save_current_image(self):
        """Save the current image with markup points."""
        if not self.patient_folders:
            return

        # Load current image and points
        image, points = self._load_image_and_points(
            self.current_patient_index, self.current_image_index
        )

        if image is None:
            print("❌ Failed to load current image for saving")
            return

        # Draw points
        display_image = image.copy()
        self.draw_points(display_image, points)

        # Save image
        patient_name = self.patient_folders[self.current_patient_index]
        images_dir = os.path.join(self.dataset_path, patient_name, "images")
        png_files = [f for f in os.listdir(images_dir) if f.endswith(".png")]
        png_files.sort()
        current_file = png_files[self.current_image_index]

        save_name = current_file.replace(".png", "_with_markup.png")
        save_path = os.path.join(images_dir, save_name)
        cv2.imwrite(save_path, display_image)
        print(f"💾 Saved: {save_path}")

    def run(self):
        """Run the interactive visualization interface."""
        if not self.patient_folders:
            print("❌ No patients to display")
            return

        print("\n🎮 Controls:")
        print("  'a' - previous image")
        print("  'd' - next image")
        print("  'w' - previous patient")
        print("  's' - next patient")
        print("  'q' - quit")
        print("  'z' - save current image with markup")

        while True:
            self.show_current_image()

            key = cv2.waitKey(0) & 0xFF

            if key == ord("q"):
                break
            elif key == ord("a"):  # previous image
                self.previous_image()
            elif key == ord("d"):  # next image
                self.next_image()
            elif key == ord("w"):  # previous patient
                self.previous_patient()
            elif key == ord("s"):  # next patient
                self.next_patient()
            elif key == ord("z"):  # save
                self.save_current_image()

        cv2.destroyAllWindows()


def visualize_dataset(dataset_path: str):
    """
    Visualize all images from all patients in the dataset.

    Args:
        dataset_path (str): Path to the dataset directory containing patient folders
    """
    visualizer = DatasetVisualizer(dataset_path)
    visualizer.run()


if __name__ == "__main__":
    # Path to the dataset directory
    load_dotenv()
    dataset_path = os.getenv("DATASET_VIS_PATH")
    if not dataset_path:
        raise ValueError("DATASET_VIS_PATH must be set in .env")

    print(f"🚀 Starting dataset visualization for: {dataset_path}")
    visualize_dataset(dataset_path)
