I couldn't write `docs/reviews/R31-decisions.md` because this reviewer role may not write files, so the full table is below.

**Engines:** Claude + GPT (gpt-6.1-sol, medium). Of the 113 rows, 96 had both engines agreeing. On 9 they disagreed about the verdict and I settled each one from the code or a recorded decision. 6 answers come from GPT only and 2 from Claude only. 6 single-engine positions were dropped after checking them.

**Counts:** 95 DECIDE · 9 DEFER-ACCOUNTING · 6 USER. Withdrawals: 2 RESTORE (FR-258, FR-471) · 1 KEEP-WITHDRAWN (FR-397).

**USER items:**
- **BND-OPEN-01:** is normal MOOWR process loss a bonded loss or register-only waste? Recommend keeping it a bonded loss until a customs adviser rules.
- **BND-OPEN-02:** should MOOWR job work be enabled under a bond-officer permission? Recommend only once the permission and the return-period source are confirmed.
- **NFR-OPEN-01:** keep or withdraw the style/variant/ratio-pack FRs? Recommend keeping the built schema, building nothing more and fencing ratio packs.
- **NFR-OPEN-02:** serve the pharma segment or decline it? Recommend declining in writing and fencing the pack behind a setting.
- **RMV-OPEN-03:** what meters 3PL freight? Recommend a quoted amount from the 3PL's own tariff, trued up when the carrier invoice arrives.
- **FBL-OPEN-02:** should a capacity breach at putaway block or warn? Recommend block where a capacity is set, with a per-site warn option.

**Things the caller should know:**
- **AHO-OPEN-09:** `V511065__Seed_wh_rpt_stock_to_gl_permissions_menu_and_grid.sql` already exists. Claiming the "next free number" for it would collide, so only the documents need updating.
- **AHO-OPEN-05:** the bucket mapping is already built in `WhStockToGlRepositoryCustomImpl.java:37-46`. The row only needs ratifying.
- **Settled disagreements:** I settled MOD-OPEN-01 (withdraw) from the D-1 amendment at `DECISIONS.md:63-66`. I settled RPN-OPEN-01 (remove the manual lost-sale screen) from D-17 item 4 at `DECISIONS.md:583`.

**Legend:** in the engines column, `Both` means the engines agreed. `Both (settled)` means they disagreed and I settled it from the cited evidence. `GPT` or `Claude` means that engine's answer was adopted. Paths are relative to `warehouse-issues/docs/` unless they name a classic file.

