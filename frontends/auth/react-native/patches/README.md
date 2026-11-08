<!-- ©AngelaMos | 2026 -->
<!-- README.md -->

# Native dependency patch

`tamagui@1.144.1.patch` corrects the input ref declaration for React Native's
strict TypeScript API. It derives the native instance from the input component
with `React.ComponentRef`, preserving the wrapper's native ref contract. The
patch changes declarations only.

pnpm applies it through `patchedDependencies`; Docker includes it before
installation. Review the patch with any Tamagui upgrade and remove it when the
upstream declaration supports the installed React Native version. Run
`pnpm check` after installing the reviewed dependency graph.
