"""
Build systems command handlers for plan-marshall-config.

Handles: build-systems
"""

from config_core import (
    EXIT_ERROR,
    MarshalNotInitializedError,
    require_initialized,
    load_config,
    save_config,
    error_exit,
    success_exit,
)
from config_defaults import BUILD_SYSTEM_DEFAULTS
from config_detection import detect_build_systems


def cmd_build_systems(args) -> int:
    """Handle build-systems noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    build_systems = config.get('build_systems', [])

    if args.verb == 'list':
        systems = [{"system": bs.get("system"), "skill": bs.get("skill")} for bs in build_systems]
        return success_exit({"build_systems": systems, "count": len(systems)})

    elif args.verb == 'get':
        system = args.system
        for bs in build_systems:
            if bs.get("system") == system:
                return success_exit({
                    "system": system,
                    "skill": bs.get("skill"),
                    "commands": bs.get("commands", {})
                })
        return error_exit(f"Build system not found: {system}")

    elif args.verb == 'get-command':
        system = args.system
        label = args.label
        for bs in build_systems:
            if bs.get("system") == system:
                commands = bs.get("commands", {})
                if label in commands:
                    return success_exit({
                        "system": system,
                        "label": label,
                        "command": commands[label],
                        "skill": bs.get("skill")
                    })
                return error_exit(f"Command label not found: {label}")
        return error_exit(f"Build system not found: {system}")

    elif args.verb == 'add':
        system = args.system
        for bs in build_systems:
            if bs.get("system") == system:
                return error_exit(f"Build system already exists: {system}")

        if system in BUILD_SYSTEM_DEFAULTS:
            defaults = BUILD_SYSTEM_DEFAULTS[system]
            new_system = {
                "system": system,
                "skill": defaults["skill"]
            }
        else:
            new_system = {
                "system": system,
                "skill": "pm-dev-java:plan-marshall-plugin"
            }

        build_systems.append(new_system)
        config['build_systems'] = build_systems
        save_config(config)
        return success_exit({"system": system, "added": new_system})

    elif args.verb == 'remove':
        system = args.system
        original_count = len(build_systems)
        build_systems = [bs for bs in build_systems if bs.get("system") != system]
        if len(build_systems) == original_count:
            return error_exit(f"Build system not found: {system}")
        config['build_systems'] = build_systems
        save_config(config)
        return success_exit({"system": system, "removed": True})

    elif args.verb == 'detect':
        detected = detect_build_systems()
        # Merge with existing (don't overwrite customizations)
        existing_systems = {bs.get("system") for bs in build_systems}
        for new_bs in detected:
            if new_bs["system"] not in existing_systems:
                build_systems.append(new_bs)
        config['build_systems'] = build_systems
        save_config(config)
        detected_names = [bs["system"] for bs in detected]
        return success_exit({
            "detected": detected_names,
            "count": len(detected_names),
            "total": len(build_systems)
        })

    return EXIT_ERROR
