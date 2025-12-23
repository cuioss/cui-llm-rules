"""
Skill domains command handlers for plan-marshall-config.

Handles: skill-domains, resolve-domain-skills, get-workflow-skills
"""

import json
import os
import subprocess
from pathlib import Path

from config_core import (
    EXIT_ERROR,
    MarshalNotInitializedError,
    require_initialized,
    load_config,
    save_config,
    error_exit,
    success_exit,
    get_skill_description,
    is_nested_domain,
)
from config_defaults import (
    RESERVED_DOMAIN_KEYS,
    DEFAULT_SYSTEM_DOMAIN,
)
from config_detection import detect_domains


def get_plugin_cache_path() -> Path:
    """Get the plugin cache path."""
    env_path = os.environ.get("PLUGIN_CACHE_PATH")
    if env_path:
        return Path(env_path)
    return Path.home() / ".claude" / "plugins" / "cache" / "plan-marshall"


def discover_available_domains() -> dict:
    """Call discover_domains.py and parse TOON output.

    Returns dict with 'domains' and 'supplements' lists.
    """
    plugin_cache = get_plugin_cache_path()

    # Find the discover_domains.py script
    # Try non-versioned path first (standard structure)
    script_path = plugin_cache / "plan-marshall" / "skills" / "domain-extension-api" / "scripts" / "discover_domains.py"
    if not script_path.exists():
        # Fall back to versioned path
        script_path = plugin_cache / "plan-marshall" / "1.0.0" / "skills" / "domain-extension-api" / "scripts" / "discover_domains.py"

    if not script_path.exists():
        return {"domains": [], "supplements": [], "error": "discover_domains.py not found"}

    try:
        result = subprocess.run(
            ["python3", str(script_path), "discover"],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "PLUGIN_CACHE_PATH": str(plugin_cache)}
        )
        if result.returncode != 0:
            return {"domains": [], "supplements": [], "error": result.stderr}

        # Parse TOON output
        return parse_discover_toon_output(result.stdout)
    except subprocess.TimeoutExpired:
        return {"domains": [], "supplements": [], "error": "Discovery timed out"}
    except Exception as e:
        return {"domains": [], "supplements": [], "error": str(e)}


def parse_discover_toon_output(output: str) -> dict:
    """Parse TOON output from discover_domains.py.

    Expected format:
    status: success
    domains_found: N
    supplements_found: M

    domains[N]{key,name,bundle,has_outline,has_triage}:
    java\tJava Development\tpm-dev-java\ttrue\ttrue
    ...

    supplements[M]{domain,bundle,description}:
    java\tpm-dev-java-cui\tCUI-specific Java patterns
    ...
    """
    domains = []
    supplements = []
    current_section = None

    for line in output.strip().split("\n"):
        line = line.strip()
        if not line:
            current_section = None
            continue

        # Detect section headers
        if line.startswith("domains[") and "]{" in line:
            current_section = "domains"
            continue
        elif line.startswith("supplements[") and "]{" in line:
            current_section = "supplements"
            continue
        elif ":" in line and "\t" not in line:
            # Header line like "status: success"
            continue

        # Parse data rows
        if current_section == "domains" and "\t" in line:
            parts = line.split("\t")
            if len(parts) >= 5:
                domains.append({
                    "key": parts[0],
                    "name": parts[1],
                    "bundle": parts[2],
                    "has_outline": parts[3] == "true",
                    "has_triage": parts[4] == "true"
                })
        elif current_section == "supplements" and "\t" in line:
            parts = line.split("\t")
            if len(parts) >= 3:
                supplements.append({
                    "domain": parts[0],
                    "bundle": parts[1],
                    "description": parts[2]
                })

    return {"domains": domains, "supplements": supplements}


def load_domain_config_from_bundle(domain_key: str) -> dict | None:
    """Load domain configuration from bundle's plan-marshall-plugin manifest.

    Args:
        domain_key: Domain key to look for (e.g., 'java', 'javascript')

    Returns:
        Domain config dict or None if not found
    """
    discovery = discover_available_domains()
    domains = discovery.get("domains", [])

    # Find the bundle for this domain
    for domain in domains:
        if domain.get("key") == domain_key:
            bundle_name = domain.get("bundle")
            if bundle_name:
                return load_manifest_from_bundle(bundle_name)
    return None


