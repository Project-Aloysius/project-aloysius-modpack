# E2E:E release-only fork setup

This overlay builds the fork from the newest **published GitHub release tag**
of E2E:E. It does not merge or follow upstream `master`.

Gameplay additions:

- Railcraft 12.0.0 stable
- Computronics 1.6.6
- Project Red 4.9.4.120: Core, Compat, Fabrication, Integration,
  Illumination, Expansion and Exploration

Computronics is downloaded by Mod Director from its external upstream host; it
is not placed in the CurseForge `manifest.json`.

## Install

1. Fork `Krutoy242/Enigmatica2Expert-Extended` on GitHub.
2. Clone your fork and enter it:

   ```bash
   git clone https://github.com/YOUR-NAME/Enigmatica2Expert-Extended.git
   cd Enigmatica2Expert-Extended
   ```

3. Extract this starter over the repository root.
4. Generate and commit the initial overlay:

   ```bash
   python .fork/generate_moddirector.py
   git add .fork .github/workflows/sync-upstream.yml FORK-SETUP.md config/mod-director
   git commit -m "Add release-only extra-mod overlay"
   git push origin master
   ```

5. In GitHub, enable Actions for the fork.
6. In **Settings > Actions > General**, set **Workflow permissions** to
   **Read and write permissions**.
7. Run **Sync latest E2E:E release** manually once.

That first run is important: a newly created GitHub fork initially points at
upstream `master`. The workflow replaces the branch with the newest release tag
plus this overlay, removing any post-release commits.

## Update behavior

Each scheduled run asks the GitHub Releases API for the newest published,
non-draft release. If its tag is unchanged, nothing happens. If it is new, the
workflow:

1. saves the small fork overlay;
2. hard-resets the branch to the new upstream release tag;
3. restores the overlay;
4. regenerates the Mod Director entries; and
5. force-pushes with a lease check.

Do not use GitHub's **Sync fork** button: that follows upstream `master`, not
published releases.

## Important branch rule

Treat the branch as generated output. The release-sync workflow intentionally
replaces its history on every E2E:E release. Do not make unrelated manual edits
there; encode any permanent custom change in `.fork` and add it to the overlay
backup list in the workflow.

The upstream CurseForge publishing workflow may still target the upstream
CurseForge project. Do not add its API token to your fork until you replace the
project ID with one you control, or disable that workflow.
