"""
Skill domains command handlers for plan-marshall-config.

Handles: skill-domains, resolve-domain-skills, get-workflow-skills

Domain discovery uses extension.py files in each bundle's plan-marshall-plugin skill.
Extension API functions:
- get_skill_domains() -> domain metadata with profiles
- get_domain_supplements() -> supplement metadata (for supplement bundles)
- provides_triage() -> triage skill reference or None
- provides_outline() -> outline skill reference or None
"""

import copy
import importlib.util
import os
import sys
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


def get_marketplace_bundles_path() -> Path:
    """Get the path to marketplace bundles directory.

    Searches for marketplace bundles in:
    1. Source: marketplace/bundles relative to script (development)
    2. Cache: ~/.claude/plugins/cache/plan-marshall (installed)

    Returns:
        Path to bundles directory
    """
    script_path = Path(__file__).resolve()

    # Try to find marketplace/bundles by walking up from script location
    current = script_path.parent
    for _ in range(10):  # Safety limit
        candidate = current / "bundles"
        if candidate.is_dir() and (candidate / "plan-marshall").is_dir():
            return candidate
        if current.name == "bundles" and (current / "plan-marshall").is_dir():
            return current
        current = current.parent
        if current == current.parent:
            break

    # Fallback: check plugin cache
    cache_path = get_plugin_cache_path()
    if cache_path.is_dir():
        return cache_path

    return script_path.parent.parent.parent.parent.parent / "bundles"


