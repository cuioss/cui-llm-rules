#!/usr/bin/env python3
"""Validate domain and supplement manifests."""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# Default plugin cache location
DEFAULT_PLUGIN_CACHE = Path.home() / ".claude" / "plugins" / "cache" / "plan-marshall"

# Valid profile names
VALID_PROFILES = {"core", "implementation", "testing", "quality"}

# Supported schema versions
SUPPORTED_VERSIONS = {"v1"}

# Skill reference pattern: bundle:skill-name
SKILL_REF_PATTERN = re.compile(r"^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$")


def get_plugin_cache_path() -> Path:
    """Get the plugin cache path, allowing override via environment variable."""
    env_path = os.environ.get("PLUGIN_CACHE_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_PLUGIN_CACHE


def find_bundle_path(bundle_name: str) -> Path | None:
    """Find the bundle path in the plugin cache.

    Args:
        bundle_name: Name of the bundle

    Returns:
        Path to bundle directory, or None if not found
    """
    plugin_cache = get_plugin_cache_path()

    # Check versioned structure: {bundle}/{version}/
    bundle_dir = plugin_cache / bundle_name
    if bundle_dir.exists():
        for version_dir in bundle_dir.iterdir():
            if version_dir.is_dir():
                return version_dir

    return None


def extract_schema_version(schema_url: str) -> str:
    """Extract version from schema URL.

    Args:
        schema_url: URL like '.../domain-manifest-v1.json'

    Returns:
        Version string like 'v1'
    """
    if not schema_url:
        return "unknown"
    filename = schema_url.split("/")[-1]
    if "-v" in filename:
        version_part = filename.split("-v")[-1]
        version = "v" + version_part.replace(".json", "")
        return version
    return "unknown"


def detect_manifest_type(manifest: dict) -> str:
    """Detect manifest type from content."""
    if "domain" in manifest:
        return "domain"
    if "supplements" in manifest:
        return "supplement"
    return "unknown"


def validate_skill_reference(ref: str) -> tuple[bool, str]:
    """Validate a skill reference format.

    Args:
        ref: Skill reference like 'bundle:skill'

    Returns:
        (is_valid, error_message)
    """
    if not SKILL_REF_PATTERN.match(ref):
        return False, f"Invalid skill reference format: {ref}"
    return True, ""


def check_skill_exists(ref: str, bundle_path: Path) -> tuple[bool, str]:
    """Check if a skill exists in the same bundle.

    Args:
        ref: Skill reference like 'bundle:skill'
        bundle_path: Path to the bundle

    Returns:
        (exists, error_message)
    """
    # Extract bundle and skill from reference
    parts = ref.split(":")
    if len(parts) != 2:
        return False, f"Invalid reference format: {ref}"

    ref_bundle, skill_name = parts

    # Get current bundle name from path
    current_bundle = bundle_path.parent.name

    # If same bundle, check skill directory exists
    if ref_bundle == current_bundle:
        skill_dir = bundle_path / "skills" / skill_name
        if skill_dir.exists():
            return True, ""
        return False, f"Skill not found: {ref}"

    # For cross-bundle references, check other bundle
    other_bundle_path = find_bundle_path(ref_bundle)
    if other_bundle_path is None:
        return False, f"Bundle not found: {ref_bundle}"

    skill_dir = other_bundle_path / "skills" / skill_name
    if skill_dir.exists():
        return True, ""
    return False, f"Skill not found: {ref}"


def validate_profile(profile: dict, profile_name: str) -> list[str]:
    """Validate a single profile structure.

    Args:
        profile: Profile dict
        profile_name: Name of the profile

    Returns:
        List of error messages
    """
    errors = []

    if not isinstance(profile, dict):
        errors.append(f"Profile '{profile_name}' must be an object")
        return errors

    if "defaults" not in profile:
        errors.append(f"Profile '{profile_name}' missing 'defaults' array")
    elif not isinstance(profile.get("defaults"), list):
        errors.append(f"Profile '{profile_name}.defaults' must be an array")

    if "optionals" not in profile:
        errors.append(f"Profile '{profile_name}' missing 'optionals' array")
    elif not isinstance(profile.get("optionals"), list):
        errors.append(f"Profile '{profile_name}.optionals' must be an array")

    # Validate skill references
    for skill in profile.get("defaults", []):
        valid, err = validate_skill_reference(skill)
        if not valid:
            errors.append(f"Profile '{profile_name}.defaults': {err}")

    for skill in profile.get("optionals", []):
        valid, err = validate_skill_reference(skill)
        if not valid:
            errors.append(f"Profile '{profile_name}.optionals': {err}")

    return errors


def validate_domain_manifest(manifest: dict, bundle_path: Path) -> dict:
    """Validate a domain manifest.

    Args:
        manifest: Parsed plugin.json content
        bundle_path: Path to the bundle

    Returns:
        Validation result dict
    """
    result = {
        "type": "domain",
        "domain": "",
        "schema_version": "unknown",
        "validation": {
            "manifest": "valid",
            "extensions": {},
            "profiles": {},
        },
        "errors": [],
    }

    # Check schema
    schema_url = manifest.get("$schema", "")
    version = extract_schema_version(schema_url)
    result["schema_version"] = version

    if version not in SUPPORTED_VERSIONS:
        result["errors"].append(f"Unsupported schema version: {version}")
        result["validation"]["manifest"] = "invalid"

    # Check domain field
    domain = manifest.get("domain", {})
    if not isinstance(domain, dict):
        result["errors"].append("'domain' must be an object")
        result["validation"]["manifest"] = "invalid"
        return result

    domain_key = domain.get("key", "")
    result["domain"] = domain_key

    if not domain_key:
        result["errors"].append("Missing 'domain.key'")
        result["validation"]["manifest"] = "invalid"

    if not domain.get("name"):
        result["errors"].append("Missing 'domain.name'")
        result["validation"]["manifest"] = "invalid"

    # Check extensions (optional)
    extensions = manifest.get("extensions", {})
    if extensions:
        for ext_type in ["outline", "triage"]:
            ext_ref = extensions.get(ext_type)
            if ext_ref:
                valid, err = validate_skill_reference(ext_ref)
                if not valid:
                    result["errors"].append(f"Extension '{ext_type}': {err}")
                    result["validation"]["extensions"][ext_type] = "invalid"
                else:
                    exists, err = check_skill_exists(ext_ref, bundle_path)
                    if exists:
                        result["validation"]["extensions"][ext_type] = f"valid ({ext_ref} exists)"
                    else:
                        result["errors"].append(f"Extension '{ext_type}': {err}")
                        result["validation"]["extensions"][ext_type] = "invalid"

    # Check profiles
    profiles = manifest.get("profiles", {})
    if not isinstance(profiles, dict):
        result["errors"].append("'profiles' must be an object")
        result["validation"]["manifest"] = "invalid"
        return result

    # Core profile is required
    if "core" not in profiles:
        result["errors"].append("Missing required profile: 'core'")
        result["validation"]["profiles"]["core"] = "missing"

    # Validate each profile
    for profile_name, profile_data in profiles.items():
        if profile_name not in VALID_PROFILES:
            result["errors"].append(f"Invalid profile name: '{profile_name}'")
            result["validation"]["profiles"][profile_name] = "invalid"
            continue

        profile_errors = validate_profile(profile_data, profile_name)
        if profile_errors:
            result["errors"].extend(profile_errors)
            result["validation"]["profiles"][profile_name] = "invalid"
        else:
            result["validation"]["profiles"][profile_name] = "valid"

    if result["errors"]:
        result["validation"]["manifest"] = "invalid"

    return result


def validate_supplement_manifest(manifest: dict, bundle_path: Path) -> dict:
    """Validate a supplement manifest.

    Args:
        manifest: Parsed plugin.json content
        bundle_path: Path to the bundle

    Returns:
        Validation result dict
    """
    result = {
        "type": "supplement",
        "target_domain": "",
        "schema_version": "unknown",
        "validation": {
            "manifest": "valid",
            "profiles": {},
            "skills_exist": True,
        },
        "errors": [],
    }

    # Check schema
    schema_url = manifest.get("$schema", "")
    version = extract_schema_version(schema_url)
    result["schema_version"] = version

    if version not in SUPPORTED_VERSIONS:
        result["errors"].append(f"Unsupported schema version: {version}")
        result["validation"]["manifest"] = "invalid"

    # Check supplements field
    supplements = manifest.get("supplements", {})
    if not isinstance(supplements, dict):
        result["errors"].append("'supplements' must be an object")
        result["validation"]["manifest"] = "invalid"
        return result

    target_domain = supplements.get("domain", "")
    result["target_domain"] = target_domain

    if not target_domain:
        result["errors"].append("Missing 'supplements.domain'")
        result["validation"]["manifest"] = "invalid"

    # Check skills
    skills = supplements.get("skills", {})
    if not isinstance(skills, dict):
        result["errors"].append("'supplements.skills' must be an object")
        result["validation"]["manifest"] = "invalid"
        return result

    # Validate each profile in skills
    for profile_name, profile_data in skills.items():
        if profile_name not in VALID_PROFILES:
            result["errors"].append(f"Invalid profile name: '{profile_name}'")
            result["validation"]["profiles"][profile_name] = "invalid"
            continue

        if not isinstance(profile_data, dict):
            result["errors"].append(f"Profile '{profile_name}' must be an object")
            result["validation"]["profiles"][profile_name] = "invalid"
            continue

        # Validate skill references
        errors = []
        for skill in profile_data.get("defaults", []):
            valid, err = validate_skill_reference(skill)
            if not valid:
                errors.append(err)
            else:
                exists, err = check_skill_exists(skill, bundle_path)
                if not exists:
                    errors.append(err)
                    result["validation"]["skills_exist"] = False

        for skill in profile_data.get("optionals", []):
            valid, err = validate_skill_reference(skill)
            if not valid:
                errors.append(err)
            else:
                exists, err = check_skill_exists(skill, bundle_path)
                if not exists:
                    errors.append(err)
                    result["validation"]["skills_exist"] = False

        if errors:
            result["errors"].extend(errors)
            result["validation"]["profiles"][profile_name] = "invalid"
        else:
            result["validation"]["profiles"][profile_name] = "valid"

    if result["errors"]:
        result["validation"]["manifest"] = "invalid"

    return result


def cmd_validate(args):
    """Handle 'validate' subcommand."""
    bundle_path = find_bundle_path(args.bundle)

    if bundle_path is None:
        print(f"status: error", file=sys.stderr)
        print(f"error: Bundle not found: {args.bundle}", file=sys.stderr)
        sys.exit(1)

    # Find manifest
    manifest_path = bundle_path / "skills" / "plan-marshall-plugin" / "plugin.json"

    if not manifest_path.exists():
        print(f"status: error", file=sys.stderr)
        print(f"error: No plan-marshall-plugin skill found in bundle: {args.bundle}", file=sys.stderr)
        sys.exit(1)

    # Parse manifest
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        print(f"status: error", file=sys.stderr)
        print(f"error: Invalid JSON in manifest: {e}", file=sys.stderr)
        sys.exit(1)

    # Detect type and validate
    manifest_type = detect_manifest_type(manifest)

    if manifest_type == "domain":
        result = validate_domain_manifest(manifest, bundle_path)
    elif manifest_type == "supplement":
        result = validate_supplement_manifest(manifest, bundle_path)
    else:
        print(f"status: error", file=sys.stderr)
        print(f"error: Unknown manifest type (no 'domain' or 'supplements' field)", file=sys.stderr)
        sys.exit(1)

    # Output in TOON format
    if result["errors"]:
        print("status: error")
    else:
        print("status: success")

    print(f"type: {result['type']}")

    if result["type"] == "domain":
        print(f"domain: {result['domain']}")
    else:
        print(f"target_domain: {result['target_domain']}")

    print(f"schema_version: {result['schema_version']}")
    print("validation:")
    print(f"  manifest: {result['validation']['manifest']}")

    if result["type"] == "domain":
        if result["validation"].get("extensions"):
            print("  extensions:")
            for ext_type, status in result["validation"]["extensions"].items():
                print(f"    {ext_type}: {status}")

    print("  profiles:")
    for profile, status in result["validation"].get("profiles", {}).items():
        print(f"    {profile}: {status}")

    if result["type"] == "supplement":
        print(f"  skills_exist: {str(result['validation']['skills_exist']).lower()}")

    if result["errors"]:
        print("errors:")
        for err in result["errors"]:
            print(f"  - {err}")
        sys.exit(1)

    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Validate domain and supplement manifests"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate subcommand
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a bundle's manifest"
    )
    validate_parser.add_argument(
        "--bundle",
        required=True,
        help="Bundle name to validate"
    )
    validate_parser.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
