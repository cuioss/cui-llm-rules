= Coverage Analysis Pattern
:toc: left
:toclevels: 3
:sectnums:

== Overview

This standard defines the coverage analysis workflow for Java test implementation. Coverage analysis identifies untested code paths, prioritizes gaps, and guides test improvement efforts.

== Core Principle

**Measure, analyze, prioritize, test.** Use coverage data to systematically identify and close testing gaps, focusing on high-value code first.

== Coverage Types

=== Line Coverage

**Definition:** Percentage of code lines executed during tests

**Measurement:** Lines executed / Total lines

**Target:** ≥80% for production code

**Use Case:** Basic coverage metric, identifies completely untested code

=== Branch Coverage

**Definition:** Percentage of decision branches (if/else, switch, ternary) executed

**Measurement:** Branches executed / Total branches

**Target:** ≥70% for production code

**Use Case:** Ensures both true and false paths tested

=== Method Coverage

**Definition:** Percentage of methods executed during tests

**Measurement:** Methods executed / Total methods

**Target:** 100% for public methods, ≥80% for package-private

**Use Case:** Identifies completely untested methods

== Coverage Thresholds

=== Production Code Requirements

[cols="1,1,2"]
|===
|Coverage Type |Minimum |Rationale

|Line Coverage
|80%
|Ensures most code paths tested

|Branch Coverage
|70%
|Ensures major decision paths tested

|Method Coverage
|100% (public), 80% (package-private)
|All public APIs must have tests
|===

=== Test Code Exclusions

**Do not measure coverage for:**

* Test classes (*Test.java, *Tests.java)
* Test utilities (src/test/java)
* Generated code
* Configuration classes
* Constants classes

== JaCoCo Integration

=== Maven Configuration

JaCoCo plugin configuration in pom.xml:

[source,xml]
----
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <version>0.8.10</version>
  <executions>
    <execution>
      <goals>
        <goal>prepare-agent</goal>
      </goals>
    </execution>
    <execution>
      <id>report</id>
      <phase>test</phase>
      <goals>
        <goal>report</goal>
      </goals>
    </execution>
    <execution>
      <id>jacoco-check</id>
      <goals>
        <goal>check</goal>
      </goals>
      <configuration>
        <rules>
          <rule>
            <element>PACKAGE</element>
            <limits>
              <limit>
                <counter>LINE</counter>
                <value>COVEREDRATIO</value>
                <minimum>0.80</minimum>
              </limit>
              <limit>
                <counter>BRANCH</counter>
                <value>COVEREDRATIO</value>
                <minimum>0.70</minimum>
              </limit>
            </limits>
          </rule>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>
----

=== Report Generation

**Generate coverage report:**

[source,bash]
----
# Run tests with coverage
mvn clean test

# Generate report
mvn jacoco:report

# Report location
target/site/jacoco/jacoco.xml  # XML for parsing
target/site/jacoco/index.html  # HTML for viewing
----

=== Report Formats

**XML Format (jacoco.xml):**

* Machine-readable
* Used by analyze-coverage-gaps.py script
* Contains detailed line/branch data

**HTML Format (index.html):**

* Human-readable
* Visual coverage indicators
* Drilldown to file/line level

== Coverage Analysis Workflow

=== Step 1: Generate Coverage Report

Execute tests with JaCoCo:

[source,bash]
----
# Single-module
mvn clean test jacoco:report

# Multi-module with specific module
mvn clean test jacoco:report -pl :module-name

# Report path
target/site/jacoco/jacoco.xml
----

=== Step 2: Parse Coverage Data

Use analyze-coverage-gaps.py script:

[source,bash]
----
python3 analyze-coverage-gaps.py \
  --report target/site/jacoco/jacoco.xml \
  --output coverage-gaps.json \
  --pretty
----

**Script Output:**

[source,json]
----
{
  "summary": {
    "line_coverage": 75.5,
    "branch_coverage": 68.2,
    "method_coverage": 82.3,
    "meets_thresholds": false
  },
  "gaps": [
    {
      "file": "src/main/java/com/example/UserValidator.java",
      "class": "com.example.UserValidator",
      "uncovered_lines": [45, 46, 52, 78],
      "uncovered_branches": [
        {"line": 34, "missed": 1, "covered": 1}
      ],
      "uncovered_methods": ["validateEmail"],
      "priority": "high"
    }
  ],
  "recommendations": [
    "Test error paths in UserValidator.validateEmail (lines 45-46)",
    "Test false branch in UserValidator.isValid (line 34)"
  ]
}
----

=== Step 3: Prioritize Gaps

**Priority Criteria:**

[cols="1,2,1"]
|===
|Priority |Characteristics |Action

|**High**
|Public methods, error handling, critical paths
|Test immediately

|**Medium**
|Package-private methods, non-critical paths
|Test after high priority

|**Low**
|Edge cases, rare paths, defensive code
|Test if time permits
|===

**High Priority Patterns:**

* Public method with 0% coverage
* Error handling code (catch blocks, exceptions)
* Validation logic
* Business rules
* Security checks

