# R19 — integration, device and channel surface

> **Date** 2026-09-02 · **Branch** `docs/round-3-functional-completeness` · **Finding prefix** `RD-`
> (`grep -rohE "\bRD-[0-9]{1,3}\b" docs/ issues/ | wc -l` → **0**, so the namespace was free; and
> `FINDING_CITE_RE` at `tools/check-design-set.py:178` requires `\b` immediately before its register
> letter, so `RD-001` can never be misread as a `D-` id.)
>
> **File set.** The design set was **186 markdown files / 58,046 lines when I began reading**
> (`find docs issues -name '*.md' | wc -l` → `186`; `cat $(find docs issues -name '*.md') | wc -l`
> → `58046`) and **190 / 61,099 when I finished** — round 3's `R16`, `R17` and `R18` landed in
> `docs/reviews/` while this lens was running, and my own file is the fourth. **The four new files
> are not in my file set and I did not read them**; the arithmetic above is stated twice rather than
> once because a single number here would be false by the time anyone re-ran it. Read whole: `DECISIONS.md`, `PORT-AND-ADAPTER-CONTRACT.md`,
> `PLATFORM-DEPENDENCIES.md`, `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §§6.11–6.12, 6.19, 6.27,
> `IRREVERSIBLE.md` §§1–2 and §6, `MODULE-INTEGRATION.md` §§1–2, plus the boundary rows of
> `DATA-MODEL.md` §§2.1.12, 1034–1038, 1031–1033, 1056, `BUILD-SPEC-SCREENS.md` rows WS-053…WS-058
> and WS-131…WS-134, `SCENARIO-CATALOGUE.md` rows WH-SC-195, 203–205, 252, 262–267. Task files read
> whole: `p0-08`, `p2-14`, `p3-22`, `p5-11`, `p5-22`. Reviews read for ownership: `R7` §§2.6–2.7 and
> §5, `R10`, `R11`, `R12`, `R13` (whole), `R5` §1.5 and §5.6–5.7. Every other file was grepped, and
> every negative-evidence command below was run over **all** of `docs/` and `issues/`.
>
> On the live side I read `platform/backend/pom.xml`,
> `platform/backend/src/main/java/ai/platform/config/SecurityConfig.java`,
> `platform/backend/src/main/java/ai/platform/constants/SecurityConstants.java`,
> `platform/backend/src/main/java/ai/platform/config/RateLimitingConfig.java`,
> `platform/backend/src/main/java/ai/platform/service/notification/email/EmailTemplateService.java`,
> `platform/backend/src/main/java/ai/platform/service/QrCodeService.java`,
> `automotive/backend/src/main/java/ai/automotive/controller/BoomBarrierWebhookController.java`,
> `mobile/src/config/reactQuery.ts`, `mobile/src/contexts/NetworkContext.tsx` and
> `mobile/src/services/backgroundLocationService.ts`.
>
> **Method, in three sentences.** I took the eight boundaries this lens owns — scanners, printing,
> weighing, carriers, channels, automation, the outbound API/webhook surface, and the
> idempotency/ordering/back-pressure rules at each — and, for each, first established what the set
> and the sibling registers **already own**, because fifteen prior lenses dispositioned 637 findings
> and a restatement is worse than silence. Where a boundary was correctly specified I recorded it in
> §3 with its id. I filed only where the **specification of an interface** is defective — never the
> bare absence of a capability that `PLATFORM-DEPENDENCIES.md` §3 already books as missing.

---

## §1 · Verdict

The boundary work in this set is much better than the prior art it replaces, and three things in
particular are right in a way most products get wrong: the port is an **idempotent journal with a
caller-supplied key whose namespace is partitioned by `source_system`** (`PC-15`, `PC-16`, `L-9`,
`IRR-04`) rather than a CRUD endpoint; the outbox **emits at billable granularity from day one**
because that grain is the one event decision that is irreversible rather than additive (`PC-42`,
`FR-331`, `IRR-50`); and the scan surface is designed for a **keyboard wedge with no vendor SDK**
through one resolution service that logs unresolved strings (`FR-062`, `WH-SC-265`), which is the
only scanner architecture that survives an estate refresh. `PC-33` and `p3-22`'s *Blocked on* block
name the out-of-process authentication hole honestly instead of hiding it. Nothing here needs
re-litigating.

**What is wrong has one shape, and it repeats at five of the eight boundaries: the set specifies the
_object_ at the boundary and never the _protocol_ across it.** There is a subscription table with an
`endpoint_url` and a `secret_ref` and no statement of what is sent, how the receiver knows it is us,
or which HTTP status means delivered. There is a print template with a `body TEXT` and a format enum
and no statement of what that body is written in or how a pick list's N lines get into it. There is
a batch endpoint whose response shape is specified to the byte and whose **request** shape is
specified nowhere, with no size bound. There is a carrier master with `api_enabled` and
`credentials_ref` and two task headers that name *"the carrier adapters"* — a module class that
`D-1` does not contain. In every case the column is right, the table lands in the right band, and
the thing that actually has to be built across the wire is undescribed.

**The single most expensive item is not on that list, and it is a live fact rather than a design
gap.** The design set says of mobile that *"`NetworkContext` reports `isConnected` and nothing queues
behind it"* (`PLATFORM-DEPENDENCIES.md` §3.3). That is wrong in both directions, and both errors cost.
TanStack Query's `onlineManager` is **never wired to NetInfo** in this app
(`grep -rn "onlineManager" mobile/src` → **0**), so `networkMode: 'online'`
(`mobile/src/config/reactQuery.ts:70`, `:111`) — sitting under a comment that reads *"optimized for
offline support"* at `:69` — never pauses anything; combined with `MUTATION: false` at `:58` a write
attempted in a dead aisle fails once and is discarded. And a fully working, AsyncStorage-persisted,
NetInfo-triggered offline mutation queue **does** exist at
`mobile/src/services/backgroundLocationService.ts:96-97`, `:399-403`, `:508-536` — whose overflow
policy is `slice(-maxPoints)`, **drop the oldest** (`:522-529`). That is the correct policy for GPS
breadcrumbs and a data-loss bug for stock movements, and no document in this set states a
queue-overflow policy at all (`grep -rniE "drop.?oldest|queue overflow|max queue" docs/ issues/` →
**0**).

**At what event does this design first embarrass itself in front of a customer?** On the receiving
dock, in the first week, when the operator prints the pallet label. `p2-14`'s own acceptance
criterion is *"The GS1-128 LPN label encodes AI `00`"* — AI `00` **is** the SSCC — while `FR-452`
puts SSCC allocation in **v1.1** (`P3-24`) and says explicitly *"`FR-100` gives the LPN an `sscc`
column and nothing fills it"*. So a v1 install prints a GS1-128 pallet label with a blank or
hand-typed licence plate; and if the operator scans it back, `FR-063`'s element-string parser is also
v1.1, so our own v1 resolver returns *unresolved* for a label our own v1 printer produced. Labels are
glued to physical pallets. `FR-064`'s own reason for making `sscc` a v1 column is *"issuing them
later means re-labelling"* — and this is the version pairing that guarantees the re-labelling.

**Is the fix a v1 column or a v2 project?** Neither, mostly. Six of the eight findings are paragraphs
of specification against tables and versions that already exist, and only two touch a migration:
`RD-002` needs a `delivery_timeout_seconds`/`signing_algorithm` pair on a v1 table if the outbound
contract is to be honoured without a second migration, and `RD-004` needs no column at all but does
need a code in `FR-039`'s frozen vocabulary, which `PC-29` makes additive-only. The expensive one is
`RD-001`, and the fix there is a **version move, not code**: either the SSCC allocator moves from
`P3-24` into `P2-14`'s wave, or the GS1-128 LPN label leaves the v1 eleven.

---

## §1.1 · The boundary inventory, computed

Eight boundaries, each with where it is specified, the version it lands in, and the verdict. The
negative-evidence commands are below the table; every one was run in this session against the live
`classic` checkout at `/Users/bbhushan/work/git/workspace/classic` and against this repository.

| # | Boundary | Specified in | Version | Verdict |
|---|---|---|---|---|
| 1 | **Scanners / RF** — symbologies, GS1 parsing, keyboard wedge, offline capture | `FR-057` `FR-062` `FR-063` `FR-454` · `WH-SC-262` `WH-SC-265` `WH-SC-266` | v1 resolver · v1.1 GS1 parse | **sound in architecture**, broken in version pairing — `RD-001` |
| 2 | **Printing** — templates, ZPL, eleven kinds, reprint audit | `FR-224` `FR-225` `FR-226` · `p2-14` · `wh_print_template*` | v1 template + renderer · v1.1 print server | object right, **protocol absent** — `RD-006` |
| 3 | **Weighing / dimensioning / cubing** | `FR-206` `FR-223` `FR-341` `FR-191` · `WH-SC-296` | v1 capture · v2 legal instrument · v2 cubing | **sound** — §3 D |
| 4 | **Carrier / courier** — rate shop, label buy, AWB pool, tracking, NDR, COD, manifest | `FR-196`…`FR-206` · `p5-11` `p5-12` · `wh_carriers` `V510044` | v1 masters · v1.1–v2 the rest | masters right, **no connector contract** — `RD-005` |
| 5 | **Channels** — marketplace intake, inventory publish, ASN/EDI | `FR-207`…`FR-209` `FR-136` · `whb_channels` `V500051` | v1 channel master · v1.1 ASN · v2 intake | **sound** — §3 E; EDI is refusal #20 |
| 6 | **Automation** — WCS/WES, AS/RS, pick-to-light, robotics | `FR-229` · `actor_type = DEVICE` (`FR-024`) · task table (`FR-212`) | v3 | **shaped, not built** — §3 F |
| 7 | **The outbound API and webhooks** a 3PL client integrates against | `PC-36`…`PC-48` · `FR-330`…`FR-334` `FR-458` · `p3-22` `p5-22` | v1 tables · v1.1 HTTP delivery · v2 client identity | **no delivery contract** — `RD-002`; retention consequence in v1 |
| 8 | **Idempotency, replay, ordering, back-pressure** at each boundary | `PC-15`…`PC-25` `PC-44`…`PC-47` · `L-9` `IRR-04` `IRR-49` | v1 | idempotency and ordering **excellent**; **back-pressure absent** — `RD-004` |

Plus the device surface that is not a boundary in the FRD's sense but decides whether five of the
eight work at all: **the mobile write path** — `FR-047` `FR-221` `FR-222`, v1 statement, v1.1 queue —
`RD-003`.

**The commands, and their output.** Run against `classic` unless the path says otherwise.

```bash
# 1 — no label or document rendering of any kind
grep -rli "zpl\|escpos\|dymo" --include=*.java --include=*.ts --include=*.tsx . | grep -v node_modules | wc -l   # → 0
# 2 — no transactional outbox anywhere
grep -rli "outbox" --include=*.java --include=*.sql . | grep -v node_modules | wc -l                             # → 0
# 3 — no API-key table for a machine caller
grep -rn "CREATE TABLE.*api_key" --include=*.sql . | wc -l                                                       # → 0
# 4 — TanStack Query's online/focus managers are never wired to NetInfo
grep -rn "onlineManager\|focusManager" mobile/src | wc -l                                                        # → 0
# 5 — no query-client persister, no named offline queue
grep -rli "persistQueryClient\|createAsyncStoragePersister\|offlineQueue" mobile/src | wc -l                     # → 0
# 6 — but a hand-rolled persisted offline mutation queue DOES exist, in two services
grep -rln "PENDING_\|pendingLocations" mobile/src/services | wc -l                                               # → 2
# 7 — a PDF page model is already on the runtime classpath and used 20 times
grep -rl "com.lowagie" --include=*.java . | wc -l                                                                # → 20
# 8 — a barcode encoder is already on the classpath, used once, for QR only
grep -rl "com.google.zxing" --include=*.java . | wc -l                                                           # → 1
```

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
# 9  — no webhook signing scheme is described anywhere in the set
grep -rniE "hmac|webhook signature|signing key|x-signature|mtls" docs/ issues/ | wc -l   # → 0
# 10 — no queue-overflow policy is stated anywhere in the set
grep -rniE "drop.?oldest|queue overflow|queue depth cap|max queue" docs/ issues/ | wc -l # → 0
# 11 — no batch size bound is stated anywhere in the set
grep -rniE "max_batch|batch size limit|BATCH_TOO_LARGE|maximum batch" docs/ issues/ | wc -l  # → 0
# 12 — the platform security allow-list is named nowhere in the set
grep -rn "SecurityConstants\|SecurityConfig\|permitAll" docs/ issues/ | wc -l            # → 0
# 13 — no template-body representation or placeholder syntax is named anywhere
grep -rniE "mustache|handlebars|freemarker|thymeleaf|placeholder syntax|\{\{" docs/ issues/ | wc -l  # → 0
```

