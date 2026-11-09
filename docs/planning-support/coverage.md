# Additive warehouse support for planning

Eight tasks extend existing public contracts for a new planning consumer. They are not blanket refilings of historical bugs, a second stock ledger, a second procurement product or another manufacturing MRP. Existing open and closed issue bodies/states remain unchanged. The authoritative source files are top-level `issues/planning-support-01.md` through `planning-support-08.md`, with literal TITLE/LABELS/issue metadata compatible with the existing issue workflow. Publication is targeted; never run global sync as part of this work.

- [WH-P01](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-01.md): Expose a scope-safe, versioned planning stock and master-data read port
- [WH-P02](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-02.md): Capture line-level planning demand facts without changing frozen warehouse KPI history
- [WH-P03](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-03.md): Publish detailed dated supply and supplier-confirmation facts for planning
- [WH-P04](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-04.md): Arbitrate multiple planning engines and publish versioned stocking policy through one authority
- [WH-P05](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-05.md): Extend external recommendations with planning origin and end-to-end conversion lineage
- [WH-P06](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-06.md): Extend outbox bootstrap and replay contracts for consistent planning ingestion
- [WH-P07](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-07.md): Preserve source versions and archive-safe planning extraction without promising full ledger time travel
- [WH-P08](https://github.com/neetub1508/warehouse-issues/blob/main/issues/planning-support-08.md): Expose optional purchase source, price and receipt-performance inputs without duplicating commercial masters

The complete source/case/competitor coverage is in the [planning ledger](https://github.com/neetub1508/warehouse-planning-issues/blob/main/docs/COVERAGE.md). Original tasks such as [external planning 577](https://github.com/neetub1508/warehouse-issues/issues/577), [planning masters 602](https://github.com/neetub1508/warehouse-issues/issues/602) and [manufacturing MRP 603](https://github.com/neetub1508/warehouse-issues/issues/603) remain canonical. The proposed planning V57 band is not warehouse allocation authority; warehouse changes take next-free additive versions within their actual owning module after contract/data-model adoption.

This is pre-build source coverage. Existing design-checker baseline has 579 violations, which this work must not increase. No implementation/runtime conformance, new FR identifier or WH scenario namespace is allocated by these additions. The separate publication registry stamps only confirmed new issue numbers.

The verified review also preserves [existing monthly ABC task 33](https://github.com/neetub1508/warehouse-issues/issues/33): WH-P04 extends authority to explicit classification fields only when reviewed handover is enabled. The legacy job must honor current producer authority, next-run and disable/re-enable behavior; planning derived classes remain separate. [Cost follow-up 673](https://github.com/neetub1508/warehouse-issues/issues/673) is conditional source reuse, not duplicate implementation.
