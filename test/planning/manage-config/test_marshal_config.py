#!/usr/bin/env python3
"""Tests for marshal-config.py script."""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Import shared infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from conftest import run_script, TestRunner, get_script_path

# Get script path
SCRIPT_PATH = get_script_path('planning', 'manage-config', 'marshal-config.py')

# Import toon_parser for output parsing
TOON_PARSER_DIR = Path(__file__).parent.parent.parent.parent / 'marketplace' / 'bundles' / 'general-tools' / 'skills' / 'toon-usage' / 'scripts'
sys.path.insert(0, str(TOON_PARSER_DIR))
from toon_parser import parse_toon


# =============================================================================
# Test Context
# =============================================================================

class TestContext:
    """Context manager for test with temp directory."""

    def __init__(self):
        self.temp_dir = None
        self.original_env = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_env = os.environ.get('PLAN_BASE_DIR')
        os.environ['PLAN_BASE_DIR'] = str(self.temp_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_env is None:
            os.environ.pop('PLAN_BASE_DIR', None)
        else:
            os.environ['PLAN_BASE_DIR'] = self.original_env
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @property
    def marshal_path(self) -> Path:
        return self.temp_dir / 'marshal.json'

    def write_marshal(self, config: dict):
        """Write marshal.json with given config."""
        self.marshal_path.parent.mkdir(parents=True, exist_ok=True)
        self.marshal_path.write_text(json.dumps(config, indent=2))


# =============================================================================
# Test: Not Initialized Error
# =============================================================================

def test_not_initialized_error():
    """Test that commands fail with helpful message when not initialized."""
    with TestContext():
        # Don't call init - directory exists but no marshal.json
        result = run_script(SCRIPT_PATH, 'domain-agents', 'list')
        assert not result.success
        data = parse_toon(result.stdout)
        assert data['status'] == 'error'
        assert '/plan-marshall' in data['error']


# =============================================================================
# Test: Init Command
# =============================================================================

def test_init_creates_marshal_json():
    """Test init creates marshal.json with defaults."""
    with TestContext() as ctx:
        result = run_script(SCRIPT_PATH, 'init')
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert ctx.marshal_path.exists()


def test_init_fails_if_exists():
    """Test init fails if marshal.json already exists."""
    with TestContext() as ctx:
        ctx.write_marshal({"test": "data"})
        result = run_script(SCRIPT_PATH, 'init')
        assert not result.success
        data = parse_toon(result.stdout)
        assert data['status'] == 'error'


def test_init_force_overwrites():
    """Test init --force overwrites existing file."""
    with TestContext() as ctx:
        ctx.write_marshal({"test": "data"})
        result = run_script(SCRIPT_PATH, 'init', '--force')
        assert result.success, f"Script failed: {result.stderr}"


# =============================================================================
# Test: Domain Agents
# =============================================================================

def test_domain_agents_list_defaults():
    """Test domain-agents list returns defaults after init."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'domain-agents', 'list')
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        # data contains nested dict - check it's non-empty
        assert data['data']  # non-empty


def test_domain_agents_get():
    """Test domain-agents get returns agent mapping."""
    with TestContext() as ctx:
        ctx.write_marshal({
            "domain_agents": {
                "planning:plan-type-java": {
                    "goals_agent": "cui-java-expert:java-goals-agent",
                    "plan_agent": "cui-java-expert:java-plan-agent"
                }
            }
        })
        result = run_script(SCRIPT_PATH, 'domain-agents', 'get',
                           '--plan-type', 'planning:plan-type-java')
        assert result.success, f"Script failed: {result.stderr}"
        data = parse_toon(result.stdout)
        assert data['status'] == 'success'
        assert data['data']['goals_agent'] == 'cui-java-expert:java-goals-agent'


def test_domain_agents_get_unknown():
    """Test domain-agents get fails for unknown plan-type."""
    with TestContext():
        result = run_script(SCRIPT_PATH, 'domain-agents', 'get',
                           '--plan-type', 'unknown:type')
        assert not result.success
        data = parse_toon(result.stdout)
        assert data['status'] == 'error'


def test_domain_agents_set():
    """Test domain-agents set updates mapping."""
    with TestContext() as ctx:
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'domain-agents', 'set',
                           '--plan-type', 'planning:plan-type-java',
                           '--goals-agent', 'test:goals-agent')
        assert result.success, f"Script failed: {result.stderr}"

        # Verify it was saved
        config = json.loads(ctx.marshal_path.read_text())
        assert config['domain_agents']['planning:plan-type-java']['goals_agent'] == 'test:goals-agent'


def test_domain_agents_set_null():
    """Test domain-agents set with null clears the agent."""
    with TestContext() as ctx:
        ctx.write_marshal({
            "domain_agents": {
                "planning:plan-type-java": {
                    "goals_agent": "some:agent",
                    "plan_agent": "some:other"
                }
            }
        })
        result = run_script(SCRIPT_PATH, 'domain-agents', 'set',
                           '--plan-type', 'planning:plan-type-java',
                           '--goals-agent', 'null')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        assert config['domain_agents']['planning:plan-type-java']['goals_agent'] is None


# =============================================================================
# Test: Defaults
# =============================================================================

def test_defaults_list():
    """Test defaults list returns all defaults."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'defaults', 'list')
        assert result.success
        data = parse_toon(result.stdout)
        assert 'create_pr' in data['data']
        assert 'verification_required' in data['data']


def test_defaults_get():
    """Test defaults get returns specific field."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'defaults', 'get', '--field', 'create_pr')
        assert result.success
        data = parse_toon(result.stdout)
        assert 'create_pr' in data['data']


def test_defaults_set_boolean():
    """Test defaults set handles boolean conversion."""
    with TestContext() as ctx:
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'defaults', 'set',
                           '--field', 'create_pr', '--value', 'true')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        assert config['defaults']['create_pr'] is True


# =============================================================================
# Test: Plan Type Defaults
# =============================================================================

def test_plan_type_defaults_get_empty():
    """Test plan-type-defaults get returns empty for unknown type."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'plan-type-defaults', 'get',
                           '--plan-type', 'planning:plan-type-java')
        assert result.success
        data = parse_toon(result.stdout)
        # TOON: empty dict serializes as empty string
        assert data['data'] == '' or data['data'] == {}


