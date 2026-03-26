# Git Hooks

Repository-managed hooks live here and are enabled with:

```bash
make hooks-install
```

## Hooks

- `pre-commit`: regenerates committed derived docs and stages them
- `pre-push`: regenerates derived docs and blocks the push if tracked outputs changed
