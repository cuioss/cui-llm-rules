# Tracking Patterns - JSON Structures for Fix Workflow

Defines standard JSON structures for tracking fixes throughout the workflow lifecycle.

## Core Principle

**Consistent tracking** enables:
- Clear reporting to users
- Before/after comparison
- Metrics for fix effectiveness
- Audit trail of changes made

## Primary Tracking Structure

### Complete Fix Workflow Tracking

```json
{
  "fix_workflow": {
    "auto_fix_enabled": true|false,
    "categorization": {
      "total_issues": 15,
      "safe_fixes": 8,
      "risky_fixes": 7
    },
    "safe_fixes": {
      "executed": true|false,
      "applied": 8,
      "by_type": {
        "yaml_fixes": 3,
        "formatting_fixes": 2,
        "reference_fixes": 2,
        "obsolete_content": 1
      },
      "details": [
        {
          "type": "yaml_fixes",
          "component": "cui-java-core",
          "file": "SKILL.md",
          "line": 5,
          "description": "Fixed invalid YAML syntax in frontmatter",
          "before": "name cui-java-core",
          "after": "name: cui-java-core"
        }
      ]
    },
    "risky_fixes": {
      "prompted": 7,
      "applied": 4,
      "skipped": 3,
      "by_category": {
        "duplication": {
          "prompted": 3,
          "applied": 2,
          "skipped": 1
        },
        "integration": {
          "prompted": 2,
          "applied": 1,
          "skipped": 1
        },
        "references": {
          "prompted": 2,
          "applied": 1,
          "skipped": 1
        }
      },
      "details": [
        {
          "category": "duplication",
          "component": "cui-javascript",
          "issue": "Duplicate code example in two files",
          "location": "standards/modern-patterns.md:104",
          "action": "applied",
          "user_decision": "Fix: Remove duplicate from modern-patterns.md"
        },
        {
          "category": "integration",
          "component": "cui-css",
          "issue": "Orphaned file not referenced",
          "location": "examples/legacy-example.md",
          "action": "skipped",
          "user_decision": "Skip all integration fixes"
        }
      ]
    },
    "verification": {
      "executed": true|false,
      "components_verified": 5,
      "results_summary": {
        "issues_resolved": 12,
        "issues_remaining": 3,
        "new_issues": 0
      },
      "by_component": {
        "cui-java-core": {
          "issues_before": 6,
          "issues_after": 1,
          "issues_resolved": 5,
          "new_issues": 0,
          "quality_before": 95,
          "quality_after": 99,
          "status": "success"
        }
      }
    },
    "summary": {
      "total_fixes_attempted": 12,
      "total_fixes_successful": 12,
      "total_fixes_failed": 0,
      "components_modified": 5,
      "execution_time_seconds": 45
    }
  }
}
```

## Categorization Tracking

Track the initial categorization of issues:

```json
{
  "categorization": {
    "timestamp": "2025-11-14T10:30:00Z",
    "total_issues": 15,
    "safe_fixes": {
      "count": 8,
      "types": ["yaml_fixes", "formatting_fixes", "reference_fixes"],
      "by_type": {
        "yaml_fixes": 3,
        "formatting_fixes": 2,
        "reference_fixes": 2,
        "obsolete_content": 1
      }
    },
    "risky_fixes": {
      "count": 7,
      "categories": ["duplication", "integration", "references"],
      "by_category": {
        "duplication": 3,
        "integration": 2,
        "references": 2
      }
    }
  }
}
```

## Safe Fix Tracking

Track application of safe fixes:

```json
{
  "safe_fixes_applied": {
    "total": 8,
    "successful": 8,
    "failed": 0,
    "by_type": {
      "yaml_fixes": {
        "attempted": 3,
        "successful": 3,
        "failed": 0,
        "fixes": [
          {
            "component": "cui-java-core",
            "file": "SKILL.md",
            "line": 5,
            "issue": "Missing colon in YAML field",
            "fix_applied": "Added colon after 'name'",
            "timestamp": "2025-11-14T10:31:15Z"
          }
        ]
      },
      "formatting_fixes": {
        "attempted": 2,
        "successful": 2,
        "failed": 0,
        "fixes": [...]
      },
      "reference_fixes": {
        "attempted": 2,
        "successful": 2,
        "failed": 0,
        "fixes": [...]
      }
    }
  }
}
```

## Risky Fix Tracking

Track prompting and user decisions for risky fixes:

