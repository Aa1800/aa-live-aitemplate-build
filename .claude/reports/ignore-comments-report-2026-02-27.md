# Ignore Comments Report — 2026-02-27

Scanned all `*.py` files for `# noqa` and `# type: ignore` suppressions.

**Total found:** 3 comments

---

## 1. `app/core/config.py:37` — `# noqa: ANN401`

```python
def decode_complex_value(
    self,
    field_name: str,
    field: FieldInfo,
    value: Any,  # noqa: ANN401
) -> Any:  # noqa: ANN401
```

**Rule suppressed:** `ANN401` — "Dynamically typed expressions (`typing.Any`) are disallowed"

**Why it exists:**
`decode_complex_value` is an override of `EnvSettingsSource.decode_complex_value` from the `pydantic-settings` library. The parent method's signature uses `Any` for both the `value` parameter and the return type. To correctly override the method, the subclass must match the parent's type contract — using a narrower type would violate the Liskov Substitution Principle and would cause a mypy/pyright override error. `Any` is not a design choice here; it is a constraint imposed by the library.

**Options to resolve:**

1. **Keep the `# noqa: ANN401` suppressions (current approach)**
   - Effort: None
   - Breaking: No
   - Impact: Two suppressed warnings. The `Any` is fully justified by the library override contract.

2. **Add `object` instead of `Any` for the parameter type**
   - Effort: Low
   - Breaking: Potentially — `object` is more restrictive than `Any` for a parameter (contravariant), which would widen the contract rather than match it. Mypy would likely reject this as an incompatible override.
   - Impact: Would likely introduce a new type error to fix one warning. Not a net improvement.

3. **Add `# type: ignore[override]` instead of `# noqa`**
   - Effort: Low
   - Breaking: No
   - Impact: Shifts suppression from ruff to mypy/pyright. Does not actually improve type safety — just moves the annotation to a different tool. No benefit.

**Tradeoffs:**

- Removing the suppression without changing the type would cause `ANN401` to re-fire on every run, breaking the CI check.
- Using a narrower type than the parent introduces real type errors and breaks the override pattern.
- The `Any` here is a legitimate use case: the function's purpose is to decode arbitrary env var values of unknown shape before pydantic validates them.

**Recommendation:** Keep

`Any` is the correct type here. The library's own interface uses `Any`, and we cannot change that contract. The `# noqa: ANN401` suppressions are well-placed and appropriately scoped (one per line, not file-wide). No action needed.

---

---

## 2. `app/main.py:51` — `# noqa: S104`

```python
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8123, reload=True)  # noqa: S104
```

**Rule suppressed:** `S104` — "Possible binding to all interfaces"

**Why it exists:**
`host="0.0.0.0"` is required for the Docker `__main__` entrypoint. When uvicorn binds to `127.0.0.1` (loopback only), the container is unreachable from the host even with Docker's port mapping (`-p 8123:8123`). Binding to `0.0.0.0` tells uvicorn to accept connections on all network interfaces inside the container, which is the standard and expected configuration for containerised services.

**Options to resolve:**

1. **Keep the `# noqa: S104` suppression (current approach)**
   - Effort: None
   - Breaking: No
   - Impact: One suppressed warning. Binding to all interfaces is the correct and intended behaviour here.

2. **Move host config to an environment variable**
   - Effort: Low
   - Breaking: No
   - Impact: `host=settings.host` would move the string out of source code and suppress the rule implicitly (ruff only flags the literal `"0.0.0.0"`). Adds flexibility but also adds a settings field purely to satisfy a linter — marginal benefit.

3. **Remove `__main__` block and rely solely on the Dockerfile CMD**
   - Effort: Medium
   - Breaking: No — Docker already uses `python -m app.main`, but removing `__main__` means the local `uv run python -m app.main` path disappears
   - Impact: Eliminates the suppression by eliminating the code, but removes a useful local dev entry point.

**Tradeoffs:**

- `0.0.0.0` is a well-understood convention for container networking; the S104 rule is a useful reminder in application code but is a false positive in a Docker entrypoint context.
- Option 2 adds complexity (a new settings field) purely to work around a linter rule — not worth it.
- The suppression is correctly scoped to one line, not the whole file.

**Recommendation:** Keep

`0.0.0.0` is correct and intentional. The `# noqa: S104` is a narrow, justified suppression on the `__main__` Docker entrypoint line. No action needed.

---

## Summary

| File | Line | Rule | Verdict |
|------|------|------|---------|
| `app/core/config.py` | 37 | `ANN401` | **Keep** — required by library override |
| `app/core/config.py` | 38 | `ANN401` | **Keep** — required by library override |
| `app/main.py` | 51 | `S104` | **Keep** — intentional Docker entrypoint binding |
