# R25 — Competitor gap, round 3: what the benchmark and R15 both walked past

**Date:** 2026-09-10 · **Finding prefix:** `RK-` · **Lens:** round 4, R25, third competitor pass

**What this pass is, and is not.** [`COMPETITOR-BENCHMARK.md`](../COMPETITOR-BENCHMARK.md) scored 236
capabilities, mostly from category knowledge. [`R15`](R15-competitor-benchmark-r2.md) diffed it against the
2026 market and found eight things, all about AI, India statute and the benchmark's own stale text. Both
passes are done, and neither is repeated here: R15 §3 and the benchmark's §7 refusals are treated as settled.
This pass does two things they did not:

1. It scores **17 named products one by one, from their own 2026 documentation**, on a fixed list of 31
   capabilities. The benchmark scored six *segments* by their modal product. A segment mark hides exactly the
   kind of gap this pass is looking for: a capability that three Indian mid-market products ship and the
   modal global product does not.
2. It looks at **multi-branch operation** — how a dealership group with 3–8 branches actually moves and
   sells stock — which is our target segment (benchmark §1.1 row 1) and a place neither pass looked.

**File set.** The design set proper, excluding `docs/reviews/` for the reason R15 gives (review output, not
design, and sibling round-4 lenses write there concurrently):

```bash
cd warehouse-issues            # branch docs/round-4-cardinality-and-gaps
ls docs/*.md issues/*.md | wc -l      # → 173
cat docs/*.md issues/*.md | wc -l     # → 43123
```

Read in full: `DECISIONS.md` §2 (`D-12`), §3, §5 (the ladder and `A-1`…`A-4`), §6; `COMPETITOR-BENCHMARK.md`
all of it; `R15` all of it. Then ~70 targeted `FR-` rows, `DATA-MODEL.md` §2 table rows, `BUILD-SPEC-SCREENS.md`
`WS-090`/`WS-141`/`WS-194`/`WS-215`, `GAP-REGISTER.md` §4 and the owning task files. **Every absence below
was grepped against `docs/*.md` and `issues/*.md` before it was allowed to become a finding**, and the grep
is printed with it.

**How competitors were scored.** Each product was checked against its own help or product pages (2025–2026),
by four parallel research passes over the same 31-capability list. `Y` = ships natively · `P` = partial,
add-on, separately licensed, or tier-gated · `N` = confirmed absent · `?` = **not verified — not the same as
absent**. Each `Y`/`P` cell rests on a vendor URL; the ones a finding depends on are printed in that finding.
**A capability counts toward a gap only if at least three products score `Y` or `P` on it, with the Indian
mid-market seven weighted first** — Zoho Inventory, Tally Prime, Odoo, SAP Business One, Unicommerce,
EasyEcom and Vinculum. Honest limits: two passes hit a 200-search cap; Fishbowl's and Cin7's help sites
returned 401/403, so those cells rest on vendor page titles and snippets; Vinculum's detail pages did not
resolve (DNS); Manhattan and Blue Yonder publish no public functional help, so their cells are vendor claims.
Where a `?` would matter, the finding says so.

---

## §1 · Verdict

