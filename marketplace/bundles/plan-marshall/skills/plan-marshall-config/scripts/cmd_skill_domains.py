"""
Skill domains command handlers for plan-marshall-config.

Handles: skill-domains, resolve-domain-skills, get-workflow-skills
"""

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
    DOMAIN_TEMPLATES,
    BUILD_SYSTEM_TO_DOMAIN,
)
from config_detection import detect_domains


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
            if profile not in domain_config and profile not in ['core', 'architecture', 'planning', 'implementation', 'testing', 'quality']:
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
            for key in ['core', 'architecture', 'planning', 'implementation', 'testing', 'quality']:
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
        detected = detect_domains()
        # Add detected domains to config
        for domain_name, domain_config in detected.items():
            if domain_name not in skill_domains:
                skill_domains[domain_name] = domain_config
        save_config(config)
        detected_names = list(detected.keys())
        return success_exit({
            "detected": detected_names,
            "count": len(detected_names),
            "message": f"Detected domains: {', '.join(detected_names)}" if detected_names else "No domains detected"
        })

    elif args.verb == 'get-available':
        # Read build_systems from marshal.json to determine available domains
        build_systems = config.get('build_systems', [])
        build_system_names = [bs.get('system', '') for bs in build_systems]

        detected = []
        for system in build_system_names:
            if system in BUILD_SYSTEM_TO_DOMAIN:
                domain_key = BUILD_SYSTEM_TO_DOMAIN[system]
                if domain_key not in [d['key'] for d in detected]:
                    detected.append({
                        'key': domain_key,
                        'name': f"{domain_key.title()} Development",
                        'build_system': system
                    })

        # Optional domains (always available)
        optional = [
            {'key': 'requirements', 'name': 'Requirements Engineering'},
            {'key': 'documentation', 'name': 'Documentation'},
        ]

        return success_exit({
            'detected_domains': detected,
            'optional_domains': optional
        })

    elif args.verb == 'configure':
        import copy
        selected_domains = [d.strip() for d in args.domains.split(',') if d.strip()]

        # Always add system domain with workflow_skills
        skill_domains['system'] = copy.deepcopy(DEFAULT_SYSTEM_DOMAIN)

        # Apply domain templates for each selected domain
        domains_configured = []
        for domain_key in selected_domains:
            if domain_key in DOMAIN_TEMPLATES:
                skill_domains[domain_key] = copy.deepcopy(DOMAIN_TEMPLATES[domain_key])
                domains_configured.append(domain_key)

        config['skill_domains'] = skill_domains
        save_config(config)

        return success_exit({
            'system_domain': 'configured',
            'domains_configured': len(domains_configured),
            'domains': ','.join(domains_configured)
        })

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