def test_plan_type_defaults_set():
    """Test plan-type-defaults set stores values."""
    with TestContext() as ctx:
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'plan-type-defaults', 'set',
                           '--plan-type', 'planning:plan-type-java',
                           '--verification-command', '/builder:builder-build-and-fix',
                           '--pr-workflow', 'true')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        pt = config['plan_type_defaults']['planning:plan-type-java']
        assert pt['verification_command'] == '/builder:builder-build-and-fix'
        assert pt['pr_workflow'] is True


# =============================================================================
# Test: Rules
# =============================================================================

def test_rules_list():
    """Test rules list returns all rules."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'rules', 'list')
        assert result.success
        data = parse_toon(result.stdout)
        assert isinstance(data['data'], list)


def test_rules_match_default():
    """Test rules match returns generic for unknown pattern."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'rules', 'match', '--file', 'unknown.xyz')
        assert result.success
        data = parse_toon(result.stdout)
        assert data['data']['plan_type'] == 'planning:plan-type-generic'


def test_rules_match_specific():
    """Test rules match finds specific pattern."""
    with TestContext() as ctx:
        ctx.write_marshal({
            "plan_type_rules": [
                {"pattern": "*.java", "plan_type": "planning:plan-type-java", "description": "Java"},
                {"pattern": "*", "plan_type": "planning:plan-type-generic", "description": "Default"}
            ]
        })
        result = run_script(SCRIPT_PATH, 'rules', 'match', '--file', 'Foo.java')
        assert result.success
        data = parse_toon(result.stdout)
        assert data['data']['plan_type'] == 'planning:plan-type-java'


