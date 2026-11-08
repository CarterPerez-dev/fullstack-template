# =============================================================================
# AngelaMos | 2026
# justfile
# =============================================================================

set shell := ["bash", "-uc"]

# List recipes
default:
    @just --list --unsorted

# Install the `template` command onto PATH (~/.local/bin by default)
install bin="":
    @bash template-tool/install.sh {{bin}}

# Show the available template types
list:
    @bash template-tool/template list

# Scaffold from a template, e.g. `just new go my-api`
new type name="" *flags="":
    @bash template-tool/template {{type}} {{name}} {{flags}}

check-template:
    python3 -B -m unittest discover -s template-tool -p 'test_*.py' -v
    python3 -B -m unittest discover -s tests/release -p 'test_*checks.py' -v
    shellcheck install.sh uninstall.sh template-tool/template template-tool/install.sh
    bash -n install.sh
    bash -n uninstall.sh
    bash -n template-tool/template
    bash -n template-tool/install.sh

check-generated variant="all" environment="all":
    python3 -B tests/release/check_generated.py {{quote(variant)}} {{quote(environment)}}

resume-generated report:
    python3 -B tests/release/check_generated.py all all --resume {{quote(report)}}

check-postgres group="all":
    python3 -B tests/release/check_postgres.py {{quote(group)}}

resolve-dependencies group="all":
    python3 -B tests/release/resolve_dependencies.py {{quote(group)}}

dependency-plan group="all":
    python3 -B tests/release/resolve_dependencies.py {{quote(group)}} --plan

check-dependencies group="all":
    python3 -B tests/release/check_dependencies.py {{quote(group)}}

dependency-check-plan group="all":
    python3 -B tests/release/check_dependencies.py {{quote(group)}} --plan

package version output:
    python3 -B template-tool/release.py --version {{quote(version)}} --output {{quote(output)}}
