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


def cmd_init(args) -> int:
    """Handle init command."""
    if is_initialized() and not getattr(args, 'force', False):
        return error_exit("marshal.json already exists. Use --force to overwrite.")

    config = get_default_config()

    # Auto-detect build systems
    detected_bs = detect_build_systems()
    if detected_bs:
        config['build_systems'] = detected_bs

    # Auto-detect technical domains
    detected_domains = detect_domains()
    if detected_domains:
        skill_domains = config.get('skill_domains', {})
        for domain_name, domain_config in detected_domains.items():
            if domain_name not in skill_domains:
                skill_domains[domain_name] = domain_config
        config['skill_domains'] = skill_domains

    save_config(config)
    return success_exit({
        "created": str(MARSHAL_PATH),
        "build_systems_detected": len(detected_bs),
        "domains_detected": list(detected_domains.keys())
    })