def test_rules_match_or_pattern():
    """Test rules match handles | OR pattern."""
    with TestContext() as ctx:
        ctx.write_marshal({
            "plan_type_rules": [
                {"pattern": "*.js|*.ts|*.tsx", "plan_type": "planning:plan-type-javascript", "description": "JS"},
                {"pattern": "*", "plan_type": "planning:plan-type-generic", "description": "Default"}
            ]
        })
        result = run_script(SCRIPT_PATH, 'rules', 'match', '--file', 'app.tsx')
        assert result.success
        data = parse_toon(result.stdout)
        assert data['data']['plan_type'] == 'planning:plan-type-javascript'


def test_rules_add():
    """Test rules add inserts new rule."""
    with TestContext() as ctx:
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'rules', 'add',
                           '--pattern', '*.kt',
                           '--plan-type', 'planning:plan-type-java',
                           '--description', 'Kotlin files')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        # New rule should be before fallback
        patterns = [r['pattern'] for r in config['plan_type_rules']]
        assert '*.kt' in patterns


def test_rules_remove():
    """Test rules remove deletes a rule."""
    with TestContext() as ctx:
        ctx.write_marshal({
            "plan_type_rules": [
                {"pattern": "*.java", "plan_type": "planning:plan-type-java", "description": "Java"},
                {"pattern": "*", "plan_type": "planning:plan-type-generic", "description": "Default"}
            ]
        })
        result = run_script(SCRIPT_PATH, 'rules', 'remove', '--pattern', '*.java')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        patterns = [r['pattern'] for r in config['plan_type_rules']]
        assert '*.java' not in patterns


def test_rules_remove_not_found():
    """Test rules remove fails for non-existent pattern."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'rules', 'remove', '--pattern', 'nonexistent')
        assert not result.success


# =============================================================================
# Test: Keywords
# =============================================================================

def test_keywords_list_empty():
    """Test keywords list returns empty after init."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'keywords', 'list')
        assert result.success
        data = parse_toon(result.stdout)
        # TOON: empty dict serializes as empty string
        assert data['data'] == '' or data['data'] == {}


def test_keywords_add_and_list():
    """Test keywords add and list."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        run_script(SCRIPT_PATH, 'keywords', 'add',
                  '--plan-type', 'planning:plan-type-java',
                  '--keyword', 'junit')

        result = run_script(SCRIPT_PATH, 'keywords', 'list',
                           '--plan-type', 'planning:plan-type-java')
        assert result.success
        data = parse_toon(result.stdout)
        assert 'junit' in data['data']


def test_keywords_match():
    """Test keywords match finds plan-type from text."""
    with TestContext() as ctx:
        ctx.write_marshal({
            "detection_keywords": {
                "planning:plan-type-java": ["java", "junit", "maven"]
            }
        })
        result = run_script(SCRIPT_PATH, 'keywords', 'match',
                           '--text', 'implement junit test for service')
        assert result.success
        data = parse_toon(result.stdout)
        assert data['data']['plan_type'] == 'planning:plan-type-java'
        assert 'junit' in data['data']['matched']


def test_keywords_match_no_match():
    """Test keywords match returns null when no keywords match."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'keywords', 'match',
                           '--text', 'just some random text')
        assert result.success
        data = parse_toon(result.stdout)
        assert data['data']['plan_type'] is None


# =============================================================================
# Test: Build Systems
# =============================================================================

def test_build_systems_list_empty():
    """Test build-systems list returns empty after init."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'build-systems', 'list')
        assert result.success
        data = parse_toon(result.stdout)
        assert data['data'] == []


def test_build_systems_set():
    """Test build-systems set updates active status."""
    with TestContext() as ctx:
        ctx.write_marshal({
            "build_systems": [
                {"detected": "maven", "skill": "builder:builder-maven-rules", "active": True}
            ]
        })
        result = run_script(SCRIPT_PATH, 'build-systems', 'set',
                           '--system', 'maven', '--active', 'false')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        assert config['build_systems'][0]['active'] is False


def test_build_systems_set_not_found():
    """Test build-systems set fails for unknown system."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'build-systems', 'set',
                           '--system', 'nonexistent', '--active', 'true')
        assert not result.success


# =============================================================================
# Test: Custom Types
# =============================================================================

