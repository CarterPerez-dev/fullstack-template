<!-- ©AngelaMos | 2026 -->
<!-- DEPENDENCIES.md -->

# Dependency maintenance

Keep Expo's coordinated native package versions aligned. After changing the
manifest or overrides, resolve the lock with pnpm and check a fresh installation
with strict peer validation. Lint, types, bundle exports, and dependency audits
do not replace native binary and device testing.

Biome is pinned to 2.6.4 alongside its configuration schema. Its raw-text rule
recognizes the four card text components because they extend Tamagui `Text`.
Keep the rule enabled for layout containers. Review the configuration when
upgrading Biome.

Tamagui 1.144.1 uses a recorded declaration patch to match React Native's input
instance type. See [the patch notes](patches/README.md). The patch changes no
runtime JavaScript.

Expo's dependency overrides address the October 27, 2026
[glob cancellation advisory](https://github.com/advisories/GHSA-3g3m-2fjr-6pw4)
and [minimatch amplification advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249).
They are limited to these parent versions:

| Parent | Dependency selected |
| --- | --- |
| @expo/cli 58.1.18 | glob 14.0.3 |
| @expo/config 58.0.10 | glob 14.0.3 |
| @expo/config-plugins 58.0.11 | glob 14.0.3 |
| @expo/fingerprint 0.21.8 | glob 14.0.3 and minimatch 11.0.4 |
| @expo/metro-config 58.0.20 | glob 14.0.3 |

These overrides cross the parents' declared major-version ranges. The repository's
native release checks exercise their file discovery, routing, native project
paths, workspace matching, fingerprint ignores, and cancellation behavior. Review
and remove the overrides as upstream packages adopt patched dependencies; an
updated parent version intentionally does not inherit an old override.

The production audit covers the installed dependency graph, including Expo tools.
A reported package path may represent one of several parents sharing that version.
Inspect the complete graph when repairing an advisory rather than assuming the
printed path is the only affected reference.
