# Skill: OpenSpec Git Discipline

## Purpose
Enforces git branch discipline for Spec-Driven Development (SDD) to prevent state drift and merge conflicts.

## Rules
1. **Gate: propose & continue**: 
   - Must be executed on a branch branched from `main`. 
   - The proposal and specifications must be merged to `main` before `apply` starts.
2. **Gate: apply**: 
   - Code changes must be developed in a dedicated feature branch or git worktree, never directly on `main` without a clean spec.
3. **Gate: archive**: 
   - Implementation must be fully merged back to `main` before `archive` is executed to clean up change artifacts.
