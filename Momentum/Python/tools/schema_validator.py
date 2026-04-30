"""
Schema validation utilities for SRS artifacts.

Validates domain objects and events against canonical JSON schemas.
"""

from pathlib import Path
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from jsonschema import validate, ValidationError, Draft7Validator


class SchemaValidator:
    """Load and validate JSON schemas from SRS/schemas/"""

    def __init__(self, schema_base_path: str = "SRS"):
        self.schema_base = self._resolve_schema_base_path(schema_base_path)
        self.schemas: Dict[str, Dict] = {}
        self._load_all_schemas()

    def _resolve_schema_base_path(self, schema_base_path: str) -> str:
        """Resolve the schema base path relative to the repository root if needed."""
        candidate = Path(schema_base_path)
        if candidate.is_dir():
            return str(candidate)

        module_path = Path(__file__).resolve()
        for parent in module_path.parents:
            repo_candidate = parent / schema_base_path
            if repo_candidate.is_dir():
                return str(repo_candidate)

        return schema_base_path

    def _load_all_schemas(self) -> None:
        """Load all JSON schemas from SRS/schemas/ and SRS/event_schemas/"""
        for folder in ["schemas", "event_schemas"]:
            schema_path = os.path.join(self.schema_base, folder)
            if not os.path.exists(schema_path):
                continue
            for fname in os.listdir(schema_path):
                if fname.endswith(".json"):
                    fpath = os.path.join(schema_path, fname)
                    try:
                        with open(fpath, "r") as f:
                            self.schemas[fname.replace(".schema.json", "")] = json.load(f)
                    except Exception as e:
                        print(f"Warning: Failed to load schema {fname}: {e}")

    def validate_driver(self, driver: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate driver object against driver.schema.json"""
        if "driver" not in self.schemas:
            return True, "Driver schema not available"
        try:
            validate(instance=driver, schema=self.schemas["driver"])
            return True, None
        except ValidationError as e:
            return False, str(e)

    def validate_team(self, team: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate team object against team.schema.json"""
        if "team" not in self.schemas:
            return True, "Team schema not available"
        try:
            validate(instance=team, schema=self.schemas["team"])
            return True, None
        except ValidationError as e:
            return False, str(e)

    def validate_track(self, track: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate track object against track.schema.json"""
        if "track" not in self.schemas:
            return True, "Track schema not available"
        try:
            validate(instance=track, schema=self.schemas["track"])
            return True, None
        except ValidationError as e:
            return False, str(e)

    def validate_result(self, result: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate race result object against result.schema.json"""
        if "result" not in self.schemas:
            return True, "Result schema not available"
        try:
            validate(instance=result, schema=self.schemas["result"])
            return True, None
        except ValidationError as e:
            return False, str(e)

    def validate_event(self, event: Dict[str, Any], event_type: str) -> Tuple[bool, Optional[str]]:
        """Validate event object against its specific schema (e.g., lap_complete, overtake, incident)"""
        schema_key = event_type.replace("event_", "")
        if schema_key not in self.schemas:
            return True, f"Event schema {schema_key} not available"
        try:
            validate(instance=event, schema=self.schemas[schema_key])
            return True, None
        except ValidationError as e:
            return False, str(e)

    def validate_batch(self, objects: List[Dict[str, Any]], object_type: str) -> Tuple[bool, List[str]]:
        """Validate a batch of objects; return (all_valid, list_of_errors)"""
        errors = []
        validator = getattr(self, f"validate_{object_type}", None)
        if not validator:
            return False, [f"Unknown object type: {object_type}"]
        for i, obj in enumerate(objects):
            valid, error = validator(obj)
            if not valid:
                errors.append(f"Object {i}: {error}")
        return len(errors) == 0, errors