---

## §2 · The findings

### `RD-001` · v1 prints a GS1-128 pallet label carrying an SSCC that v1 cannot allocate and v1 cannot read back — and the label is glued to a pallet — **BLOCKER**

- **What is missing or wrong:** three version cells that were each defensible on their own do not
  compose.
  1. **The label is v1.** `FR-225` puts *"LPN or pallet label with a GS1-128 symbology"* in the
     eleven kinds that ship in **v1/P2**; `WH-SC-203` (`v1·P2`, `happy`) has the storekeeper print
     *"an `LPN_LABEL` in **ZPL** … The LPN label carries a **GS1-128** symbology and the SSCC"*;
     `p2-14`'s acceptance list contains, verbatim, **"The GS1-128 LPN label encodes AI `00`"**.
     AI `00` is the SSCC — there is no other thing it can be.
  2. **The SSCC cannot be allocated until v1.1.** `FR-452` (§6.27, `v1.1·P3`, task `P3-24`) opens
     with *"An SSCC is allocated, not typed in. `FR-100` gives the LPN an `sscc` column and **nothing
     fills it**."* The allocator — GS1 company prefix, extension digit, per-key gapless counter,
     mod-10 check digit — and its two tables `whb_gs1_settings` / `whb_gs1_serial_counters` are
     `V500056`, `WHB-56`, **v1.1**. `GAP-REGISTER.md` §4.1 row 2 establishes the absence with
     `grep -in "gs1" docs/DATA-MODEL.md` → **0** at the time it was written.
  3. **The label cannot be scanned back until v1.1 either.** `FR-062`'s single scan-resolution
     service is **v1/P1**; `FR-063`'s GS1 element-string parsing — the AI table, fixed vs variable
     length, the FNC1 separator — is **v1.1/P3**, and `WH-SC-266` is filed `v1.1·P3`. So in v1 the
     six scan surfaces of `WH-SC-265` (receive, putaway, move, pick, pack, count) hand a GS1-128
     element string to a resolver that has no parser for it and, per `FR-062`, log it as
     **unresolved**.

  The set has no row that notices the composition. `grep -rn "WH-SC-203\|FR-452\|P3-24" docs/` returns
  the scenario, the requirement and the task and **no document that reads two of them together**.

- **The printing side is worse than "blank", because nothing forbids typing one in.** `FR-452`'s
  title is a prohibition — *"allocated, not typed in"* — and it lands in v1.1. In v1
  `whb_lpns.sscc` is a nullable column on a screen. The two available v1 behaviours are therefore
  (a) print a GS1-128 barcode whose AI `00` field is empty, which most ZPL renderers will emit as a
  malformed element string, or (b) let a user key an SSCC, which is exactly the practice `FR-452`
  exists to prevent and which produces duplicate licence plates across two sites within a month.

- **Why it matters:** the failure is **physical and irreversible in the world**, not in the schema.
  `FR-064`'s stated reason for making `sscc` and `gln` v1 columns is *"They are printed on physical
  labels and exchanged with trading partners; **issuing them later means re-labelling**"* — and this
  version pairing is precisely the one that forces the re-labelling it was written to avoid. A
  warehouse that has run for the v1.1 development window has pallets in racking, in transit and at
  customers carrying labels that either have no licence plate or have one from a namespace the
  allocator does not know about. When `P3-24` ships, the allocator's counter cannot be seeded to
  avoid collision with hand-typed values because nothing recorded which values were hand-typed.
  Second-order: `PC-42`'s `carton.packed` event and `FR-100`'s per-pallet storage billing both key
  on the LPN, and a 3PL client's storage invoice referencing a pallet with no SSCC is not auditable.