```json
{
  "risky_fixes_prompted": {
    "total_prompted": 7,
    "total_applied": 4,
    "total_skipped": 3,
    "by_category": {
      "duplication": {
        "prompted": 3,
        "applied": 2,
        "skipped": 1,
        "issues": [
          {
            "component": "cui-javascript",
            "issue": "Duplicate code example in two files",
            "location": "standards/modern-patterns.md:104",
            "impact": "Removes duplicate example, keeps authoritative version",
            "user_decision": "applied",
            "selected_option": "Fix: Remove duplicate from modern-patterns.md",
            "timestamp": "2025-11-14T10:32:00Z"
          },
          {
            "component": "cui-css",
            "issue": "Similar content in two sections",
            "location": "standards/css-quality.md:250",
            "impact": "Consolidates similar guidance into single section",
            "user_decision": "applied",
            "selected_option": "Fix: Consolidate content in css-quality.md",
            "timestamp": "2025-11-14T10:32:00Z"
          },
          {
            "component": "cui-cypress",
            "issue": "Example repeated across files",
            "location": "standards/testing-patterns.md:180",
            "impact": "Removes example from testing-patterns.md",
            "user_decision": "skipped",
            "selected_option": null,
            "timestamp": "2025-11-14T10:32:00Z"
          }
        ]
      },
      "integration": {
        "prompted": 2,
        "applied": 1,
        "skipped": 1,
        "issues": [...]
      }
    },
    "skipped_categories": ["references"]
  }
}
```

## Verification Tracking

Track verification results after fixes:

```json
{
  "verification": {
    "timestamp": "2025-11-14T10:35:00Z",
    "components_verified": 5,
    "verification_summary": {
      "issues_resolved": 12,
      "issues_remaining": 3,
      "new_issues": 0,
      "quality_improved": 4,
      "quality_maintained": 1,
      "quality_degraded": 0
    },
    "by_component": {
      "cui-java-core": {
        "before": {
          "critical": 0,
          "warnings": 2,
          "suggestions": 4,
          "total": 6,
          "architecture_score": 100,
          "integrated_content_score": 90,
          "overall_quality": 95
        },
        "after": {
          "critical": 0,
          "warnings": 0,
          "suggestions": 1,
          "total": 1,
          "architecture_score": 100,
          "integrated_content_score": 98,
          "overall_quality": 99
        },
        "changes": {
          "issues_resolved": 5,
          "issues_remaining": 1,
          "new_issues": 0,
          "score_change": +4,
          "status": "success"
        },
        "resolved_issues": [
          "YAML frontmatter syntax error",
          "Broken reference to non-existent file",
          "Duplicate content in two sections",
          "Formatting inconsistency",
          "Missing cross-reference"
        ],
        "remaining_issues": [
          "Optional suggestion for additional documentation"
        ]
      },
      "cui-javascript": {
        "before": {...},
        "after": {...},
        "changes": {...}
      }
    },
    "failed_verifications": [],
    "warnings": []
  }
}
```

## Summary Statistics

Track overall fix workflow statistics:

```json
{
  "fix_workflow_summary": {
    "execution_started": "2025-11-14T10:30:00Z",
    "execution_completed": "2025-11-14T10:35:30Z",
    "duration_seconds": 330,
    "auto_fix_enabled": true,
    "components_analyzed": 26,
    "components_with_issues": 12,
    "components_modified": 5,
    "components_verified": 5,
    "fixes_summary": {
      "safe_fixes_applied": 8,
      "risky_fixes_prompted": 7,
      "risky_fixes_applied": 4,
      "risky_fixes_skipped": 3,
      "total_fixes_applied": 12
    },
    "results_summary": {
      "issues_before": 47,
      "issues_after": 35,
      "issues_resolved": 12,
      "issues_remaining": 35,
      "new_issues": 0,
      "success_rate": "100%"
    },
    "quality_metrics": {
      "avg_quality_before": 94.5,
      "avg_quality_after": 96.2,
      "avg_improvement": +1.7,
      "components_improved": 4,
      "components_maintained": 1,
      "components_degraded": 0
    }
  }
}
```

## Component-Specific Tracking

Different component types may track additional metrics:

### Skills

```json
{
  "skill_specific_tracking": {
    "standards_files_modified": 3,
    "yaml_fields_fixed": 2,
    "cross_references_fixed": 1,
    "duplication_resolved": 2
  }
}
```

### Agents

```json
{
  "agent_specific_tracking": {
    "tool_declarations_fixed": 2,
    "architectural_violations_fixed": 1,
    "prompt_clarity_improved": 1
  }
}
```

### Commands

```json
{
  "command_specific_tracking": {
    "workflow_steps_clarified": 2,
    "bloat_extracted": 1,
    "obsolete_content_removed": 3,
    "parameter_docs_improved": 1
  }
}
```

## Incremental Tracking

Update tracking as workflow progresses:

1. **After categorization**: Update categorization tracking
2. **After safe fixes**: Update safe_fixes_applied tracking
3. **After prompting**: Update risky_fixes_prompted tracking
4. **After verification**: Update verification tracking
5. **At completion**: Update summary statistics

## Quality Standards

- All timestamps in ISO 8601 format
- All counts as integers (no floats for counts)
- All scores rounded to 1 decimal place
- Status values: "success" | "failure" | "partial" | "skipped"
- Include component names and file paths for traceability
- Track both successful and failed operations
