from dotenv import load_dotenv
import os
import cv2


class SequenceVisualizer:
    """
    Visualizer for sequential display of annotations on images.
    """

    def __init__(self, images_path, labels_path, output_path=None):
        """
        Initialize the visualizer.

        Args:
            images_path (str): Path to the folder with images
            labels_path (str): Path to the folder with annotations
            output_path (str): Path for saving results (optional)
        """
        self.images_path = images_path
        self.labels_path = labels_path
        self.output_path = output_path

        # Create output directory if specified
        if self.output_path and not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # Colors for different points
        self.colors = [
            (0, 255, 0),  # Green - left infraorbital
            (255, 0, 0),  # Red - left mental
            (255, 255, 0),  # Yellow - right infraorbital
            (0, 0, 255),  # Blue - right mental
        ]

        # Point names
        self.point_names = [
            "Left Infraorbital",
            "Left Mental",
            "Right Infraorbital",
            "Right Mental",
        ]

    def load_image_and_labels(self, image_name):
        """
        Load image and corresponding annotation.

        Args:
            image_name (str): Image name (without extension)

        Returns:
            tuple: (image, list of point coordinates)
        """
        # Load image
        image_path = os.path.join(self.images_path, f"{image_name}.png")
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return None, []

        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not load image: {image_path}")
            return None, []

        # Load annotation
        label_path = os.path.join(self.labels_path, f"{image_name}.txt")
        if not os.path.exists(label_path):
            print(f"❌ Annotation not found: {label_path}")
            return image, []

        points = []
        try:
            with open(label_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) < 2:
                    return image, []
                # Skip first line (YOLO bbox)
                for line in lines[1:]:
                    line = line.strip()
                    if line:
                        coords = line.split()
                        if len(coords) >= 2:
                            # Normalized coordinates (float 0-1)
                            px_norm = float(coords[0])
                            py_norm = float(coords[1])
                            h, w = image.shape[:2]
                            x = int(px_norm * w)
                            y = int(py_norm * h)
                            points.append((x, y))
        except Exception as e:
            print(f"❌ Error reading annotation: {e}")
            return image, []

        return image, points

    def draw_point(self, image, point, color, point_name, point_index, show_text=True):
        """
        Draw a point on the image.

        Args:
            image: Image for drawing
            point (tuple): Point coordinates (x, y)
            color (tuple): Point color (B, G, R)
            point_name (str): Point name
            point_index (int): Point index
            show_text (bool): Whether to show text

        Returns:
            numpy.ndarray: Image with the point drawn
        """
        x, y = point

        # Draw circle
        cv2.circle(image, (x, y), 8, color, -1)
        cv2.circle(image, (x, y), 8, (255, 255, 255), 2)  # White outline

        if show_text:
            # Add text
            text = f"{point_index + 1}: {point_name}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2

            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                text, font, font_scale, thickness
            )

            # Text position (shift right and up from the point)
            text_x = x + 15
            text_y = y - 10

            # Draw text background
            cv2.rectangle(
                image,
                (text_x - 5, text_y - text_height - 5),
                (text_x + text_width + 5, text_y + baseline + 5),
                (0, 0, 0),
                -1,
            )

            # Draw text
            cv2.putText(
                image,
                text,
                (text_x, text_y),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
            )

        return image

    def visualize_single_image_sequence(self, image_name, delay=1.0, save_steps=False):
        """
        Visualize the sequence of points for a single image.

        Args:
            image_name (str): Image name (without extension)
            delay (float): Delay between points in seconds
            save_steps (bool): Whether to save intermediate steps
        """
        print(f"\n🖼️  Processing image: {image_name}")

        # Load image and annotation
        image, points = self.load_image_and_labels(image_name)

        if image is None:
            print("❌ Could not load image")
            return

        if not points:
            print("⚠️  No annotation points found")
            return

        print(f"📊 Found {len(points)} points")

        # Create a copy of the image for drawing
        working_image = image.copy()

        # Show original image
        cv2.imshow("Annotation Sequence", working_image)
        cv2.waitKey(1000)  # Show for 1 second

        # Draw points sequentially
        for i, (point, color, point_name) in enumerate(
            zip(points, self.colors, self.point_names)
        ):
            print(f"  {i+1}. Drawing {point_name}: ({point[0]}, {point[1]})")

            # Draw point
            working_image = self.draw_point(working_image, point, color, point_name, i)

            # Show result
            cv2.imshow("Annotation Sequence", working_image)

            # Wait for key press or timer
            key = cv2.waitKey(int(delay * 1000))

            # Save intermediate step if needed
            if save_steps and self.output_path:
                step_filename = f"{image_name}_step_{i+1:02d}.png"
                step_path = os.path.join(self.output_path, step_filename)
                cv2.imwrite(step_path, working_image)
                print(f"    💾 Saved step: {step_filename}")

            # Check for key presses
            if key == ord("q"):  # Exit
                print("  ⏹️  Stopped by user")
                break
            elif key == ord("s"):  # Skip
                print("  ⏭️  Skipped")
                break
            elif key == ord(" "):  # Pause/continue
                print("  ⏸️  Pause (press any key to continue)")
                cv2.waitKey(0)

        # Save final result if needed
        if self.output_path:
            final_filename = f"{image_name}_final.png"
            final_path = os.path.join(self.output_path, final_filename)
            cv2.imwrite(final_path, working_image)
            print(f"  💾 Saved final result: {final_filename}")

    def get_image_list(self):
        """
        Get a list of all image names.

        Returns:
            list: List of image names (without extension)
        """
        image_files = []
        for file in os.listdir(self.images_path):
            if file.endswith(".png"):
                image_name = file.replace(".png", "")
                image_files.append(image_name)

        return sorted(image_files)

    def visualize_all_images(self, delay=1.0, save_steps=False):
        """
        Visualize the sequence for all images.

        Args:
            delay (float): Delay between points in seconds
            save_steps (bool): Whether to save intermediate steps
        """
        image_list = self.get_image_list()

        if not image_list:
            print("❌ No images found")
            return

        print(f"📁 Found {len(image_list)} images:")
        for img in image_list:
            print(f"  - {img}")

        print(f"\n🎬 Starting visualization...")
        print(f"   Controls:")
        print(f"   - Space: pause/continue")
        print(f"   - S: skip current image")
        print(f"   - Q: exit")

        for i, image_name in enumerate(image_list):
            print(f"\n{'='*60}")
            print(f"Image {i+1}/{len(image_list)}: {image_name}")
            print(f"{'='*60}")

            self.visualize_single_image_sequence(image_name, delay, save_steps)

            # Check if user pressed Q
            key = cv2.waitKey(100)
            if key == ord("q"):
                print("⏹️  Stopped by user")
                break

        cv2.destroyAllWindows()
        print(f"\n🎉 Visualization finished!")

    def create_summary_image(self, image_name, save_path=None):
        """
        Create a final image with all points.

        Args:
            image_name (str): Image name (without extension)
            save_path (str): Path for saving (optional)
        """
        print(f"📊 Creating summary image for: {image_name}")

        # Load image and annotation
        image, points = self.load_image_and_labels(image_name)

        if image is None or not points:
            print("❌ Could not load data")
            return

        # Draw all points
        working_image = image.copy()

        for i, (point, color, point_name) in enumerate(
            zip(points, self.colors, self.point_names)
        ):
            working_image = self.draw_point(
                working_image, point, color, point_name, i, show_text=True
            )

        # Add title
        title = f"Annotation: {image_name}"
        cv2.putText(
            working_image,
            title,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

        # Show result
        cv2.imshow("Final Annotation", working_image)
        cv2.waitKey(0)

        # Save if path is specified
        if save_path:
            cv2.imwrite(save_path, working_image)
            print(f"💾 Saved: {save_path}")

        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Paths to data
    load_dotenv()
    images_path = os.getenv("SEQ_IMAGES_PATH")
    labels_path = os.getenv("SEQ_LABELS_PATH")
    output_path = os.getenv("SEQ_OUTPUT_PATH")
    if not images_path or not labels_path or not output_path:
        raise ValueError(
            "SEQ_IMAGES_PATH, SEQ_LABELS_PATH, and SEQ_OUTPUT_PATH must be set in .env"
        )

    # Create visualizer
    visualizer = SequenceVisualizer(
        images_path=images_path, labels_path=labels_path, output_path=output_path
    )

    # Start visualizing all images
    visualizer.visualize_all_images(delay=1.5, save_steps=True)

    # Example of creating a summary image for one file
    # visualizer.create_summary_image("image_pitch00")
