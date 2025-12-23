"""
Default configurations for plan-marshall-config.

Contains build system and domain default structures used during
project initialization and detection.
"""

# Reserved keys in nested domain config (not profile names)
# workflow_skills: System domain only - 5 workflow phases
# workflow_skill_extensions: Domain extensions (outline, triage)
# core: Core skills loaded for all profiles
RESERVED_DOMAIN_KEYS = ['workflow_skills', 'workflow_skill_extensions', 'core', 'defaults', 'optionals']

# 5-phase workflow model
DEFAULT_PROFILES = ['architecture', 'planning', 'implementation', 'testing', 'quality']

# System workflow skills (always from system domain)
DEFAULT_SYSTEM_WORKFLOW_SKILLS = {
    "init": "pm-workflow:plan-init",
    "outline": "pm-workflow:solution-outline",
    "plan": "pm-workflow:task-plan",
    "execute": "pm-workflow:task-execute",
    "finalize": "pm-workflow:plan-finalize"
}

# Default system domain configuration
DEFAULT_SYSTEM_DOMAIN = {
    "defaults": ["plan-marshall:general-development-rules"],
    "optionals": ["plan-marshall:diagnostic-patterns"],
    "workflow_skills": DEFAULT_SYSTEM_WORKFLOW_SKILLS
}

# Build system defaults (detection reference only - commands are in modules)
BUILD_SYSTEM_DEFAULTS = {
    "maven": {
        "skill": "plan-marshall:build-operations"
    },
    "gradle": {
        "skill": "plan-marshall:build-operations"
    },
    "npm": {
        "skill": "plan-marshall:build-operations"
    }
}

# Build system to domain mapping for detection
BUILD_SYSTEM_TO_DOMAIN = {
    "maven": "java",
    "gradle": "java",
    "npm": "javascript"
}

# Domain templates with profile-based structure (5 profiles)
DOMAIN_TEMPLATES = {
    "java": {
        "workflow_skill_extensions": {
            "outline": "pm-dev-java:java-outline-ext",
            "triage": "pm-dev-java:java-triage"
        },
        "core": {
            "defaults": ["pm-dev-java:java-core"],
            "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok"]
        },
        "architecture": {
            "defaults": ["pm-dev-java:java-packages"],
            "optionals": []
        },
        "planning": {
            "defaults": [],
            "optionals": []
        },
        "implementation": {
            "defaults": [],
            "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
        },
        "testing": {
            "defaults": ["pm-dev-java:junit-core"],
            "optionals": ["pm-dev-java:junit-integration"]
        },
        "quality": {
            "defaults": ["pm-dev-java:javadoc"],
            "optionals": []
        }
    },
    "javascript": {
        "workflow_skill_extensions": {
            "outline": "pm-dev-frontend:js-outline-ext",
            "triage": "pm-dev-frontend:javascript-triage"
        },
        "core": {
            "defaults": ["pm-dev-frontend:cui-javascript"],
            "optionals": ["pm-dev-frontend:cui-jsdoc", "pm-dev-frontend:cui-javascript-project"]
        },
        "architecture": {
            "defaults": [],
            "optionals": []
        },
        "planning": {
            "defaults": [],
            "optionals": []
        },
        "implementation": {
            "defaults": [],
            "optionals": ["pm-dev-frontend:cui-javascript-linting", "pm-dev-frontend:cui-javascript-maintenance"]
        },
        "testing": {
            "defaults": ["pm-dev-frontend:cui-javascript-unit-testing"],
            "optionals": ["pm-dev-frontend:cui-cypress"]
        },
        "quality": {
            "defaults": [],
            "optionals": []
        }
    },
    "plan-marshall-plugin-dev": {
        "workflow_skill_extensions": {
            "outline": "pm-plugin-development:plugin-outline-ext",
            "triage": "pm-plugin-development:plugin-triage"
        },
        "core": {
            "defaults": ["pm-plugin-development:plugin-architecture"],
            "optionals": []
        },
        "architecture": {
            "defaults": [],
            "optionals": []
        },
        "planning": {
            "defaults": [],
            "optionals": []
        },
        "implementation": {
            "defaults": [],
            "optionals": []
        },
        "testing": {
            "defaults": [],
            "optionals": []
        },
        "quality": {
            "defaults": [],
            "optionals": []
        }
    }
}

# Legacy DOMAIN_DEFAULTS for backward compatibility
# New code should use DOMAIN_TEMPLATES
DOMAIN_DEFAULTS = DOMAIN_TEMPLATES