On the ground the benchmark scores, the design set is **thorough, and R15 was right to call it the best
document in the set.** Twenty-two of the 31 capabilities checked here are already correctly placed, ahead of the market, or filed in round 3 (§2.0's verdict column) —
consignment, landed cost, kits with derived availability, variants, the master-data audit trail, serial
warranty dates, per-owner visibility, the transfer price. On several the design is **ahead** of named
competitors: warranty start/end dates sit on the serial in v1 (`DATA-MODEL.md:575`), and none of the four
Indian e-commerce platforms could be shown to carry them. A kit's availability is
`MIN(component ÷ required)` (`FR-075`), where D365 and NetSuite kits show no available quantity at all.

**The gaps are in the one area neither pass looked at: how stock moves between the branches of one
customer.** The benchmark's §2.7 scores inter-site transfer as three legs through in-transit, and it is. But
a transfer in the design is something **the sending branch pushes**. The receiving branch — the one whose
counter has a customer waiting — has no way to *ask*. `wh_transfer_orders` carries `requires_approval`,
`approved_by` and `requested_date` (`DATA-MODEL.md:1003`), and **nothing uses them**: no Approve action, no
`:approve` permission, no status, no scenario (`RK-001`). Next to that, the counter sale records a `branch_id`
and a `warehouse_id` with **no rule relating the two** (`RK-002`), so the design never says whether a
satellite branch may sell from the hub's warehouse — the most common operating model for a small dealer
group — or what GSTIN the bill carries when it does.

Two further gaps are the design contradicting **its own rules**, which a competitor comparison exposes:

- `FR-156` ships a **v1** cycle-count programme scoped **by ABC class**, but `FR-070` computes the class only
  at **v3**. For two versions the class is whatever someone typed (`RK-003`).
- `FR-165` says *"a threshold column with no scheduled job that reads it is a defect at the moment it is
  merged"* — and the reorder point is exactly such a column. The replenishment run is manual (`run_by`), and
  the low-stock screen is a report nobody is told to open (`RK-004`). Zoho, Unicommerce and EasyEcom
  notify on it and Odoo schedules it; of the Indian seven only Tally leaves it to a report — and today so do we.

**The blunt answer.** The competitor capability absent from this set that would most often lose a
**dealership-group** deal is the **branch stock request**: *"Nashik has the part, Pune's counter needs it —
raise it, have Nashik approve it, ship it."* SAP Business One calls it an *Inventory Transfer Request*,
Zoho puts single- or multi-level approval on its transfer orders, NetSuite approves the transfer order, EasyEcom has an Unapproved → Approve stage, and Fishbowl and
Cin7 Omni carry an issue/approve step. It is not large. The schema is already paid for, and the design has
simply never finished it. It belongs in v1, because v1's exit criterion *is* a transfer to a second site.

Everything else found is v2, a decision that must be written down now, or documentation. Four
capabilities are recommended to be **declined in writing** (§4).

---

## §2 · The findings

### §2.0 · The capability matrix — 17 products × 31 capabilities, against the design set

Columns: **D365** Dynamics 365 SCM · **NS** NetSuite (+WMS) · **EWM** SAP EWM · **MAN** Manhattan Active WM ·
**BY** Blue Yonder · **FB** Fishbowl · **C7** Cin7 Core/Omni · **LGW** Logiwa IO · **SHH** ShipHero · **UNI**
Unicommerce · **EEC** EasyEcom · **VIN** Vinculum · **INC** Increff · **ZOHO** Zoho Inventory · **TALLY** Tally
Prime · **ODOO** Odoo 18 · **B1** SAP Business One. **IN-7** = the Indian mid-market seven the brief weights
first (UNI, EEC, VIN, ZOHO, TALLY, ODOO, B1). `Y`/`P`/`N`/`?` as defined above — **`?` is unverified, never
absent**. *Ours* is the design set's placement; *Verdict* is this lens's.

<div style="overflow-x:auto">

| # | Capability | D365 | NS | EWM | MAN | BY | FB | C7 | LGW | SHH | UNI | EEC | VIN | INC | ZOHO | TALLY | ODOO | B1 | Y+P of 17 | Y+P of IN-7 | Ours | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Per-user/branch warehouse visibility; selling unit ≠ fulfilling warehouse | P | P | Y | P | ? | ? | ? | P | Y | Y | Y | P | P | Y | P | P | ? | 13 | 6 | v1 `FR-404`/`FR-405`; **serving rule absent** | sound · `RK-002` |
| 2 | Inter-warehouse transfer at a transfer price / markup | P | Y | P | N | N | ? | P | ? | ? | P | P | ? | ? | ? | Y | ? | ? | 7 | 3 | v1 `transfer_price_basis` (`DATA-MODEL.md:1003`) | ahead |
| 3 | Transfer **request** / indent with approval | P | Y | P | ? | N | P | P | ? | N | ? | P | P | P | P | ? | P | Y | 11 | 5 | columns only — nothing uses them | **`RK-001`** |
| 4 | Channel stock sync with per-channel buffer | P | P | P | P | P | ? | Y | P | ? | Y | Y | P | Y | P | N | P | ? | 13 | 5 | v2 `FR-209` | sound |
| 5 | Drop-ship | Y | Y | P | P | P | ? | Y | Y | Y | ? | ? | Y | Y | Y | ? | Y | Y | 13 | 4 | **undecided** (`G-037`) | **`RK-005`** |
| 6 | Backorders | Y | Y | P | P | P | ? | Y | Y | Y | Y | Y | Y | ? | Y | P | ? | Y | 14 | 6 | v1 `FR-178` / v1.1 `FR-184` | sound |
| 7 | Landed cost | Y | Y | P | N | P | Y | Y | ? | ? | ? | ? | ? | ? | Y | Y | Y | Y | 10 | 4 | v1 / v1.1 / v2 (§2.13) | sound |
| 8 | Consignment (in and out) | Y | Y | Y | ? | ? | Y | ? | ? | ? | ? | ? | ? | ? | ? | Y | Y | ? | 6 | 2 | v1 `FR-113` | ahead |
| 9 | Kits / bundles, availability from components | P | P | Y | P | P | P | P | P | Y | Y | Y | Y | Y | Y | P | Y | P | 17 | 7 | v1.1 `FR-075` | ahead of D365/NS |
| 10 | Variants / attributes | Y | Y | ? | ? | ? | ? | Y | ? | ? | P | ? | Y | ? | Y | ? | Y | ? | 7 | 4 | v1 schema / v2 screens (`A-3`) | sound |
| 11 | Price lists | Y | Y | ? | N | N | ? | Y | ? | ? | P | Y | ? | ? | P | Y | Y | Y | 9 | 6 | `RA-002` / `E-078` | filed (R16) |
| 12 | Reorder point → suggestion / PO | Y | Y | P | P | P | Y | P | ? | P | P | P | P | P | Y | P | Y | Y | 16 | 7 | v1 manual run `FR-253` | sound |
| 13 | Low-stock / expiry **alerts** | P | P | ? | ? | P | P | ? | ? | ? | Y | P | P | P | P | ? | P | ? | 10 | 5 | expiry v1 `FR-160`; **reorder: none** | **`RK-004`** |
| 14 | Mobile barcode scanning | Y | P | Y | P | P | ? | Y | Y | Y | Y | Y | Y | Y | Y | ? | P | ? | 14 | 5 | v1.1 (§2.12) | sound |
| 15 | Label / barcode printing | Y | Y | Y | Y | Y | ? | Y | Y | Y | Y | Y | Y | Y | Y | ? | P | ? | 14 | 5 | v1 `FR-225` | sound |
| 16 | Slotting / directed putaway | Y | P | Y | Y | Y | ? | ? | P | Y | P | P | P | P | P | N | P | P | 14 | 6 | refusal #7; v1.1 putaway | sound |
| 17 | Labour management | Y | ? | Y | Y | Y | ? | ? | Y | Y | P | ? | ? | P | N | N | ? | ? | 8 | 1 | v2 actuals; refusal #3 | sound |
| 18 | Dock appointment / gate / yard | P | ? | Y | P | Y | ? | ? | ? | ? | P | P | ? | P | N | N | ? | ? | 7 | 2 | v1.1 dock; refusal #23 | sound |
| 19 | Returns with inspection / grading | Y | P | Y | Y | Y | P | P | P | Y | Y | Y | Y | Y | P | P | P | P | 17 | 7 | v1 basic (`A-1`) / v2 grading | sound |
| 20 | B2B trade-customer portal | P | P | ? | ? | P | ? | Y | P | N | ? | P | P | ? | P | N | Y | ? | 9 | 4 | **none** | **`RK-006`** |
| 21 | Vendor / supplier portal | Y | P | ? | ? | P | ? | ? | ? | ? | ? | ? | Y | P | P | N | ? | ? | 6 | 2 | none | decline (§4.2 a) |
| 22 | Public API + outbound webhooks | Y | P | P | Y | Y | P | Y | Y | Y | P | Y | P | P | Y | P | Y | ? | 16 | 6 | v1 REST · v1.1 HTTP · v2 keys | sound |
| 23 | Ageing / dead stock / ABC | Y | P | P | P | ? | Y | ? | ? | ? | P | P | ? | Y | Y | Y | Y | ? | 11 | 5 | v1 `FR-162`; **ABC computed v3** | sound · `RK-003` |
| 24 | Master-data field-level audit trail | Y | Y | ? | ? | ? | ? | Y | ? | P | P | P | ? | P | P | Y | ? | ? | 9 | 4 | v1 `FR-427` | sound |
| 25 | Configurable / multi-level approvals | Y | Y | P | ? | ? | P | P | ? | ? | P | P | ? | ? | Y | ? | P | ? | 9 | 4 | single-step v1 `FR-408` | **`RK-008`** |
| 26 | AI / ML demand forecasting | Y | ? | P | P | P | P | P | P | ? | ? | P | ? | Y | ? | ? | P | P | 11 | 3 | refusal #8; `J-003` | sound |
| 27 | Serial tracking / warranty | P | P | ? | N | P | P | P | ? | P | Y | Y | Y | Y | ? | ? | ? | Y | 11 | 4 | v1 warranty dates on `whb_serials` | ahead |
| 28 | GRNI / pending-bill report | ? | P | P | N | N | ? | ? | ? | ? | ? | ? | ? | ? | P | Y | P | ? | 5 | 3 | `FR-242` column; accounting report | sound |
| 29 | Native PO and SO | Y | Y | P | N | N | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y | 15 | 7 | v1 | sound |
| 30 | Inter-company transfer | Y | Y | P | N | N | ? | P | ? | ? | ? | ? | Y | ? | ? | ? | Y | ? | 6 | 2 | **none** | **`RK-007`** |
| 31 | Custom fields | Y | Y | P | Y | P | Y | Y | ? | ? | P | Y | ? | Y | Y | P | P | ? | 13 | 5 | refusal #12; v3 typed `FR-076` | sound |

</div>

```bash
F=docs/reviews/R25-competitor-gap-r3.md
grep -cE '^\| [0-9]+ \|' $F                                   # → 31 capability rows
grep -E '^\| [0-9]+ \|' $F | grep -c '| \*\*`RK-0'          # → 6  rows that are wholly a finding
grep -E '^\| [0-9]+ \|' $F | grep -c 'sound · `RK-0'         # → 2  rows half-covered (visibility→RK-002, ageing→RK-003)
grep -E '^\| [0-9]+ \|' $F | grep -c 'decline'               # → 1
grep -E '^\| [0-9]+ \|' $F | grep -cE '\| (sound|ahead[^|]*|filed \(R16\)) \|$'   # → 22 placed, ahead, or already filed
```

**Reading the matrix.** The rows that became findings all clear the threshold with room to spare, and the
Indian seven carry them: request/indent **5 of 7**, drop-ship **4**, alerts **5**, B2B portal **4**,
approvals **4**. The two rows where the design is simply *ahead* of the Indian e-commerce set — consignment
and serial warranty — are the ones no Indian e-commerce page could evidence at all.

---

### `RK-001` · A transfer can only be pushed by the sender; the request-and-approve half is paid for in the schema and never built — **MAJOR**

- **What is missing or wrong:** `wh_transfer_orders` carries `requested_date`, `requires_approval` and
  `approved_by` (`DATA-MODEL.md:1003`). Nothing reads or writes them:
  - `WS-090`'s actions are *Add · Pick · Dispatch · Receive · Report variance · Cancel · Generate delivery
    challan · Print* (`BUILD-SPEC-SCREENS.md:1620-1623`). There is no **Approve** and no **Request**.
  - The permission table lists only `wh_transfer_orders:dispatch` · `:receive` (`BUILD-SPEC-SCREENS.md:2228`).
  - Neither owning task mentions approval or a request: `issues/p1-17.md` (schema) and `issues/p2-02.md`
    (workflow) both return **0** for `approv|request`.
  - Every transfer scenario starts with the **source** raising the document — `WH-SC-058`: *"`mgr1` raises
    transfer `TR-2026-00042`"* (`SCENARIO-CATALOGUE.md:229`).

  The pull side of the flow is missing: the branch that needs the stock raises a request, the holding branch
  approves, part-approves or rejects it, and only then does the transfer become pickable.
- **Who ships it:** NetSuite — transfer-order approval
  ([docs.oracle.com](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N2311649.html)) ·
  EasyEcom — Unapproved → Approve stage on warehouse transfers
  ([support.easyecom.io](https://support.easyecom.io/portal/en/kb/articles/transferring-stock-from-one-warehouse-to-another-warehouse)) ·
  Cin7 Omni — branch transfer approved before costs are added
  ([help.omni.cin7.com](https://help.omni.cin7.com/hc/en-us/articles/9128531866511-Create-a-branch-transfer)) ·
  Fishbowl — an issue step before fulfilment
  ([fishbowlinventory.com](https://www.fishbowlinventory.com/blog/touring-the-transfer-order-module)) ·
  D365 — journal approval workflow, not on the transfer order
  ([learn.microsoft.com](https://learn.microsoft.com/en-us/dynamics365/supply-chain/inventory/inventory-journal-workflow)) ·
  Zoho Inventory — transfer orders with single- or multi-level approval, but no separate request document ([zoho.com](https://www.zoho.com/us/inventory/help/warehouses/transfer-orders.html)) · **SAP Business One — the *Inventory Transfer Request*, a request distinct from the transfer** ([learning.sap.com](https://learning.sap.com/courses/managing-logistics-in-sap-business-one/managing-warehouses-in-sap-business-one)) · Odoo — resupply-from-another-warehouse routes that raise the inter-warehouse move ([odoo.com](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/resupply_warehouses.html)). **IN-7: 5 of 7**
- **Why it matters:** a customer at the Pune counter wants a brake master cylinder. `FR-073` shows
  *"2 available at Nashik"* — the design is proud of that line, and rightly. And then there is nothing to
  press. The Pune clerk cannot create a transfer *out of* Nashik's warehouse, because `FR-405` scopes
  warehouse access by branch. So the clerk phones Nashik, and Nashik keys a transfer from memory. The request
  that caused it is recorded nowhere, and neither is the time it waited. The lost sale `FR-257` would have
  captured never happens, because the counter did not refuse — it just never sold. The ledger stays correct.
  What is lost is the demand signal a parts manager is judged on, because it lived in a phone call. For a
  multi-branch dealer group this is the single most frequent inter-branch transaction, and we ship its second
  half only.
- **Negative evidence:**
  ```bash
  grep -rciE "wh_transfer_orders:approve" docs/ issues/ | awk -F: '{s+=$2} END{print s}'   # → 0
  grep -ciE "approv|request" issues/p2-02.md issues/p1-17.md                               # → 0 and 0
  grep -n "requires_approval" docs/DATA-MODEL.md | grep transfer                            # → 1003 only — the column, nothing that reads it
  ```
- **Proposal (minimum, no new table):** extend the transfer status vocabulary with `REQUESTED` →
  `APPROVED` / `REJECTED` / `PARTIALLY_APPROVED` ahead of `DRAFT`→pick. A transfer may be **created by a user
  scoped to the destination warehouse** in `REQUESTED` state. Only a holder of `wh_transfer_orders:approve`
  scoped to the **source** warehouse moves it on, and `FR-408` (approver ≠ requester) already applies.
  Approval **reserves** the approved quantity at the source through the ordinary `L-10` reservation, with
  `expires_at`. A rejection or a part-approval carries a reason code, and the unapproved remainder writes
  `wh_insufficient_stock_log` with `source_type = TRANSFER_REQUEST`, so the refused demand is still demand.
  `requires_approval` stays as the per-transfer switch. Mobile: request creation on
  `screens/whTransferOrder` (`BUILD-SPEC-SCREENS.md:1626` already says *"creation is available"*). One new
  scenario in the `WH-SC-058` shape, raised at the destination.
- **Version:** **V1** — table-stakes. The v1 exit criterion *is* "transfers stock to a second site", and the
  columns are already v1. **Phase:** P2.
- **Owning task:** **`P2-02`** (workflow, permission, scenario), with a one-line status-vocabulary note in
  **`P1-17`** (schema already present). The `FR-254` sister-branch suggestion (`P5-18`, v2) later *creates*
  these requests instead of creating transfers — it becomes a producer of the same object, not a second one.
- **Irreversibility:** `reversible` — the columns exist. The status value `REQUESTED` should go into the first
  status migration rather than being added to a live vocabulary.
- **Relationship to earlier rounds:** **new.** R3 `E-041` and `FR-254` cover the *system* proposing a
  sister-branch transfer (v2). No finding covers a *person* at the receiving branch requesting one.

---

### `RK-002` · The design never says whether a branch may sell or issue from another branch's warehouse — and the counter sale records both without relating them — **MAJOR**

- **What is missing or wrong:** `FR-079` makes a warehouse belong to **exactly one** branch
  (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:219`), correctly, because GSTIN is per branch. But the documents
  that *consume* stock carry the branch and the warehouse independently:
  - `whad_counter_sales` carries `branch_id` **and** `warehouse_id` (`DATA-MODEL.md:1272`), and `WS-194`
    cascades `branchId → warehouseId` in its filter (`BUILD-SPEC-SCREENS.md:1910`). No rule says the warehouse
    must be one of the selling branch's own, or says it need not be.
  - `whas_material_requests` names a `warehouse_id` against a `job_card_id` whose branch lives in `services`
    (`DATA-MODEL.md:1290`). Again, no rule.

  So the set is silent on the **hub-and-spoke** model: one parts warehouse at the main branch, serving the
  counters and workshops of two or three satellite branches that hold little or no stock. It is also silent
  on the tax consequence when the two branches sit under different GSTINs. A supply is made from the
  registration where the goods are, so the counter bill's GSTIN must be the **warehouse's** branch, not the
  **selling** branch.