- **The smallest correct fix, and it is a version move rather than code.** Either
  (a) **move the SSCC allocator into the v1 wave** — it is `whb_gs1_settings` plus
  `whb_gs1_serial_counters` plus a mod-10 function, the same locked-counter-row idiom `FR-426`
  already builds in v1 for document numbers, so the marginal cost against `P2-14` is small; or
  (b) **remove the GS1-128 LPN label from the v1 eleven**, ship a Code-128 licence plate carrying the
  internal `lpn_code` only, and state in `FR-225` and `WH-SC-203` that GS1-128 arrives with the
  allocator. Whichever wins, `p2-14`'s acceptance criterion *"encodes AI `00`"* and `WH-SC-203`'s
  *"and the SSCC"* must move with it, and the print-side FNC1 encoding rule of `RD-006` must land in
  the same task. **Option (a) is the recommendation** — GS1-128 without an SSCC is not GS1-128, and
  a v1 that prints a nearly-compliant pallet label is worse than one that prints an honest internal
  one.

- **Negative evidence:**
  ```bash
  grep -rn "WH-SC-203" docs/ issues/ | wc -l   # → 4: the scenario, p2-14 twice, R10 once — none reads it against FR-452
  grep -rniE "FNC1" docs/ issues/              # → 4 matches, ALL on the parse side (FR-063, R5, p3-15 ×2); zero on the print side
  ```

---

### `RD-002` · `whb_outbox_subscriptions` ships an `endpoint_url` and a `secret_ref` in v1 and no document says what is sent, how the receiver verifies us, or which HTTP status means delivered — and a v1 HTTP subscription pins outbox retention forever — **BLOCKER**

- **What is missing or wrong:** the set specifies the outbound event boundary as a **table** and never
  as a **protocol**. `PC-39` ships `whb_outbox_subscriptions` in v1 with
  `target_kind ∈ {IN_PROCESS, HTTP}`, `endpoint_url`, `secret_ref`, `event_type_filter`,
  `max_attempts`; `whb_outbox_deliveries` records `http_status`; `PC-44` promises at-least-once in
  `sequence_no` order with exponential backoff; `PC-47` dead-letters after `max_attempts` and
  deliberately blocks the cursor; `p3-22` builds HTTP delivery in v1.1. Six things a webhook
  publisher cannot be built without are absent from the entire set:

  1. **What the secret does.** `secret_ref` is described only as *"a reference to a secret, never the
     secret"* (`PC-39`) and, in `p3-22`'s Traps and `R13`:282, only in terms of **masking it in the
     API response**. No document states an algorithm, a canonical string-to-sign, a header name, or a
     timestamp/replay window. `grep -rniE "hmac|webhook signature|signing key|x-signature|mtls" docs/ issues/`
     → **0**.
  2. **What is in the request.** No body schema, no `Content-Type`, no batching rule (one event per
     POST, or N up to the cursor?), no header carrying `subscriber_code` / `sequence_no` /
     `event_type` so a receiver can dedupe **before** parsing — even though `PC-44` makes
     dedupe on `(subscriber_code, sequence_no)` a **consumer obligation**.
  3. **What counts as delivered.** `whb_outbox_deliveries.status ∈ {OK, RETRY, DEAD}` with an
     `http_status` column, and nothing maps status codes onto that ladder. Is `202` OK? Is a `301`
     followed? Is `422` retried eight times or dead-lettered at once? Under `PC-47` the answer is
     load-bearing: the wrong choice **blocks the subscriber's cursor permanently**.
  4. **A timeout.** None stated. A subscriber that accepts the connection and never responds holds a
     publisher thread; `PC-44`'s *"a slow or dead subscriber never blocks posting"* is a promise about
     the **posting** transaction and says nothing about the publisher's own liveness.
  5. **TLS.** `endpoint_url VARCHAR(500)` with no scheme constraint. `http://` is accepted by the
     column and by every acceptance criterion in `p3-22`.
  6. **Per-subscriber concurrency.** `PC-44` requires strict `sequence_no` order per subscriber,
     which means exactly one in-flight delivery per subscription — a real constraint that no document
     states and that `K-001`'s missing single-instance guarantee makes violable by a second replica.

- **And there is a consequence inside v1, before any of this is built.** `WS-057 Outbox
  Subscriptions` is a **v1·P2** screen of kind **D** — full Add/Edit — with `transport` selectable
  between `IN_PROCESS` and `HTTP` (`BUILD-SPEC-SCREENS.md:506`, `:1435`), and `target_kind` carries
  **no `CHECK`** by `D-10`. `PC-46` states that *"the outbox is **never** pruned below the oldest
  active subscriber's cursor"*. So in v1 an administrator can create an active HTTP subscription that
  v1 has no code path to deliver; its `last_delivered_cursor` stays at `0` forever; and from that
  moment `whb_outbox` — the table fed by every movement, every receipt line and every pick line at
  `FR-422`'s one million ledger rows a day — can never be pruned. `WS-058`'s `httpStatus` column is
  likewise a v1 column that can only ever be null, which is the `U-006` shape again.

- **Why it matters:** a 3PL client or a separately-deployed `logistics` module is the *whole point*
  of `G-046` and `PC-40`, and the first thing that consumer's security review asks is *"how do I know
  a POST to my endpoint came from you?"* With no signature the honest answers are a bearer secret in
  a header (never stated), IP allow-listing (never stated), or nothing. Worse, the failure is silent
  in the direction that matters: an attacker who can reach the subscriber's URL can inject
  `stock.movement.posted` events, and because `PC-44` tells the consumer to **dedupe on
  `(subscriber_code, sequence_no)`** the consumer will happily accept a forged event carrying an
  unused sequence number and reject the real one that follows it as a duplicate. The design's own
  ordering guarantee is what turns an unauthenticated webhook into a data-integrity attack.

- **This is not `OD-8`, `PC-33` or `S-097`, and the distinction is the finding.** All three ask **how
  an out-of-process consumer authenticates _to us_** — an inbound question, whose answer is a
  platform service principal or `whb_api_clients` (`P5-22`, v2). This finding is the **outbound**
  half: how *we* authenticate *to them*, and what we put on the wire. `p3-22`'s *Blocked on* block
  says *"an **HTTP subscriber that calls us back** is the second half of the same question"* — but a
  subscriber does not call us back; we call it. The half that `p3-22` names is still the inbound one,
  and the outbound one is named nowhere.

- **The smallest correct fix.** One subsection in `PORT-AND-ADAPTER-CONTRACT.md` §4.5 — three `PC-`
  rows: the signed-request contract (`SHA-256` HMAC over
  `subscriber_code . sequence_no . timestamp . body`, header name, tolerance window reusing
  `p5-22`'s `max_clock_skew_seconds`), the status→ladder mapping (`2xx` = `OK`; `408`/`429`/`5xx` =
  `RETRY`; every other `4xx` = `DEAD` at once, because retrying a `400` eight times only delays the
  dead-letter), and one-in-flight-per-subscription with a stated timeout. Two nullable columns —
  `signing_algorithm`, `delivery_timeout_seconds` — belong on the **v1** table in `P0-11`'s
  migration rather than in `P3-22`, on the same argument `PC-40` already makes about the table
  itself. Separately and immediately: `WS-057` must refuse `transport = HTTP` in v1, or `PC-46`'s
  retention rule must exempt a subscription that has never had a delivery attempt.

- **Negative evidence:**
  ```bash
  grep -rn "secret_ref" docs/ issues/ | wc -l    # → 5, all about the table shape or masking; none about use
  grep -rniE "http_status|httpStatus" docs/ | wc -l  # → 3, all column declarations; no status→ladder mapping
  grep -rniE "timeout" docs/PORT-AND-ADAPTER-CONTRACT.md issues/p3-22.md | wc -l   # → 0
  ```

---

### `RD-003` · The v1 offline statement is written against a mobile substrate nobody examined: mutations are dropped today, a persisted queue already exists with a drop-oldest policy, and no document in the set states a queue-overflow rule — **BLOCKER**

