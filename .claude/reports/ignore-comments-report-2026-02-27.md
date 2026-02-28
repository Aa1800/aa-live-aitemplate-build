# Ignore Comments Report — 2026-02-27

Scanned all `*.py` files for `# noqa` and `# type: ignore` suppressions.

**Total found:** 2 comments (same method, same rule)

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

## Summary

| File | Line | Rule | Verdict |
|------|------|------|---------|
| `app/core/config.py` | 37 | `ANN401` | **Keep** — required by library override |
| `app/core/config.py` | 38 | `ANN401` | **Keep** — required by library override |
