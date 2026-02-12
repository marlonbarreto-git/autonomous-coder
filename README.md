# Autonomous Coder

Agent that receives coding tasks, writes code, executes tests, and iterates until tests pass.

## Overview

Autonomous Coder implements a generate-test-fix loop where an AI agent writes code to satisfy a given task, runs the test suite against it, and if tests fail, feeds the error output back to a fix function for iterative improvement. It uses temporary directories for isolated execution and pytest for test validation, continuing the loop until all tests pass or the iteration limit is reached.

## Architecture

```
Task Description + Test Code
         |
         v
+-------------------+
| AutonomousCoder   |
| (generate-test-fix|
|  loop controller) |
+-------------------+
    |          ^
    v          |
generate_fn  fix_fn
    |          ^
    v          |
source code  error output
    |          ^
    v          |
+-------------------+
|  CodeExecutor     |
| (temp dir setup,  |
|  pytest runner)   |
+-------------------+
         |
         v
    TestResult
    (passed, output,
     num_passed, num_failed)
```

## Features

- Generate-test-fix iteration loop
- Pluggable code generation and fix functions
- Isolated test execution in temporary directories
- Pytest-based test validation with pass/fail counts
- Configurable max iterations
- Step-by-step execution trace (generate, test, fix)
- Direct code execution support
- Timeout enforcement for test runs

## Tech Stack

- Python 3.11+
- Pydantic (data validation)

## Quick Start

```bash
git clone https://github.com/marlonbarreto-git/autonomous-coder.git
cd autonomous-coder
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Project Structure

```
src/auto_coder/
  __init__.py
  models.py      # StepType, CodeFile, TestResult, CodingStep, CodingTask
  agent.py       # AutonomousCoder with generate-test-fix loop
  executor.py    # CodeExecutor with pytest runner
tests/
  test_models.py
  test_agent.py
  test_executor.py
```

## Testing

```bash
pytest -v --cov=src/auto_coder
```

29 tests covering data models, agent iteration loop, code execution, and test runner behavior.

## License

MIT