- **What is missing or wrong:** `FR-047` and `FR-221` are **v1/P0** requirements. They do not build
  the queue — that is `P3-04`, v1.1 — they **decide and state** the offline behaviour per screen, and
  `FR-218` makes silence a defect. That v1 statement is written against a description of the mobile
  app that is wrong in two directions, and one of the two is a live data-loss path.

  1. **What the set says.** `PLATFORM-DEPENDENCIES.md` §3.3: *"`mobile/src/contexts/NetworkContext.tsx`
     reports `isConnected` and **nothing queues behind it**"*, established by
     `grep -ril "persistQueryClient\|createAsyncStoragePersister\|offlineQueue" mobile/src` → 0. I
     re-ran it: **still 0**. The grep is right and the conclusion drawn from it is not.
  2. **Today, a write in a dead aisle is dropped, not queued and not paused.** The app is
     `@tanstack/react-query ^5.17.19` (`mobile/package.json:86`). Its defaults set
     `mutations.networkMode: 'online'` (`mobile/src/config/reactQuery.ts:111`) under a comment
     reading *"Network mode - optimized for offline support"* (`:69`), and `RETRY_CONFIG.MUTATION`
     is `false` (`:58`) — *"No retry for mutations"*. `networkMode: 'online'` only pauses a mutation
     if the library believes it is offline, and on React Native the library's default online detector
     is the DOM `online`/`offline` events, which do not exist; the app must call
     `onlineManager.setEventListener(...)` with NetInfo. It never does:
     `grep -rn "onlineManager\|focusManager" mobile/src` → **0**. So `onlineManager.isOnline()` is
     permanently `true`, nothing is ever paused, the mutation fires, fails on the socket, is not
     retried, and surfaces as a toast. The config comment actively teaches the next implementer the
     opposite.
  3. **A persisted offline mutation queue already exists in this app, and its overflow policy is the
     wrong one for a ledger.** `mobile/src/services/backgroundLocationService.ts` holds
     `private pendingLocations: PendingLocation[]` (`:96-97`), persists it to AsyncStorage under
     `@attendance_pending_locations` (`:35`, `:508-536`), flushes on NetInfo reconnect (`:399-403`)
     and on app foreground (`:391-393`), and **caps the queue by discarding the oldest entries** —
     `this.pendingLocations = this.pendingLocations.slice(-maxPoints)` at `:522-529`, default
     `maxPendingLocations: 100` (`:45`), admin-setting driven. Structurally this is exactly the shape
     `FR-221` needs. Behaviourally, drop-oldest is correct for GPS breadcrumbs and catastrophic for
     scans.
  4. **No document in the set states a queue-overflow policy at all.**
     `grep -rniE "drop.?oldest|queue overflow|queue depth cap|max queue" docs/ issues/` → **0**.
     `FR-221` specifies *"queued writes with a per-scan idempotency key and surfaced — never
     swallowed — conflicts"*; a conflict is what happens when a queued item **reaches** the server.
     An item evicted from the head of a bounded client queue never reaches it, so
     `whb_inbound_messages` has no row, `WS-053 Port Monitor` shows nothing, `WS-054` shows nothing,
     and the loss is invisible on every surface the set builds.

- **Why it matters:** two concrete moments.

  **A picker in a cold room, v1.** The web-and-handheld v1 is declared online-only by `FR-047`, so
  today's behaviour is the behaviour: the pick confirm fails, one toast, and the operator — who is
  holding a carton and cannot read a toast through a glove — carries on. The ledger has no row, the
  reservation stays open, and the discrepancy surfaces at the next cycle count as unexplained
  shrinkage. This is the failure `PLATFORM-DEPENDENCIES.md` §3.3 books as *"the queue itself is
  v1.1"*, but it books it as an absence of function rather than as a silent-loss default that ships
  in v1 and is described in the codebase as offline support.

  **A counter with a full queue, v1.1.** `FR-221` puts counting behind queued writes. A ten-counter
  physical count of `FR-422`'s five thousand lines, in a zone with no coverage, on a device whose
  queue was implemented by copying `backgroundLocationService` — the only precedent in the app —
  loses the **first** scans of the session, keeps the last hundred, and reports success. Every
  variance posted from that count is wrong in a direction nobody can reconstruct, and `L-4`'s drift
  rebuild will not find it because the ledger and the position cache agree: both are missing the
  same rows.

- **The smallest correct fix.** Three sentences in `FR-221` and `p3-04`, and one correction to
  `PLATFORM-DEPENDENCIES.md` §3.3:
  (a) **the queue is durable and never evicts** — it is bounded by refusing new scans with a visible
  *"queue full, N pending, reconnect to continue"* state, because refusing to accept work is honest
  and discarding accepted work is not;
  (b) **the substrate is chosen explicitly**, and if it is TanStack Query then wiring
  `onlineManager.setEventListener` with NetInfo is a named, testable line item, not an assumption;
  (c) `backgroundLocationService.ts` is cited as **the structural precedent and the policy
  counter-example**, so the next implementer copies the persistence and not the `slice()`.
  None of this is a migration and none of it is v1.1 — it is the v1 statement `FR-047`/`FR-218`
  already promise to make.

- **Negative evidence:**
  ```bash
  grep -rn "onlineManager\|focusManager" mobile/src | wc -l                        # → 0
  grep -rn "networkMode" mobile/src                                                # → :70 and :111, both 'online'
  grep -rn "MUTATION: false" mobile/src/config/reactQuery.ts                       # → :58
  grep -rniE "drop.?oldest|queue overflow|queue depth cap|max queue" docs/ issues/ | wc -l  # → 0
  ```

---

### `RD-004` · `POST /movements/batch` has a response specified to the byte, a request specified nowhere, no size bound, and a unique key on the batch envelope with no replay rule — **MAJOR**

- **What is missing or wrong:** the batch endpoint is the port's back-pressure surface — it exists
  precisely so a device can drain a shift — and it is the one endpoint with no bound and no defined
  request.

  1. **No request envelope.** `PC-18` gives the 207-style **response** body in full JSON, including
     `accepted`/`replayed`/`rejected` counts. `§2.3` gives the envelope for the **single** endpoint.
     Nothing anywhere gives the batch request shape. `p0-08`'s endpoint table row is one line.
     Meanwhile `DATA-MODEL.md`:875 requires `whb_movement_batches` to store `source_system`,
     **`batch_reference`**, `submitted_by`, `actor_type`, `device_id`, `total_count` — so the request
     must carry a batch envelope with at least `batch_reference` and `device_id`, and no document
     says so. `grep -rn "batch_reference\|batchReference" docs/ issues/` returns **4** matches: the
     data-model row, the screen row, `p0-08`'s grid column list, and nothing else.
  2. **`uk(source_system, batch_reference)` has no replay rule.** `DATA-MODEL.md`:875 declares the
     unique key. `PC-15`'s idempotency ladder — 201 / 200 / 409 / 422 — is specified for the
     **movement** key and is silent on the batch key. So the defined behaviour of a device that
     re-sends an identical batch after an HTTP timeout is: every movement replays correctly per
     `PC-15` (`200`, `idempotent_replay: true`) and the batch **header insert violates a unique
     constraint**. What the caller sees is a raw `23505` surfacing as a `500`, and `FR-039`'s
     vocabulary has no code for it. `WH-SC-195` (400 queued movements sync) and `WH-SC-167` (40
     movements, one bad) both walk the happy path and neither re-sends the batch.
  3. **No size bound anywhere.** `grep -rniE "max_batch|batch size limit|BATCH_TOO_LARGE|maximum batch" docs/ issues/`
     → **0**. `p0-08`'s acceptance uses 400 as an example, `PC-18`'s argument uses 40 and 400,
     `FR-034` uses 400. Nothing declares a maximum. The endpoint opens **N transactions** — `PC-18` is
     explicit that each movement gets its own — and holds one HTTP connection open for all of them,
     which is the classic shape of a request that is fine at 400 and takes a connection pool down at
     40,000. `FR-422`'s target is one million ledger rows a day.
  4. **The error vocabulary has no capacity class.** All 43 codes in §3.9 are business refusals.
     There is no `429`, no `RETRY_AFTER`, no `BATCH_TOO_LARGE`, no `PAYLOAD_TOO_LARGE`. `PC-29`
     freezes the vocabulary from v1 and permits **addition** but never renaming, so adding these
     later is legal — but a producer that has already shipped retry logic branching on a body code
     will meet a bare `413` from the servlet container or a `500` from the constraint, both of which
     carry no code at all, and `§10.2` instructs a consumer to treat an unrecognised code as
     **non-retryable**. A genuinely retryable capacity refusal will therefore be permanently
     discarded by a correctly-implemented consumer.
  5. **The batch tables are write-only through the port.** `whb_movement_batches` and
     `whb_movement_batch_results` exist with `succeeded_count`, `failed_count` and `completed_at`,
     and `§2.2`'s endpoint surface has **no** `GET /movements/batch/{id}`. The rows are reachable only
     through `WS-055`, a web grid. A device whose connection dropped after the server committed
     cannot ask what happened; its only recovery is to re-POST, which is item 2.

