# R27 — client purchase-to-stores flow: coverage, gaps and root cause

<!-- check-design-set: finding-citations file Q-043 — the accounting design set's open question (cited by `classic` `V610132:29-30`, accounting purchase requisition), not a warehouse R8 finding -->

**Date** 2026-10-22 · **Prefix** `RM-` · **Status** findings recorded; dispositions pending the user's decisions (§6)

**Scope boundary.** This review takes one client-supplied process diagram — a manufacturing
purchase-to-stores flow — and checks every step in it against the **built code** in `classic`
(`warehouse-base`, `warehouse`, `warehouse-3pl`, `warehouse-india`, with `mobile/` out of scope by
the 2026-09-11 user rule) and against this design set. Accounting is recorded in §4 for reference
only; the user deferred accounting work on 2026-10-22.

**Why this lens exists.** Unlike R3–R5, it starts from an outside business process, not from
competitor products. Unlike R10–R26, it does not start from this design set's own documents. Every
earlier lens either predates the design (R3/R4/R5 note that the repo was empty) or reads only what
the set already says (R10, R16, R20, R24). §5 shows that is why none of them caught these gaps.

`grep -rohE "\bRM-[0-9]{1,3}\b" docs issues tools | wc -l` → 0 before this file (the prefix was free).

---

## 1. The client flow (source requirement)

```
Purchase Department                       Store
  1 Purchase Requisition                    4 Gate Entry  (party name, PO no, bill no, bill date)
  2 Purchase Quotation                      5 Stock Inward (bill 100: short → debit note, excess → credit note)
  3 Purchase Order                          6 Quality Check — sampling by lot size
      a Fixed order  — qty and rate fixed         (1–1000 → 5 samples, 1–10000 → 20 samples)
      b Open order   — rate fixed               7 QC reject → material return through debit note
      c Blanket agreement — delivery schedule   8 MRN — authorised → Store
          (item, qty, delivery date)            9 Store
                                               10 Material (store) requisition
                                               11 Store issue
                                               12 Store return
```

## 2. Coverage against built code

Paths: `WH` = `classic/warehouse/backend/src/main/`, `MIG` = `WH/resources/db/migration/`,
`WHB-MIG` = `classic/warehouse-base/backend/src/main/resources/db/migration/`.