- **Who ships it:** SAP EWM — one warehouse number serving several plants/storage locations
  ([learning.sap.com](https://learning.sap.com/courses/basic-customizing-in-sap-s-4hana-ewm/defining-the-warehouse)) ·
  NetSuite — a location belongs to one subsidiary, shareable down the hierarchy with *Include Children*
  ([docs.oracle.com](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N263263.html)) ·
  Unicommerce — facility-scoped users
  ([support.unicommerce.com](https://support.unicommerce.com/index.php/knowledge-base/restricted-sale-order-item-visiblity-to-the-facility-user-only/)) ·
  ShipHero — per-user warehouse visibility
  ([software-help.shiphero.com](https://software-help.shiphero.com/hc/en-us/articles/4419353987853-Managing-a-User-s-Warehouse-Visibility)) ·
  Zoho Inventory — per-warehouse user access ([zoho.com](https://www.zoho.com/de-de/inventory/kb/warehouses/manage-specific-warehouse.html)) · Tally Prime — godowns and locations under one company ([help.tallysolutions.com](https://help.tallysolutions.com/inventory-storage-using-godowns-locations-tally/)) · Odoo — warehouses per company in a multi-company install ([odoo.com](https://www.odoo.com/documentation/18.0/applications/general/companies/multi_company.html))
  *(Per-user warehouse restriction is already `FR-405` and is not the gap. The gap is the
  **selling-unit ↔ fulfilling-warehouse** relation.)*
- **Why it matters:** the design has two failure modes here and does not choose between them.
  - **Permissive.** A clerk at Nashik (GSTIN 27…, Maharashtra) sells from the Indore warehouse (GSTIN 23…,
    Madhya Pradesh) because `FR-073` showed stock there. The bill carries Nashik's registration and CGST+SGST
    on goods that left Madhya Pradesh — an inter-state supply billed as intra-state, from the wrong GSTIN.
    `A-4` is built to prevent exactly that class of wrong document.
  - **Restrictive by accident.** A satellite branch with no warehouse of its own cannot select one at all,
    because the cascade offers only its own. The group is then forced to create a paper warehouse per
    satellite, and transfer every part it sells into it first.

  A dealership group will hit one of the two in its first week, and the design lets two engineers build it
  two different ways.
- **Negative evidence:**
  ```bash
  grep -niE "serves (several|multiple) branch|shared warehouse|serving warehouse|hub.and.spoke|another branch's warehouse" docs/*.md issues/*.md   # → no output
  grep -niE "branch_id" docs/DATA-MODEL.md | grep -iE "counter_sales|material_requests"   # → 1272 (branch_id, warehouse_id side by side); material requests: none
  ```
- **Proposal (a rule, not a table):** add to `FR-079`: *"A stock-consuming document (counter sale, job issue,
  demand order) names a **selling branch** and a **fulfilling warehouse**. They may differ **only if both
  resolve to the same GSTIN**; the tax registration on the document is always the fulfilling warehouse's
  branch. Across GSTINs the path is a transfer (`RK-001`), never a direct sale. The user must hold
  `FR-405` access to the fulfilling warehouse."* One service guard, one `WH-SC-` scenario for each of the two
  cases, and the `WS-194` warehouse picker lists every warehouse sharing the selling branch's GSTIN, not only
  the branch's own. **Do not** build a branch↔warehouse service-map table unless a customer asks for a
  restriction narrower than the GSTIN. The GSTIN rule answers the statutory question, and `FR-405` answers the
  access question.
- **Version:** **V1** — the counter sale is v1 (`FR-359`), and so is the wrong bill. **Phase:** P1 (the rule
  in `FR-079`) · P2 (the guard at the counter and the job issue).
- **Owning task:** **`P1-05`** (owns `FR-079` / `whb_warehouses`) for the rule; **`P2-25`** (counter sale)
  and **`P2-26`** (material request) for the guard. `P2IN-01` reads the fulfilling warehouse's GSTIN.
- **Irreversibility:** **partly irreversible.** A counter sale posted under the wrong GSTIN is a filed
  document, and the ledger cannot later say which registration each historic sale should have used unless
  both branch and warehouse are recorded. They are — so capture is safe, and only the *rule* is missing.
- **Relationship to earlier rounds:** **new.** `C-016`/`C-030` (R1) and `E-048` (R3) established one GSTIN
  per warehouse. None asks what a *document* does when its branch and its warehouse differ.

---

### `RK-003` · v1 ships a cycle-count programme scoped by ABC class, and nothing computes the class until v3 — **MINOR**

- **What is missing or wrong:** `FR-156` (**v1**, `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:326`) makes cycle
  counting a policy object whose programme type includes `ABC` and whose scope may be *"by … ABC class"*.
  `WS-093` offers `programType = ABC` in v1 (`BUILD-SPEC-SCREENS.md:1635`). But `FR-070` puts only the
  **column** in v1 and the **recompute job in v3** (`:205`), owned by `P6-02` (`issues/p1-03.md:40-41`). For
  v1 and v1.1, every item's ABC class is whatever the import or a user typed. `FR-070`'s own sentence reads
  *"a classification stored and never consumed is a defect the prior product shipped"*. This is the mirror
  image: a classification consumed and never computed.
- **Who ships it:** SAP EWM — ABC analysis inside EWM
  ([help.sap.com](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/9832125c23154a179bfa1784cdc9577a/8185e8e4c4e349aab86f070b808e3fd9.html)) ·
  Increff — ageing and classification in the WMS
  ([increff.com](https://www.increff.com/solution/warehouse-management-system)) ·
  Fishbowl — inventory reports
  ([help.fishbowlinventory.com](https://help.fishbowlinventory.com/advanced/s/article/Reports)) ·
  Tally Prime — stock ageing analysis ([help.tallysolutions.com](https://help.tallysolutions.com/tally-prime/inventory-reports/stock-ageing-analysis-report-tally/)) · Odoo — ageing report ([odoo.com](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/warehouses_storage/reporting/aging.html)) · Zoho — inventory valuation reports ([zoho.com](https://www.zoho.com/us/inventory/help/reports/inventory-valuation-reports.html)). **Honest limit:** those three verify *ageing*, not ABC; only SAP EWM's ABC analysis was isolated. The competitor count for ABC *computation* is below this lens's threshold of three, so this finding stands on the design contradicting itself — which is why it is MINOR
  *(D365's ABC page could not be confirmed on Learn, so D365 is scored `?` on ABC, and the benchmark's §2.8
  row "cycle count driven by ABC" is not challenged — it is the **computation** that is missing.)*
- **Why it matters:** ABC cycle counting exists so that the 20% of parts carrying 80% of issue value get
  counted monthly and the tail yearly. With typed classes, what actually happens is simple. The opening-stock
  import (`S-079`) leaves the class blank or copies it from Tally, where it was set years ago. The programme
  then counts the wrong parts at the wrong frequency, and it looks correct on screen. The stock controller is
  the persona R16 called *"the best-designed persona in the set"*
  (`R16-role-and-persona-completeness.md:620`), and that design rests on a column v1 cannot fill. The inputs
  are already v1: `wh_demand_history` is maintained by movement posting (`FR-256`), and position value is
  v1. What is missing is one scheduled job.
- **Negative evidence:**
  ```bash
  grep -nE "^\| \*\*FR-070\*\*" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | grep -o "v1·v3"   # → v1·v3
  grep -nE "^\| \*\*FR-156\*\*" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | grep -oE "\| v1 \|"  # → | v1 |
  grep -n "recompute" issues/p1-03.md                                                            # → 41: "the recompute." (P6-02)
  ```
- **Proposal:** split `FR-070`. A **simple ABC recompute** ships at **v1.1**: a scheduled job over
  `wh_demand_history` (12-month issue value per item × site), Pareto cut-offs as three configurable
  percentages on the site, a `whb_job_runs` record per `FR-165`, and the previous class kept on the row for
  one cycle so a count programme can see the movers. The **velocity/affinity/XYZ** work stays in `P6-02` at v3.
  Until v1.1, `WS-093` must label `programType = ABC` *"uses manually maintained classes"*, rather than imply
  a computation that does not exist.
- **Version:** **V1.1 (PHASE-2)** — not table-stakes on day one. A v1 customer counting by zone or at random
  is fine. But a v1 screen must not claim the computation. **Phase:** P3.
- **Owning task:** **NEW** — the next free P3 id by the file glob (`P3-25` at the time of writing), or folded
  into `P2-04` if the product owner prefers it in v1. Remove the recompute from `P6-02`'s scope, and leave it a
  note.
- **Irreversibility:** `reversible`.
- **Relationship to earlier rounds:** **new.** `T-027`, `E-066`, `P-051` and `P-058` placed the columns and
  the v3 job; none cross-read `FR-156`'s v1 programme type.

---

### `RK-004` · A reorder point is a threshold column with no job that reads it — the design's own `FR-165` calls that a defect — **MAJOR**

- **What is missing or wrong:** `FR-165` (**v1**, `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:335`): *"A threshold
  column with no scheduled job that reads it is a defect at the moment it is merged. Every dated obligation …
  ships with its job, its notification recipients and its report."* The list that follows is all **dated**
  obligations — expiry, reservation expiry, e-way validity. It omits the **quantity** thresholds:
  reorder point, min and safety stock on item × site (`FR-252`, v1). These are read only by:
  - the replenishment run, which is **manual** — `wh_replenishment_runs` has `run_by` and no schedule
    (`DATA-MODEL.md:1093`), and `issues/p2-15.md` returns **0** for `schedul|notif|cron`;
  - the `WS-215` *Low & Insufficient Stock* **report** (`BUILD-SPEC-SCREENS.md:1989`).

  Nobody is told that a part crossed its reorder point.
- **Who ships it:** Unicommerce — reorder list with notification
  ([support.unicommerce.com](https://support.unicommerce.com/index.php/knowledge-base/reorders/)) ·
  EasyEcom — inventory-threshold notifications
  ([support.easyecom.io](https://support.easyecom.io/portal/en/kb/articles/inventory-threshold)) ·
  Fishbowl — reorder-driven purchasing
  ([fishbowlinventory.com](https://www.fishbowlinventory.com/purchasing)) ·
  Cin7 Omni — Smart Reorder
  ([help.omni.cin7.com](https://help.omni.cin7.com/hc/en-us/articles/11937683806223-Smart-Reorder)) ·
  NetSuite — saved-search alerts
  ([docs.oracle.com](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N681962.html)) ·
  D365 — generic alert rules
  ([learn.microsoft.com](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/fin-ops/get-started/create-alerts)) ·
  Zoho Inventory — item reorder notification ([zoho.com](https://www.zoho.com/us/inventory/kb/items/item-reorder-notification.html)) · Odoo — reordering rules run by the scheduler ([odoo.com](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/reordering_rules.html)) · SAP Business One — MRP ([learning.sap.com](https://learning.sap.com/courses/managing-logistics-in-sap-business-one/exploring-the-materials-requirements-planning-mrp-process)) · Tally Prime — a Reorder Status **report** only, no alert ([help.tallysolutions.com](https://help.tallysolutions.com/reorder-stock-items-reorder-status-and-reorder-quantity/)). **Today we match Tally — the one product in the sample that leaves it to a report**
- **Why it matters:** the design put reorder points on item × site so that *"a ten-branch dealer does not
  want the same reorder point at the flagship and the satellite"* (`FR-252`). That is ten sets of numbers
  someone must *act on*. In practice a parts manager runs the suggestion screen when they remember to. On the
  week they do not, the fast movers go to zero, the counter refuses, and the lost-sale log fills. It records
  the damage faithfully, after the fact. Of the Indian seven, only Tally leaves the threshold to a report. We ship the
  most careful threshold model in the sample and then wait for someone to look at it.
- **Negative evidence:**
  ```bash
  grep -niE "low[- ]stock.{0,80}(notif|alert|email)|(notif|alert).{0,60}(reorder point|below min)" docs/*.md issues/*.md   # → no output
  grep -ciE "schedul|notif|cron" issues/p2-15.md                                                                          # → 0
  ```
- **Proposal:** two lines, in `FR-253` and `FR-165`. (a) `wh_replenishment_runs.run_type` gains
  `SCHEDULED`, and a per-warehouse schedule (nightly by default) runs it through the ordinary job framework,
  with its `whb_job_runs` record. (b) A run that produces suggestions notifies the site's buyer role through
  the platform's existing notification providers — an in-app notification and email — with the count and
  value and a link to `WS-141`. **No new table, no auto-PO.** `FR-253`'s *"the warehouse never becomes a
  purchase-order engine"* stands: the human still accepts. Add *"quantity thresholds — reorder point, min,
  safety stock"* to `FR-165`'s enumerated list, so the rule reads as it is applied.
- **Version:** **V1** — cheap, and it is the design's own rule. **Phase:** P2.
- **Owning task:** **`P2-15`** (owns `FR-253`).
- **Irreversibility:** `reversible`.
- **Relationship to earlier rounds:** **new.** `FR-165` came from `P-051`/`E-018`/`E-043` about dated
  clocks; no finding applied it to quantity thresholds.

---

### `RK-005` · Drop-ship: round 1 said "decide in v1, implement in v2", and the decision was never taken — **MINOR**

- **What is missing or wrong:** `GAP-REGISTER.md:1034` records `G-037` as *"An `OD-` row, not a task"*,
  quoting R7: *"decide in v1's FRD; implement in v2, because choosing it in v3 means history is missing or
  double-counted"*. `DECISIONS.md` §3 runs `OD-1`…`OD-17` and none is drop-ship. The phrase appears in **one**
  design file — the register row that says it is owed. It was carried through three rounds as a known
  undischarged item. It is re-raised here because the competitor count makes the decision urgent rather than
  academic.
- **Who ships it:** D365 — direct deliveries
  ([learn.microsoft.com](https://learn.microsoft.com/en-us/dynamics365/supply-chain/sales-marketing/direct-deliveries)) ·
  NetSuite
  ([docs.oracle.com](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N2239232.html)) ·
  Cin7 Core ([help.core.cin7.com](https://help.core.cin7.com/hc/en-us/articles/9034481322639-Dropshipping)) ·
  ShipHero ([software-help.shiphero.com](https://software-help.shiphero.com/hc/en-us/articles/4419345418253-How-to-Drop-Ship-Orders)) ·
  Vinculum ([vinculumgroup.com](https://www.vinculumgroup.com/use-cases/inventory-order-management/brands/)) ·
  Increff — vendor-fulfilled inventory
  ([increff.com](https://www.increff.com/solution/vendor-inventory-management-fulfillment-system)) ·
  Zoho Inventory ([zoho.com](https://www.zoho.com/us/inventory/help/drop-shipments/drop-shipments.html)) · Odoo ([odoo.com](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/shipping_receiving/daily_operations/dropshipping.html)) · SAP Business One ([help.sap.com](https://help.sap.com/docs/SAP_BUSINESS_ONE/87e1767ca7584b8f8d60775347637b07/2b7f2b9e536448f68bc6528cdef385e2.html)). **IN-7: 4 of 7**
  *(Unicommerce and EasyEcom "dropship" integrations are the seller shipping marketplace orders — not
  supplier-to-customer — and are scored `?`.)*
- **Why it matters:** in dealer parts this is the OEM shipping a heavy or VOR part **straight to the
  workshop or the fleet customer**. The dealer never touches the goods, but still bills the customer, owns
  the warranty and may take the return. If the choice is "no movements", then `L-12` traceability for a
  serialised part ends at the supplier. The part the customer later returns (`A-1`, v1) arrives from a
  customer it was never shipped to. If the choice is "a SUPPLIER→CUSTOMER movement pair", every
  drop-shipped serial is traceable, and the return has an origin.
- **Negative evidence:**
  ```bash
  grep -rliE "drop.?ship" docs/*.md issues/*.md                          # → docs/GAP-REGISTER.md only
  grep -nE "^\| \*\*OD-[0-9]+\*\*" docs/DECISIONS.md | grep -ci "drop"   # → 0
  ```
- **Proposal — the decision text, for `DECISIONS.md` §3 to number:** *"A drop-shipment posts **one movement,
  two lines**: `−q` at the `SUPPLIER` virtual location and `+q` at the `CUSTOMER` virtual location, with the
  drop-ship movement type, the purchase and the demand document both in the source quad, `owner_id` = house
  from the moment of supplier dispatch, and `occurred_at` = the supplier's dispatch date. It never touches a
  physical location, is never counted, and is never valued at a site. Serial and lot capture is mandatory
  where the item is tracked."* This needs **no new column**: both virtual locations are seeded (`FR-084`),
  and the movement type is a catalogue row (`D-10`).
- **Version:** **decision V1** (it shapes history). **Feature V2** — the drop-ship order flow in P5.
- **Owning task:** an `OD-` row in `DECISIONS.md` §3 (that file allocates; **not numbered here**); the
  feature lands with **`P5-09`** (channel/order intake). The movement-type seed row joins `P1-05`'s
  `V500013` if the decision is taken before that migration.
- **Irreversibility:** **the decision is irreversible once v1 posts a purchase for a drop-shipped part** —
  exactly R7's point.
- **Relationship to earlier rounds:** **re-raises `G-037`** (R7), undischarged across rounds 1–3. New here:
  the competitor count, the dealer-parts case, and the decision text.

---

### `RK-006` · No B2B trade-customer portal — the independent garage ordering parts from the dealer — **MINOR**

- **What is missing or wrong:** the only portal in the set is the **3PL client** portal (`FR-284`, v2), whose
  user is an *owner of goods* scoped by `FR-300`. Refusal #19 (FRD §10) declines the **consumer** returns
  portal. Nothing covers the **trade buyer**: the garage, fleet operator or sub-dealer who buys parts from the
  dealer's wholesale counter, and wants to see availability, place an order and download the challan without
  phoning.
- **Who ships it:** Cin7 Core — B2B portal
  ([help.core.cin7.com](https://help.core.cin7.com/hc/en-us/articles/9034604614543-Using-the-B2B-Portal)) ·
  EasyEcom — branded B2B customer portals
  ([easyecom.io](https://easyecom.io/whatsnew-articles/new-feature-branded-b2b-customer-sales-team-portals)) ·
  Vinculum ([vinculumgroup.com](https://www.vinculumgroup.com/products/vin-eretail/)) ·
  D365 Commerce B2B
  ([learn.microsoft.com](https://learn.microsoft.com/en-us/dynamics365/commerce/b2b/set-up-b2b-site)) ·
  NetSuite customer centre / SuiteCommerce
  ([docs.oracle.com](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_1105105840.html)) ·
  Zoho Inventory — client portal ([zoho.com](https://www.zoho.com/us/inventory/help/client-portal/)) · Odoo — customer portal ([odoo.com](https://www.odoo.com/documentation/18.0/applications/general/users/portal.html)). **IN-7: 4 of 7**
- **Why it matters:** Indian OEMs push dealers to supply the independent aftermarket, so a dealer's parts
  counter is increasingly a wholesale business. That business runs on WhatsApp messages and phone calls.
  This is not v1 — the v1 buyer is the dealer's own counter and workshop. But it is the first thing a
  wholesaling parts manager asks for once v1 works, and `FR-284`'s design (*"a permission surface over the
  existing screens, not a second application"*) is exactly the right shape to reuse.
- **Negative evidence:**
  ```bash
  grep -rliE "customer portal|B2B portal|trade portal|dealer portal" docs/*.md issues/*.md | wc -l   # → 0
  grep -ciE "customer|B2B|buyer" issues/p5-08.md                                                   # → 0
  ```
- **Proposal:** a **second persona on `FR-284`'s surface**. The scope key is `customer_counterparty_id`
  instead of `owner_id`, and the resolver is the same single server-side one (`FR-406`). Its screens are an
  availability **flag** (in stock / on order / not stocked — never a quantity, never another customer's),
  demand-order creation as `demand_type = SALES` in `DRAFT` for the counter to confirm, order and shipment
  status, and document download. No pricing engine: prices come from the price-level home that `RA-002` and
  `E-078` resolve. No payment: refusal #18 stands.
- **Version:** **V2 (PHASE-2).** **Phase:** P5.
- **Owning task:** **`P5-08`** (client portal), widened by one persona. Or NEW if the product owner wants the
  3PL portal to ship alone.
- **Irreversibility:** `reversible`.
- **Relationship to earlier rounds:** **new.** `F-008` is the 3PL client portal. `E-079` covers channels, not
  trade buyers.

---

### `RK-007` · A transfer between two legal entities in one install is neither supported nor refused — **MINOR**

- **What is missing or wrong:** `whb_companies` is *"≥1 seeded on install"* (`DATA-MODEL.md:450`), so a
  multi-company install is intended. `FR-001` balances every movement **per company**, and
  `wh_transfer_orders` carries **one** `company_id` (`DATA-MODEL.md:1003`). A cross-company transfer therefore
  cannot post, which is correct: between two legal entities it is a sale and a purchase, not a transfer. But
  no document says so. The user finds out when a movement is rejected with an `L-1` conservation error.
- **Who ships it:** D365 — intercompany trade
  ([learn.microsoft.com](https://learn.microsoft.com/en-us/dynamics365/supply-chain/sales-marketing/intercompany-trade-set-up)) ·
  NetSuite OneWorld intercompany transfer orders
  ([docs.oracle.com](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3675550.html)) ·
  S/4 intercompany STO behind EWM
  ([learning.sap.com](https://learning.sap.com/courses/configuring-cross-application-processes-in-sap-s-4hana-sales-and-procurement/processing-advanced-intercompany-stock-transfers-in-sap-s-4hana)) ·
  Vinculum ([vinculumgroup.com](https://www.vinculumgroup.com/products/vin-eretail/)) · Cin7 Omni
  ([cin7.com](https://www.cin7.com/solutions/omni/)) · Odoo — multi-company inter-company flows ([odoo.com](https://www.odoo.com/documentation/18.0/applications/general/companies/multi_company.html)). *(Tally records a cross-**GSTIN** transfer as a GST sale and purchase, which is `FR-305`'s case, not this one)*
- **Why it matters:** Indian dealer groups routinely run one private limited company per brand or per
  territory under one family, and move parts between them. In v1 that move must be a counter sale in company
  A plus a receipt in company B, keyed twice. That is acceptable, if it is said. What is not acceptable is a
  transfer screen whose company filter (`WS-090` `companyId → sourceWarehouseId → destinationWarehouseId`)
  offers both companies' warehouses and then fails at post.
- **Negative evidence:**
  ```bash
  grep -rliE "inter-?company|cross-company" docs/*.md issues/*.md | wc -l   # → 0
  ```
- **Proposal:** **V1 — one sentence and one guard** in `P1-17`: *"A transfer order's source and destination
  warehouses belong to the same company; a cross-company movement of goods is a sale from one and a purchase
  into the other, never a transfer."* The `WS-090` destination picker is filtered to the source's company.
  **V2 — a linked pair**: a demand order in company A and a purchase order in company B, created in one
  action and cross-referenced in the source quad, with the transfer price (`FR-244`'s columns) as the sale
  price. No new ledger concept.
- **Version:** **statement V1 · feature V2.** **Phase:** P1 · P5.
- **Owning task:** **`P1-17`** (statement and guard); **NEW** in P5 for the linked pair — the next free P5 id
  by the glob.
- **Irreversibility:** `reversible` — `company_id` is on every line already (`IRR-17`).
- **Relationship to earlier rounds:** **new.** `F-025` and `FR-305` cover cross-**GSTIN** transfers within
  one legal entity. No finding covers cross-**entity**.

---

### `RK-008` · Every approval in the set is one step; the market's is a value-banded chain — **MINOR**

- **What is missing or wrong:** approval exists across the design and is well-guarded: `FR-408` (approver ≠
  actor), value thresholds on adjustments and counts (`DATA-MODEL.md:1001`, `:1007`), and the PO's
  `SUBMITTED → APPROVED` above a value threshold (`BUILD-SPEC-SCREENS.md:285`). **Every one is a single
  approver.** There is no way to say *"POs over ₹5 lakh need the parts manager, then the general manager"*,
  or *"a write-off over ₹50,000 needs the branch manager and then finance"*.
- **Who ships it:** D365 — procurement workflows
  ([learn.microsoft.com](https://learn.microsoft.com/en-us/dynamics365/supply-chain/procurement/procurement-sourcing-workflows)) ·
  NetSuite SuiteFlow approvals
  ([docs.oracle.com](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/book_N2723865.html)) ·
  S/4 flexible workflow
  ([help.sap.com](https://help.sap.com/docs/SAP_S4HANA_CLOUD/0e602d466b99490187fcbb30d1dc897c/f83f5260160d40a4ac1797e7d8b1eb5e.html)) ·
  Unicommerce PO approval
  ([support.unicommerce.com](https://support.unicommerce.com/index.php/knowledge-base/purchase-orders-2/)) ·
  Cin7 Core purchase process settings
  ([help.core.cin7.com](https://help.core.cin7.com/hc/en-us/articles/11073310369679-Purchase-process-customization-settings)) ·
  Zoho Inventory — single- or multi-level approval ([zoho.com](https://www.zoho.com/us/inventory/help/warehouses/transfer-orders.html)) · Odoo Studio approval rules, Enterprise ([odoo.com](https://www.odoo.com/documentation/18.0/applications/studio/approval_rules.html)) · SAP Business One approval procedures scored `?` — help.sap.com did not render. **IN-7: 4 of 7**
- **Why it matters:** a dealer principal who signs large POs personally will ask for it in the demo. Today the
  honest answer is to give the principal the approve permission and nobody else, which blocks every small PO.
  The ask is real but not large, which is why this is MINOR.
- **Negative evidence:**
  ```bash
  grep -niE "approval (workflow|procedure|matrix|rule)|approval_rule|multi-level approval|approval_level" docs/*.md   # → no output
  ```
- **Proposal:** **V2** — one bounded table, `wh_approval_levels` (document kind × value band × sequence ×
  permission), read by the existing approve actions. It is *ordered, typed rows*, so it stays inside refusal
  #10 / FRD §10 row 11 and is not a workflow engine. `FR-408` applies at each level, and no user approves the
  same document twice.
- **Version:** **V2 (PHASE-2).** **Phase:** P5.
- **Owning task:** **NEW** — the next free P5 id by the glob.
- **Irreversibility:** `reversible` — the single-step `approved_by` columns stay as the last approver.
- **Relationship to earlier rounds:** **new.** `T-090` and `E-034` gave us the approver ≠ actor rule; no
  finding asked for levels.

---

### `RK-009` · The benchmark has no row for any of `RK-001`…`RK-008`, and a round-3 `UNVERIFIED` is answerable — **MINOR**

- **What is missing or wrong:** `COMPETITOR-BENCHMARK.md` §2 has no row for: a branch stock request, the
  selling-branch ↔ fulfilling-warehouse rule, the ABC *computation*, reorder alerting, drop-ship, a B2B trade
  portal, cross-entity transfer or approval levels. Separately, `GAP-REGISTER-R3.md:487-493` carries as
  **UNVERIFIED** whether an inter-branch transfer has a transfer-price column distinct from
  `whin_delivery_challans.declared_value`. **It does:** `wh_transfer_orders` carries `transfer_price_basis`
  (`COST`/`TRANSFER_PRICE`/`OPEN_MARKET_VALUE`), `transfer_price` and `cost_value` (`DATA-MODEL.md:1003`), and
  `WS-090` shows `transferPrice` (`BUILD-SPEC-SCREENS.md:1615`). The same register's own settling condition
  (*"a `valuation_basis` … semantics sentence in `DATA-MODEL.md`"*) is met by the enum on that row.
- **Why it matters:** the benchmark is the sales document. A capability the matrix does not list is one a
  salesperson will say we have, or say we lack, from memory. And an `UNVERIFIED` left open invites round 5 to
  re-derive something already in the data model.
- **Negative evidence:**
  ```bash
  grep -ciE "transfer request|drop.?ship|ABC.{0,20}(recompute|computed)|reorder alert|B2B portal|inter-?company|approval level" docs/COMPETITOR-BENCHMARK.md   # → 0
  grep -n "transfer_price_basis" docs/DATA-MODEL.md                                                                                                         # → 1003
  ```
- **Proposal:** add eight rows under §2.5, §2.7, §2.8, §2.9, §2.11, §2.14 and §2.17, carrying this file's
  matrix marks and the version each finding proposes. Mark the `GAP-REGISTER-R3.md` transfer-price item
  **RESOLVED — `DATA-MODEL.md:1003`**.
- **Version:** documentation. **Owning task:** fold into **`X-050`**'s remediation pass (as `J-004` did).
- **Irreversibility:** `reversible`.
- **Relationship to earlier rounds:** **extends `X-050` / `J-004`**; **closes** one `GAP-REGISTER-R3.md`
  UNVERIFIED.

---

## §3 · What I checked and found sound

Each row was a candidate finding, and each is already placed correctly or refused with a reason. It is listed
so round 5 does not walk it again.

| Capability | Market (from §2.0) | Where the set covers it | Verdict |
|---|---|---|---|
| Per-user / per-branch warehouse visibility | Y at Unicommerce, EasyEcom, SAP EWM, ShipHero | `FR-404` three-mode view, `FR-405` warehouse-scoped access, both v1, enforced in `WHERE` | sound |
| Inter-branch transfer at a transfer price, not cost | Y NetSuite; P D365 (India), Unicommerce, EasyEcom (entered price); Cin7 at cost only | `transfer_price_basis` + `transfer_price` + `cost_value` on `wh_transfer_orders` (`DATA-MODEL.md:1003`), `FR-244` | **ahead of the Indian e-commerce set**, which types a price and has no basis |
| Channel inventory buffer / per-channel allocation | Y Unicommerce, EasyEcom, Increff, Cin7 | `FR-209` publish rules, v2 | sound — the D2C segment is declined at v1 (benchmark §4.1) |
| Backorders | Y at 10 of 17 | `FR-178` six quantity columns v1; `FR-184` fulfilment policy v1.1 | sound |
| Landed cost | Y D365, NetSuite, Fishbowl, Cin7; **no Indian e-commerce product verified** | v1 value-only movement type / v1.1 apportionment / v2 retro (benchmark §2.13) | sound, and ahead of the Indian e-commerce set |
| Consignment in and out, goods on approval | Y D365, NetSuite, SAP EWM, Fishbowl; none verified in Indian e-commerce | `FR-108`, `FR-113` — one model, three configurations, v1 | **ahead** — R15 already said so |
| Kits / bundles with derived availability | Y SAP EWM, ShipHero, all four Indian e-commerce; **D365 and NetSuite kits show no availability** | `FR-075`: `MIN(component ÷ required)`, v1.1 | **ahead of D365/NetSuite** |
| Variants | Y D365, NetSuite, Cin7, Vinculum | `A-3`: v1 schema, v2 screens | sound |
| Price lists | Y at 5+ | `RA-002` (fold into `P2-25`, `whad_price_levels`) and `E-078` (the home) | **already filed in round 3** — not re-filed |
| Master-data field-level audit trail | Y D365, NetSuite, Cin7; ShipHero quantity-only | `whb_audit_events` + `whb_audit_event_changes`, hash-chained, v1 (`DATA-MODEL.md:920-921`, `FR-427`) | **ahead of ShipHero** |
| Serial-number warranty tracking | serial capture everywhere; **warranty dates verified nowhere** in the Indian e-commerce set | `warranty_start_date`, `warranty_end_date`, `sold_to_counterparty_id` on `whb_serials`, v1 (`DATA-MODEL.md:575`) | **ahead** |
| Public API + outbound webhooks | Y EasyEcom, Cin7, Logiwa, ShipHero, D365, Manhattan; **Unicommerce API Enterprise-only, no webhooks found** | REST v1; `FR-333` HTTP outbox delivery v1.1 (`P3-22`); `FR-458` keys and rate limits v2; R19 covers signing | sound as scheduled — HTTP delivery at v1.1 matches the Indian mid-market |
| Native PO and SO creation | Y at 13 of 17 | `wh_purchase_orders` with a full status vocabulary (`BUILD-SPEC-SCREENS.md:279-289`) and `wh_demand_orders`, v1 | sound |
| Label and barcode printing, incl. item labels for parts with no manufacturer barcode | Y at every product verified | `FR-225` item and shelf label encoding `item_code` (`FR-060`), v1 | sound |
| Ageing / dead stock | Y D365, Fishbowl, Increff | `FR-162` measured from last outward movement, value per bucket, branch split, v1 | sound — the *ABC* half is `RK-003` |
| GRNI | only S/4 FI; nothing verified in any WMS or Indian product | `invoice_matched` on the receipt (`FR-242`), report on the accounting side | sound — correctly an accounting report |
| Returns with grading | Y at every product verified | basic returns v1 (`A-1`), grading v2 (`P5-13`) | sound |
| Mobile scanning, slotting, labour, dock / yard, AI forecasting, custom fields | as the benchmark scores them | §2.12, refusals #3, #7, #8, #12, #23; `J-003` | sound — not re-scored |
| Tax invoice on a standalone install | Zoho, Tally, Odoo and SAP B1 all invoice | `INDIA-LOCALISATION-PACK.md:612-616`: *"accounting raises the invoice … Where no accounting module is installed (D-7), the envelope exports and the transfer is marked invoiced externally"* | a **stated** boundary (`D-6`), not a gap. Sales should say it: a standalone buyer keeps Tally for billing |

---

## §4 · Refused

### 4.1 · Candidate findings I did not file

- **Branch↔warehouse service-map table** (one row per branch per warehouse it may draw from). Zoho's
  *Locations* and NetSuite's location hierarchy model one. `RK-002` deliberately proposes the GSTIN rule
  instead: it answers the statutory question with no table, and `FR-405` already answers access. Build the
  table only when a customer asks for a restriction **narrower** than the GSTIN.
- **Auto-created purchase orders at the reorder point** (Fishbowl, EasyEcom for backorders, Odoo reordering
  rules). `FR-253`'s *"the warehouse never becomes a purchase-order engine"* is the right line for a dealer,
  whose PO goes to an OEM with its own ordering rules. `RK-004` adds the *alert* and keeps the human.
- **Scheduled e-mailed reports for internal users** (NetSuite saved searches, D365 alerts). A **platform**
  capability used by every module. Asking warehouse to build one creates the second report-scheduler
  `FR-284`'s *"never a second mechanism"* discipline forbids. It is referred to the platform backlog, not
  filed here. The 3PL portal's v2 *"scheduled reports"* (`FR-284`) should use the platform one when it exists.
- **Anything the benchmark, its §7 refusals or R15 §3 already settled** — not restated.

### 4.2 · What we should explicitly decline — proposed refusal rows

Following R15 §4.2's rule: each is a capability ≥3 named products ship, which a real target customer of
**this** product does not need, stated so that silence does not read as an oversight. They extend the
benchmark's §7, and the FRD §10 table as its next rows.

| # | Decline | Who ships it | Why we decline it | Re-entry path |
|---|---|---|---|---|
| a | **Vendor / supplier portal** — suppliers log in to acknowledge POs, post ASNs, see payments | D365 vendor collaboration · Vinculum · NetSuite (view-only) · Increff | A dealer's dominant supplier is the OEM, which runs **its own** portal and will not log into ours. The long tail of local suppliers sends a WhatsApp and an invoice PDF. It is a public attack surface with no user | `R15` `J-005`'s document capture over `doc-ocr-ai` reads the supplier's paper instead of asking the supplier to key it. ASN ingestion stays an API (`PC-` port) |
| b | **Per-channel marketplace catalogue management** — listing, content and price sync per marketplace | Unicommerce · EasyEcom · Vinculum · Increff | Benchmark §4.3 already concedes connector *breadth*. This is the catalogue half of the same thing, and it belongs to the seller's channel tool | `FR-209` publishes *stock*; the channel tool owns the listing |
| c | **A generic workflow designer** (draw any approval graph) | D365 workflow editor · NetSuite SuiteFlow · SAP flexible workflow | Refusal #10 in a workflow costume. `RK-008`'s bounded level table covers what a dealer asks for | a new **bounded** column on `wh_approval_levels`, reviewed once |
| d | **Sale-or-return (SOR) consignment *to* customers with automatic invoicing on non-return** | Vinculum `P` · several Indian distribution ERPs | Stock placed at a customer is already modelled (`FR-113`, consignment out). *Converting* it to a sale on a date is a receivable decision, which refusal #18 / `FR-274` keep out of warehouse | emit the aged consignment-out position; accounting or the channel invoices |

---

## §5 · Counts

```bash
cd warehouse-issues
grep -cE '^### `RK-[0-9]{3}`' docs/reviews/R25-competitor-gap-r3.md                          # → 9
grep -oE '^### `RK-[0-9]{3}`.*— \*\*(BLOCKER|MAJOR|MINOR)\*\*$' docs/reviews/R25-competitor-gap-r3.md \
  | grep -oE 'BLOCKER|MAJOR|MINOR' | sort | uniq -c
# →   3 MAJOR
#     6 MINOR
grep -cE '^\| [a-d] \| \*\*' docs/reviews/R25-competitor-gap-r3.md                            # → 4  (proposed refusals a–d)
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | **0** | — |
| **MAJOR** | **3** | `RK-001` `RK-002` `RK-004` |
| **MINOR** | **6** | `RK-003` `RK-005` `RK-006` `RK-007` `RK-008` `RK-009` |
| **Total** | **9** | |

| Class (brief) | Ladder slot | Findings |
|---|---|---|
| **V1 — table-stakes** | v1 · P1/P2 | `RK-001` transfer request & approval · `RK-002` selling-branch ↔ fulfilling-warehouse rule · `RK-004` reorder alerting |
| **V1 — decision now, feature later** | decision v1 · feature v2 | `RK-005` drop-ship · `RK-007` cross-entity transfer (statement v1, linked pair v2) |
| **V2 / PHASE-2** | v1.1 | `RK-003` ABC recompute |
| **V2 / PHASE-2** | v2 · P5 | `RK-006` B2B trade portal · `RK-008` approval levels |
| **Documentation** | — | `RK-009` benchmark rows + one R3 UNVERIFIED closed |

**Dispositions:** 5 *fold into an existing task* (`RK-001` → `P2-02`+`P1-17` · `RK-002` → `P1-05`+`P2-25`+`P2-26` ·
`RK-004` → `P2-15` · `RK-006` → `P5-08` · `RK-007` statement → `P1-17`) · 3 *NEW task* (`RK-003` P3 ·
`RK-007` feature P5 · `RK-008` P5) · 1 *`OD-` row owed to `DECISIONS.md` §3* (`RK-005`) · 1 *fold into `X-050`*
(`RK-009`) · **no id allocated in any other register by this file.** 4 proposed refusal rows (§4.2) · 19
capabilities checked and found sound (§3).

**Unverified, carried openly:** every `?` cell in §2.0. The weakest columns are Fishbowl, Logiwa and Vinculum
(search cap and unreachable help sites). Manhattan and Blue Yonder cells rest on marketing and developer pages,
not functional documentation. D365 ABC classification is not confirmed on Learn. No finding depends on a
single `?`, and each finding's competitor count holds with every `?` read as `N`.
