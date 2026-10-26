# Functional Contract — India movement documents, statutory clocks and registers

> **What this is.** The functional truth for `warehouse-india`: the GST-aware **stock transfer**
> (derived and frozen branch references, same-company rule), the **delivery challan** as a numbered
> document per registered branch, **transport details**, the **e-way bill lifecycle** (Part-A, Part-B,
> validity, extension, cancellation window, consolidation, blocked GSTIN), the **transfer IRN** gate, the
> **job-work** and **goods-on-approval** clocks, **bonded / MOOWR** warehousing, the **statutory stock
> account**, ITC reversal, scrap and TCS, MRP on the lot, EPR, the **tax-document modes**, the compliance
> provider abstraction and the two **retention clocks**. The README lists e-way bill lifecycle and job-work
> return window as contract-required.
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.18 (`FR-304`…`FR-329`)
> for R30 `CP-FR-007` row 17 under `D-17` item a. Verified against `classic/warehouse-india`,
> `warehouse-base` and `warehouse` by grep. Not ratified.
>
> **Alignment.** Job work for production is dispatched by MFG through the core port and registered here
> (`mfg-subcontracting.contract.md` `SUB-GRD-04`, `SUB-T4-11`, `SUB-UNR-04`, `SUB-UNR-05`); bonded exits of
> production stock and the MOOWR monthly return are `mfg-bonded-issue.contract.md` (`BND-GRD-01`,
> `BND-GRD-02`, `BND-T1-01`…`-03`, `BND-UNR-04`). This contract owns the india side of those seams and does
> not restate their rules; where a row here meets one of theirs it names it.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Transfer (core) created → GST fields derived and frozen → challan issued → e-way bill Part-A → Part-B → dispatch gate (e-way, IRN, bonded, regulated) → arrival / return; job-work and approval clocks age open challan lines; periodic registers (stock account, ITC reversal, ITC-04, EPR, MOOWR, Form 3CD) are generated then filed |
| **Module** | `warehouse-india` (`ai.warehouseindia`, band `V540000`–`V549999`, prefix `whin_`, flag `enable.warehouse.india`, `WarehouseIndiaModuleConfig`) with v1 hooks in `warehouse-base` and `warehouse` |
| **Domain baseline** | `FR-304`…`FR-329` · `D-8`, `D-12`, `D-16`, `D-17` · `OD-1`, `OD-9` · `L-1`, `L-11` · core `wh_transfer_orders` (`V510031`), base `whb_transport_details` (`V500052`), `whb_reason_codes`, `whb_reason_code_tax_treatments` (`V500072`), `whb_uoms.gst_uqc_code` (`V500009`), lots and lot parties (`V500018`), `whb_retention_policies` (`V500067`) |
| **Owning tasks** (R30 §4) | `issues/p2in-01.md` (`FR-304`) · `p1-17` (`305`, `306`) · `p2in-03` (`307`) · `p1-11` (`308`) · `p2in-04` (`309`) · `p2in-02` (`310`, `326`) · `p4-01` (`311`, `325`) · `p4-02` (`312`) · `p4-03` (`314`) · `p0-04` (`315`) · `p4-04` (`316`, `317`) · `p0-02` (`318`) · `p1-03` (`319`, `320`, `327`) · `p4-05` (`321`) · `p4-06` (`322`) · `p4-07` (`323`) · `p4-08` (`324`) · `p2-20` (`328`) · `p4-09` (`329`) |
| **Primary tables** | `whin_gstin_profiles`, `_profile_branches`, `whin_compliance_registrations` (`V540010`) · compliance providers / environments / credential specs / credentials / auth sessions (`V540011`) · `whin_compliance_documents`, `whin_compliance_api_logs` (`V540012`) · `whin_delivery_challans`, `_lines` (`V540020`) · `whin_eway_bills`, `_lines`, `_events` (`V540030`), vehicle updates / cancellations / extensions (`V540100`), consolidated (`V540101`) · `whin_eway_bill_evidence` (`V541148`, `V541152`) · `whin_transfer_irn_evidence` (`V540112`) · `whin_job_work_registrations`, `_dispatch_lines`, `whin_itc04_returns`, `_lines` (`V540120`), processed-form return and scrap on dispatch lines (`V540190`, to build in `p10-10`) · `whin_stock_account_periods`, `_lines` (`V540130`) · `whin_itc_reversals`, `whin_tcs_sections` (`V540131`) · bonded licences, warehousing bonds, bond utilisations, ex-bond clearances (`V540140`) · `whin_approval_dispatches`, `whin_approval_clocks` (`V540150`) · EPR (`V540160`) · `whin_retention_policies` (`V540170`) · `whin_form3cd_runs`, `_lines` (`V540181`) |
| **Routes / screens** | WS-173…WS-191, WS-226 |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | A cross-GSTIN transfer is a taxable supply derived, not chosen, and frozen at creation | `IMD-GRD-01`, `IMD-GRD-02` |
| A2 | Goods do not leave without an active e-way bill (Part-B filed, in validity) where one is required | `IMD-GRD-07` |
| A3 | Job work and goods on approval age against their statutory clocks from the challan date | `IMD-T3-01`, `IMD-T3-02` |
| A4 | The stock account is per registration and recomputable for history | `IMD-T1-12`, `IMD-GRD-12` |
| A5 | Missing tax never defaults to zero; mode `NONE` cannot finalise a document that needs tax evidence | `IMD-GRD-15` |
| A6 | Compliance bodies are never stored in clear; no controller can trigger a real filing from a demo | `IMD-UNR-04`, `IMD-UNR-05` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Source |
|---|---|---|---|
| Delivery challan | `ISSUED` · `CLOSED` *(reserved — no transition reaches it, `IMD-DIV-07`)* · `CANCELLED` | `whin_delivery_challans.status` (`WhinDeliveryChallan`) | FR-307 |
| E-way bill | `PART_A_PENDING` · `PART_A` · `ACTIVE` · `CLOSED` *(reserved, `IMD-DIV-07`)* · `CANCELLED` · `REJECTED` · `BLOCKED_GSTIN`; Part-B `EMPTY` · `PENDING` · `FILED`; `EXPIRED` is **derived on read, never stored** (`IMD-GRD-21`) | code list `WHIN_EWAY_BILL_STATUS` (no CHECK, `D-10`) | FR-309 |
| Recorded e-way evidence (manual, no provider) | `ACTIVE` · `CANCELLED` · `EXPIRED` (stored only by a challan cancel past validity) | `whin_eway_bill_evidence.status`, `chk_whin_ewbe_status` (`V541148`, widened `V541152`) | FR-309, FR-325 |
| Consolidated e-way bill | `GENERATE_PENDING` · `GENERATED` · `CANCELLED` · `REJECTED` | `WHIN_EWAY_CONSOLIDATED_STATUS` | FR-309 |
| Job-work registration | `REGISTERED` · `DISPATCHED` · `PARTIALLY_RETURNED` · `RETURNED` · `CANCELLED` | `whin_job_work_registrations.status` | FR-312 |
| Approval dispatch | `REGISTERED` · `AT_CUSTOMER` · `PARTIALLY_SETTLED` · `SETTLED` · `DEEMED_SUPPLY_RAISED` · `CANCELLED` | `whin_approval_dispatches.status` | FR-322 |
| Stock account period | `GENERATED` · `FILED` | `whin_stock_account_periods.status` | FR-314 |
| Compliance document | `PENDING` · `SUBMITTED` · `ACCEPTED` · `REJECTED` · `UNKNOWN` · `CANCELLED` | `whin_compliance_documents.status` | FR-326 |
| Transfer IRN evidence | `ACTIVE` · `CANCELLED` | `whin_transfer_irn_evidence.status` | FR-311 |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor / class | Side effects | UI | Source |
|---|---|---|---|---|---|---|---|---|
| IMD-T1-01 | — | Issue a delivery challan for a transfer / demand order / job work / approval / exhibition / repair / other movement (`WHIN_CHALLAN_PURPOSE`) | `ISSUED` | one live challan per source, else `409 CHALLAN_ALREADY_LIVE` · `sourceDocumentId`; print template present | `WhinDeliveryChallanService` | gapless number from the issuing site's **`REGISTERED` branch at the document date** (series `DC`); lines carry UQC and HSN | WS-178 | FR-307, FR-426 |
| IMD-T1-02 | `ISSUED` | Cancel challan | `CANCELLED` | no live e-way bill (`409 CHALLAN_HAS_LIVE_EWAY_BILL`), no live IRN (`409 CHALLAN_HAS_LIVE_IRN`), no open job-work registration (`409 CHALLAN_HAS_OPEN_REGISTRATION`) | same | number stays issued; print marked cancelled | WS-178 | FR-307 |
| IMD-T1-03 | — | Generate Part-A (consignor) | `PART_A_PENDING` → `PART_A` / `REJECTED` / `BLOCKED_GSTIN` | one live bill per challan, else `409 EWAY_BILL_ALREADY_LIVE` · `challanId`; thresholds `warehouse.india.eway_bill.threshold.*`; settings configured, else `422 EWAY_BILL_SETTING_NOT_CONFIGURED` | `WhinEwayBillService` via `WhinComplianceGateway` | compliance document + event `PART_A_GENERATED` | WS-179 | FR-309 |
| IMD-T1-04 | `PART_A` · `ACTIVE` | Fill / update Part-B (vehicle) | `ACTIVE` (Part-B `FILED`) | transport details complete (`IMD-GRD-05`); a road movement without a vehicle is refused `422 VEHICLE_NUMBER_REQUIRED`, a missing mode `422 TRANSPORT_MODE_REQUIRED` (`WhinEwayBillValidationService.java:71-77`) — the null-Part-B defect is not reproduced (`EMPTY` is the Part-B status a bill starts in, `WhinEwayBill.java:105`, not a refusal) | same | `whin_eway_bill_vehicle_updates` row; validity from distance (`validity_km_per_day.regular` / `.odc`) | WS-179 | FR-309, FR-308 |
| IMD-T1-05 | `ACTIVE` | Extend in transit | `ACTIVE` | inside `extension_window_hours`; ≤ `extension_max_days`; remaining distance later than before (`EWAY_BILL_EXTENSION_NOT_LATER`, `EWAY_BILL_EXTENSION_CEILING`, `409 EWAY_BILL_EXTENSION_WINDOW_CLOSED`) | same | `whin_eway_bill_extensions` row | WS-179 | FR-309 |
| IMD-T1-06 | `PART_A` · `ACTIVE` | Cancel | `CANCELLED` | inside `cancel_window_hours`, else `409 EWAY_BILL_CANCEL_WINDOW_CLOSED`; goods not moved (`EWAY_BILL_GOODS_ALREADY_MOVED`); not inside a consolidated bill (`EWAY_BILL_IN_CONSOLIDATED_BILL`); reason required (`CANCEL_REASON_REQUIRED`) | same | `whin_eway_bill_cancellations` row | WS-179 | FR-309 |
| IMD-T1-07 | — | Consolidate bills of one vehicle | `GENERATE_PENDING` → `GENERATED` | one live consolidated membership per bill (`V540102`) | `WhinEwayBillConsolidatedService` | — | WS-180 | FR-309 |
| IMD-T1-08 | — → `REGISTERED` → `DISPATCHED` → `PARTIALLY_RETURNED` → `RETURNED` | Register job work against a `JOB_WORK` challan; returns post against it | as named | challan is `JOB_WORK` (`422 CHALLAN_NOT_JOB_WORK`), issued, registered once (`409 CHALLAN_ALREADY_REGISTERED`); job-work type `INPUTS` / `CAPITAL_GOODS` | `WhinJobWorkRegistrationService` (MFG dispatch reaches it through `SUB-T4-03`; licensed-status stock adds `SUB-T4-11`) | owner unchanged (`L-11`, `SUB-GRD-04` backstop); clock `IMD-T3-01` | WS-181 | FR-312 |
| IMD-T1-08a | `DISPATCHED` · `PARTIALLY_RETURNED` | MFG subcontract receipt (`registerReturn`), write-off approve (`registerLoss`) or receipt reversal (`reverseReturn`) through the job-work port | `PARTIALLY_RETURNED` / `RETURNED` (a reversal steps back) | the return is in processed form (`returnedAsItemId`, consumed input, scrap, scrap retained); a reversal or loss against a **filed** ITC-04 period is refused (`IMD-GRD-22`) | india job-work bean (to build, `p10-10`) | dispatch-line return / scrap columns (`V540190`); ITC-04 lines | — | FR-312 |
| IMD-T1-08b | — | Record an e-way bill generated on the portal (manual evidence, no provider) | evidence `ACTIVE` | `IMD-GRD-23` | `WhinEwayBillEvidenceService` | audit `WHIN_EWAY_BILL_RECORDED` | WS-178 | FR-309, FR-325 |
| IMD-T1-08c | evidence `ACTIVE` | Record the bill as cancelled at the portal | evidence `CANCELLED` | an `ACTIVE` row exists, else `EWAY_EVIDENCE_NOTHING_TO_CANCEL`; reason-coded; `EWAY_EVIDENCE_CANCEL_NOT_ISSUED` | `WhinEwayBillEvidenceService` (takes the evidence row lock the dispatch guard takes) | audit `WHIN_EWAY_BILL_CANCELLED_AT_PORTAL` | WS-178 | FR-309 |
| IMD-T1-08d | evidence `ACTIVE` | Challan cancelled while the evidence is past `valid_until` | evidence `EXPIRED` | — | challan cancel (`V541152`) | local close-out; nothing filed | — | FR-309 |
| IMD-T1-09 | — → `REGISTERED` → `AT_CUSTOMER` → `PARTIALLY_SETTLED` / `SETTLED` / `DEEMED_SUPPLY_RAISED` | Goods on approval against an `APPROVAL` challan | as named | challan is `APPROVAL` (`422 CHALLAN_NOT_APPROVAL`); `warehouse.india.approval.deemed_supply_months` configured (`APPROVAL_PERIOD_NOT_CONFIGURED`) | `WhinApprovalDispatchService`, `WhinApprovalReversalRecorder` | stock stays ours at a customer location on the challan | WS-188 | FR-322 |
| IMD-T1-10 | — | Record / clear ex-bond | posted clearance | licence and bond valid on the bill-of-entry date (`LICENCE_NOT_VALID_ON_DATE`, `BOND_NOT_VALID_ON_DATE`); utilisation not exceeded (`409 BOND_UTILISATION_EXCEEDED` · `amount`) | `WhinExBondClearancePostingService`, `WhinExBondClearancePostGuard` | consumes an **identified** bonded quantity; bond utilisation reduced | WS-185…WS-187 | FR-323 |
| IMD-T1-11 | — | Record transfer IRN evidence | `ACTIVE` → `CANCELLED` | tax mode admits it (`IMD-GRD-15`) | `WhinTransferIrnService` | — | WS-176 | FR-311, FR-325 |
| IMD-T1-12 | — → `GENERATED` → `FILED` | Generate / regenerate / file the statutory stock account per registration × period | as named | not filed (`409 STOCK_ACCOUNT_FILED`); snapshot current (`STOCK_ACCOUNT_SNAPSHOT_STALE`); register reconciles (`STOCK_ACCOUNT_REGISTER_MISMATCH`) | `WhinStockAccountPeriodService` | lines in the mandated categories, RM / FG / scrap / wastage, goods with job workers | WS-183 | FR-314 |
| IMD-T1-13 | — → computed → reported | Compute / report ITC reversals for a period | reported rows frozen (`V540133`) | treatment present (`ITC_REVERSAL_TREATMENT_MISSING`); receipt resolvable | `WhinItcReversalService`, `WhinReceiptReachBack` | — | WS-184 | FR-316, FR-315 |
| IMD-T1-14 | — → generated → filed (or discarded) | EPR return per category × period | as named | `EPR_RETURN_FILED`, `EPR_RETURN_INCOMPLETE` | `WhinEprReturnService`, `WhinEprMovementRecorder` | — | WS-189 | FR-324 |
| IMD-T1-15 | — → `PENDING` → `SUBMITTED` → `ACCEPTED` / `REJECTED` / `UNKNOWN` | Any provider call (e-way, e-invoice) | as named | idempotency key unique (`V540184`) | `WhinComplianceGateway`, `WhinComplianceProviderAdapter` | `whin_compliance_api_logs` row, encrypted | WS-176, WS-177 | FR-326 |
| IMD-T1-16 | — | Generate Form 3CD quantitative statement / regenerate | new run; prior kept superseded (`V540182`) | — | `WhinForm3cdService` | — | WS-191 | FR-329, FR-328 |