| id | contract | verdict | answer/options | evidence | engines |
|---|---|---|---|---|---|
| TPB-OPEN-01 | 3pl-billing | DECIDE | Default replaced: build the FR's seven bases. Add `SQ_FT_ALLOCATED` (contracted area on the rate card) and `SQ_FT_OCCUPIED` (needs a location footprint column). Don't restate the FR down to five. | FR-288 names seven bases. TPB-DIV-01 shows code has five. D-16 item 1 keeps storage for hire. Billing per sq ft is standard 3PL practice (Extensiv) and the main Indian warehousing rent basis. | Both |
| TPB-OPEN-02 | 3pl-billing | DECIDE | Default stands. The rest of `p5-08` (3PL client portal) still owes ASN and order create, CSV upload, cancel-while-unallocated and returns. D-16 removed only the trade-customer persona. | FR-284. D-16 item 3. TPB-DIV-03. | Both |
| TPB-OPEN-03 | 3pl-billing | DECIDE | Default stands. When the carrier invoice arrives, the difference (markup included) becomes an adjusting billable event in an open billing run; frozen runs are never edited. No tolerance and no silent write-off. | FR-295. `Wh3plFreightBillingService.java:38`. | Both |
| AHO-OPEN-01 | accounting-handover | DEFER-ACCOUNTING | Carrier: accounting `P4-01` / #174, band V620500–V620599. INTEGRATED is not offered on this release. | AHO-OPEN-01 record. D-16 item 6. | Both |
| AHO-OPEN-03 | accounting-handover | DEFER-ACCOUNTING | Carrier: accounting `P4-01` / #174 with `P2-18`. Until then, as built: an all-`ZERO_BAILMENT` movement emits nothing and is never valued. | D-6 (`DECISIONS.md:206`). AHO-ENV-05. | Both |
| AHO-OPEN-04 | accounting-handover | DECIDE | Remove the reclassify-to-`NOT_APPLICABLE` branch from RJ-011 and WS-052; no v1 transition writes that value. It comes back only with the accounting adapter. | ACC-GRD-04 as built. P2-22 D4. | Both |
| AHO-OPEN-05 | accounting-handover | DECIDE | Ratify the as-built map: buckets come from `direction` + `reason_context`; a reversal takes its original's bucket; VALUE_ONLY goes to revaluations; adjustment and count contexts go to adjustments; OPENING_BALANCE sits in its own period. Cut-off columns stay on drill-downs; envelope carriage waits for the accounting adapter. | `WhStockToGlRepositoryCustomImpl.java:37-50`. `V500003:87`. | Both |
| AHO-OPEN-06 | accounting-handover | DEFER-ACCOUNTING | Columns built (V510031); the open point is only the residual. Header-level amounts stay; any per-line split for partial receipts belongs to accounting `P4-01` using `P2-18` evidence. Don't invent line values. | AHO-OPEN-06 CLOSED note. DATA-MODEL §2.2. | Both |
| AHO-OPEN-07 | accounting-handover | DEFER-ACCOUNTING | Carrier: accounting `P4-01` + `P2-18` (provider grain and the difference formula). Meanwhile, no provider means "unavailable", never zero. | `WhbGlBalanceProvider.java:23-29`. RC-002. | Both |
| AHO-OPEN-08 | accounting-handover | DEFER-ACCOUNTING | The queue only fills under INTEGRATED, which isn't offered (AHO-01). Decide requester vs assigned worker with `P4-01` / #174. Keep P2-22 D1 as built until then. | AHO-OPEN-01 default. P2-22 D1. | Both (settled: Claude said DECIDE, GPT said USER) |
| AHO-OPEN-09 | accounting-handover | DECIDE | Don't claim a new number. Update `p2-18.md` line 5 and DATA-MODEL §7.2 to name the existing V511065. | `V511065__Seed_wh_rpt_stock_to_gl_permissions_menu_and_grid.sql:34,57` | GPT |
| AHO-OPEN-10 | accounting-handover | DECIDE | Amend BUILD-SPEC WS-219 to as-built: owner/group dimensions, `ownerType` default OWN, `posting_date` clock, stats tiles, empty state. Add the `GlBalanceProvider` line to PORT §4, documenting the existing interface. | `WhbGlBalanceProvider.java:35`. RC-001, RC-002, RC-006. | Both |
| AHO-OPEN-11 | accounting-handover | DEFER-ACCOUNTING | The switch runbook belongs to accounting `P4-01` / #174. The recommendations on record (emit nothing; DISCARDED) remain recommendations. | P0-12 OPEN-05/06/07. | Both |
| AHO-OPEN-12 | accounting-handover | DECIDE | Align the design set to the built six and seven status sets, the predecessor/void columns, `OPENING_BALANCE` and the envelope vocabulary. Remove the resolved OD-1 blocker wording; fix the FR-357/FR-398 citation. Owner: design-set fold. | accounting-handover contract rows 80/87/196. OD-1 RESOLVED (`DECISIONS.md:647`). | Both |
| AHO-OPEN-13 | accounting-handover | DEFER-ACCOUNTING | Carrier: accounting `P4-01`, with `P2-18` publishing a period-scoped pending-handover read port. Accounting never reads `whb_*` directly. | FR-251. WH-SC-163. D-6. | Both |
| CVL-OPEN-01 | costing-valuation | DECIDE | Default stands for standalone: warehouse maker-checker approval. Whether an accounting gate applies when installed goes to `P4-01`. | D-7. D-6 (`DECISIONS.md:175`). | Both (settled: Claude said DEFER, GPT said DECIDE) |
| CVL-OPEN-02 | costing-valuation | DEFER-ACCOUNTING | Carrier: accounting-india / accounting integration, with warehouse `P4-11`. The tax basis is a statutory valuation (India s.145A). Not built, but not withdrawn. | FR-250. OD-9 (`DECISIONS.md:648`). | Both |
| CVL-OPEN-03 | costing-valuation | DEFER-ACCOUNTING | Carrier: accounting `P4-01`. The stock-side lock stands as built. | FR-251. D-16 item 6. | Both |
| CPM-OPEN-01 | counterparty-master | DECIDE | Default stands: warehouse-base owns the thin identity; other modules join through external references. | OD-4 RESOLVED (`DECISIONS.md:670`) | Both |
| CCT-OPEN-01 | cycle-count | DECIDE | Default replaced: a FROZEN stocktake location refuses putaway into it, moves in or out and allocation. Only the stocktake's own count adjustments post. Receipts to dock or staging go ahead. | FR-157. CCT-T4-04. SAP MM physical-inventory posting block; EWM bin block. | Both (settled: GPT said USER with the same recommendation) |
| CCT-OPEN-02 | cycle-count | DECIDE | A = up to 80% of cumulative 12-month issue value, B = up to 95%, C = the rest. Editable per site; zero-value items are C. | FR-463. Pareto ABC practice (SAP MC40 and EWM ABC analysis use configurable %). | Both (settled: GPT said USER, recommended 80/95) |
| CCT-OPEN-03 | cycle-count | DECIDE | Default stands: 0–30, 31–60, 61–90, 91–180, 181–365, >365 days from the last outward movement. Stock with no outward movement goes in the oldest bucket. | FR-162. WS-212 as built. | Both |
| FBL-OPEN-01 | facility-branch-link | DECIDE | Default stands: refused while the site holds stock, reservations, transfers, counts or open documents. No adviser bypass. | OD-19 RESOLVED (`DECISIONS.md:693`) | Both |
| FBL-OPEN-02 | facility-branch-link | USER | Key `warehouse.putaway.capacity_enforcement` = `BLOCK` or `WARN` (warn needs an acknowledgement reason). **Recommend BLOCK** wherever a capacity column is set (null = unconstrained), with WARN as a per-site option. Temperature and owner rules stay hard either way. | FR-086. Advisory capacity at `WhPutawayRuleEngine.java:126`. SAP EWM capacity check per storage type. | Both (settled: Claude said DECIDE/WARN, GPT said USER/BLOCK) |
| GTE-OPEN-01 | gate-entry | DECIDE | Default stands: no override. Raise a store issue to cost object MACHINE first. | STO-D4 | Both |
| GTE-OPEN-02 | gate-entry | DECIDE | Default stands: one `GE` series per site; `gate_code` is a column. | gate-entry contract | Both |
| GBM-OPEN-01 | grn-bill-match | DECIDE | Default stands: wait for the bill; a manager may resolve `ACCEPT_FREE_OF_CHARGE` on the case only. The posted GRN line is never edited. | OD-28 (`FRD-STORES.md:371`). RQP-UNR-01. | Both |
| GBM-OPEN-02 | grn-bill-match | DECIDE | Default stands: two records, both linked to the source line, with no double recovery. Short against the bill is an invoice-quantity claim; short against the PO is an open delivery quantity (SAP practice). | grn-bill-match contract | Both |
| IGL-OPEN-01 | import-go-live | DECIDE | Default stands: record only. The runbook captures movements made during the window. | FR-413 ("anything that moves between is manual") | Both |
| IIS-OPEN-01 | incoming-inspection-sampling | DECIDE | Default stands: seed the `Z14-GII-AQL-<aql>` system family in V511314, taken cell by cell from a named edition of ANSI Z1.4 / IS 2500-1. | P8-05. ANSI/ASQ Z1.4 Table II-A. | Both |
| IIS-OPEN-02 | incoming-inspection-sampling | DECIDE | Default stands: contiguous bands with an open top band. | OD-25 (`FRD-STORES.md:368`) | Both |
| IMD-OPEN-01 | india-movement-documents | DECIDE | Default stands: the UQC lives on the UoM master and is frozen onto each statutory document line. Restate FR-319. | SAP India UQC mapping per UoM | Both |
| IMD-OPEN-02 | india-movement-documents | DECIDE | Default stands: withdraw FR-321's MRP back-calculation clause. | OD-9 RESOLVED (no warehouse tax engine) | Both |
| IMD-OPEN-03 | india-movement-documents | DECIDE | Default stands: one MOOWR monthly return per licensed premises covers all bonded stock, including storage-only. | MOOWR Regulations 2019 (return per licensed premises). BND-T1-01. | Both |
| ITM-OPEN-01 | item-master | DECIDE | Default stands: in-scope sites only. | FR-405 | Both |
| LSS-OPEN-01 | lot-serial-status | DECIDE | Default replaced with a stated rule: past use-by blocks despatch; past best-before warns, and despatch needs a reason. Customer minimum remaining shelf life is a separate setting with no universal margin. | FR-095. EU 1169/2011 Art. 24. FSSAI labelling regs. SAP SLED/BBD. | Both (settled: GPT said USER with the same recommendation) |
| MRQ-OPEN-01 | material-requisition | DECIDE | Default stands: one level, plus a second level above `warehouse.stores.requisition_second_approval_value` (null = off). | OD-29 (`FRD-STORES.md:372`) | Both |
| MRQ-OPEN-02 | material-requisition | DECIDE | Default stands: MFG creates through the `WhMaterialRequisitionPort` port. A requisition made on the screen is not port-owned. | material-requisition contract §8a | Both |
| BOM-OPEN-01 | mfg-bom | DECIDE | Default stands: use the default alternative if it is among the matches, otherwise the lowest `alternative_no`. | SAP alternative selection by lot size | Both |
| BOM-OPEN-02 | mfg-bom | DECIDE | Default stands: refuse outputs on a phantom (`422 PHANTOM_OUTPUTS_NOT_ALLOWED`). Its operations are appended to the parent at explosion and keep their links. | Odoo kit BoMs (no by-products). SAP phantom. | Both |
| BOM-OPEN-03 | mfg-bom | DECIDE | Default stands (already adopted): a COALESCE unique index. | PostgreSQL treats NULLs as distinct | Both |
| BOM-OPEN-04 | mfg-bom | DECIDE | Default stands: no auto-OBSOLETE; effectivity is checked when read. | BOM-T3-02. SAP date effectivity. | Both |
| BND-OPEN-01 | mfg-bonded-issue | USER | (a) a bonded LOSS, duty-accountable (the default); (b) register-only process waste. **Recommend (a)** until a customs adviser rules. | D-17 item 3 leaves GitHub 539 with the product owner | Both |
| BND-OPEN-02 | mfg-bonded-issue | USER | (a) allow MOOWR job work with a bond-officer permission; (b) keep it refused. **Recommend (a)**, enabled only once the permission and the return-period source are confirmed. | D-17 item 3 leaves GitHub 543 with the product owner | Both |
| CST-OPEN-05 | mfg-costing-close | DECIDE | Default stands: cap the credit at `A_r`; flag the excess on the cost sheet. | IAS 2 §14 | Both |
| CST-OPEN-06 | mfg-costing-close | DECIDE | Default replaced: quantity consumed into a parent order follows the parent. While the parent is open it goes to the parent's `VIRT-PRODUCTION`; once closed, to the parent's output lots still on hand (capped as in CST-07), with the remainder to COGS. Parent closure alone isn't treated as a sale. | FR-633. FR-656. SAP ML multi-level settlement. | GPT |
| CST-OPEN-07 | mfg-costing-close | DECIDE | Default stands: cap at the positions' carried value; the remainder goes to the target from CST-06. | FR-656 | Both |
| CST-OPEN-08 | mfg-costing-close | DECIDE | Default stands: exempt a zero residual from the movement requirement; post no movement. | mfg-costing-close contract | Both |
| MSI-OPEN-01 | mfg-material-staging-issue | DECIDE | Default stands (adopted): the order owns its reservations. | MD-16 | Both |
| MSI-OPEN-02 | mfg-material-staging-issue | DECIDE | Default stands: a child `whm_staging_list_line_postings` table in V560040. | mfg-material-staging-issue contract | Both |
| MSI-OPEN-03 | mfg-material-staging-issue | DECIDE | Default stands: MSI-T1-13 captures the reason on the order. | mfg-material-staging-issue contract | Both |
| MSI-OPEN-04 | mfg-material-staging-issue | DECIDE | Default stands: no reversal hook; a correction is a store return. | FR-533. STO-D11. MD-17. | Both |
| MSI-OPEN-05 | mfg-material-staging-issue | DECIDE | Default stands: a STRICT substitution is pending while `approved_by` is null. Add a status only if a reject path is wanted. | mfg-material-staging-issue contract | Both |
| MRP-OPEN-03 | mfg-mrp | DECIDE | Default replaced: add `INSIDE_TIME_FENCE` to `WHM_MRP_EXCEPTION`. Keep START_IN_PAST for a start that really is in the past. | FR-665. D365 firm time fence / SAP planning time fence. | Both |
| MRP-OPEN-04 | mfg-mrp | DECIDE | Default stands: converting from OPEN firms and converts atomically. | FR-666. SAP planned-order conversion. | Both |
| MRP-OPEN-05 | mfg-mrp | DECIDE | Default stands: seed an `MRP_DISMISS` reason context in V560001. | D-10 | Both |
| MRP-OPEN-06 | mfg-mrp | DECIDE | Default stands: archiving needs `:activate`. | FR-663 | Both |
| MRP-OPEN-07 | mfg-mrp | DECIDE | Default stands: exclude lots that expire before the requirement date. | MRP-N-05. D365 shelf-life planning. | Both |
| MRP-OPEN-08 | mfg-mrp | DECIDE | Default stands: `warehouse.manufacturing.mrp.schedule_cron` (null = manual). | FR-664 | Both |
| MRP-OPEN-10 | mfg-mrp | DECIDE | Default stands: core replenishment skips items planned as `MRP`. With MFG absent, core settings rule. | FR-662 | Both |
| PRO-OPEN-02 | mfg-production-order | DECIDE | Take the alternative: add `release_requested_by/at`. `released_*` is stamped only at actual release. | FR-635 | Both |
| PRC-OPEN-05 | mfg-production-receipt | DECIDE | Default stands: a `PRODUCTION_REVERSAL` transformation row linked to the original. Base change owned by `p0`, carrier P10-07. | FR-649 | Both |
| PRC-OPEN-06 | mfg-production-receipt | DECIDE | Default stands: a scrap-only final receipt is allowed. | PRC-GRD-02. SAP scrap-only confirmation. | Both |
| QRW-OPEN-04 | mfg-qc-rework | DECIDE | Add an `OPERATION_CONFIRMATION_CANCEL` reason context in V560001, matching MRP-05 in the same migration. | D-10. MRP-OPEN-05. | Claude |
| QRW-OPEN-05 | mfg-qc-rework | DECIDE | Default stands: no rework order for IN_PROCESS. | FR-653 | Both |
| QRW-OPEN-06 | mfg-qc-rework | DECIDE | Default stands: the rework order is a system effect of `:disposition`. | FR-653 | Both |
| QRW-OPEN-09 | mfg-qc-rework | DECIDE | Default stands: no; the tolerance counts receipt good quantity. | FR-647. SAP over-delivery tolerance. | Both |
| SUB-OPEN-06 | mfg-subcontracting | DECIDE | Default stands: a value-only `LANDED_COST_APPLY` from the service-PO bill, owned by trade. | FR-658. P2-28. | Both |
| SUB-OPEN-07 | mfg-subcontracting | DECIDE | Default stands (v1 scope). | SUB-GRD-10 | Both |
| SUB-OPEN-08 | mfg-subcontracting | DECIDE | Default stands: its own grid and filter scope in V560080. | FR-669 | Both |
| SUB-OPEN-09 | mfg-subcontracting | DECIDE | Default stands: the india bean decides. | D-8 | Both |
| MOD-OPEN-01 | module-contract | DECIDE | Withdraw FR-363 and FR-364; void `p3-20` / `p3-21`. Plant spares to machines are covered by core store issue to MACHINE. | D-1 amendment (`DECISIONS.md:63-66`). D-16 item 6. | Both (settled: Claude said USER, GPT said DECIDE) |
| MOD-OPEN-02 | module-contract | DECIDE | Default stands: extend the fixture to reserve, consume and subscribe (`p0-14`). | D-11. FR-353. | Both |
| MPR-OPEN-18 | movement-post-reverse | DECIDE | Default stands: `P7-13` narrows the index in V500030. | D-16 item 4. R30 CP-GA-012. | Both |
| MRA-OPEN-01 | mrn-authorisation | DECIDE | Default stands. | OD-26 (`FRD-STORES.md:369`) | Both |
| MRA-OPEN-02 | mrn-authorisation | DECIDE | Default stands: no putaway before authorisation. | SAP GR-blocked stock | Both |
| MRA-OPEN-03 | mrn-authorisation | DECIDE | Default stands: restore the prior status; `P8-08` verifies. | MRA-GRD-08 | Both |
| NFR-OPEN-01 | non-functional | USER | (a) keep FR-443…445; (b) withdraw them as apparel retail. **Recommend** keeping the built schema, building nothing more and fencing ratio packs. | Segment call (sorting rule, `DECISIONS.md:612`). D-16 item 2. | Both |
| NFR-OPEN-02 | non-functional | USER | (a) serve pharma; (b) decline in writing and fence the pack. **Recommend (b)** until a funded requirement exists. | S-035 | Both |
| NFR-OPEN-03 | non-functional | DECIDE | Default stands: per customer / ship-to. A channel key with only one possible value (B2B) separates nothing. | D-16 item 2. SAP customer-material info record. | Claude |
| ODS-OPEN-01 | outbound-despatch | DECIDE | Default stands: the chain ends at the manifest. Logistics owns the trip. | FR-330…348 | Both |
| ODS-OPEN-02 | outbound-despatch | DECIDE | Default stands for v1 (evidence only). The v2 dispute half stays in the FR, not scheduled. | FR-206 | Both (settled: GPT said USER) |
| OEV-OPEN-01 | outbox-events | DECIDE | Default stands: base keys only narrow an authenticated user. | OD-8 RESOLVED. P5-22 build note. | Both |
| OEV-OPEN-02 | outbox-events | DECIDE | Default stands: restate FR-338 to the equipment issue/return pair. | FR-338 | Both |
| POS-OPEN-01 | po-schedule-port | DECIDE | Default stands. | po-schedule-port contract | Both |
| POS-OPEN-02 | po-schedule-port | DECIDE | Default stands: in-process and REST, same command semantics. | po-schedule-port contract | Both |
| POS-OPEN-03 | po-schedule-port | DECIDE | Default stands: OD-45 (A). | `DECISIONS.md:704`. OD-32. | Both |
| RQP-OPEN-22 | receipt-qc-putaway | DECIDE | Default replaced: add per-warehouse default settings for the four behaviours, frozen onto each GRN. Defaults are the simple ones. | FR-126. `V510014:145-149` (comment says "per-warehouse configuration… frozen onto the receipt"). | Both |
| RQP-OPEN-23 | receipt-qc-putaway | DECIDE | Default replaced: Resolve opens the prefilled create flow of the resolution document and links the result. A document already completed may still be linked. | FR-138 says "creates". RQP-DIV-03. | GPT |
| RQP-OPEN-24 | receipt-qc-putaway | DECIDE | Default replaced: auto-open INVOICE on a bill-vs-GRN variance (P8-04), ASN on an ASN-vs-GRN difference at post, SUPPLIER_RETURN on a short-accepted return. Deduplicate per source line. | FR-138 | GPT |
| RMV-OPEN-01 | rem-removal | DECIDE | Default stands: drop `supports_cod`. | OD-22 | Both |
| RMV-OPEN-02 | rem-removal | DECIDE | Default stands: 8 values. | OD-23 | Both |
| RMV-OPEN-03 | rem-removal | USER | (a) a quoted amount from the 3PL's own tariff, trued up on the invoice; (b) the actual invoice only. **Recommend (a)**, keeping FR-295. `P7-02`'s comment-only change is fine as interim cleanup. | OD-24. FR-295. | Both |
| RMV-OPEN-04 | rem-removal | DECIDE | Default replaced: a B2B failed delivery maps to `EXCEPTION`, keeping the raw carrier status. `P7-03` states it in its acceptance. | `V510203:79-82` | Both |
| RPN-OPEN-01 | replenishment | DECIDE | Default replaced: remove the manual POST from WS-096 and restate FR-257. Lost sales come through trade. | D-17 item 4 (`DECISIONS.md:583`) | Both |
| RKP-OPEN-02 | reports-kpis | DECIDE | The ten seeded metrics stand. All 29 must have a written disposition (placed with a carrier, or refused) in the reports-kpis contract. | FR-394. `p2-21` acceptance. | Both |
| RMR-OPEN-01 | returns-rma | DECIDE | Default stands: withdrawn. | D-16 item 6 | Both |
| RMR-OPEN-02 | returns-rma | DECIDE | Not withdrawn. FR-272's checklist half stays v2, marked deferred against PARTIALLY VOID `P5-13`. A new task is needed when it is scheduled. | FR-272. `IMPLEMENTATION-PLAN.md:612`. | Both |
| STR-OPEN-01 | stock-transfer | DECIDE | Default stands: an over-days parameter per run. | FR-149 | Both |
| SIR-OPEN-01 | store-issue-return | DECIDE | Default stands. | OD-27 (`FRD-STORES.md:370`) | Both |
| SIR-OPEN-02 | store-issue-return | DECIDE | Default stands: name + time; optional signature document. | FR-535 | Both |
| SIR-OPEN-03 | store-issue-return | DECIDE | Default stands: `P8-13` names a grid id and scope per tab before build. | FR-539 | Both |
| TEP-OPEN-01 | task-execution-printing | DECIDE | v1 publishes `task.completed`. The FR-229 v3 contract (owner `P6-04`) adds versioned created, assigned, started and exception events carrying the `DEVICE` actor. | FR-229. `IMPLEMENTATION-PLAN.md:633`. | Both (settled: GPT said USER with the same recommendation) |
| TCE-OPEN-01 | trade-counterparty-evaluation | DECIDE | Default stands: seed under the owning-module guard. | D-16 item 5 | Both |
| TCE-OPEN-02 | trade-counterparty-evaluation | DECIDE | Default replaced: copy at create; refresh while DRAFT only by an explicit, audited user action; freeze at submit / RFQ issue. | FR-584 | GPT |
| TPO-OPEN-02 | trade-purchase-order | DECIDE | Pickers match `po_number` OR `source_document_ref` and show both. Owed by `p8-03` / `p8-04`. | OD-30 (`FRD-TRADE.md:590`) | Both |
| TPR-OPEN-02 | trade-purchase-requisition | DECIDE | Default stands; MFG has confirmed it. | FRD-MFG OD-41, OD-44 | Both |
| TPR-OPEN-03 | trade-purchase-requisition | DECIDE | Default stands: `409 CONCURRENT_MODIFICATION`. | PRO-GRD-21. PRC-GRD-18. | Both |
| TRA-OPEN-01 | trade-rfq-award | DECIDE | Default stands: print + download in v1. | trade-rfq-award contract | Both |
| VWO-OPEN-01 | vas-work-order | DECIDE | Default replaced: hard-reserve at Issue components, consume at Complete, release on cancel only with a recorded return. | `WhWorkOrderService.java:391`. MSI-OPEN-01 pattern. | Both |
| FR-258 | (replenishment / mfg-mrp) | RESTORE | Rewritten without the dealer-parts wording: a computed reorder-point and safety-stock proposal from consumption history for items planned by `REORDER_POINT`, with an override that needs a reason. Stays v3. Carrier: live `P10-11`, as a later-version increment. Note that installs without MFG would need it in core replenishment. | `FRD-MFG.md:415` (FR-662 typed only). SAP MRP type VM. D365 safety-stock journal. | GPT (Claude's KEEP dropped) |
| FR-471 | (reports-kpis) | RESTORE | Location-utilisation analysis stays v3. Carrier: live `P8-13` as a later-version increment (precedent: FR-463 in `P1-03`). It was withdrawn only because its owner went VOID, and storage stays in scope. | D-16 item 1. `IMPLEMENTATION-PLAN.md:1744`. SAP EWM bin utilisation. | Both |
| FR-397 | (reports-kpis) | KEEP-WITHDRAWN | Accessories coexistence is removed, so there is no second inventory to report on. | D-16 item 3 / RN-051. `P7-09`. | Both |

**Dropped after verification:**
- **Claude, AHO-OPEN-09** ("claim the next free number"): V511065 already exists, so a new number would collide.
- **Claude, MOD-OPEN-01** (USER): the D-1 amendment already records the decision.
- **Claude, FR-258** (KEEP-WITHDRAWN): typed FR-662 parameters don't compute a level, and SAP VM / D365 show computed levels are plant practice.
- **GPT, NFR-OPEN-03** (keep the channel axis): a key with only one value separates nothing.
- **GPT, QRW-OPEN-04** (free-text note): it breaks consistency with the reason context in the same V560001.
- **GPT, CST-OPEN-06** ("refuse an allocation it can't resolve"): it would block settlement. Replaced with the follow-the-parent cap.

**Contract quality:**
- The R30 index still lists AHO-OPEN-06 as open, but its own text says CLOSED.
- AHO-OPEN-05's row says "no source", but code already implements and documents the P2-18 decision.

**Parity:** the answers cover warehouse-base, warehouse, warehouse-3pl, warehouse-india, warehouse-trade and warehouse-manufacturing. The dealer, automotive, accessories, services, insurance and assets modules stay fenced (D-16 item 6). Mobile stays deferred (D-17 item 2).

**Referred to standards reviewer:** none.