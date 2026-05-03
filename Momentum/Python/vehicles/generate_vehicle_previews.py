"""
Vehicle Preview Generator

Creates PNG preview images of all vehicle types for visual verification.
Run this script to generate preview images in the vehicles/ directory.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter, QColor

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vehicles.vehicle_appearance import (
    VehicleType,
    VehicleRenderer,
    Livery,
    create_team_livery,
)


def generate_preview(
    vehicle_type: VehicleType,
    livery: Livery,
    output_path: Path,
    scale: float = 3.0,
    steering_angle: float = 0.0,
) -> None:
    """
    Generate a preview PNG for a specific vehicle type.

    Args:
        vehicle_type: Type of vehicle to render
        livery: Car livery colors
        output_path: Path to save PNG file
        scale: Rendering scale (larger = bigger image)
        steering_angle: Steering angle for demonstration
    """
    # Image dimensions (adjust based on vehicle type)
    if vehicle_type == VehicleType.DRAG_ACCELERATION:
        width, height = 400, 1200  # Tall for dragster
    else:
        width, height = 600, 800

    # Create image with white background
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(QColor(255, 255, 255))

    # Setup painter
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Translate to center and render
    painter.translate(width // 2, height // 2)
    VehicleRenderer.render_car(painter, vehicle_type, livery, scale, steering_angle)

    # Add label
    painter.resetTransform()
    painter.setPen(QColor(0, 0, 0))
    painter.drawText(10, 20, f"{vehicle_type.value.upper().replace('_', ' ')}")
    painter.drawText(10, 40, f"Team: {livery.team_name} #{livery.driver_number}")

    painter.end()

    # Save to file
    image.save(str(output_path))
    print(f"✓ Generated: {output_path.name}")


def main():
    """Generate preview images for all vehicle types."""
    # Ensure QApplication exists for QPainter without leaving an unused variable
    if not QApplication.instance():
        QApplication(sys.argv)

    output_dir = Path(__file__).parent / "previews"
    output_dir.mkdir(exist_ok=True)

    print("Generating vehicle preview images...\n")

    # Define vehicle types with sample liveries
    vehicles = [
        (VehicleType.SINGLE_SEATER, create_team_livery(0, "Velocity Racing", 44), 0.0),
        (VehicleType.ENDURANCE, create_team_livery(1, "Endurance Motorsport", 7), 0.0),
        (
            VehicleType.DRAG_ACCELERATION,
            create_team_livery(2, "Top Fuel Racing", 1),
            0.0,
        ),
        (
            VehicleType.SPRINT_RALLYCROSS,
            create_team_livery(3, "Rally Cross Team", 27),
            0.0,
        ),
        (VehicleType.PRODUCTION_TOURING, create_team_livery(4, "GT Racing", 99), 0.0),
        (VehicleType.URBAN_STREET, create_team_livery(0, "Drift Kings", 88), 0.0),
    ]

    # Generate straight previews
    for vehicle_type, livery, steering in vehicles:
        filename = f"{vehicle_type.value}_preview.png"
        output_path = output_dir / filename
        generate_preview(
            vehicle_type, livery, output_path, scale=6.0, steering_angle=steering
        )

    # Generate steering angle demonstrations for steerable vehicles
    print("\nGenerating steering angle demonstrations...\n")

    steerable_vehicles = [
        (VehicleType.SINGLE_SEATER, create_team_livery(0, "Velocity Racing", 44)),
        (VehicleType.ENDURANCE, create_team_livery(1, "Endurance Motorsport", 7)),
        (VehicleType.SPRINT_RALLYCROSS, create_team_livery(3, "Rally Cross Team", 27)),
        (VehicleType.PRODUCTION_TOURING, create_team_livery(4, "GT Racing", 99)),
        (VehicleType.URBAN_STREET, create_team_livery(0, "Drift Kings", 88)),
    ]

    for vehicle_type, livery in steerable_vehicles:
        filename = f"{vehicle_type.value}_steering.png"
        output_path = output_dir / filename
        # Use more extreme angle for drift car
        angle = 35.0 if vehicle_type == VehicleType.URBAN_STREET else 15.0
        generate_preview(
            vehicle_type, livery, output_path, scale=6.0, steering_angle=angle
        )

    print(f"\n✓ All previews generated in: {output_dir}")
    print(f"  Total images: {len(list(output_dir.glob('*.png')))}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