def load_manifest_from_bundle(bundle_name: str) -> dict | None:
    """Load plan-marshall-plugin manifest from a bundle.

    Args:
        bundle_name: Name of the bundle (e.g., 'pm-dev-java')

    Returns:
        Manifest dict or None if not found
    """
    plugin_cache = get_plugin_cache_path()

    # Try non-versioned path first
    manifest_path = plugin_cache / bundle_name / "skills" / "plan-marshall-plugin" / "plugin.json"
    if not manifest_path.exists():
        # Try versioned path
        manifest_path = plugin_cache / bundle_name / "1.0.0" / "skills" / "plan-marshall-plugin" / "plugin.json"

    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def convert_manifest_to_domain_config(manifest: dict) -> dict:
    """Convert bundle manifest to skill_domains config format.

    Args:
        manifest: Domain manifest from plugin.json

    Returns:
        Config dict compatible with marshal.json skill_domains
    """
    config = {}

    # Extract extensions
    extensions = manifest.get("extensions", {})
    if extensions:
        config["workflow_skill_extensions"] = {}
        if "outline" in extensions:
            config["workflow_skill_extensions"]["outline"] = extensions["outline"]
        if "triage" in extensions:
            config["workflow_skill_extensions"]["triage"] = extensions["triage"]

    # Extract profiles
    profiles = manifest.get("profiles", {})
    for profile_name in ["core", "implementation", "testing", "quality"]:
        if profile_name in profiles:
            config[profile_name] = {
                "defaults": profiles[profile_name].get("defaults", []),
                "optionals": profiles[profile_name].get("optionals", [])
            }

    return config


def merge_supplement_config(domain_config: dict, supplement_manifest: dict) -> dict:
    """Merge supplement skills into domain config as optionals.

    Args:
        domain_config: Existing domain configuration
        supplement_manifest: Supplement manifest from plugin.json

    Returns:
        Updated domain config with merged supplement skills
    """
    import copy
    merged = copy.deepcopy(domain_config)

    supplements = supplement_manifest.get("supplements", {})
    supplement_skills = supplements.get("skills", {})

    for profile_name in ["core", "implementation", "testing", "quality"]:
        if profile_name in supplement_skills:
            profile_data = supplement_skills[profile_name]

            # Ensure profile exists in merged config
            if profile_name not in merged:
                merged[profile_name] = {"defaults": [], "optionals": []}

            # Add defaults from supplement as optionals (supplements shouldn't force defaults)
            supplement_defaults = profile_data.get("defaults", [])
            supplement_optionals = profile_data.get("optionals", [])

            # Merge into optionals, avoiding duplicates
            existing_optionals = set(merged[profile_name].get("optionals", []))
            for skill in supplement_defaults + supplement_optionals:
                if skill not in existing_optionals:
                    merged[profile_name]["optionals"].append(skill)

    return merged


