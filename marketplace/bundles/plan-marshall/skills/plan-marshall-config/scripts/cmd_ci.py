"""
CI command handlers for plan-marshall-config.

Handles: ci noun for reading/writing CI provider configuration.

Storage split:
- marshal.json (shared via git): provider, repo_url, detected_at
- run-configuration.json (local): authenticated_tools, verified_at
"""

from datetime import datetime, timezone

from config_core import (
    EXIT_ERROR,
    MarshalNotInitializedError,
    require_initialized,
    load_config,
    save_config,
    load_run_config,
    save_run_config,
    error_exit,
    success_exit,
)


def cmd_ci(args) -> int:
    """Handle ci noun."""
    try:
        require_initialized()
    except MarshalNotInitializedError as e:
        return error_exit(str(e))

    config = load_config()
    ci_config = config.get('ci', {})

    if args.verb == 'get':
        # Return marshal.json ci section (provider info only)
        return success_exit({
            "ci": ci_config
        })

    elif args.verb == 'get-provider':
        return success_exit({
            "provider": ci_config.get('provider', 'unknown'),
            "repo_url": ci_config.get('repo_url'),
            "confidence": "persisted" if ci_config.get('detected_at') else "unknown"
        })

    elif args.verb == 'set-provider':
        ci_config['provider'] = args.provider
        ci_config['repo_url'] = args.repo_url
        ci_config['detected_at'] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        config['ci'] = ci_config
        save_config(config)
        return success_exit({
            "provider": args.provider,
            "repo_url": args.repo_url
        })

    elif args.verb == 'set-tools':
        # Tools stored in run-configuration.json (local, machine-specific)
        run_config = load_run_config()
        run_ci = run_config.get('ci', {})
        tools = [t.strip() for t in args.tools.split(',') if t.strip()]
        run_ci['authenticated_tools'] = tools
        run_ci['verified_at'] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        run_config['ci'] = run_ci
        save_run_config(run_config)
        return success_exit({
            "authenticated_tools": tools
        })

    elif args.verb == 'get-tools':
        # Tools stored in run-configuration.json (local, machine-specific)
        run_config = load_run_config()
        run_ci = run_config.get('ci', {})
        return success_exit({
            "authenticated_tools": run_ci.get('authenticated_tools', [])
        })

    return EXIT_ERROR