**Medium Priority Patterns:**

* Package-private methods
* Helper methods
* Data transformation
* Logging statements

**Low Priority Patterns:**

* Defensive null checks after validation
* Impossible branches (after exhaustive validation)
* Logging only
* Generated code

=== Step 4: Identify Test Strategies

For each gap, determine test approach:

**Uncovered Lines:**

* Add test case exercising that path
* Parameterized test for variations
* Edge case test for boundary conditions

**Uncovered Branches:**

* Test both true and false conditions
* Add test for else branch
* Test all switch cases

**Uncovered Methods:**

* Add basic happy path test
* Add error path tests
* Add null/invalid input tests

=== Step 5: Implement Tests

For each gap:

1. **Write test** covering uncovered code
2. **Run test** to verify coverage increases
3. **Verify** gap closed with jacoco:report
4. **Iterate** until thresholds met

== Gap Analysis Patterns

=== Pattern 1: Error Handling Gaps

**Symptom:** Catch blocks or throw statements uncovered

**Example:**

[source,java]
----
public User loadUser(String id) {
    try {
        return repository.find(id);
    } catch (NotFoundException e) {  // ← Uncovered
        log.error("User not found", e);
        throw new UserNotFoundException(id);
    }
}
----

**Test Strategy:**

* Mock repository to throw NotFoundException
* Verify exception propagation
* Verify logging occurred

[source,java]
----
@Test
void loadUser_whenNotFound_throwsUserNotFoundException() {
    when(repository.find("123"))
        .thenThrow(new NotFoundException());

    assertThrows(UserNotFoundException.class,
        () -> service.loadUser("123"));

    verify(logger).error(contains("User not found"), any());
}
----

=== Pattern 2: Branch Coverage Gaps

**Symptom:** One branch of if/else covered, other uncovered

**Example:**

[source,java]
----
public boolean isValid(String email) {
    if (email == null || email.isEmpty()) {  // ← True branch covered
        return false;
    }
    return email.contains("@");  // ← False branch uncovered
}
----

**Test Strategy:**

* Add test for uncovered branch (valid email)
* Parameterized test for multiple cases

[source,java]
----
@ParameterizedTest
@ValueSource(strings = {"", "user@example.com"})
void isValid_variousInputs_returnsExpected(String email) {
    boolean result = validator.isValid(email);
    // Assertions based on input
}
----

=== Pattern 3: Method Coverage Gaps

**Symptom:** Public method with 0% coverage

**Example:**

[source,java]
----
public void deleteUser(String id) {  // ← Completely uncovered
    repository.delete(id);
    cache.invalidate(id);
}
----

**Test Strategy:**

* Add basic test exercising method
* Verify side effects (mocks)

[source,java]
----
@Test
void deleteUser_removesFromRepositoryAndCache() {
    service.deleteUser("123");

    verify(repository).delete("123");
    verify(cache).invalidate("123");
}
----

=== Pattern 4: Complex Conditional Gaps

**Symptom:** Complex conditions with partial coverage

**Example:**

[source,java]
----
if (user != null && user.isActive() && user.hasRole("ADMIN")) {
    // Only some combinations tested
}
----

**Test Strategy:**

* Truth table analysis
* Test all relevant combinations
* Parameterized tests

== Integration with Workflows

=== java-implement-tests Command

[source]
----
Step 1: Parse and verify parameters
  ↓
Step 2: Verify build precondition
  ↓
Step 3: Load testing standards
  ↓
Step 4: Analyze code under test
  ↓
Step 5: Generate coverage baseline ← THIS STANDARD
  mvn test jacoco:report
  Parse existing coverage
  ↓
Step 6: Implement tests
  ↓
Step 7: Verify coverage improvement ← THIS STANDARD
  mvn test jacoco:report
  Compare before/after
  Verify gaps closed
----

=== analyze-test-coverage Workflow

Reference this standard in cui-java-unit-testing SKILL.md:

[source,yaml]
----
workflow: analyze-test-coverage
parameters:
  - report_path: string (default: target/site/jacoco/jacoco.xml)
  - threshold_line: number (default: 80)
  - threshold_branch: number (default: 70)

steps:
  1. Generate coverage report (mvn test jacoco:report)
  2. Parse report (analyze-coverage-gaps.py)
  3. Identify gaps and prioritize
  4. Generate recommendations
  5. Return analysis for Claude to process

references:
  - standards/coverage-analysis-pattern.md
  - scripts/analyze-coverage-gaps.py
----

== Coverage Report Interpretation

=== JaCoCo XML Structure

[source,xml]
----
<report name="project">
  <package name="com/example">
    <class name="com/example/UserService">
      <method name="validateUser" desc="(Ljava/lang/String;)Z">
        <counter type="INSTRUCTION" missed="10" covered="25"/>
        <counter type="BRANCH" missed="2" covered="6"/>
        <counter type="LINE" missed="3" covered="8"/>
        <counter type="METHOD" missed="0" covered="1"/>
      </method>
    </class>
  </package>
</report>
----

**Key Elements:**