def test_custom_types_list_empty():
    """Test custom-types list returns empty after init."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'custom-types', 'list')
        assert result.success
        data = parse_toon(result.stdout)
        assert data['data'] == []


def test_custom_types_add():
    """Test custom-types add creates new type."""
    with TestContext() as ctx:
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'custom-types', 'add',
                           '--name', 'security-review',
                           '--skill-path', '.claude/plan-types/security/SKILL.md',
                           '--goals-agent', 'null',
                           '--plan-agent', 'null')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        assert len(config['custom_plan_types']) == 1
        assert config['custom_plan_types'][0]['name'] == 'security-review'


def test_custom_types_add_duplicate():
    """Test custom-types add fails for duplicate name."""
    with TestContext() as ctx:
        ctx.write_marshal({
            "custom_plan_types": [
                {"name": "security-review", "skill_path": "path", "goals_agent": None, "plan_agent": None}
            ]
        })
        result = run_script(SCRIPT_PATH, 'custom-types', 'add',
                           '--name', 'security-review',
                           '--skill-path', 'another-path')
        assert not result.success


def test_custom_types_remove():
    """Test custom-types remove deletes type."""
    with TestContext() as ctx:
        ctx.write_marshal({
            "custom_plan_types": [
                {"name": "security-review", "skill_path": "path", "goals_agent": None, "plan_agent": None}
            ]
        })
        result = run_script(SCRIPT_PATH, 'custom-types', 'remove', '--name', 'security-review')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        assert len(config['custom_plan_types']) == 0


# =============================================================================
# Test: State
# =============================================================================

def test_state_get_empty():
    """Test state get returns empty after init."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'state', 'get')
        assert result.success
        data = parse_toon(result.stdout)
        # TOON: empty dict serializes as empty string
        assert data['data'] == '' or data['data'] == {}


def test_state_set():
    """Test state set stores value."""
    with TestContext() as ctx:
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'state', 'set',
                           '--field', 'last_generated',
                           '--value', '2025-12-09T12:00:00')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        assert config['state']['last_generated'] == '2025-12-09T12:00:00'


def test_state_set_number():
    """Test state set handles numeric conversion."""
    with TestContext() as ctx:
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'state', 'set',
                           '--field', 'script_count', '--value', '42')
        assert result.success
        config = json.loads(ctx.marshal_path.read_text())
        assert config['state']['script_count'] == 42


def test_state_update_checksum():
    """Test state update-checksum calculates checksum."""
    with TestContext():
        run_script(SCRIPT_PATH, 'init')
        result = run_script(SCRIPT_PATH, 'state', 'update-checksum')
        assert result.success
        data = parse_toon(result.stdout)
        assert 'checksum' in data['data']
        assert len(data['data']['checksum']) == 8  # 8 char hex


# =============================================================================
# Test Runner
# =============================================================================

if __name__ == '__main__':
    runner = TestRunner()
    runner.add_tests([
        # Not initialized error
        test_not_initialized_error,
        # Init
        test_init_creates_marshal_json,
        test_init_fails_if_exists,
        test_init_force_overwrites,
        # Domain agents
        test_domain_agents_list_defaults,
        test_domain_agents_get,
        test_domain_agents_get_unknown,
        test_domain_agents_set,
        test_domain_agents_set_null,
        # Defaults
        test_defaults_list,
        test_defaults_get,
        test_defaults_set_boolean,
        # Plan type defaults
        test_plan_type_defaults_get_empty,
        test_plan_type_defaults_set,
        # Rules
        test_rules_list,
        test_rules_match_default,
        test_rules_match_specific,
        test_rules_match_or_pattern,
        test_rules_add,
        test_rules_remove,
        test_rules_remove_not_found,
        # Keywords
        test_keywords_list_empty,
        test_keywords_add_and_list,
        test_keywords_match,
        test_keywords_match_no_match,
        # Build systems
        test_build_systems_list_empty,
        test_build_systems_set,
        test_build_systems_set_not_found,
        # Custom types
        test_custom_types_list_empty,
        test_custom_types_add,
        test_custom_types_add_duplicate,
        test_custom_types_remove,
        # State
        test_state_get_empty,
        test_state_set,
        test_state_set_number,
        test_state_update_checksum,
    ])
    sys.exit(runner.run())