| ID | Step | Status | Evidence | Exact gap |
|---|---|---|---|---|
| `RM-001` | 1 Purchase Requisition | ABSENT | Zero hits for requisition, purchase_request or indent in the four modules. The nearest artefact is a system replenishment suggestion turned into a PO: `WH/java/ai/warehouse/service/WhReplenishmentSuggestionService.java:287`, linked by `wh_purchase_orders.replenishment_suggestion_id` (`MIG/V510011:106`) | No requisition document, requester, requesting department or approval |
| `RM-002` | 2 Purchase Quotation | ABSENT | No quotation, RFQ or bid tables. `outbound/rate-quotes` is carrier rate shopping (`WhRateQuote.java:25`) | No vendor quotation, comparison or award |
| `RM-003` | 3a Fixed PO | IMPLEMENTED | Header `MIG/V510011:81-151`. Line `:202-250`, where `ordered_quantity` is NOT NULL and > 0 (`:208, :235`) and `unit_price` is `:210`. `WhPurchaseOrderController.java:240-313` provides create/submit/approve/return/cancel/close | — |
| `RM-004` | 3b Open PO (rate only) | ABSENT | No PO-type column. `order_source` (STOCK/DAILY/VOR/EMERGENCY/…, `MIG/V510011:127-128`) is a reason code, not a contract type. Quantity is mandatory and must be > 0 | An open-quantity PO cannot be stored; no release or call-off document |
| `RM-005` | 3c Blanket agreement + delivery schedule | ABSENT | One `expected_delivery_date` per line (`MIG/V510011:213`), unique `(po_id, line_no)` (`:231`) | No agreement header, validity, drawn-down quantity or schedule-line table |
| `RM-006` | Agreed or contract rate | ABSENT (deliberate) | `whb_item_supplier_sources` refuses a price column (`WHB-MIG/V500050…:41, :200, :594-595`, FR-119) | Every PO line price is typed by hand |
| `RM-007` | 4 Gate Entry | PARTIAL | `wh_receiving_sessions` holds supplier, vehicle, driver, seal, free-text `gate_pass_ref` and photo (`MIG/V510013:98-110`). A PO or ASN is linked only after creation (`POST /{id}/documents`, `WhReceivingSessionController.java:216,247`). Boom-barrier gate events carry only a free `reference` (`WarehouseGateEvent.java:21-27`) | No supplier bill number or bill date at arrival; PO not on the arrival form; no gate-entry register or number |
| `RM-008` | 5 Stock Inward vs bill | PARTIAL | GRN has `po_id`, `asn_id`, supplier and an `invoice_matched` boolean (`MIG/V510014:128-156`). Lines have expected, received, accepted, rejected and free quantities (`:262-271`) | No bill number, bill date or billed quantity. `WhGoodsReceiptLine.billedQuantity()` returns `receivedQuantity` (`:207-209`). The invoice ref first appears on the v2 three-way match (`MIG/V510201:92-93`) |
| `RM-009` | 5 Short receipt → debit note | PARTIAL | `QTY_UNDER` auto-opens a QUANTITY reconciliation case (`WhGoodsReceiptService.java:164-171`). A `SHORT_SHIPMENT` supplier claim is manual, with its quantity pre-filled (`WhSupplierClaimValidationService.java:216-244`) | Compares against the PO/ASN, not the bill. No debit note; claim settlement is a reference only (`WhSupplierClaimService.java:66-67`) |
| `RM-010` | 5 Excess receipt → credit note | PARTIAL | Over-receipt tolerance resolved PO line → header → item → site; over-tolerance is refused with `OVER_RECEIPT_TOLERANCE_EXCEEDED` and opens an `OVER_RECEIPT` case (`WhGoodsReceiptPostingService.java:133, 477-509`) | No accept-excess path, no excess claim type (`MIG/V510216:107`), no credit note. The over-receipt contract has "no ratified rows" (`warehouse/docs/contracts/goods-receipt.contract.md:9,61`) |
| `RM-011` | 6 QC sampling by lot size | PARTIAL | Sample size proposed from the quantity on QC hold (`WhQualityInspectionService.java:274-284`). Passed and failed quantities are recorded (`MIG/V510016:183-185`). Bands are the hard-coded ANSI Z1.4 Level II table (`WhQualityInspectionSampleSize.java:35-38`) | The client's own bands cannot be configured. `FIXED_QUANTITY` and `PERCENTAGE` fall back to the whole lot (same file `:22-24, :55`) because no column holds the count or % |
| `RM-012` | 7 QC reject → supplier return | PARTIAL (deliberate) | RTV moves stock to BLOCKED (`MIG/V510016:61-64`). Supplier return DRAFT→APPROVED→PICKED→DISPATCHED→CLOSED with a `QUALITY_REJECTED` reason (`MIG/V510020:64-66, 97-98`). FR-139 refuses an automatic return | No action to raise a return from the inspection; `debit_note_ref` is free text (`MIG/V510020:110`) |
| `RM-013` | 8 MRN (authorised) | ABSENT | GRN is DRAFT→POSTED→REVERSED (`MIG/V510014:51-58`). The inspector alone releases to AVAILABLE and creates putaway (`WhQualityInspectionService.java:449`); only scrap needs a second person. A SYS-GRN print template exists (`MIG/V510060:323, 412-418`) | No MRN document, number, authoriser or status; the GRN page has no print action. "MRN" appears 0 times in the design set |
| `RM-014` | 9 Store | IMPLEMENTED | Site types STORE and WORKSHOP (`WHB-MIG/V500012:196-200`); SITE→…→POSITION location hierarchy; location custodian (`WHB-MIG/V500013:258-299`) | — |
| `RM-015` | 10 Material requisition | ABSENT | Demand types include WORK_ORDER/SCRAP/SAMPLE/JOB_ISSUE (`WHB-MIG/V500010:144-152`), but a demand order follows the shipping ladder OPEN→…→SHIPPED→DELIVERED (`MIG/V510040:111`) and has no department, cost centre, requester or approval | No requisition document |
| `RM-016` | 11 Store issue | PARTIAL | `ISSUE` movement type, `VIRT-CONSUMED-<site>` location and `CONSUMABLE` item type exist (`WHB-MIG/V500003:212`, `V500006:136`, `V500008:96`) | Nothing posts to `VIRT-CONSUMED`. No issue document, no department or cost object on an issue (`S-052` never filed) |
| `RM-017` | 12 Store return | ABSENT | Return types are all customer/vendor (`WHB-MIG/V500010:154-163`). Return receipt always books against `VIRT-CUSTOMER` (`WhReturnReceiptPostingService.java:63,112`). `ISSUE_REVERSAL` cancels a whole movement | No partial return of unused material from a department |

**Totals:** 2 implemented · 8 partial · 7 absent (17 rows; `RM-006` is the agreed-rate prerequisite of `RM-004`/`RM-005`).

## 3. Root cause — why these gaps survived the design and the build