def cmd_skill_domains(args) -> int:
    """Handle skill-domains noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()

    if "skill_domains" not in config:
        return error_exit("skill_domains not configured. Run command /marshall-steward first")

    skill_domains = config.get('skill_domains', {})

    if args.verb == 'list':
        domains = list(skill_domains.keys())
        return success_exit({"domains": domains, "count": len(domains)})

    elif args.verb == 'get':
        domain = args.domain
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        domain_config = skill_domains[domain]

        # Check if nested structure (has core or workflow_skills)
        if is_nested_domain(domain_config):
            result = {"domain": domain}
            # Include workflow_skills if present
            if "workflow_skills" in domain_config:
                result["workflow_skills"] = domain_config["workflow_skills"]
            # Include workflow_skill_extensions if present
            if "workflow_skill_extensions" in domain_config:
                result["workflow_skill_extensions"] = domain_config["workflow_skill_extensions"]
            # Include top-level defaults/optionals if present (system domain)
            if "defaults" in domain_config:
                result["defaults"] = domain_config["defaults"]
            if "optionals" in domain_config:
                result["optionals"] = domain_config["optionals"]
            # Include profile blocks
            if "core" in domain_config:
                result["core"] = domain_config["core"]
            if "architecture" in domain_config:
                result["architecture"] = domain_config["architecture"]
            if "planning" in domain_config:
                result["planning"] = domain_config["planning"]
            if "implementation" in domain_config:
                result["implementation"] = domain_config["implementation"]
            if "testing" in domain_config:
                result["testing"] = domain_config["testing"]
            if "quality" in domain_config:
                result["quality"] = domain_config["quality"]
            return success_exit(result)
        else:
            # Flat structure (backward compatible)
            return success_exit({
                "domain": domain,
                "defaults": domain_config.get("defaults", []),
                "optionals": domain_config.get("optionals", [])
            })

    elif args.verb == 'get-defaults':
        domain = args.domain
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        domain_config = skill_domains[domain]
        # For nested structure, return core.defaults
        if is_nested_domain(domain_config):
            defaults = domain_config.get("core", {}).get("defaults", [])
        else:
            defaults = domain_config.get("defaults", [])
        return success_exit({"domain": domain, "defaults": defaults})

    elif args.verb == 'get-optionals':
        domain = args.domain
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        domain_config = skill_domains[domain]
        # For nested structure, return core.optionals
        if is_nested_domain(domain_config):
            optionals = domain_config.get("core", {}).get("optionals", [])
        else:
            optionals = domain_config.get("optionals", [])
        return success_exit({"domain": domain, "optionals": optionals})

    elif args.verb == 'set':
        domain = args.domain
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}. Use 'add' to create new domain.")

        domain_config = skill_domains[domain]
        profile = getattr(args, 'profile', None)

        if profile:
            # Profile-based update
            if not is_nested_domain(domain_config):
                return error_exit(f"Domain '{domain}' uses flat structure. Cannot set profile.")
            if profile not in domain_config and profile not in ['core', 'implementation', 'testing', 'quality']:
                return error_exit(f"Unknown profile: {profile}")
            # Initialize profile if not exists
            if profile not in domain_config:
                domain_config[profile] = {"defaults": [], "optionals": []}
            if args.defaults:
                domain_config[profile]["defaults"] = args.defaults.split(',')
            if args.optionals is not None:
                domain_config[profile]["optionals"] = args.optionals.split(',') if args.optionals else []
            skill_domains[domain] = domain_config
        else:
            # Flat structure update (backward compatible)
            if args.defaults:
                skill_domains[domain]["defaults"] = args.defaults.split(',')
            if args.optionals is not None:
                skill_domains[domain]["optionals"] = args.optionals.split(',') if args.optionals else []

        config['skill_domains'] = skill_domains
        save_config(config)
        return success_exit({
            "domain": domain,
            "profile": profile,
            "updated": skill_domains[domain] if not profile else skill_domains[domain].get(profile, {})
        })

    elif args.verb == 'get-extensions':
        domain = args.domain
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        domain_config = skill_domains[domain]
        extensions = domain_config.get('workflow_skill_extensions', {})
        return success_exit({
            "domain": domain,
            "extensions": extensions
        })

    elif args.verb == 'set-extensions':
        domain = args.domain
        ext_type = args.type
        skill = args.skill
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        domain_config = skill_domains[domain]
        if 'workflow_skill_extensions' not in domain_config:
            domain_config['workflow_skill_extensions'] = {}
        domain_config['workflow_skill_extensions'][ext_type] = skill
        skill_domains[domain] = domain_config
        config['skill_domains'] = skill_domains
        save_config(config)
        return success_exit({
            "domain": domain,
            "type": ext_type,
            "skill": skill
        })

    elif args.verb == 'add':
        domain = args.domain
        if domain in skill_domains:
            return error_exit(f"Domain already exists: {domain}")
        defaults = args.defaults.split(',') if args.defaults else []
        optionals = args.optionals.split(',') if args.optionals else []
        skill_domains[domain] = {"defaults": defaults, "optionals": optionals}
        config['skill_domains'] = skill_domains
        save_config(config)
        return success_exit({
            "domain": domain,
            "added": skill_domains[domain]
        })

    elif args.verb == 'validate':
        domain = args.domain
        skill = args.skill
        if domain not in skill_domains:
            return error_exit(f"Unknown domain: {domain}")
        domain_config = skill_domains[domain]

        # Handle nested structure
        if is_nested_domain(domain_config):
            # Collect all defaults and optionals across all profiles
            all_defaults = []
            all_optionals = []
            for key in ['core', 'implementation', 'testing', 'quality']:
                if key in domain_config:
                    all_defaults.extend(domain_config[key].get("defaults", []))
                    all_optionals.extend(domain_config[key].get("optionals", []))
            valid = skill in all_defaults or skill in all_optionals
            return success_exit({
                "domain": domain,
                "skill": skill,
                "valid": valid,
                "in_defaults": skill in all_defaults,
                "in_optionals": skill in all_optionals
            })
        else:
            # Flat structure
            all_skills = domain_config.get("defaults", []) + domain_config.get("optionals", [])
            valid = skill in all_skills
            return success_exit({
                "domain": domain,
                "skill": skill,
                "valid": valid,
                "in_defaults": skill in domain_config.get("defaults", []),
                "in_optionals": skill in domain_config.get("optionals", [])
            })

    elif args.verb == 'detect':
        detected_keys = detect_domains()  # Returns list of domain keys
        # Load configs from discovery for detected domains
        for domain_key in detected_keys:
            if domain_key not in skill_domains:
                domain_config = load_domain_config_from_bundle(domain_key)
                if domain_config:
                    skill_domains[domain_key] = domain_config
        save_config(config)
        return success_exit({
            "detected": detected_keys,
            "count": len(detected_keys),
            "message": f"Detected domains: {', '.join(detected_keys)}" if detected_keys else "No domains detected"
        })

    elif args.verb == 'get-available':
        # Use dynamic discovery to find available domains and supplements
        discovery = discover_available_domains()

        result = {
            'discovered_domains': discovery.get("domains", []),
            'supplements': discovery.get("supplements", [])
        }
        if "error" in discovery and discovery["error"]:
            result['error'] = discovery["error"]

        return success_exit(result)

    elif args.verb == 'configure':
        import copy
        selected_domains = [d.strip() for d in args.domains.split(',') if d.strip()]
        selected_supplements = []
        if hasattr(args, 'supplements') and args.supplements:
            selected_supplements = [s.strip() for s in args.supplements.split(',') if s.strip()]

        # Always add system domain with workflow_skills
        skill_domains['system'] = copy.deepcopy(DEFAULT_SYSTEM_DOMAIN)

        # Apply domain config for each selected domain from bundle manifests
        domains_configured = []
        domains_not_found = []

        for domain_key in selected_domains:
            # Load from bundle manifest
            manifest = load_domain_config_from_bundle(domain_key)
            if manifest:
                domain_config = convert_manifest_to_domain_config(manifest)
                skill_domains[domain_key] = domain_config
                domains_configured.append(domain_key)
            else:
                domains_not_found.append(domain_key)

        # Apply supplements to their target domains
        supplements_applied = []
        for supplement_bundle in selected_supplements:
            supplement_manifest = load_manifest_from_bundle(supplement_bundle)
            if supplement_manifest and "supplements" in supplement_manifest:
                target_domain = supplement_manifest["supplements"].get("domain")
                if target_domain and target_domain in skill_domains:
                    skill_domains[target_domain] = merge_supplement_config(
                        skill_domains[target_domain],
                        supplement_manifest
                    )
                    supplements_applied.append(f"{supplement_bundle}→{target_domain}")

        config['skill_domains'] = skill_domains
        save_config(config)

        result = {
            'system_domain': 'configured',
            'domains_configured': len(domains_configured),
            'domains': ','.join(domains_configured)
        }
        if domains_not_found:
            result['domains_not_found'] = ','.join(domains_not_found)
        if supplements_applied:
            result['supplements_applied'] = ','.join(supplements_applied)

        return success_exit(result)

    return EXIT_ERROR


def cmd_resolve_domain_skills(args) -> int:
    """Handle resolve-domain-skills command.

    Aggregates {domain}.core + {domain}.{profile} skills with descriptions.
    """
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    skill_domains = config.get('skill_domains', {})

    domain = args.domain
    profile = args.profile

    # Validate domain exists and has nested structure
    if domain not in skill_domains:
        return error_exit(f"Unknown domain: {domain}")

    domain_config = skill_domains[domain]

    if not is_nested_domain(domain_config):
        return error_exit(f"Domain '{domain}' does not support profiles (flat structure)")

    # Validate profile exists in domain config (profile = any key except reserved keys)
    valid_profiles = [k for k in domain_config.keys() if k not in RESERVED_DOMAIN_KEYS]
    if profile not in domain_config or profile in RESERVED_DOMAIN_KEYS:
        return error_exit(f"Unknown profile: {profile} for domain: {domain}. Available profiles: {', '.join(valid_profiles)}")

    # Aggregate: {domain}.core + {domain}.{profile}
    core_config = domain_config.get('core', {})
    profile_config = domain_config.get(profile, {})

    defaults = core_config.get('defaults', []) + profile_config.get('defaults', [])
    optionals = core_config.get('optionals', []) + profile_config.get('optionals', [])

    # Build output with descriptions
    defaults_with_desc = {skill: get_skill_description(skill) for skill in defaults}
    optionals_with_desc = {skill: get_skill_description(skill) for skill in optionals}

    return success_exit({
        "domain": domain,
        "profile": profile,
        "defaults": defaults_with_desc,
        "optionals": optionals_with_desc
    })


def cmd_get_workflow_skills(args) -> int:
    """Handle get-workflow-skills command.

    Returns all workflow skills from the system domain (5-phase model).
    """
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    skill_domains = config.get('skill_domains', {})

    # Get workflow_skills from system domain
    if 'system' not in skill_domains:
        return error_exit("System domain not configured. Run /marshall-steward to initialize.")

    system_config = skill_domains['system']
    workflow_skills = system_config.get('workflow_skills', {})

    if not workflow_skills:
        return error_exit("System domain has no workflow_skills configured")

    return success_exit({
        "init": workflow_skills.get("init", ""),
        "outline": workflow_skills.get("outline", ""),
        "plan": workflow_skills.get("plan", ""),
        "execute": workflow_skills.get("execute", ""),
        "finalize": workflow_skills.get("finalize", "")
    })


def cmd_resolve_workflow_skill(args) -> int:
    """Resolve system workflow skill for a phase.

    Always returns the system workflow skill from skill_domains.system.workflow_skills.{phase}.
    Domain-specific behavior is provided by extensions loaded via resolve-workflow-skill-extension.

    Phases: init, outline, plan, execute, finalize
    """
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    skill_domains = config.get('skill_domains', {})

    phase = args.phase

    # Always use system domain for workflow skills
    if 'system' not in skill_domains:
        return error_exit("System domain not configured. Run /marshall-steward to initialize.")

    system_config = skill_domains['system']
    workflow_skills = system_config.get('workflow_skills', {})

    if not workflow_skills:
        return error_exit("System domain has no workflow_skills configured")

    if phase not in workflow_skills:
        available = list(workflow_skills.keys())
        return error_exit(f"Unknown phase: {phase}. Available: {', '.join(available)}")

    return success_exit({
        "phase": phase,
        "workflow_skill": workflow_skills[phase]
    })


def cmd_resolve_workflow_skill_extension(args) -> int:
    """Resolve workflow skill extension for a domain and type.

    Returns the extension skill from skill_domains.{domain}.workflow_skill_extensions.{type}.
    Returns null for extension field if domain has no extension of that type.

    Extension types: outline (for solution-outline phase), triage (for plan-finalize phase)
    """
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    skill_domains = config.get('skill_domains', {})

    domain = args.domain
    ext_type = args.type

    # Return null extension if domain doesn't exist (not an error)
    if domain not in skill_domains:
        return success_exit({
            "domain": domain,
            "type": ext_type,
            "extension": None
        })

    domain_config = skill_domains[domain]
    extensions = domain_config.get('workflow_skill_extensions', {})
    extension = extensions.get(ext_type)  # None if not present

    return success_exit({
        "domain": domain,
        "type": ext_type,
        "extension": extension
    })
