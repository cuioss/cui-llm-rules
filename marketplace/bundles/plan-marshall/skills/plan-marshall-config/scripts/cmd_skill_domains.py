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
from config_defaults import RESERVED_DOMAIN_KEYS
from config_detection import detect_domains


def cmd_skill_domains(args) -> int:
    """Handle skill-domains noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()

    if "skill_domains" not in config:
        return error_exit("skill_domains not configured. Run command /plan-marshall-hq first")

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
            if "workflow_skills" in domain_config:
                result["workflow_skills"] = domain_config["workflow_skills"]
            if "core" in domain_config:
                result["core"] = domain_config["core"]
            if "implementation" in domain_config:
                result["implementation"] = domain_config["implementation"]
            if "testing" in domain_config:
                result["testing"] = domain_config["testing"]
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
        if args.defaults:
            skill_domains[domain]["defaults"] = args.defaults.split(',')
        if args.optionals is not None:
            skill_domains[domain]["optionals"] = args.optionals.split(',') if args.optionals else []
        config['skill_domains'] = skill_domains
        save_config(config)
        return success_exit({
            "domain": domain,
            "updated": skill_domains[domain]
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
            for key in ['core', 'implementation', 'testing']:
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

    Returns domain-agnostic workflow skills for java/javascript domains.
    """
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    skill_domains = config.get('skill_domains', {})

    # Get workflow_skills from first domain that has them (java or javascript)
    workflow_skills = None
    for domain_name in ['java', 'javascript']:
        if domain_name in skill_domains:
            domain_config = skill_domains[domain_name]
            if 'workflow_skills' in domain_config:
                workflow_skills = domain_config['workflow_skills']
                break

    if not workflow_skills:
        return error_exit("No workflow_skills configured in any domain")

    return success_exit({
        "solution_outline": workflow_skills.get("solution_outline", ""),
        "task_plan": workflow_skills.get("task_plan", ""),
        "implementation": workflow_skills.get("implementation", ""),
        "testing": workflow_skills.get("testing", "")
    })


def cmd_resolve_workflow_skill(args) -> int:
    """Resolve workflow skill for domain + phase.

    Returns the specific workflow skill from skill_domains.{domain}.workflow_skills.{phase}

    Phases: solution_outline, task_plan, implementation, testing
    """
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    skill_domains = config.get('skill_domains', {})

    domain = args.domain
    phase = args.phase

    if domain not in skill_domains:
        available = [d for d in skill_domains.keys() if d != 'system']
        return error_exit(f"Unknown domain: {domain}. Available: {', '.join(available)}")

    domain_config = skill_domains[domain]
    workflow_skills = domain_config.get('workflow_skills', {})

    if not workflow_skills:
        return error_exit(f"Domain '{domain}' has no workflow_skills configured")

    if phase not in workflow_skills:
        available = list(workflow_skills.keys())
        return error_exit(f"Unknown phase: {phase} for domain: {domain}. Available: {', '.join(available)}")

    return success_exit({
        "domain": domain,
        "phase": phase,
        "workflow_skill": workflow_skills[phase]
    })