| ID | Cause | Evidence |
|---|---|---|
| `RM-020` | **The product was framed for a vehicle-dealer parts department.** The segment table names it "**this is the target**". None of its 14 segments is manufacturing or factory stores. Multi-level BOM was pushed to "a manufacturing module" | `docs/COMPETITOR-BENCHMARK.md:99-112`; FR-268 (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:496`) |
| `RM-021` | **No department-side persona.** The persona list has storekeeper, supervisor, manager, inventory controller, buyer/parts manager, finance, auditor and 3PL client. R16 checked only those, plus five it inferred from the design | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:92-104`; `reviews/R16-role-and-persona-completeness.md` (method) |
| `RM-022` | **Requisition, issue and return lived only in the services adapter**, against workshop job cards (FR-360). Commit `64d1fe74d5` (2026-09-21, "remove both product adapters") deleted that adapter and re-homed none of it. `BATCH-WAREHOUSE-P2.md` says "DO NOT REBUILD" | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:655`; `issues/p2-26.md`; `classic` commit `64d1fe74d5` |
| `RM-023` | **A MAJOR finding stayed open.** `S-052` ("every issue carries a cost object — job, cost centre, work order") was marked NEEDS-TASK with a warning that it cannot be retrofitted, and was never filed | `GAP-REGISTER.md:614, 1025, 1061` |
| `RM-024` | **A raised gap was refused as covered.** "There is no inbound gate entry" was refused as a duplicate | `reviews/R10-operational-walkthrough.md:606` |
| `RM-025` | **Purchasing was assigned to a module that does not exist.** Requisition and RFQ went to a v2/v3 supply-chain module; warehouse owns the PO only "if SC is absent". Blanket and open PO were never mentioned | `reviews/R7-logistics-supply-chain-seam.md:418-424, 741` |
| `RM-026` | **Supplier bills were treated as an accounting/OCR concern.** In the dealer framing the dominant supplier is the OEM and local suppliers send "a message and an invoice PDF", so the bill never reaches the gate | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:298, 300, 1101` |
| `RM-027` | **No reference process catalogue.** The lenses benchmarked products from memory ("no web access", `R3:11-12`). No lens walked a standard purchase-to-pay or stores flow. Rounds 2–4 checked internal consistency only (R24 "derived the contracts from the design set") | `reviews/R3-erp-midmarket-audit.md:11-12`; `reviews/R24-workflow-contract-completeness.md:3` |
| `RM-028` | **The refusals list cannot record what nobody proposed.** Its rule is "an unstated absence reads as an oversight", yet none of its 25 rows covers requisition, MRN, store issue or gate entry | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:1076-1104` |

## 4. Adjacent modules (recorded for reference — accounting is deferred)

| ID | Finding | Evidence |
|---|---|---|
| `RM-030` | **A PO and a GRN exist in three modules.** `warehouse` (`wh_purchase_orders`, `wh_goods_receipts`), `accounting` (`AccPurchaseOrder`, `AccGoodsReceipt` posting Dr inventory / Cr GRNI, `AccBill`, value-only `AccDebitNote`) and `assets` (`asset_purchase_orders`, `asset_po_receipts`). Which module owns each step must be decided before any purchasing build | `classic/accounting/backend/.../service/AccGoodsReceiptService.java:55-69`; `classic/assets/.../V60057, V60059` |
| `RM-031` | **The warehouse→accounting handover has no receiver.** The warehouse emits `WhbAccountingEnvelopeV1` into `whb_accounting_handovers`, but nothing implements `WhbAccountingHandoverSink`. `accounting-adapter-dealer` is an empty shell. The contract cites accounting "P2-18", which is actually "Grid configuration". No warehouse-adapter task is filed in either design repo | `classic/warehouse-base/docs/contracts/accounting-handover.contract.md:159, 189, 227` |
| `RM-032` | **Accounting lacks** a supplier credit note (its `AccCreditNote` is a sales document), a purchase-return goods document (P3-09) and valuation from stock movements (P3-02). Requisition is deferred (`V610132:29-30`, Q-043) | `classic/accounting/.../AccCreditNote.java:85` |
| `RM-033` | **`accessories` and `assets` run separate stock stacks.** `accessories` has its own warehouses, bins, ledger and ISSUE/RETURN types. `assets` has a consumable issuance to USER/DEPARTMENT/WORK_ORDER (`V60565:82,167`). These are design references for `RM-015`–`RM-017`, not code to reuse | `classic/accessories/.../V30131`; `classic/assets/.../V60565` |

## 5. Prevention — process rules this review proposes

| ID | Rule |
|---|---|
| `RM-040` | **Maintain a reference process catalogue** (purchase-to-pay, inbound, quality, stores issue/return, production supply, outbound, inventory control) and score every row against the built code at each review round |
| `RM-041` | **Every catalogue row has exactly one owning module that exists.** A row owned by an unbuilt or deleted module is a gap, not coverage |
| `RM-042` | **Re-home or refuse before deleting.** Removing a module or adapter requires each function it owned to be moved or written into the refusals list in the same change (this was skipped in `64d1fe74d5`) |
| `RM-043` | **Every catalogue row must be covered, assigned to an existing module, or refused in writing.** The refusals list is checked against the catalogue, not against proposals |
| `RM-044` | **NEEDS-TASK cannot stay open** past the round that raised it: each one gets a task, a fold into a task, or a refusal (cf. `S-052`) |
| `RM-045` | **Run a client-walkthrough lens** on every real client flow supplied, end to end against the screens, as this review does |

## 6. Decisions pending (user)

1. Re-target the warehouse to manufacturing and storage only, with no dealer or retail framing. Requested 2026-10-22; impact analysis to follow this review.
2. Where purchasing (`RM-001`…`RM-006`) lives: the warehouse core or a separate module integrated with the warehouse.
3. Where manufacturing stores (`RM-013`, `RM-015`…`RM-017`, plus production supply) live: the warehouse core or a sibling module on the `warehouse-india` pattern.
4. Accounting items `RM-030`…`RM-032`: deferred by the user on 2026-10-22.
