"""
Init command handler for plan-marshall-config.

Handles: init
"""

from config_core import (
    MARSHAL_PATH,
    is_initialized,
    save_config,
    error_exit,
    success_exit,
)
from config_defaults import get_default_config
from config_detection import detect_build_systems, detect_domains
from cmd_skill_domains import load_domain_config_from_bundle


def cmd_init(args) -> int:
    """Handle init command."""
    if is_initialized() and not getattr(args, 'force', False):
        return error_exit("marshal.json already exists. Use --force to overwrite.")

    config = get_default_config()

    # Auto-detect build systems
    detected_bs = detect_build_systems()
    if detected_bs:
        config['build_systems'] = detected_bs

    # Auto-detect technical domains (returns list of domain keys)
    detected_keys = detect_domains()
    if detected_keys:
        skill_domains = config.get('skill_domains', {})
        for domain_key in detected_keys:
            if domain_key not in skill_domains:
                domain_config = load_domain_config_from_bundle(domain_key)
                if domain_config:
                    skill_domains[domain_key] = domain_config
        config['skill_domains'] = skill_domains

    save_config(config)
    return success_exit({
        "created": str(MARSHAL_PATH),
        "build_systems_detected": len(detected_bs),
        "domains_detected": detected_keys
    })