- **Why it matters:** the batch endpoint is the single most likely place a partner integration first
  goes wrong, because it is the only endpoint whose input size is controlled entirely by the
  producer. The realistic incident is a device that has been in a warehouse basement for three days
  and syncs eleven thousand scans in one request over site Wi-Fi: the connection drops at movement
  8,900, 8,900 movements are committed, the device retries the whole batch, the movements replay
  correctly and the **batch header** collides, and the operator sees a 500 with no code while the
  ledger is — correctly but invisibly — already right. Every retry after that produces the same 500.
  `R13`'s `K-001` shows the same class of failure from the job side; this is the producer side of it,
  and it is not the same finding.

- **The smallest correct fix.** Four lines. A `PC-` row giving the batch **request** envelope
  (`source_system`, `batch_reference`, `device_id`, `actor_type`, `movements[]`); a `PC-` row
  extending `PC-15`'s ladder to the batch key — *"a repeated `batch_reference` returns `200` with the
  **stored** per-movement result array from `whb_movement_batch_results`, which is what `PC-34`'s
  persist-first rule already makes possible"*, which simultaneously closes item 5 without a new
  endpoint; a declared maximum (`max_batch_size`, an `admin_settings` row so it is tunable per
  install, defaulting to a number the acceptance test uses) with a `BATCH_TOO_LARGE` **422**; and
  `RETRY_AFTER`/`429` reserved in `FR-039` now even though `P5-22` builds the limiter in v2, because
  `PC-29` makes the vocabulary a compatibility surface.

---

### `RD-005` · Channel connectors have an adapter contract and carrier connectors have none — while `wh_carriers.api_enabled` and `wh_carrier_accounts.credentials_ref` ship in v1 and two task headers name a module class `D-1` does not contain — **MAJOR**

- **What is missing or wrong:** the set is careful and explicit about one third-party integration
  class and silent about the other, and the silent one is larger.

  **Channels are governed.** `FR-207`: *"The **channel master lives in base** … per-owner channel
  accounts live in `warehouse` … **each connector is an adapter and `warehouse-base` never names a
  channel vendor**."* `whb_channels` carries `owning_module` (`DATA-MODEL.md`:926, `V500051`, v1) —
  the column whose whole job is to say which module owns a row. `COMPETITOR-BENCHMARK.md`:479 states
  the shape again: *"**v2**, one adapter per channel"*.

  **Carriers are not.** Eleven requirements — `FR-196`…`FR-206` — specify carrier masters, stored
  labels with a void path, normalised-and-raw tracking events with per-carrier mappings held as data,
  rate shopping that persists the quote, pincode serviceability, an AWB pool claimed with
  `FOR UPDATE SKIP LOCKED`, NDR with a response clock, and COD remittance reconciliation. Not one of
  them says where the vendor-facing code lives, and:
  - `wh_carriers`, `wh_carrier_services`, `wh_carrier_accounts` are **`V510044`, v1**, in the
    `warehouse` **app** module (`DATA-MODEL.md`:1031-1033, `WH-34`). `wh_carriers` carries
    **`api_enabled`** and **`tracking_url_template`**; `wh_carrier_accounts` carries
    **`credentials_ref`**. Those are v1 columns that describe a live vendor API, in the module every
    install ships, and no document says what setting `api_enabled = true` causes to happen or where
    that code sits.
  - `wh_carriers` has **no `owning_module`** column — the one dimension `whb_channels` has.
  - `p5-11` and `p5-12` both open *"Modules **`warehouse`** + **the carrier adapters**"*. There is no
    such module class. `D-1` defines exactly five: `warehouse-base`, `warehouse`,
    `warehouse-adapter-<vertical>` (per vertical), `warehouse-3pl`, `warehouse-india`. A "carrier
    adapter" has no Java package, no Flyway band, no `pom.xml` profile, no `ModuleImportSelector`
    constant and no column in `MODULE-INTEGRATION.md`'s 22-row *"complete touchpoint matrix"*. Both
    task headers then assign their migrations to `V510203`–`V510207`, which is the **`warehouse` app
    band** — so the tasks say "adapters" and the migrations say "app".
  - `p5-11`'s `LABELS:` line reads `warehouse,phase-p5,warehouse,warehouse-adapter-dealer`. A
    carrier integration is labelled with the dealer adapter.

  `FR-199`'s *"five relocatable objects"* is adjacent and does not close this: it governs how carriers
  are **referenced** (by stable code, never by an FK) so they can move to a future `logistics` module,
  which is a data-model rule about relocation. It says nothing about which module may name Delhivery
  in a Java class.

- **Why it matters:** table placement decides package placement. Once `wh_carriers` and
  `wh_carrier_accounts.credentials_ref` live in `warehouse` at `V510044` in **v1**, the first
  carrier's API client, its status-code mapping, its AWB-pool fetcher and its webhook receiver will
  be built beside them — inside the core app module that every install of this product ships,
  including a dealer parts department in Nagpur that will never use a courier. That is precisely the
  coupling `D-11` and `FR-207` forbid for channels, and the argument is identical: the connector
  breadth is unbounded (`COMPETITOR-BENCHMARK.md`:749 concedes the marketplace-breadth race
  permanently), each carrier's API is a moving target, and a vendor integration in the core module
  means every carrier's outage, credential rotation and API deprecation is a release of the
  warehouse product. The channel side got this right; the carrier side got the same problem and no
  rule.

- **The smallest correct fix.** One amendment to `FR-196` in the shape `FR-207` already uses:
  *"`warehouse` owns the carrier, service and account masters and **never names a carrier vendor**;
  each carrier connector is an adapter registered through the `PC-04` `List<T>` bean registry, and a
  connector that is not on the classpath leaves `api_enabled` inert with a stated fallback."*
  Add `owning_module` to `wh_carriers` — one nullable column at `V510044`, in **v1**, on the same
  argument that put it on `whb_channels`. Then fix the two task headers to name a real module and
  correct `p5-11`'s label. If the decision is instead that carriers deliberately live in the app,
  that is a legitimate answer and it needs an `OD-` row, because it is the mirror image of a decision
  the set took explicitly in the other direction.

---

### `RD-006` · The print template's `body` has no representation, no variable-binding contract, no repeat construct and no escaping rule — and the "zero precedent" claim misallocates the budget across the three ingredients that are already on the classpath — **MAJOR**

