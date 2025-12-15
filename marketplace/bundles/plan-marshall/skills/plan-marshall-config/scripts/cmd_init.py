"""
Init command handler for plan-marshall-config.

Handles: init
"""

import json

from config_core import (
    DEFAULTS_TEMPLATE,
    MARSHAL_PATH,
    is_initialized,
    save_config,
    error_exit,
    success_exit,
)
from config_detection import detect_build_systems, detect_domains


def cmd_init(args) -> int:
    """Handle init command."""
    if is_initialized() and not getattr(args, 'force', False):
        return error_exit("marshal.json already exists. Use --force to overwrite.")

    # Copy from template
    if not DEFAULTS_TEMPLATE.exists():
        return error_exit(f"Template not found: {DEFAULTS_TEMPLATE}")

    config = json.loads(DEFAULTS_TEMPLATE.read_text(encoding='utf-8'))

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