* `<package>`: Package-level aggregation
* `<class>`: Class coverage data
* `<method>`: Method-level details
* `<counter>`: Coverage metrics (missed vs covered)

**Counter Types:**

* INSTRUCTION: Bytecode instructions
* BRANCH: Decision branches
* LINE: Source lines
* METHOD: Methods
* COMPLEXITY: Cyclomatic complexity

=== Coverage Calculation

**Line Coverage:**

[source]
----
line_coverage = (covered_lines / (covered_lines + missed_lines)) * 100

Example:
  covered_lines = 8
  missed_lines = 3
  line_coverage = (8 / 11) * 100 = 72.7%
----

**Branch Coverage:**

[source]
----
branch_coverage = (covered_branches / (covered_branches + missed_branches)) * 100

Example:
  covered_branches = 6
  missed_branches = 2
  branch_coverage = (6 / 8) * 100 = 75%
----

== Best Practices

=== For Coverage Analysis

**DO:**

* Generate coverage report after every test run
* Focus on high-priority gaps first
* Use coverage to guide test creation (not as goal)
* Track coverage trends over time

**DON'T:**

* Write tests just to hit coverage targets
* Ignore meaningful gaps to meet numbers
* Test private methods directly (test through public API)
* Rely solely on coverage metrics (quality matters)

=== For Test Implementation

**DO:**

* Test behavior, not implementation
* Cover error paths and edge cases
* Use meaningful assertions
* Keep tests focused and isolated

**DON'T:**

* Test framework code
* Test external dependencies
* Write integration tests as unit tests
* Inflate coverage with trivial tests

== Script Contract

=== analyze-coverage-gaps.py

**Purpose:** Parse JaCoCo XML report to identify untested code

**Input:**

* report_path: Path to jacoco.xml
* threshold_line: Line coverage threshold (default: 80)
* threshold_branch: Branch coverage threshold (default: 70)

**Output:** JSON with gap analysis

[source,json]
----
{
  "summary": {
    "line_coverage": 75.5,
    "branch_coverage": 68.2,
    "method_coverage": 82.3,
    "meets_thresholds": false,
    "gaps_count": 5
  },
  "gaps": [
    {
      "file": "src/main/java/com/example/UserValidator.java",
      "class": "com.example.UserValidator",
      "package": "com.example",
      "uncovered_lines": [45, 46, 52, 78],
      "uncovered_branches": [
        {
          "line": 34,
          "missed": 1,
          "covered": 1,
          "coverage": 50.0
        }
      ],
      "uncovered_methods": ["validateEmail"],
      "priority": "high",
      "reasons": ["public method uncovered", "error handling uncovered"]
    }
  ],
  "recommendations": [
    {
      "gap": "UserValidator.validateEmail lines 45-46",
      "strategy": "Add test for error path when email is invalid",
      "priority": "high"
    }
  ]
}
----

**Exit Codes:**

* 0: Analysis successful
* 1: Report file not found or parse error

== Examples

=== Example 1: High Coverage (PASS)

**Coverage Report:**

[source]
----
Line Coverage: 85%
Branch Coverage: 78%
Method Coverage: 100%
----

**Gap Analysis:**

[source,json]
----
{
  "summary": {
    "line_coverage": 85.0,
    "branch_coverage": 78.0,
    "method_coverage": 100.0,
    "meets_thresholds": true
  },
  "gaps": []
}
----

**Action:** Coverage acceptable, no action needed

=== Example 2: Method Coverage Gap (FAIL)

**Coverage Report:**

[source]
----
Line Coverage: 72%
Branch Coverage: 65%
Method Coverage: 80%
----

**Gap Analysis:**

[source,json]
----
{
  "summary": {
    "meets_thresholds": false
  },
  "gaps": [
    {
      "file": "src/main/java/com/example/UserService.java",
      "uncovered_methods": ["deleteUser", "updateEmail"],
      "priority": "high"
    }
  ],
  "recommendations": [
    {
      "gap": "UserService.deleteUser",
      "strategy": "Add test verifying user deletion and cache invalidation",
      "priority": "high"
    }
  ]
}
----

**Action:** Implement tests for deleteUser and updateEmail methods

=== Example 3: Branch Coverage Gap (FAIL)

**Gap Analysis:**

[source,json]
----
{
  "gaps": [
    {
      "file": "src/main/java/com/example/Validator.java",
      "uncovered_branches": [
        {
          "line": 34,
          "missed": 1,
          "covered": 1,
          "coverage": 50.0
        }
      ],
      "priority": "high"
    }
  ],
  "recommendations": [
    {
      "gap": "Validator.isValid line 34 false branch",
      "strategy": "Add test for case when validation passes",
      "priority": "high"
    }
  ]
}
----

**Action:** Add test exercising false branch at line 34

== References

* JaCoCo Documentation: https://www.jacoco.org/jacoco/trunk/doc/[JaCoCo]
* xref:cui-java-unit-testing.adoc[CUI Java Unit Testing Standards]
* Maven JaCoCo Plugin: https://www.jacoco.org/jacoco/trunk/doc/maven.html[Maven Plugin]