## 2. Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | DB backstop | Source |
|---|---|---|---|---|
| IMD-GRD-01 | Source and destination sites of a transfer belong to the transfer's company | `422 CROSS_COMPANY_TRANSFER` (`WhTransferOrderCreationRules`) | — | FR-305 |
| IMD-GRD-02 | `source_warehouse_branch_id`, `destination_warehouse_branch_id` and `is_taxable_supply` are **derived at creation** from the two sites' `REGISTERED` links (or the serving branch) and never chosen by a user | edit refused | `trg_wh_transfer_orders_freeze_endpoints` (`V510031`) | FR-305 |
| IMD-GRD-03 | A site's registration may not change while it holds stock under another GSTIN | `409 WAREHOUSE_INDIA_REGISTRATION_CHANGE_WITH_STOCK` (`WhinRegistrationChangeStockValidator`) | — | FR-305, FR-314 |
| IMD-GRD-04 | A transfer records `transfer_price_basis` and `transfer_price` (and `cost_value`) as stored numbers | — | `V510031` columns, CHECK on `transfer_price_basis` | FR-306 |
| IMD-GRD-05 | Transport details for an e-way bill carry mode, transporter document number and date, vehicle number / type, from / to blocks, distance — optional at the core, required by the india rule | `422 TRANSPORT_MODE_REQUIRED` · `transportMode`, `422 TRANSPORT_DOC_REQUIRED` · `transporterDocNo`, `422 TRANSPORT_DOC_DATE_INVALID` | `whb_transport_details` polymorphic on `(document_type, document_id)` | FR-308 |
| IMD-GRD-06 | An e-way bill reads only `whb_transport_details`, the challan / transfer v1 columns and the compliance store | — | build rule `ArchitectureInvariantsTest$ComplianceGatewayRule$FilingReadBoundaryRule` (warehouse-india, P2-IN-02 #135 R33): guarded set = the frozen submission builders (`WhinEwayBillService`, `WhinEwayBillConsolidatedService`; EINVOICE `WhinTransferIrnService` exempt) + `service/whinewaybill/**` + `service/whincompliance/**` + `WhinEwayBill*` + the `*Sql` helpers they name; every `whin_*` table, plus a column ratchet: `whb_transport_details` (document_type, document_id, distance_km), `wh_transfer_orders` (id, demand_order_id), `wh_shipment_orders` (shipment_id, demand_order_id), `wh_shipments` (id, status, shipment_number, created_at), `whb_warehouses` (id, code, name, timezone), `whb_code_list_values` (id, list_code, code, name, is_active, sort_order), `whb_reason_codes` (id, code, name, context, is_active, requires_note, sort_order); repository / entity types limited to `Whin*` + `UserRepository`, `User`, `BaseEntity`, `WhbNativeRowValues`, `WhbJobRun`. The scan reads a file's string literals and text blocks joined in source order and cut at each top-level statement start, so a query split across variables or concatenated from one-word literals is scanned whole (a lone one-word literal is a parameter name and is dropped); core table names match in any case, quoted or `public.`-qualified. A statement that reads a core table names every column as `alias.column` — a bare column or wildcard fails; an upper-case FROM / JOIN binds any table, a lower-case one only a `whin_` / `wh_` / `whb_` table, so prose ("Select the bill from the portal") binds nothing. A JPQL query names only `Whin*` entities (a lower-case `from` refuses only a `Wh*` / `Whb*` entity). The ratchet compares `table.column` both ways: a new table or column is added to the rule and to this cell together, and one no longer read is removed from both | FR-310 |
| IMD-GRD-07 | Dispatch of a challan line that needs a bill requires a bill `ACTIVE`, Part-B `FILED`, `valid_until ≥ site today`, no cancellation in flight | `409 EWAY_BILL_REQUIRED` · `status`; `409 EWAY_BILL_NOT_ACTIVE` · `status` (`WhinEwayBillDispatchGuard`) | — | FR-309 |
| IMD-GRD-08 | Dispatch of an inter-state transfer that needs an IRN requires live IRN evidence | `409 IRN_REQUIRED` · `status`; `409 IRN_REQUIRED_TAX_MODE_NONE`; `IRN_CANCEL_IN_FLIGHT` (`WhinTransferIrnDispatchGuard`) | — | FR-311 |
| IMD-GRD-09 | Job-work return period resolves from `warehouse.india.job_work.return_period_years.inputs` / `.capital_goods` | `422 JOB_WORK_PERIOD_NOT_CONFIGURED` · `jobWorkType` | — | FR-312 |
| IMD-GRD-10 | A dispatch of duty-status stock to another site keeps its duty status; the destination holds the licence | `DESTINATION_LICENCE_REQUIRED` (`WhinBondedTransferDispatchGuard`); production exits: `BND-GRD-01`, `BND-GRD-02` | — | FR-323 |
| IMD-GRD-11 | A bond's amount is never below its utilised balance; a licence with an active bond cannot deactivate | `409 BOND_AMOUNT_BELOW_UTILISED` · `bondAmount`; `409 LICENCE_HAS_ACTIVE_BOND` · `isActive` | — | FR-323 |
| IMD-GRD-12 | A movement belongs to the registration of its site's `REGISTERED` link at `occurred_at`; a mid-period re-registration splits the account at the switch with no synthetic line | — | `WhinStockAccountRegistrationSplitIntegrationTest` | FR-314 |
| IMD-GRD-13 | A reason code carries `statutory_category` and an ITC treatment (dated in `whb_reason_code_tax_treatments`) | ITC reversal refuses `ITC_REVERSAL_TREATMENT_MISSING` | — | FR-315 |
| IMD-GRD-14 | A scrap sale line names a TCS section in force | `422 TCS_SECTION_NOT_IN_FORCE` · `lines` | scrap stock status seeded (`V540131`) | FR-317 |
| IMD-GRD-15 | `warehouse.tax.mode` ∈ {`PROVIDER`, `MANUAL_EVIDENCE`, `NONE`}; `NONE` permits only operations that need no tax document; a missing tax is never zero | `IRN_REQUIRED_TAX_MODE_NONE`, `422 EWAY_EVIDENCE_TAX_MODE_NONE` · `ewbNumber` | — | FR-325 |
| IMD-GRD-16 | `tax_classification_code` is snapshotted on every movement and document line | — | base movement-line column (`p0-02`) | FR-318 |
| IMD-GRD-17 | The statutory unit code (UQC) is on every india document line (challan, e-way, ITC-04, EPR) | — | `gst_uqc_code` columns `V540020`, `V540030`, `V540120`, `V540160` | FR-319 |
| IMD-GRD-18 | MRP, net content, country of origin and pack month/year are on the lot with item defaults; the packer / importer is a lot party | — | `V500018` lot columns, `whb_lot_counterparties` | FR-320 |
| IMD-GRD-19 | Statutory, expiry, manufacture and count dates are `DATE` with a date-only filter | — | e.g. `challan_date DATE`, `expected_return_date DATE` (`V540020`) | FR-327 |
| IMD-GRD-21 | An e-way bill past `valid_until` shows `EXPIRED`: a display and filter value computed on read, never stored, never in `WHIN_EWAY_BILL_STATUS`, a CHECK or a transition set; it has no row action | — | `WhinEwayBill.java:68-74` (`STATUS_EXPIRED`); dispatch still refuses on validity (`IMD-GRD-07`) | FR-309 |
| IMD-GRD-22 | A job-work return reversal or loss may not touch an ITC-04 period already filed | **to build** (`p10-10`): no refusal code exists today — grep finds only the audit type `WHIN_ITC04_RETURN_FILED`; `mfg-subcontracting` `SUB-GRD-13` names `409 JOB_WORK_RETURN_FILED`, which the bean must add | — | FR-312 |
| IMD-GRD-23 | Recording e-way evidence: tax mode not `NONE`; no provider ready for the branch; number, date and validity valid; number not already recorded | `EWAY_EVIDENCE_TAX_MODE_NONE`, `EWAY_EVIDENCE_PROVIDER_READY`, `EWB_NUMBER_REQUIRED`, `EWB_NUMBER_INVALID`, `EWB_DATE_INVALID`, `EWB_VALID_UNTIL_INVALID`, `EWB_NUMBER_ALREADY_RECORDED` (`WhinEwayBillEvidenceValidationService`) | one `ACTIVE` row per challan (partial unique index, `V541148`) | FR-309, FR-325 |
| IMD-GRD-20 | The **gate pass is e-way-bill-conditional**: it issues freely where no e-way bill is required, and is blocked only where one is legally required for a shipment on the handover and none is in validity (missing, Part-B pending, expired, cancellation in flight, recorded evidence cancelled at the portal, or the order's only challan cancelled). The core asks every registered gate bean before stamping the gate pass and names no jurisdiction | `422 HANDOVER_GATE_PASS_BLOCKED` naming each blocking shipment (`WhHandoverGatePassGate`, `WhHandoverService#issueGatePass`) | `WhinEwayBillHandoverGatePassGate` (warehouse-india, #147 G1–G3, R33): `needsBill` first (a lapsed voluntary bill below the threshold is ignored, unlike dispatch), then the dispatch guard's shared `activeRefusal` test; bill + evidence row locks after the core handover lock, never the challan lock; switched by `warehouse.india.eway_bill.handover_gate_mode` `ENFORCE_REQUIRED` (default) · `DISPATCH_ONLY` (V541162); `WhinEwayBillHandoverGatePassGateTest` | FR-195 |
| IMD-GRD-24 | **Trap (R33, #140 G3):** `CLOSED` is reserved on both the challan and the e-way bill. A future `CLOSED` writer must widen every `status = 'ISSUED'` reader to `IN ('ISSUED','CLOSED')`, backfill rows with `closed_at IS NOT NULL`, and flip back to `ISSUED` on reversal — otherwise the dispatch guards fail open (a `CLOSED` challan's order drops out of the dispatch facts and moves with no e-way or IRN check) | — (no writer: `IMD-DIV-07`) | readers: e-way dispatch facts and generate candidates (`WhinEwayBillRepositoryCustomImpl`), IRN dispatch facts and statistics (`WhinDeliveryChallanRepositoryCustomImpl`), evidence cancel (`WhinEwayBillEvidenceValidationService`), IRN cancel (`WhinTransferIrnValidationService`), `WhinEwayBillService#requireIssuedChallanLocked`, job-work / approval ageing; the freeze trigger has no `CLOSED`-terminal clause. p10-10's MFG job-work `registerReturn` (`IMD-T1-08a`) calls the same clock helpers, never a status | FR-307, FR-309 |

### 2.1 Unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| IMD-UNR-01 | A user choosing the transfer document kind or taxable flag | derived columns + freeze trigger (`IMD-GRD-02`) | FR-305 |
| IMD-UNR-02 | A second challan table | one `whin_delivery_challans`; MFG calls the port once per dispatch (`SUB-UNR-04`) | FR-313, FR-307 |
| IMD-UNR-03 | Editing a filed stock account, a reported ITC reversal or a filed EPR return | `STOCK_ACCOUNT_FILED`; `V540133` freezes every column; `EPR_RETURN_FILED` | FR-314, FR-316, FR-324 |
| IMD-UNR-04 | A compliance request / response body stored unencrypted | `chk_whin_cd_request_encrypted`, `_response_encrypted`, `_error_message_encrypted` (`enc:v<n>:` marker, `V540012`) | FR-326 |
| IMD-UNR-05 | A demo or test controller that can trigger a real statutory filing | no such controller under `ai.warehouseindia.controller` (grep) | FR-326 |
| IMD-UNR-06 | Base or core importing `ai.warehouseindia` or keying to a `whin_` table; MFG writing a `whin_` table | `WarehouseBaseCouplingTest`; `SUB-UNR-05`, `BND-UNR-04` | FR-304 |
| IMD-UNR-07 | A job-work clock started from anything but the challan date | clock columns live on the challan line; a movement without a challan has no clock | FR-312 |
| IMD-UNR-08 | A back-dated stock figure read from balances | as-at computed from movements (`WhStockAsAt*`, `WhReportsComputeFromLedgerTest`); snapshots are a cache | FR-328 |

## 3. T3 — Time rules

| ID | Rule | Clock | Changes | Job | Source |
|---|---|---|---|---|---|
| IMD-T3-01 | Job-work line ageing: `RETURN_DUE` at expected return − `job_work.obligation_lead_days`; `DEEMED_SUPPLY_DUE` at challan date + return period | challan date | obligation raised | `WhinJobWorkAgeingService`, `WhinJobWorkAgeingScheduler`, `WhinChallanClockAger` | FR-312 |
| IMD-T3-02 | Goods on approval: obligation due at `approval.obligation_lead_days` before the deemed-supply date (`deemed_supply_months`); crossing it raises the deemed supply | challan date | `DEEMED_SUPPLY_RAISED` | `WhinApprovalAgeingService`, `WhinApprovalAgeingJob` | FR-322 |
| IMD-T3-03 | Warehousing clock per bill of entry (`bonded.warehousing_period_days.*`, `interest_free_days`), alert at `clock_alert_days`; licence expiry alert at `licence_expiry_alert_days` | BOE date / licence `valid_to` | alert | `WhinWarehousingClockJob`, `WhinBondedLicenceExpiryJob` | FR-323 |
| IMD-T3-04 | E-way validity from distance; cancel window closes at `cancel_window_hours` | Part-B time | cancel refused after | `WhinEwayBillCancelWindowService` | FR-309 |
| IMD-T3-05 | Two retention clocks on the same rows — financial years and GST period — with per-item shelf-life retention and a legal hold that stops both | record date | purge eligibility / alert (`retention.policy_end_alert_days`) | `WhinRetentionClockJob`, `WhinRetentionClockContributor`; `whb_retention_policies.legal_hold*` | FR-329 |
| IMD-T3-06 | GSTIN drift | daily | finding | `WhinGstinDriftScheduler` (`gstin_drift.check_enabled`) | FR-305 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| IMD-T4-01 | transfer created under different GSTINs | document is a taxable supply: challan / transfer invoice series, IRN gate, valuation stored | core creation rules + india contributors (`WhinDeliveryChallanTransferActionContributor`) | FR-305, FR-306 |
| IMD-T4-02 | movement posted | stock-account register row by registration at `occurred_at` | `WhinStockAccountMovementRecorder` | FR-314 |
| IMD-T4-03 | write-off movement posted | ITC reversal candidate reaching the receipt that brought the lot in (lot-to-layer) | `WhinItcReversalMovementRecorder`, `WhinLedgerReceiptReachBack` | FR-316 |
| IMD-T4-04 | movement of an EPR-category item | EPR register quantity | `WhinEprMovementRecorder` | FR-324 |
| IMD-T4-05 | job-work return / write-off reversal | registration status and open quantity updated | `WhinJobWorkReversalRecorder`; bonded side `SUB-T4-11` | FR-312 |
| IMD-T4-06 | stock-by-MRP read | MRP as a balance dimension, incl. non-batch items | `WhinStockByMrpService` (WS-226) | FR-321 |
| IMD-T4-05a | MFG subcontract receipt / write-off / receipt reversal, india bean present | `registerReturn` records the return in processed form and waste; `registerLoss` the loss at the job worker; `reverseReturn` steps the registration back — all for ITC-04, in the caller's transaction | india job-work bean (to build, `p10-10`); `SUB-T4-06`, `SUB-T4-10` | FR-312 |
| IMD-T4-05b | dispatch of a challan with `ACTIVE` recorded evidence | the evidence satisfies `IMD-GRD-07` as an `ACTIVE` provider bill with Part-B filed does, inside its validity | `WhinEwayBillDispatchGuard` (locks the evidence row) | FR-309 |
| IMD-T4-07 | install enables india | the fifth module loads on `enable.warehouse.india`; its seeds guard ownership (`RL-003`) | `WarehouseIndiaModuleConfig` (`@ConditionalOnExpression`), `V540000` | FR-304 |

## 5. T5 — Screen contract

| ID | Screen | Offers | Source |
|---|---|---|---|
| IMD-T5-01 | WS-173…WS-177 GSTIN Profiles · Compliance Providers · Registrations · Documents · API Logs | profiles, provider environments and credentials (masked), documents with outcome, encrypted logs | FR-326, FR-305 |
| IMD-T5-02 | WS-178 Delivery Challans / WS-179 E-way Bills / WS-180 Consolidated | issue / cancel / print; record e-way evidence, record cancelled at portal (`IMD-T1-08b`/`-08c`); Part-A, Part-B, extend, cancel; consolidate; status filter offers derived `EXPIRED`. **R33:** WS-178 discloses `CLOSED` reserved (`deliveryChallan.hints.closedReserved`: a full job-work return or approval settlement stops the return clock, the challan stays `ISSUED`); WS-179 discloses it too (`ewayBill.hints.closedReserved`: no portal close step; the status filter still serves `CLOSED`, which matches no bill). WS-111 Issue gate pass (core) is refused `422 HANDOVER_GATE_PASS_BLOCKED` per `IMD-GRD-20` under `handover_gate_mode = ENFORCE_REQUIRED` | FR-307, FR-309 |
| IMD-T5-03 | WS-181 Job Work / WS-182 ITC-04 / WS-188 Goods on Approval | registrations, returns, ageing tiles | FR-312, FR-322 |
| IMD-T5-04 | WS-183 Statutory Stock Account / WS-184 ITC Reversals / WS-189 EPR Returns | generate, regenerate, file | FR-314, FR-316, FR-324 |
| IMD-T5-05 | WS-185…WS-187 Bonded | licences, bonds with utilisation, ex-bond clearances | FR-323 |
| IMD-T5-06 | WS-190 Retention Policies / WS-191 Compliance Tasks & Rules | policies, legal hold, Form 3CD runs, tasks | FR-329 |
| IMD-T5-07 | WS-226 Stock by MRP | stock by MRP band | FR-321 |

## 6. Code divergences

| ID | FR says | Code has (grep) | Source |
|---|---|---|---|
| IMD-DIV-01 | The statutory unit-quantity code is **on the item** and copied onto **every line** | `gst_uqc_code` is on `whb_uoms` (`V500009`) and on india document lines only; no item column and no movement-line column — **resolved R31**: `FR-319` restated to the build (`IMD-OPEN-01`) — **Triage 2026-10-23: AMEND-SPEC** — applied R31 (`FR-319` restated); stands as the rule | FR-319 |
| IMD-DIV-02 | MRP-inclusive **back-calculation of the taxable value** on the issue document | `WhinStockByMrpResponse` states the MRP-inclusive value is "never a taxable value (OD-9: warehouse computes no tax)" — follows `FR-325` / `OD-9`, contradicts `FR-321` — **resolved R31**: the clause is withdrawn (`IMD-OPEN-02`) — **Triage 2026-10-23: AMEND-SPEC** — applied R31 (clause withdrawn); stands as the rule | FR-321, FR-325 |
| IMD-DIV-03 | The e-way adapter reads **only** v1 columns plus the compliance store | **Built R33 (2026-10-26):** `ComplianceGatewayRule$FilingReadBoundaryRule` (#135, `IMD-GRD-06`); the S3 F1 limitations are closed — a bare column or wildcard on a core-table statement fails, including SQL split across Java statements or concatenated from one-word literals, text blocks, any-case / quoted core tables and JPQL over a non-`Whin*` entity (one scanner fixture per case, plus prose); residual (report only): a read through a core *service* is not scanned, nor a column held in a lone one-word variable (`String c = "carrier_id"`) and concatenated in | FR-310 |
| IMD-DIV-04 | "The e-invoicing adapter itself is v2/P4" | `whin_transfer_irn_evidence` + `MANUAL_EVIDENCE` path built; provider e-invoice through `WhinComplianceGateway` (`WhinComplianceGatewayIrnTest`) — built, ahead of the stated wave — **Triage 2026-10-23: AMEND-SPEC** — rule: no divergence — `FR-311` is v2/`P4`, and `P4-01` built the e-invoicing path in that wave (`WhinComplianceGatewayIrnTest`) | FR-311 |
| IMD-DIV-05 | *(withdrawn R31 `F-CB-019` — `EXPIRED` is derived on purpose; now the rule `IMD-GRD-21`)* | — — **Triage 2026-10-23: AMEND-SPEC** — withdrawn R31; stands as the rule `IMD-GRD-21` | FR-309 |
| IMD-DIV-06 | The gate pass is blocked where an e-way bill is required and not generated | the core seam `WhHandoverGatePassGate` exists (`warehouse/…/service/whhandover/WhHandoverGatePassGate.java`), but no class in `warehouse-india` `src/main` implements it (grep), so every gate pass issues on the core's rules alone — **Triage 2026-10-23: FIX-CODE** — owner `P2-IN-04` #147 (`FR-195`), reopened — **Built R33 (2026-10-26):** `WhinEwayBillHandoverGatePassGate` (`IMD-GRD-20`), setting V541162 | FR-195 |
| IMD-DIV-07 | A challan and an e-way bill can close | `CLOSED` is defined (`WhinDeliveryChallan.java:62`, `WhinEwayBill.STATUS_CLOSED`) and no code sets it; `V540030:110` "wave 1 offers no screen action that reaches it" — reserved. Owner of a close transition: challan `p2in-03`, e-way bill `p2in-04` (acceptance items) — ~~Triage 2026-10-23: FIX-CODE~~ — **reserved by decision R33 (2026-10-26, DECISION RULE default)**: no close transition is built for either document (CGST Rule 55 and the NIC e-way operations define no close; return tracking lives on WS-181 / WS-188 via `closed_at`); disclosed on WS-178 and WS-179 (`IMD-T5-02`); `DC-OPEN-04` closed; `WhinComplianceCapability.CLOSE` stays in the port with no caller; trap `IMD-GRD-24` | FR-307, FR-309 |

## 7. Out of scope

Tax computation (`OD-9`, `FR-325`); accounting postings (`D-16` item 6); MFG production exits and the MOOWR return (`mfg-bonded-issue`); subcontract orders (`mfg-subcontracting`); mobile.

## 8. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 17 (`D-17` item a); aligned with `mfg-subcontracting` and `mfg-bonded-issue` by reference, neither edited |
| 2026-10-23 | R31: `F-CB-001` (`CLOSED` reserved, `IMD-DIV-07`), `F-CB-009` (manual e-way evidence `IMD-T1-08b`…`-08d`, `IMD-GRD-23`, `IMD-T4-05b`), `F-CB-010` (job-work seam `IMD-T1-08a`, `IMD-GRD-22`, `IMD-T4-05a`; `SUB-T4-03`), `F-CB-019` (`IMD-DIV-05` withdrawn → `IMD-GRD-21`), `F-CB-023` (`IMD-T1-04` codes); `IMD-OPEN-01`…`-03` decided |
| 2026-10-26 | R33 #140 / #147: `IMD-DIV-07` reserved by decision (disclosed on WS-178 / WS-179, `IMD-T5-02`); `IMD-GRD-24` trap note; `IMD-DIV-06` built — `IMD-GRD-20` names `WhinEwayBillHandoverGatePassGate` and `warehouse.india.eway_bill.handover_gate_mode` (V541162) |
| 2026-10-26 | R33 S3 #135: `IMD-GRD-06` — bare / wildcard columns on a core-table statement refused, case-insensitive SQL keywords, column-level two-way ratchet (F1, F3); `IMD-DIV-03` marked built (F2) |
| 2026-10-26 | R33 S3 re-verify #135 (round b): `IMD-GRD-06` / `IMD-DIV-03` — file-level scan of joined literals and text blocks, concatenated one-word literals kept, any-case / quoted / schema-qualified core tables, JPQL non-`Whin*` entity refused, prose fixture |

## 9. Invariants and scenarios

`L-1`, `L-11`; scenarios `WH-SC-124`, `WH-SC-144`, `WH-SC-206`, `WH-SC-207`, `WH-SC-208`, `WH-SC-209`, `WH-SC-212`, `WH-SC-213`, `WH-SC-214`, `WH-SC-215`, `WH-SC-247`, `WH-SC-040`, `WH-SC-035`.

## 10. Open rows

| ID | Question | Default | Source |
|---|---|---|---|
| IMD-OPEN-01 | UQC home (`IMD-DIV-01`): item column + movement-line copy as the FR says, or UoM master as built | **DECIDED R31 (2026-10-23):** default stands — the UQC lives on the UoM master and is frozen onto each statutory document line; `FR-319` restated | FR-319 |
| IMD-OPEN-02 | MRP back-calculation (`IMD-DIV-02`): withdraw that clause of `FR-321` under `OD-9`, or build it | **DECIDED R31 (2026-10-23):** default stands — the clause is withdrawn from `FR-321` (`OD-9`) | FR-321 |
| IMD-OPEN-03 | `FR-322` / `FR-323` statutory statement: the FR names a "monthly statutory statement" for bonded / MOOWR; `mfg-bonded-issue` `BND-T1-01` builds it for production stock — is a storage-only MOOWR site covered by the same return | **DECIDED R31 (2026-10-23):** default stands — one MOOWR monthly return per licensed premises covers all bonded stock, storage-only included (`BND-T1-01`) | FR-323 |