- **What is missing or wrong:** `p2-14` is a careful task. It gets the version boundary right
  (`wh_printers` is `P3-08`), the mm-versus-dots rule right, `is_reprint` service-set rather than
  caller-chosen, void-never-delete, and the `documents` FK. What it — and `FR-224`, `FR-225` and
  `DATA-MODEL.md`:1035 — never say is **what a template is written in**.

  `wh_print_template_versions` is `template_id`, `version`, **`body` TEXT**, `effective_from`. The
  parent carries `format ∈ {ZPL, EPL, TSPL, PDF, HTML}`. The acceptance criterion is *"A pick list
  renders to PDF and an LPN label renders to **ZPL** from the same template object and the same
  renderer entry point."* Four things must be decided before a line of that can be written, and none
  is:

  1. **What the body is.** ZPL source with holes in it? An HTML document rendered to both targets? A
     layout DSL? The `format` column names the *output*, and the body's own language is never named.
     `grep -rniE "mustache|handlebars|freemarker|thymeleaf|placeholder syntax|\{\{" docs/ issues/` →
     **0**.
  2. **How data reaches it.** No data contract per `template_kind`. A `PICK_LIST` template needs the
     order header, the shipment, and **N pick lines**; a `LOCATION_LABEL` needs one location. Nothing
     declares either shape, so `WH-SC-203`'s *"a `LOCATION_LABEL` **batch** for the 1,152 generated
     bins"* has no defined meaning — 1,152 renders concatenated, or one render given a collection?
  3. **How a repeating section is expressed.** This is the load-bearing one, and the repo's own
     precedent gets it wrong. `platform/…/service/notification/email/EmailTemplateService.java`
     renders a DB-stored body with `{{…}}` placeholders bound from a flat
     `Map<String, String> variables` (`:121`, `:137`) and a raw `replace("{{content}}", …)` at
     `:185`. That is the only template renderer in this codebase, it is a genuinely reusable shape
     for a **label**, and a flat string map **cannot express a pick list's line table**. An
     implementer told there is no precedent, who then finds this one, will ship a renderer that
     handles ten of the eleven kinds and cannot do the pick list, the packing slip, the GRN or the
     delivery document — four of the five PDF kinds.
  4. **How field data is escaped into the target.** ZPL is a control-prefixed byte protocol: `^` and
     `~` begin commands and `\` escapes. An item description or a customer name containing a caret —
     ordinary in part numbers — corrupts every command after it, and the failure is a mis-printed
     label rather than an exception. GS1-128 needs the FNC1 escape sequences in the `^BC` field data
     (`^FD>;>8…`) to encode application identifiers at all, and `grep -rniE "FNC1" docs/ issues/`
     returns **4** matches, all on the **parse** side (`FR-063`, `R5`:130, `p3-15`:23, `:61`), **none**
     on the print side. `p2-14`'s acceptance *"The GS1-128 LPN label encodes AI `00`"* has no
     encoding rule behind it.

- **The "zero precedent" claim is wrong in a way that matters to the estimate.** `p2-14` opens with
  `grep -rli "zpl\|escpos\|dymo"` → 0 and concludes *"There is no precedent to copy inside this
  repo."* The grep is right — I re-ran it, still **0** — and the conclusion over-generalises from
  label protocols to the whole capability. Three of the four ingredients are already on the runtime
  classpath and none is named anywhere in the design set:
  - **A PDF page model.** OpenPDF 2.0.3, `platform/backend/pom.xml:177-182`, used by **20** Java
    files (`grep -rl "com.lowagie" --include=*.java . | wc -l` → 20), including
    `platform/…/service/report/ReportPdfService.java` and nine module-level `*PdfService` classes.
  - **A barcode encoder.** ZXing core + javase 3.5.3, `platform/backend/pom.xml:184-195`, used by
    exactly **one** file — `platform/…/service/QrCodeService.java:90` — and only for QR. ZXing
    encodes Code 128 and therefore GS1-128 as a raster today.
  - **A `{{…}}` template renderer over a DB-stored body**, above.

  What is genuinely net-new is the **ZPL writer** — and it is exactly the piece the three existing
  ingredients cannot supply, because ZXing returns a bitmap and a bitmap in ZPL means `^GF`, which
  produces jobs one to two orders of magnitude larger and slower than native `^BC`. So the estimate
  is misallocated in both directions: the PDF half is cheaper than budgeted and the label half is
  the whole risk. `p2-14`'s own trap — *"there is no per-module npm manifest, so a module cannot add
  a frontend library; rendering is a backend concern"* — is correct and reaches the right place, and
  then does not look at what the backend already has.

- **Why it matters:** `A-2` moved printing into v1 on the argument that a warehouse that cannot print
  loses to a spreadsheet and a Dymo, and `R5` ranks it ship-blocker #2. It is on
  `IMPLEMENTATION-PLAN.md` §3.5's critical path. A task on the critical path whose central artefact —
  the template body — has no defined representation will be estimated as a screen and discovered as a
  language design, in the wave that also owns outbound, counting, valuation and returns.

- **The smallest correct fix.** Three additions to `p2-14` and one to `FR-224`: name the body language
  per format class and say it once (recommendation: the body is **target-native source** — ZPL for
  the label kinds, an HTML/CSS document for the PDF kinds rendered through the existing OpenPDF path
  — with one `{{…}}` binding syntax shared by both); declare a **per-`template_kind` data contract**
  including the repeat construct for line collections, since that is the difference between a
  renderer and a string replace; and state the **escaping rule per format**, with the ZPL control
  characters and the GS1-128 FNC1 sequences named. Then replace the *"zero precedent"* sentence with
  the three live dependencies and the one genuinely new writer, so the risk lands where it is.

---

### `RD-007` · An unauthenticated inbound endpoint cannot be added by a module — the platform allow-list is a hard-coded constant — and the set's "complete touchpoint matrix" has no row for it, while the platform rate limiter it will duplicate is never named — **MINOR**

- **What is missing or wrong:** every third-party **push** this product is sold with needs a request
  that arrives without a platform session, and in this codebase that is a **platform source edit**,
  not a module capability. `platform/…/config/SecurityConfig.java:149-159` lists ten `permitAll`
  matchers, each a constant; the only webhook among them is
  `SecurityConstants.WEBHOOK_BOOM_BARRIER_PATTERN = "/webhook/boom-barrier/**"`
  (`platform/…/constants/SecurityConstants.java:44`, and it is the only `WEBHOOK` constant in the
  file — `grep -c "WEBHOOK" …/SecurityConstants.java` → **1**). The pattern was added for one
  vertical's device and each handler validates its own key
  (`automotive/…/BoomBarrierWebhookController.java:62` reads `X-API-Key`, `:209` delegates to
  `handler.validateApiKey(apiKey)`), which `PC-33` correctly calls *"the right shape for a **device**
  webhook and not a general machine-caller scheme"*.

  `MODULE-INTEGRATION.md` §2 is headed *"The complete touchpoint matrix"* and lists 22 files a new
  module must edit, with a *"Verified NOT required"* block beneath it. Neither `SecurityConfig.java`
  nor `SecurityConstants.java` appears in either.
  `grep -rn "SecurityConstants\|SecurityConfig\|permitAll" docs/ issues/` → **0** across the whole
  set.

  Four requirements need an inbound push and none names the dependency: `FR-198` carrier tracking
  events, `FR-203` NDR carrier acknowledgements, `FR-208` channel order intake (`last_poll_at` on
  `wh_channel_accounts` implies polling, but no marketplace is poll-only in 2026), `FR-340`'s gate
  event — which the FRD explicitly models on this very webhook: *"published to a handler list,
  exactly as the existing boom-barrier webhook does"*.

  Separately, `platform/…/config/RateLimitingConfig.java` already builds resilience4j per-IP rate
  limiters, scoped to authentication endpoints (`:20-27`). `whb_api_clients.rate_limit_per_minute`
  (`P5-22`, v2) will be the second rate limiter in the same JVM, and the set never mentions the
  first.

- **Why it matters, and why it is `MINOR` rather than higher.** Every consumer of this is **v2**, so
  by the set's own rule a deferred capability is a decision and not a gap. What is a gap **now** is
  the completeness claim: `MODULE-INTEGRATION.md` exists so that standing a module up is a checklist
  rather than a discovery, and a missing row in it is the failure mode that document was written to
  prevent — the one `MI-1` records happening twice already, where two build-time touchpoints were
  absent from R1's list. The cost is a rebuild cycle discovered at the worst moment: the first
  carrier's webhook 403s in a customer UAT, the diagnosis is a platform security config the
  warehouse team does not own, and the fix crosses a repository boundary. Naming it now costs one row.

- **The smallest correct fix.** A 23rd row in `MODULE-INTEGRATION.md` §2 —
  `platform/…/constants/SecurityConstants.java` + `SecurityConfig.java`, kind **R**, *required only
  for a module exposing an unauthenticated inbound endpoint*, evidenced by
  `SecurityConfig.java:159` — plus one sentence in `PLATFORM-DEPENDENCIES.md` §2 recording that the
  allow-list is a platform constant and that `RateLimitingConfig` already exists, so `P5-22` extends
  it rather than building a second.

---

### `RD-008` · The port's error vocabulary is 43 codes and `FR-039` — the requirement that freezes it — still lists 21; the fold the contract requires *"before v1 ships"* never happened, and the set already cites the number it does not contain — **MINOR**

- **What is missing or wrong:** `PORT-AND-ADAPTER-CONTRACT.md` §3.9.2 is unambiguous: the twelve
  codes it adds *"are not in R4 §3.5. `FR-039` names its list as **stable and documented from v1**,
  so these must be folded into `FR-039` **before v1 ships** — not discovered afterwards, which would
  be exactly the renaming `PC-29` forbids."* The fold has not been made. `FR-039`
  (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`:165) still enumerates the ratified core only and contains
  none of `UNKNOWN_SOURCE_SYSTEM`, `SOURCE_SYSTEM_NOT_CLAIMABLE`, `UNKNOWN_DOCUMENT_TYPE`,
  `UNKNOWN_STOCK_STATUS`, `UNKNOWN_DUTY_STATUS`, `UNKNOWN_REASON_CODE`, `REASON_CODE_REQUIRED`,
  `ITEM_IDENTIFIER_CONFLICT`, `OWNER_TYPE_MISMATCH`, `VALUE_UNBALANCED`,
  `MOVEMENT_TYPE_NOT_PERMITTED_FOR_SOURCE`, `WAREHOUSE_MISMATCH` or `COMPANY_MISMATCH`.

  The set has already begun citing the list it does not have: `R11`'s `Y-002` reasons over
  *"`FR-039`'s **43-code** vocabulary"* (`R11`:235) and `R12` routes import errors to
  *"`whb_import_batch_rows.errorCode` from `FR-039`'s vocabulary"* (`R12`:385). Both are reading the
  contract's number off the requirement's name — which is exactly the class of miscitation
  `DECISIONS.md` §7 rule 3 records as the accounting set's worst failure, where nineteen citations
  resolved to a different real requirement and live gaps read as closed.

