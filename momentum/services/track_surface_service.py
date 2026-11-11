"""
Track Surface Service - Surface type mapping and generation by discipline

Provides discipline-specific surface type assignment and grip characteristics
for realistic track simulation across different racing types.

Surface Types:
- asphalt: High grip, standard racing surface (default)
- concrete: Slightly lower grip than asphalt
- gravel: Low grip, used for rallycross and escapes
- mixed: Multiple surface types on same track (rallycross typical)
- dirt: Off-road surface (lower grip than gravel)
- grassy: Grass/grass-trap surface (low grip)
"""

from momentum.database.models import Track


class TrackSurfaceService:
    """Manages surface types for tracks by racing discipline"""

    # Surface grip values (0.0-1.0 scale, 1.0 = perfect grip)
    SURFACE_GRIP_MAP = {
        "asphalt": 1.0,  # High grip
        "concrete": 0.95,  # Slightly lower
        "gravel": 0.6,  # Low grip, rough
        "mixed": 0.75,  # Mix of surfaces (typically gravel + asphalt)
        "dirt": 0.55,  # Off-road, very low grip
        "grassy": 0.65,  # Grass traps
    }

    # Discipline-specific surface distributions
    DISCIPLINE_SURFACES = {
        "SINGLE_SEATER": {
            # Pure asphalt racing, but tracks may have grassy run-off areas
            "primary": "asphalt",  # Main racing surface
            "alternate": ["grassy"],  # Grass traps in run-off
            "primary_percentage": 85,  # 85% asphalt track surface
        },
        "PRODUCTION_TOURING": {
            "primary": "asphalt",
            "alternate": ["concrete", "grassy"],
            "primary_percentage": 80,
        },
        "URBAN_STREET": {
            # Street circuits use concrete/asphalt
            "primary": "concrete",  # Urban streets (concrete)
            "alternate": ["asphalt"],  # Some streets are asphalt
            "primary_percentage": 70,
        },
        "DRAG_ACCELERATION": {
            # Pure asphalt surface
            "primary": "asphalt",
            "alternate": [],
            "primary_percentage": 100,
        },
        "SPRINT_RALLYCROSS": {
            # Mixed surface racing - gravel and asphalt
            "primary": "mixed",  # Alternating gravel/asphalt sections
            "alternate": ["gravel", "asphalt"],
            "primary_percentage": 50,  # 50/50 split typical
        },
        "ENDURANCE": {
            # Long-distance circuits, primarily asphalt
            "primary": "asphalt",
            "alternate": ["grassy", "concrete"],
            "primary_percentage": 90,
        },
    }

    @classmethod
    def get_surface_for_discipline(cls, discipline: str) -> str:
        """
        Get primary surface type for a discipline

        Args:
            discipline: Racing discipline (e.g., "SINGLE_SEATER")

        Returns:
            Surface type name
        """
        if discipline not in cls.DISCIPLINE_SURFACES:
            return "asphalt"  # Default to asphalt

        primary = cls.DISCIPLINE_SURFACES[discipline]["primary"]
        return str(primary)

    @classmethod
    def get_grip_level(cls, surface: str) -> float:
        """
        Get grip level for a surface type

        Args:
            surface: Surface type name

        Returns:
            Grip level (0.0-1.0)
        """
        return cls.SURFACE_GRIP_MAP.get(surface.lower(), 0.9)

    @classmethod
    def assign_surface_to_track(cls, track: Track, discipline: str) -> Track:
        """
        Assign appropriate surface type to track based on discipline

        Args:
            track: Track object to update
            discipline: Racing discipline

        Returns:
            Track with surface assigned
        """
        if not track.surface or track.surface == "asphalt":
            # Assign discipline-appropriate surface
            track.surface = cls.get_surface_for_discipline(discipline)

        return track

    @classmethod
    def get_discipline_surface_description(cls, discipline: str) -> str:
        """
        Get human-readable description of surface for discipline

        Args:
            discipline: Racing discipline

        Returns:
            Description string
        """
        if discipline not in cls.DISCIPLINE_SURFACES:
            return "asphalt racing circuit"

        # discipline config not required for current description mapping

        descriptions = {
            "SINGLE_SEATER": "High-grip asphalt circuit with grass run-off areas",
            "PRODUCTION_TOURING": "Road course with asphalt surface and concrete sections",
            "URBAN_STREET": "Street circuit with concrete and asphalt surfaces",
            "DRAG_ACCELERATION": "Pure asphalt drag strip",
            "SPRINT_RALLYCROSS": "Mixed-surface circuit with gravel and asphalt sections",
            "ENDURANCE": "Full-length endurance circuit with high-grip asphalt surface",
        }

        return descriptions.get(discipline, "asphalt racing circuit")
