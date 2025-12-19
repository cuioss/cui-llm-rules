"""
Default configurations for plan-marshall-config.

Contains build system and domain default structures used during
project initialization and detection.
"""

# Reserved keys in nested domain config (not profile names)
RESERVED_DOMAIN_KEYS = ['workflow_skills', 'core']

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

# Domain defaults for technical domains (detected during init)
DOMAIN_DEFAULTS = {
    "java": {
        "workflow_skills": {
            "solution_outline": "pm-workflow:solution-outline",
            "task_plan": "pm-workflow:task-plan",
            "implementation": "pm-workflow:task-implementation",
            "testing": "pm-workflow:task-testing"
        },
        "core": {
            "defaults": ["pm-dev-java:java-core"],
            "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok", "pm-dev-java:javadoc"]
        },
        "implementation": {
            "defaults": [],
            "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
        },
        "testing": {
            "defaults": ["pm-dev-java:junit-core"],
            "optionals": ["pm-dev-java:junit-integration"]
        }
    },
    "javascript": {
        "workflow_skills": {
            "solution_outline": "pm-workflow:solution-outline",
            "task_plan": "pm-workflow:task-plan",
            "implementation": "pm-workflow:task-implementation",
            "testing": "pm-workflow:task-testing"
        },
        "core": {
            "defaults": ["pm-dev-frontend:cui-javascript"],
            "optionals": ["pm-dev-frontend:cui-jsdoc", "pm-dev-frontend:cui-javascript-project"]
        },
        "implementation": {
            "defaults": [],
            "optionals": ["pm-dev-frontend:cui-javascript-linting", "pm-dev-frontend:cui-javascript-maintenance"]
        },
        "testing": {
            "defaults": ["pm-dev-frontend:cui-javascript-unit-testing"],
            "optionals": ["pm-dev-frontend:cui-cypress"]
        }
    }
}
