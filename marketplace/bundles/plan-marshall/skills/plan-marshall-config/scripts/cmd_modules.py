"""
Modules command handlers for plan-marshall-config.

Handles: modules
"""

import json
from pathlib import Path

from config_core import (
    EXIT_ERROR,
    MarshalNotInitializedError,
    require_initialized,
    load_config,
    save_config,
    error_exit,
    success_exit,
)
from config_detection import detect_maven_modules


def infer_domains_from_module(module_path: str) -> list:
    """Infer skill domains from module content.

    Detection is based on:
    - pom.xml / build.gradle -> java
    - package.json -> javascript
    - *.java files with 'test' in path -> java-testing
    - *.js/*.ts files with 'test' or 'spec' -> javascript-testing
    - e2e/playwright/cypress in path -> javascript-testing
    """
    domains = []
    path = Path(module_path)

    if not path.exists():
        return domains

    # Check for build files (primary indicators)
    has_maven = (path / 'pom.xml').exists()
    has_gradle = (path / 'build.gradle').exists() or (path / 'build.gradle.kts').exists()
    has_npm = (path / 'package.json').exists()

    # Check for Java source files
    has_java = list(path.rglob('*.java'))
    has_test_java = any('test' in str(f).lower() for f in has_java)

    # Check for JavaScript/TypeScript source files
    has_js = list(path.rglob('*.js')) + list(path.rglob('*.ts'))
    has_test_js = any('test' in str(f).lower() or 'spec' in str(f).lower() for f in has_js)

    # Determine Java domains
    if has_maven or has_gradle or has_java:
        if has_test_java:
            domains.append('java-testing')
        else:
            domains.append('java')

    # Determine JavaScript domains
    if has_npm or has_js:
        if has_test_js:
            domains.append('javascript-testing')
        else:
            domains.append('javascript')

    # If path contains 'test' or 'e2e', mark as testing
    path_lower = str(path).lower()
    if 'e2e' in path_lower or 'playwright' in path_lower or 'cypress' in path_lower:
        if 'javascript-testing' not in domains and 'javascript' not in domains:
            domains.append('javascript-testing')
        elif 'javascript' in domains:
            domains.remove('javascript')
            domains.append('javascript-testing')

    return domains if domains else ['java']  # Default to java


def infer_build_systems_from_module(module_path: str) -> list:
    """Infer build systems from module files."""
    build_systems = []
    path = Path(module_path)

    if not path.exists():
        return build_systems

    if (path / 'pom.xml').exists():
        build_systems.append('maven')
    if (path / 'build.gradle').exists() or (path / 'build.gradle.kts').exists():
        build_systems.append('gradle')
    if (path / 'package.json').exists():
        build_systems.append('npm')

    return build_systems if build_systems else ['maven']


def cmd_modules(args) -> int:
    """Handle modules noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    modules = config.get('modules', {})

    if args.verb == 'list':
        module_list = []
        for name, mod_config in modules.items():
            module_list.append({
                "name": name,
                "path": mod_config.get("path", name),
                "domains": mod_config.get("domains", []),
                "build_systems": mod_config.get("build_systems", [])
            })
        return success_exit({"modules": module_list, "count": len(module_list)})

    elif args.verb == 'get':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")
        mod_config = modules[module]
        return success_exit({
            "module": module,
            "path": mod_config.get("path", module),
            "domains": mod_config.get("domains", []),
            "build_systems": mod_config.get("build_systems", []),
            "commands": mod_config.get("commands", {})
        })

    elif args.verb == 'get-domains':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")
        domains = modules[module].get("domains", [])
        return success_exit({"module": module, "domains": domains})

    elif args.verb == 'get-build-systems':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")
        build_systems = modules[module].get("build_systems", [])
        return success_exit({"module": module, "build_systems": build_systems})

    elif args.verb == 'get-command':
        module = args.module
        label = args.label

        if module not in modules:
            return error_exit(f"Unknown module: {module}")

        mod_config = modules[module]

        # Static routing: check module commands directly (label -> full command string)
        if "commands" in mod_config and label in mod_config["commands"]:
            return success_exit({
                "module": module,
                "label": label,
                "command": mod_config["commands"][label],
                "source": "module"
            })

        # Fall back to default module
        if "default" in modules and module != "default":
            default_config = modules["default"]
            if "commands" in default_config and label in default_config["commands"]:
                return success_exit({
                    "module": module,
                    "label": label,
                    "command": default_config["commands"][label],
                    "source": "default"
                })

        return error_exit(f"Command not found: {module}.{label}")

    elif args.verb == 'set-command':
        module = args.module
        label = args.label
        command = args.command

        if module not in modules:
            return error_exit(f"Unknown module: {module}")

        mod_config = modules[module]

        # Initialize commands dict if needed
        if "commands" not in mod_config:
            mod_config["commands"] = {}

        mod_config["commands"][label] = command
        config['modules'] = modules
        save_config(config)

        return success_exit({
            "module": module,
            "label": label,
            "command": command,
            "action": "set"
        })

    elif args.verb == 'add':
        module = args.module
        if module in modules:
            return error_exit(f"Module already exists: {module}")

        path = args.path if args.path else module
        domains = args.domains.split(',') if args.domains else []
        build_systems_list = args.build_systems.split(',') if args.build_systems else []

        modules[module] = {
            "path": path,
            "domains": domains,
            "build_systems": build_systems_list
        }
        config['modules'] = modules
        save_config(config)
        return success_exit({"module": module, "added": modules[module]})

    elif args.verb == 'set':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")

        if args.domains:
            modules[module]["domains"] = args.domains.split(',')
        if args.build_systems:
            modules[module]["build_systems"] = args.build_systems.split(',')

        config['modules'] = modules
        save_config(config)
        return success_exit({"module": module, "updated": modules[module]})

    elif args.verb == 'remove':
        module = args.module
        if module not in modules:
            return error_exit(f"Unknown module: {module}")

        removed = modules.pop(module)
        config['modules'] = modules
        save_config(config)
        return success_exit({"module": module, "removed": removed})

    elif args.verb == 'detect':
        detected = []

        # Detect Maven modules
        maven_modules = detect_maven_modules()
        for mod_info in maven_modules:
            mod_path = mod_info["path"]
            mod_name = mod_info["name"]
            domains = infer_domains_from_module(mod_path)
            build_systems_list = infer_build_systems_from_module(mod_path)

            if mod_name not in modules:
                modules[mod_name] = {
                    "path": mod_path,
                    "domains": domains,
                    "build_systems": build_systems_list
                }
                detected.append(mod_name)

        config['modules'] = modules
        save_config(config)
        return success_exit({
            "detected": detected,
            "count": len(detected),
            "total_modules": len(modules)
        })

    elif args.verb == 'persist-all':
        # Replace entire modules section with provided JSON
        # Used by build_env.py to persist detected modules with commands
        try:
            new_modules = json.loads(args.modules_json)
        except json.JSONDecodeError as e:
            return error_exit(f"Invalid JSON for --modules-json: {e}")

        config['modules'] = new_modules
        save_config(config)
        return success_exit({
            "modules_count": len(new_modules),
            "action": "persist-all"
        })

    return EXIT_ERROR