- **Why it matters:** `FR-039` is not documentation, it is the compatibility surface. `PC-29` makes
  the codes *"stable from v1"* and renaming one *"a breaking change to five callers"*, and `§10.2`
  instructs a consumer to treat an unrecognised code as **non-retryable**. So the requirement that
  freezes the contract does not contain twelve of the codes the contract will emit, and the builder
  who implements `FR-039` — a P0 task — will implement 21 and be told at integration that there are
  43. Under `PC-29` adding them is legal and cheap; the risk is not the addition, it is that the two
  documents disagree about what has been frozen, and only one of them is the requirement a task
  closes.

- **The smallest correct fix.** Copy §3.9.2's twelve rows into `FR-039` verbatim, state the total as
  43, and add one line to `p0-08`'s acceptance: *"`FR-039` and `PORT-AND-ADAPTER-CONTRACT.md` §3.9
  enumerate the same set, and a test asserts the enum's cardinality."* The capacity codes proposed in
  `RD-004` should land in the same edit rather than in a second one, because `PC-29` makes every
  later addition a second compatibility event.

---

## §3 · What I checked and found sound

Recorded with ids so round 4 does not re-walk this ground.

### A · Ingestion idempotency, ordering and replay

The strongest part of the set. `L-9` + `IRR-04` + `PC-15` make `(source_system, idempotency_key)`
unique with the key **caller-supplied and never server-generated**, and `PC-16` argues the case
correctly: a server-generated key makes a retried timeout post twice, which is the exact failure the
key exists to prevent. `PC-17` closes the gap no source closed by specifying the canonicalisation —
sorted keys, omitted nulls, received decimal forms, UTC millisecond timestamps, `idempotency_key`
inside the hash and the principal and `recorded_at` outside — and refuses a client-supplied hash for
the right reason. `PC-21`–`PC-25` handle out-of-order arrival as **normal**: `sequence_no` is server
acceptance order, `occurred_at` is business order, late arrival is never an error, sufficiency is
evaluated at post time with the surprising consequence stated as a decision rather than hidden, and
back-dating legitimately changes as-at answers with the caching rule named. `PC-34`'s persist-first
inbound log is what makes replay cheap. `WH-SC-023`, `WH-SC-024`, `WH-SC-165`, `WH-SC-180` and
`WH-SC-195` walk all of it. I found nothing to add except the batch-envelope gap of `RD-004`.

### B · Scanner architecture

`FR-062`'s single scan-resolution service returning a typed object, with *"no scanner SDK ever enters
the codebase"* and every scan logged resolved or not, is the only design that survives a mixed
estate; `WH-SC-265` proves it across six surfaces. `FR-057`'s separation of barcode **type**
(purpose) from barcode **format** (symbology), with quantity derived from the packaging row and never
stored on the barcode, is correct and is argued against `R2`'s contrary proposal with a reason.
`FR-059`'s deliberately non-unique alias table (`WH-SC-264`) is right — two owners do carry the same
EAN. `FR-063`'s composite return shape admitted from v1 so the v1.1 parser is a new behaviour behind
an existing contract is exactly the right deferral technique; my `RD-001` is about the **print** side
of that deferral, not the parse side.

### C · Outbox event grain

`PC-42`/`FR-331` identify correctly that grain is the one irreversible event decision and document it
per code — `pick.line.confirmed` called out as *"the single most commonly under-modelled event"* is
the sentence that separates this from every design that emits `order.shipped`. `owner_id` on every
event from day one (`PC-38`) is the same discipline applied to dimensions. `PC-44`'s at-least-once +
consumer-side dedupe, `PC-45`'s replay-from-cursor as the **only** recovery mechanism, `PC-47`'s
deliberately-blocking cursor on a poison message with the reasoning given, and `PC-48`'s dead-letter
grid built to the house grid pattern — including the `filter_definitions` versus
`grid_filter_definitions` trap — are all right. `RD-002` is about the transport under all of this,
not the design of it.

### D · Weighing, dimensioning and cubing

Correct and correctly staged. `FR-206` captures the **pack photo and scale weight at pack time in
v1** on the argument that dispute evidence cannot be created retroactively — which is the right
reason and the right version. `FR-191` puts item dimensions, weight and stackability as **v1
columns** and cartonisation and dimensional weight in v2, which is the same column-now/behaviour-later
pattern used elsewhere. `FR-223` treats a weighing instrument as a **legal instrument** with a
verification certificate and validity, flagging a weighing done out of verification — v2, `P5-17`,
and `WH-SC-296` places the weighbridge reading on the receipt rather than the yard. One observation
that is not a finding: no requirement states whether a weight is **keyed or read from an
instrument**. For v1 that is fine, because manual capture is the honest default; it becomes a real
question at `FR-223` and should be answered there rather than assumed.

### E · Channels

Better specified than carriers by a wide margin. `FR-207` puts the channel master in base with
`owning_module` and makes each connector an adapter that base never names; `FR-208`'s idempotency on
`(channel account, external order id)` **with an external version so a stale re-poll is discarded**,
plus an import decision log recording created / updated / ignored-stale / rejected, is the answer to
the commonest support call in the category and it is stated as such; `FR-209`'s publish rules — basis,
buffer, maximum, zero-below-threshold, included statuses and warehouses, and a publish log recording
what was pushed **and what the channel acknowledged** — is the oversell control, correctly modelled as
configuration rather than code. The channel↔ledger reconciliation my lens looks for is the publish
log plus `FR-208`'s decision log, and between them the two questions *"what did we tell the channel"*
and *"what did the channel send us"* are both answerable. EDI (856/940/945/947) is **refusal #20** in
`COMPETITOR-BENCHMARK.md`:889 with a stated reason, and `S-015`'s document-shaped port is dispositioned
to `P3-05`/`FR-136` as the ASN. That is a defensible refusal, not a gap.

### F · Automation, and whether the interface is shaped for it

Yes, and it is a genuinely good answer. `FR-229` puts automation at v3 and specifies the seam as *"a
published task-event contract and the movement port (`actor_type = DEVICE`), never protocol-level
control in our codebase"*. The shape is present in v1: `actor_type` includes `DEVICE` and `device_id`
is on the movement (`FR-024`); the task table exists in v1 with `device_id`, `assigned_at`,
`started_at`, `completed_at` and paused seconds (`FR-212`, `FR-213`) precisely so that RF,
interleaving and automation are new consumers rather than rewrites; the outbox is subscribable by
row rather than by code (`PC-41`); and `FR-334` names the event stream as *"the automation vendor's
integration surface"*. Supporting a WCS later would not re-cut the ledger. One caveat I checked and
decided **not** to file: the v1 event catalogue emits `task.completed` and no `task.created` or
`task.released`, so a WCS subscriber can learn that work finished and not that work exists. Under
`FR-331` adding an event code is explicitly cheap and additive, and the task rows persist with their
timestamps, so nothing about the past becomes unanswerable. It belongs in `P6`'s scope note, not in a
finding.

### G · The port's boundary discipline

