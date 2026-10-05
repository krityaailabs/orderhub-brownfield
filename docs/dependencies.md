# Dependency decisions (ADR 0002)

| Package | Added in | Why existing code can't do it | Licence | Maintenance | Approved by |
|---|---|---|---|---|---|
| hypothesis 6.168.4 (and its dependency sortedcontainers 2.4.0) | Section 4 (Lab 4.5) | Property-based testing generates thousands of orders and return sequences; writing a reliable generator and shrinker ourselves would be a project in itself | MPL-2.0 (sortedcontainers: Apache-2.0) | Actively maintained, frequent releases | Course team (record your reviewer here in your own fork) |