def load_extension_module(extension_path: Path, bundle_name: str):
    """Load an extension.py module dynamically.

    Args:
        extension_path: Path to extension.py file
        bundle_name: Name of the bundle for module naming

    Returns:
        Loaded module or None if failed
    """
    try:
        spec = importlib.util.spec_from_file_location(
            f"extension_{bundle_name}",
            extension_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Warning: Failed to load extension from {bundle_name}: {e}", file=sys.stderr)
        return None


def discover_all_extensions() -> list:
    """Discover all extension.py files in bundles.

    Scans all bundles for extension.py files in skills/plan-marshall-plugin/

    Returns:
        List of dicts with extension info: {bundle, path, module}
    """
    extensions = []
    bundles_path = get_marketplace_bundles_path()

    if not bundles_path.is_dir():
        return extensions

    for bundle_dir in bundles_path.iterdir():
        if not bundle_dir.is_dir() or bundle_dir.name.startswith('.'):
            continue

        # Try direct path first (source structure)
        extension_path = bundle_dir / "skills" / "plan-marshall-plugin" / "extension.py"

        # Try versioned path (cache structure from rsync)
        if not extension_path.exists():
            for version_dir in bundle_dir.iterdir():
                if version_dir.is_dir() and not version_dir.name.startswith('.'):
                    versioned_path = version_dir / "skills" / "plan-marshall-plugin" / "extension.py"
                    if versioned_path.exists():
                        extension_path = versioned_path
                        break

        if not extension_path.exists():
            continue

        module = load_extension_module(extension_path, bundle_dir.name)
        if module:
            extensions.append({
                "bundle": bundle_dir.name,
                "path": str(extension_path),
                "module": module
            })

    return extensions


def discover_available_domains() -> dict:
    """Discover domains and supplements from extension.py files.

    Returns dict with 'domains' and 'supplements' lists.
    """
    extensions = discover_all_extensions()
    domains = []
    supplements = []

    for ext in extensions:
        module = ext.get("module")
        if not module:
            continue

        # Check for domain (has get_skill_domains with domain.key)
        if hasattr(module, 'get_skill_domains'):
            try:
                domain_info = module.get_skill_domains()
                if domain_info and isinstance(domain_info.get("domain"), dict):
                    domain_data = domain_info["domain"]
                    has_triage = False
                    has_outline = False

                    # Check for extension functions
                    if hasattr(module, 'provides_triage'):
                        has_triage = module.provides_triage() is not None
                    if hasattr(module, 'provides_outline'):
                        has_outline = module.provides_outline() is not None

                    domains.append({
                        "key": domain_data.get("key", ""),
                        "name": domain_data.get("name", ""),
                        "description": domain_data.get("description", ""),
                        "bundle": ext["bundle"],
                        "has_triage": has_triage,
                        "has_outline": has_outline
                    })
            except Exception as e:
                print(f"Warning: Failed to get domains from {ext['bundle']}: {e}", file=sys.stderr)

        # Check for supplement (has get_domain_supplements)
        if hasattr(module, 'get_domain_supplements'):
            try:
                supplement_info = module.get_domain_supplements()
                if supplement_info and supplement_info.get("domain"):
                    supplements.append({
                        "domain": supplement_info.get("domain", ""),
                        "bundle": ext["bundle"],
                        "description": supplement_info.get("description", "")
                    })
            except Exception as e:
                print(f"Warning: Failed to get supplements from {ext['bundle']}: {e}", file=sys.stderr)

    return {"domains": domains, "supplements": supplements}


def load_domain_config_from_bundle(domain_key: str) -> dict | None:
    """Load domain configuration from bundle's extension.py.

    Args:
        domain_key: Domain key to look for (e.g., 'java', 'javascript')

    Returns:
        Domain config dict or None if not found
    """
    extensions = discover_all_extensions()

    for ext in extensions:
        module = ext.get("module")
        if not module or not hasattr(module, 'get_skill_domains'):
            continue

        try:
            domain_info = module.get_skill_domains()
            if not domain_info:
                continue

            domain_data = domain_info.get("domain", {})
            if isinstance(domain_data, dict) and domain_data.get("key") == domain_key:
                return convert_extension_to_domain_config(module, domain_info)
        except Exception:
            continue

    return None


def load_supplement_from_bundle(bundle_name: str) -> dict | None:
    """Load supplement configuration from bundle's extension.py.

    Args:
        bundle_name: Name of the bundle (e.g., 'pm-dev-java-cui')

    Returns:
        Supplement dict or None if not found
    """
    extensions = discover_all_extensions()

    for ext in extensions:
        if ext["bundle"] != bundle_name:
            continue

        module = ext.get("module")
        if not module or not hasattr(module, 'get_domain_supplements'):
            continue

        try:
            return module.get_domain_supplements()
        except Exception:
            pass

    return None


def convert_extension_to_domain_config(module, domain_info: dict) -> dict:
    """Convert extension.py data to skill_domains config format.

    Args:
        module: Loaded extension module
        domain_info: Result from get_skill_domains()

    Returns:
        Config dict compatible with marshal.json skill_domains
    """
    config = {}

    # Extract extensions from dedicated functions
    if hasattr(module, 'provides_triage') or hasattr(module, 'provides_outline'):
        config["workflow_skill_extensions"] = {}
        if hasattr(module, 'provides_outline'):
            outline = module.provides_outline()
            if outline:
                config["workflow_skill_extensions"]["outline"] = outline
        if hasattr(module, 'provides_triage'):
            triage = module.provides_triage()
            if triage:
                config["workflow_skill_extensions"]["triage"] = triage

    # Extract profiles
    profiles = domain_info.get("profiles", {})
    for profile_name in ["core", "implementation", "testing", "quality"]:
        if profile_name in profiles:
            config[profile_name] = {
                "defaults": profiles[profile_name].get("defaults", []),
                "optionals": profiles[profile_name].get("optionals", [])
            }

    return config


def merge_supplement_config(domain_config: dict, supplement_data: dict) -> dict:
    """Merge supplement skills into domain config as optionals.

    Args:
        domain_config: Existing domain configuration
        supplement_data: Supplement data from get_domain_supplements()

    Returns:
        Updated domain config with merged supplement skills
    """
    merged = copy.deepcopy(domain_config)

    supplement_profiles = supplement_data.get("profiles", {})

    for profile_name in ["core", "implementation", "testing", "quality"]:
        if profile_name in supplement_profiles:
            profile_data = supplement_profiles[profile_name]

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
        selected_domains = [d.strip() for d in args.domains.split(',') if d.strip()]
        selected_supplements = []
        if hasattr(args, 'supplements') and args.supplements:
            selected_supplements = [s.strip() for s in args.supplements.split(',') if s.strip()]

        # Always add system domain with workflow_skills
        skill_domains['system'] = copy.deepcopy(DEFAULT_SYSTEM_DOMAIN)

        # Apply domain config for each selected domain from bundle extension.py
        domains_configured = []
        domains_not_found = []

        for domain_key in selected_domains:
            # Load from bundle extension.py (returns converted config directly)
            domain_config = load_domain_config_from_bundle(domain_key)
            if domain_config:
                skill_domains[domain_key] = domain_config
                domains_configured.append(domain_key)
            else:
                domains_not_found.append(domain_key)

        # Apply supplements to their target domains
        supplements_applied = []
        for supplement_bundle in selected_supplements:
            supplement_data = load_supplement_from_bundle(supplement_bundle)
            if supplement_data:
                target_domain = supplement_data.get("domain")
                if target_domain and target_domain in skill_domains:
                    skill_domains[target_domain] = merge_supplement_config(
                        skill_domains[target_domain],
                        supplement_data
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