`FR-041`/`§2.9`'s list of what the port must **not** carry — no carrier, AWB, trip, vehicle, sales
price, customer, tax, billing charge code, channel-specific field, free-text reference or JSONB — with
a stated destination for each, is the discipline that keeps the seam from rotting, and `p0-08`'s
acceptance tests it (*"A payload carrying a carrier, a sales price or a JSONB blob is **rejected**,
not ignored"*). `§2.10`'s twelve provably unaddable properties and `§10.6`'s four unrecoverable
API decisions are the right things to have written down. `PC-30`/`PC-32` get in-process
authentication and owner scoping right — a `WHERE`-clause guard returning `403`, never a filtered
grid, because *"an empty grid is indistinguishable from no stock"*.

---

## §4 · Refused

Candidate findings I deliberately did **not** file, and the id that owns each.

| Candidate | Owned by |
|---|---|
| *"There is no offline mutation queue in mobile"* | **`S-086`** · `PLATFORM-DEPENDENCIES.md` §3.2/§3.3 · `FR-047` `FR-221` → `P0-08`/`P0-16`/`P3-04`. `RD-003` is not the absence — it is that the substrate description is wrong and no overflow policy exists |
| *"There is no label rendering anywhere in this codebase"* | **`S-087`** → `P2-14` `P3-08` · `A-2`. `RD-006` is the specification of the template, not the absence of the renderer |
| *"There is no transactional outbox anywhere"* | **`G-045`** · `FR-330` `FR-332` · `PC-35`'s six-item budget. `RD-002` is the delivery contract, not the table |
| *"There is no API-key table for an out-of-process consumer"* | **`S-097`** → `P5-22` · **`OD-8`** · `PC-33`. I verified both greps and add nothing to the inbound half |
| *"There is no service principal / no platform machine identity"* | **`OD-8`**, with a stated recommendation and a deadline, and `p3-22`'s *Blocked on* block |
| *"There is no tenancy"* | **`OD-3`** · `PLATFORM-DEPENDENCIES.md` §3.5 — resolved as one DB per customer, explicitly not to be re-litigated |
| *"There is no restore path"* | **`S-082`** · `FR-429` → `P0-16` |
| *"Queue and outbox signals are failure-shaped; a subscriber falling behind is invisible"* | **`K-005`** (R13), filed last round, and `P5-22` item 4 already carries the cursor-lag subtraction |
| *"The outbox publisher has no execution contract, and two replicas both advance the cursor"* | **`K-001`** (R13). My `RD-002` item 6 depends on it and does not restate it |
| *"`carton.packed` is a v1 event with no v1 emitter"* | **`U-001`** (R10) — no carton can be created in v1 at all; the event is the same defect seen from the outbox |
| *"`WS-057`/`WS-058` show v1 columns that can only be blank"* | Shape owned by **`U-006`** (R10) for `WS-132`. I filed only the **retention** consequence, which is new, inside `RD-002` |
| *"Rate-limit `POST /movements` in v1"* | **R13 §4** refused it explicitly as over-engineering under `OD-3`. `RD-004` asks for a **size bound and a reserved code**, not a limiter |
| *"There is no SSCC allocator"* | **`S-005`** → `P3-24` · `FR-452`. `RD-001` is the v1/v1.1 collision with `FR-225` and `p2-14`'s acceptance, which no document reads together |
| *"`barcode_format` must admit `GS1_DIGITAL_LINK` and the resolver must accept a URI"* | **`S-017`** → `P3-24` · `FR-454` |
| *"Retail-compliance EDI — 850/856/940/945/947, routing guides, chargebacks"* | **Refusal #20**, `COMPETITOR-BENCHMARK.md`:889, with a stated reason; `S-015` → `P3-05` as the ASN |
| *"Marketplace connector breadth"* | Conceded permanently and in writing, `COMPETITOR-BENCHMARK.md`:749 |
| *"No EPCIS repository"* | FRD §10 row 20 · **`S-009`** — the four EPCIS dimensions are v1 columns and the repository is a named refusal |
| *"The print server and printer registry are missing"* | Stated deferral to v1.1/`P3-08`, walked by `WH-SC-204` and bounded by `U-006`; `X-041` records that `WH-SC-204` — the 203-versus-300-dpi scenario — was claimed by no task, and `p2-14` now names it |
| *"`device_id` is a v1 column with no device registry until v1.1"* | `FR-024`/`FR-213` put the column in v1 deliberately; `FR-222` states the registry deferral and its reason. A stated deferral, not silence |
| *"`on_behalf_of_actor_id` is mandated and absent from the movement header"* | **`Y-001`** (R11) |
| *"Weighbridge / instrument verification is not built"* | **`S-034`** `S-058` → `P5-17`, v2, with `FR-223` stating it |
| *"`whb_transport_details` has no Ship-To GSTIN"* | **`J-001`** (R15) |
| *"An inserted `grid_filter_definitions` row crash-loops the backend"* | **`R1 CM-4`**, restated correctly in `PC-48` with both greps |
| *"The frontend re-closes vocabularies the backend opens"* | **`OD-5`**, referred to the standards owner, and `PC-67`/`PC-70`, which state the divergence from CLAUDE.md TYPESCRIPT RULE #6 explicitly |
| A dedicated EDI-mapper adapter contract | Follows from refusal #20. `§7.2` already notes *"an **EDI adapter** needs #13"* of the thirteen catalogues, which is the correct amount of preparation for a refused capability |
| A second reconciliation object for channel-versus-ledger stock drift | Over-engineering. `FR-209`'s publish log and `FR-208`'s decision log answer both directions of the question, and the ledger is authoritative by construction — a third object would be a report over two logs |

---

## §5 · Counts

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -c "^### \`RD-" docs/reviews/R19-integration-device-and-channel-surface.md                  # → 8
grep -o "\*\*BLOCKER\*\*$" docs/reviews/R19-integration-device-and-channel-surface.md | wc -l    # → 3
grep -o "\*\*MAJOR\*\*$"   docs/reviews/R19-integration-device-and-channel-surface.md | wc -l    # → 3
grep -o "\*\*MINOR\*\*$"   docs/reviews/R19-integration-device-and-channel-surface.md | wc -l    # → 2
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | **3** | `RD-001` `RD-002` `RD-003` |
| **MAJOR** | **3** | `RD-004` `RD-005` `RD-006` |
| **MINOR** | **2** | `RD-007` `RD-008` |
| **Total** | **8** | |

**By disposition** — seven fold into existing tasks; **no new task is proposed**. One is a version
move rather than an edit.

| Finding | Folds into | Migration touched | Irreversible? |
|---|---|---|---|
| `RD-001` | **a version decision first** — `P2-14` ↔ `P3-24`; then `FR-225`, `WH-SC-203`, `p2-14` acceptance | `V500056` moves into the v1 wave, or nothing moves | **Yes, physically** — printed labels cannot be recalled (`FR-064`) |
| `RD-002` | `P0-11` (two nullable columns + the `WS-057` v1 guard) · `P3-22` (the contract) · `PORT-AND-ADAPTER-CONTRACT.md` §4.5 | `P0-11`'s outbox migration, for `signing_algorithm` / `delivery_timeout_seconds` | columns reversible; the **retention** consequence is not, once the outbox has grown |
| `RD-003` | `P0-16` §4 (the v1 statement) · `P3-04` (the queue) · `PLATFORM-DEPENDENCIES.md` §3.3 correction | none | reversible in design; **each dropped scan is not** |
| `RD-004` | `P0-08` · `PORT-AND-ADAPTER-CONTRACT.md` §3.4 · `FR-039` | none — one `admin_settings` row in `WHB-75` for the cap | the **error code** is a `PC-29` compatibility surface; add it before a producer ships |
| `RD-005` | `FR-196` amendment · `P5-11`/`P5-12` headers and labels · `V510044` gains `owning_module` | `V510044` (v1) for one nullable column | the column is cheap now; **package placement follows table placement** and is not cheap later |
| `RD-006` | `P2-14` (three specification blocks) · `FR-224` | none | reversible, but it is on the critical path |
| `RD-007` | `MODULE-INTEGRATION.md` §2 (a 23rd row) · `PLATFORM-DEPENDENCIES.md` §2 | none | reversible |
| `RD-008` | `FR-039` (fold §3.9.2's twelve) · `p0-08` acceptance | none | `PC-29` makes the vocabulary additive-only; fold before v1 |

**One cross-cutting correction that is not a finding in its own right but must travel with the above,
because it is a load-bearing instruction that is now false:**

`PLATFORM-DEPENDENCIES.md` §3.3 and §3.2, and `p2-14`'s opening — *"nothing queues behind
`NetworkContext`"* and *"There is no precedent to copy inside this repo"*. Both greps are correct and
both conclusions over-reach. A persisted, network-triggered offline mutation queue ships today at
`mobile/src/services/backgroundLocationService.ts:96-536` with a **drop-oldest** overflow policy, and
three of printing's four ingredients — OpenPDF (`platform/backend/pom.xml:177-182`, 20 call sites),
ZXing (`:184-195`, one call site, QR only) and a `{{…}}` DB-stored template renderer
(`platform/…/EmailTemplateService.java:121-185`) — are already on the classpath. Following the
instructions as written produces a second offline queue built on the wrong policy and an estimate
that overweights the PDF half while underweighting the ZPL writer, which is the only genuinely
net-new piece.
