# W08-02 / #429 - e-way bill contract citation re-pin map (classic HEAD `9579c5a095`)

Design-set record for `neetub1508/warehouse-issues#429`, item **W08-02** (E2E-IN Wave 0, 2026-11-03). Docs only; no code changed.

The contract itself is `warehouse-india/docs/contracts/eway-bill.contract.md` in classic. A design-set task does not edit classic, so this file carries the exact old -> new citation for every operational code citation that has drifted. The classic contract takes the edits in one docs-only commit (see *Edit owed*).

## Declared revision and method

- **Declared revision:** classic HEAD `9579c5a095` (2026-11-03). The e-way service, validation, query, guard and repository files last changed at `e3bf2b387e` / `a36b544af4` (F323, 2026-10-27/28); no cited file has changed since.
- **What the contract is pinned to today.** Its header and v6.25.12 say every `TAG:line` citation was re-pinned to `22184e07de` (#476). Later rows (v6.30-v6.36: #484, #147, #323) edited code and rows without re-pinning the citations around them, which is the drift W08-02 reports.
- **How the new numbers were produced.** Each citation was carried from the revision it was authored against (`22184e07de`; the five citations added or changed by later rows were carried from the commit that wrote them: `8c464fb59a`, `6b962a6f6c`, `51aabb691f`, `a80bbaea44`) to `9579c5a095` through `git diff -U0` of its file. 334 `TAG:line` citations moved; the rest did not. For 312 of them the text of the cited lines at the old revision is identical to the text at the new lines (checked mechanically). The other 22 land in a hunk that changed the lines themselves (growth by the F147 handover gate, #477/#478 status filters, #484 evidence); their new range was found by the first and last statement of the old range and is marked *(re-read)*.
- **Legend note.** `GUARD`, `QS`, `REPOI`, `RULES`, `ENT`, `MAP`, `VAL`, `SVC`, `EXP`, `CEXP`, `GW`, `CVIEW`, `CREPOI`, `DCREPOI` are the tags that moved; `CON`, `CVAL`, `CTL`, `CCTL`, `CQS` and the rest did not.

## The two defects named by W08-02

| Contract row | Old citation | Resolves at `9579c5a095` to | New citation |
|---|---|---|---|
| `EWB-T1-12` (contract line 125) and `EWB-T2-10` (line 265) - the missing-encryption-key refusal before settlement | `SVC:707` (now Javadoc) | `gateway.requireEncryptionAvailable();` in `closeOutUnreadableFiling`, before `settleUnclaimedCancelForCloseOut` and `applyCloseOutUnreadableFiling` | **`SVC:720`** (method `SVC:714-724`, Javadoc `SVC:700-713`) |
| `EWAY_BILL_UNREADABLE_EXTENSION_MAY_BE_LIVE` (line 224) and `EWB-T1-12` (line 125) - the extension ceiling as `max(stamp, bill date + configured days)` | `VAL:520-532` / `VAL:502-511` / `VAL:490-532` | `requireUnreadableExtensionExpired`: ceiling from `ewbDate + maxDays`, raised to the stamped `extensionCeilingDate` when later, refusal `UNREADABLE_EXTENSION_MAY_BE_LIVE` | **`VAL:558-570`** (Javadoc `VAL:551-557`; the `EXTENSION_CEILING` constant is `VAL:91`, the plain ceiling check `requireExtensionAllowed` is `VAL:474-483`, its throw `VAL:484`) |
| `EWB-T1-12`, `EWB-T2-10`, `EWAY_BILL_UNREADABLE_EXTENSION_MAY_BE_LIVE` - caller of the ceiling check | `SVC:748` | `validationService.requireUnreadableExtensionExpired(...)` | **`SVC:761-762`** |

## Full map (contract line at HEAD `9579c5a095` of the classic contract)

Apply each pair in place on that line; leave changelog (`## 7`) citations as history and mark them historical.

| Contract line | Row | Old -> new |
|---|---|---|
| 74 | **Derived, never stored** | `MAP:240-245` -> `MAP:245-250`; `REPOI:288-290` -> `REPOI:328-330` (re-read); `QS:255-259` -> `QS:275-279`; `QS:272-273` -> `QS:298-299` (re-read); `MAP:117` -> `MAP:118`; `MAP:229-238` -> `MAP:234-243`; `RULES:190-201` -> `RULES:261-272`; `REPOI:266-269` -> `REPOI:306-309`; `REPOI:270-276` -> `REPOI:310-316`; `CREPOI:139-144` -> `CREPOI:150-155`; `RULES:190-196` -> `RULES:261-267`; `MAP:123-126` -> `MAP:128-131` |
| 97 | `PART_A_PENDING` | `ENT:274` -> `ENT:282` |
| 100 | `CANCELLED` | `ENT:77` -> `ENT:85` |
| 101 | `CLOSED` | `ENT:79-80` -> `ENT:87-88` |
| 102 | `REJECTED` | `ENT:77` -> `ENT:85` |
| 103 | `BLOCKED_GSTIN` | `ENT:77` -> `ENT:85`; `SVC:1673-1674` -> `SVC:1686-1687` |
| 105 |  | `ENT:77` -> `ENT:85` |
| 107 | REJECTED` (`ENT:101-103`); `pa | `ENT:101-103` -> `ENT:109-111`; `ENT:105-107` -> `ENT:113-115`; `SVC:1435-1437` -> `SVC:1448-1450`; `SVC:1679-1681` -> `SVC:1692-1694` |
| 113 | `EWB-T1-01` | `VAL:99-134` -> `VAL:102-137`; `VAL:182-188` -> `VAL:185-191`; `VAL:191-197` -> `VAL:194-200`; `SVC:269-270` -> `SVC:272-273`; `VAL:201-208` -> `VAL:214-221`; `SVC:271-273` -> `SVC:274-276`; `VAL:210-214` -> `VAL:223-227`; `SVC:329-335` -> `SVC:332-338`; `SVC:279-327` -> `SVC:282-330`; `SVC:1736` -> `SVC:1749` |
| 114 | `EWB-T1-02` | `SVC:347-348` -> `SVC:350-351`; `SVC:350-354` -> `SVC:353-357`; `SVC:355-360` -> `SVC:358-363`; `SVC:1050-1052` -> `SVC:1063-1065`; `VAL:229-233` -> `VAL:242-246`; `SVC:361` -> `SVC:364`; `SVC:365-367` -> `SVC:368-370`; `SVC:369-371` -> `SVC:372-374`; `SVC:372` -> `SVC:375` |
| 115 | `EWB-T1-03` | `SVC:1443-1458` -> `SVC:1456-1471`; `SVC:1671-1675` -> `SVC:1684-1688`; `SVC:941-966` -> `SVC:954-979`; `SVC:1018-1031` -> `SVC:1031-1044`; `SVC:1464-1470` -> `SVC:1477-1483`; `SVC:1471` -> `SVC:1484` |
| 116 | `EWB-T1-03b` | `SVC:899-900` -> `SVC:912-913`; `SVC:908-909` -> `SVC:921-922`; `SVC:910-913` -> `SVC:923-926`; `SVC:914-919` -> `SVC:927-932`; `SVC:920-925` -> `SVC:933-938`; `SVC:893-931` -> `SVC:906-944` |
| 117 | `EWB-T1-04` | `SVC:379` -> `SVC:382`; `SVC:385-386` -> `SVC:388-389`; `SVC:426-427` -> `SVC:434-435`; `SVC:428` -> `SVC:436`; `SVC:440` -> `SVC:450`; `VAL:290-330` -> `VAL:317-367` (re-read); `SVC:452` -> `SVC:465`; `RULES:56` -> `RULES:71`; `SVC:1478-1491` -> `SVC:1491-1504`; `SVC:1496-1498` -> `SVC:1509-1511`; `SVC:1500` -> `SVC:1513`; `SVC:1443-1458` -> `SVC:1456-1471`; `SVC:1668-1681` -> `SVC:1681-1694`; `SVC:395` -> `SVC:403` |
| 118 | `EWB-T1-05` | `SVC:400-411` -> `SVC:408-419`; `SVC:432` -> `SVC:440`; `SVC:433` -> `SVC:441`; `VAL:273-277` -> `VAL:286-290`; `SVC:434-438` -> `SVC:442-446`; `VAL:337-353` -> `VAL:375-391`; `SVC:1492-1505` -> `SVC:1505-1518`; `SVC:1668-1670` -> `SVC:1681-1683`; `SVC:416` -> `SVC:424` |
| 119 | `EWB-T1-06` | `SVC:475-477` -> `SVC:488-490`; `SVC:494-495` -> `SVC:507-508`; `SVC:496` -> `SVC:509`; `SVC:497` -> `SVC:510`; `SVC:498-501` -> `SVC:511-514`; `VAL:358` -> `VAL:396`; `SVC:502-504` -> `SVC:515-517`; `VAL:367-375` -> `VAL:405-413`; `RULES:190-201` -> `RULES:261-272`; `RULES:253-259` -> `RULES:339-345`; `SVC:505-507` -> `SVC:518-520`; `VAL:381` -> `VAL:419`; `SVC:508-509` -> `SVC:521-522`; `VAL:535-538` -> `VAL:573-576`; `SVC:518-522` -> `SVC:531-535`; `SVC:1547-1557` -> `SVC:1560-1570`; `SVC:1443-1458` -> `SVC:1456-1471`; `SVC:1668-1670` -> `SVC:1681-1683`; `SVC:484` -> `SVC:497` |
| 120 | `EWB-T1-07` | `SVC:533` -> `SVC:546`; `SVC:539-544` -> `SVC:552-557`; `SVC:569` -> `SVC:582`; `SVC:570` -> `SVC:583`; `SVC:572` -> `SVC:585`; `SVC:573-578` -> `SVC:586-591`; `VAL:396-412` -> `VAL:434-450`; `SVC:582-583` -> `SVC:595-596`; `VAL:421-430` -> `VAL:459-468`; `SVC:584-589` -> `SVC:597-602`; `VAL:436-448` -> `VAL:474-486`; `SVC:546-557` -> `SVC:559-570`; `SVC:1608-1624` -> `SVC:1621-1637`; `SVC:1626-1634` -> `SVC:1639-1647`; `SVC:1618-1623` -> `SVC:1631-1636`; `SVC:1443-1458` -> `SVC:1456-1471`; `SVC:1559-1593` -> `SVC:1572-1606`; `SVC:1450-1457` -> `SVC:1463-1470`; `SVC:669-679` -> `SVC:682-692`; `SVC:1668-1670` -> `SVC:1681-1683`; `SVC:559` -> `SVC:572`; `SVC:1441-1457` -> `SVC:1454-1470` |
| 121 | `EWB-T1-08` | `SVC:640` -> `SVC:653`; `SVC:660` -> `SVC:673`; `VAL:220-224` -> `VAL:233-237`; `SVC:652-653` -> `SVC:665-666`; `SVC:657-659` -> `SVC:670-672`; `SVC:660` -> `SVC:673`; `SVC:661` -> `SVC:674`; `VAL:456-473` -> `VAL:494-511`; `SVC:662-663` -> `SVC:675-676`; `VAL:479-482` -> `VAL:517-520`; `SVC:664-680` -> `SVC:677-693`; `REPOI:266-269` -> `REPOI:306-309`; `MAP:130` -> `MAP:135` |
| 123 | `EWB-T1-10` | `VAL:55-57` -> `VAL:56-58`; `VAL:108-109` -> `VAL:111-112`; `SVC:303` -> `SVC:306`; `SVC:1761` -> `SVC:1774`; `VAL:177-180` -> `VAL:180-183` |
| 124 | `EWB-T1-11` | `GW:439-467` -> `GW:445-473`; `GW:475-479` -> `GW:481-485`; `SVC:1335-1341` -> `SVC:1348-1354`; `SVC:1478` -> `SVC:1491`; `SVC:1511` -> `SVC:1524`; `SVC:1613` -> `SVC:1626`; `VAL:266-270` -> `VAL:279-283` |
| 125 | `EWB-T1-12` | `SVC:707` -> `SVC:720`; `SVC:1082-1084` -> `SVC:1095-1097`; `SVC:1160-1171` -> `SVC:1173-1184`; `SVC:1162-1167` -> `SVC:1175-1180`; `SVC:739-753` -> `SVC:752-766`; `VAL:502-511` -> `VAL:540-549`; `SVC:698-796` -> `SVC:711-809`; `VAL:490-532` -> `VAL:528-570`; `SVC:783-792` -> `SVC:796-805`; `SVC:1532-1557` -> `SVC:1545-1570` |
| 134 | `EWB-PK-01` | `SVC:1430-1438` -> `SVC:1443-1451`; `ENT:348-354` -> `ENT:356-362` |
| 135 | `EWB-PK-02` | `ENT:353-354` -> `ENT:361-362` |
| 136 | `EWB-PK-03` | `SVC:1036-1057` -> `SVC:1049-1070`; `SVC:657-659` -> `SVC:670-672` |
| 137 | `EWB-PK-04` | `SVC:520` -> `SVC:533`; `SVC:1709-1717` -> `SVC:1722-1730`; `SVC:1431-1432` -> `SVC:1444-1445`; `VAL:241-247` -> `VAL:254-260`; `GUARD:93-104` -> `GUARD:124-135` (re-read) |
| 138 | `EWB-PK-05` | `SVC:841-848` -> `SVC:854-861`; `SVC:1067-1098` -> `SVC:1080-1111`; `SVC:1156-1187` -> `SVC:1169-1200` |
| 139 | `EWB-PK-06` | `SVC:1443-1458` -> `SVC:1456-1471`; `SVC:1559-1593` -> `SVC:1572-1606`; `SVC:933-966` -> `SVC:946-979`; `SVC:950-953` -> `SVC:963-966`; `SVC:979-987` -> `SVC:992-1000`; `SVC:989-1007` -> `SVC:1002-1020`; `SVC:1009-1013` -> `SVC:1022-1026`; `SVC:1306` -> `SVC:1319`; `REPOI:501-513` -> `REPOI:549-561` |
| 140 | `EWB-PK-07` | `SVC:1016-1031` -> `SVC:1029-1044` |
| 141 | `EWB-PK-08` | `GW:565` -> `GW:571`; `GW:678-687` -> `GW:684-693`; `SVC:497` -> `SVC:510`; `REPOI:270-276` -> `REPOI:310-316`; `SVC:387` -> `SVC:390`; `SVC:1100-1136` -> `SVC:1113-1149` |
| 147 | `EWB-AD-01` | `SVC:1394-1406` -> `SVC:1407-1419`; `SVC:365` -> `SVC:368`; `SVC:911` -> `SVC:924` |
| 148 | `EWB-AD-02` | `SVC:1197-1273` -> `SVC:1210-1286`; `SVC:1292-1323` -> `SVC:1305-1336` |
| 149 | `EWB-AD-03` | `SVC:1355-1359` -> `SVC:1368-1372`; `SVC:388-390` -> `SVC:391-393`; `SVC:542-544` -> `SVC:555-557`; `VAL:256-263` -> `VAL:269-276`; `SVC:391` -> `SVC:394`; `SVC:1193-1195` -> `SVC:1206-1208`; `SVC:1326-1329` -> `SVC:1339-1342` |
| 150 | `EWB-AD-04` | `SVC:1221-1257` -> `SVC:1234-1270` |
| 151 | `EWB-AD-05` | `GUARD:52-78` -> `GUARD:58-100` (re-read) |
| 157 | `EWB-RK-01` | `VAL:138-169` -> `VAL:141-172`; `VAL:177-180` -> `VAL:180-183` |
| 158 | `EWB-RK-02` | `SVC:841-848` -> `SVC:854-861`; `SVC:841-848` -> `SVC:854-861`; `SVC:818` -> `SVC:831`; `SVC:834-840` -> `SVC:847-853`; `SVC:807-848` -> `SVC:820-861`; `SVC:1361-1392` -> `SVC:1374-1405`; `VAL:149-155` -> `VAL:152-158` |
| 159 | `EWB-RK-03` | `SVC:850-867` -> `SVC:863-880` |
| 161 | `EWB-RK-05` | `SVC:474-485` -> `SVC:487-498` |
| 178 | `EWC-T1-03` | `RULES:190-201` -> `RULES:261-272`; `RULES:253-259` -> `RULES:339-345` |
| 181 | `EWC-T1-06` | `VAL:465-476` -> `VAL:503-514`; `VAL:502-511` -> `VAL:540-549` |
| 188 | `EWC-PK-02` | `REPOI:501-513` -> `REPOI:549-561` |
| 190 | `EWC-AD-01` | `CREPOI:139-144` -> `CREPOI:150-155` |
| 191 | `EWC-AD-02` | `CREPOI:235-244` -> `CREPOI:246-255` |
| 199 | `LOCK-01` | `SVC:1879-1888` -> `SVC:1892-1901`; `REPOI:567-569` -> `REPOI:615-617` |
| 200 | `LOCK-02` | `SVC:945-947` -> `SVC:958-960`; `SVC:1019-1020` -> `SVC:1032-1033`; `GUARD:55-61` -> `GUARD:67-71` (re-read) |
| 202 | `LOCK-04` | `SVC:1635-1639` -> `SVC:1648-1652` |
| 204 | `LOCK-06` | `SVC:1875-1882` -> `SVC:1888-1895` |
| 210 | `CHALLAN_REQUIRED`, `REGISTRAT | `VAL:99-107` -> `VAL:102-110` |
| 211 | `DISTANCE_INVALID` | `VAL:108-109` -> `VAL:111-112`; `VAL:126-134` -> `VAL:129-137` |
| 212 | `IDEMPOTENCY_KEY_REQUIRED` | `VAL:117-123` -> `VAL:120-126` |
| 213 | `IDEMPOTENCY_KEY_REUSED` | `VAL:138-168` -> `VAL:141-171` |
| 214 | `CHALLAN_NOT_ISSUED` | `VAL:182-188` -> `VAL:185-191` |
| 215 | `EWAY_BILL_ALREADY_LIVE` | `VAL:191-197` -> `VAL:194-200`; `SVC:333-334` -> `SVC:336-337` |
| 216 | `SOURCE_DOCUMENT_TOO_OLD` | `VAL:201-208` -> `VAL:214-221` |
| 217 | `REGISTRATION_NOT_ELIGIBLE` | `VAL:210-214` -> `VAL:223-227` |
| 218 | `EWAY_BILL_STATE` | `VAL:220-224` -> `VAL:233-237` |
| 219 | `EWAY_BILL_FILING_IN_FLIGHT` | `VAL:229-233` -> `VAL:242-246`; `VAL:241-247` -> `VAL:254-260` |
| 220 | `EWAY_BILL_EARLIER_FILING_APPL | `VAL:256-262` -> `VAL:269-275` |
| 221 | `EWAY_BILL_ACCEPTED_FILING_UNR | `VAL:266-270` -> `VAL:279-283`; `SVC:707` -> `SVC:720` |
| 222 | `EWAY_BILL_NO_UNRECORDED_FILIN | `VAL:490-496` -> `VAL:528-534` |
| 223 | `EWAY_BILL_UNREADABLE_CANCEL_R | `VAL:502-511` -> `VAL:540-549` |
| 224 | `EWAY_BILL_UNREADABLE_EXTENSIO | `VAL:520-532` -> `VAL:558-570`; `SVC:748` -> `SVC:761` |
| 225 | `EWAY_BILL_EXPIRED` | `VAL:273-277` -> `VAL:286-290` |
| 226 | `TRANSPORT_MODE_REQUIRED` / `_ | `VAL:290-330` -> `VAL:317-367` (re-read) |
| 227 | `REASON_REQUIRED`, `REASON_UNK | `VAL:337-353` -> `VAL:375-391`; `VAL:456-473` -> `VAL:494-511` |
| 228 | `EWAY_BILL_CANCEL_WINDOW_CLOSE | `VAL:367-375` -> `VAL:405-413` |
| 229 | `EWAY_BILL_IN_CONSOLIDATED_BIL | `VAL:381` -> `VAL:419` |
| 230 | `CURRENT_PLACE_REQUIRED`, `CUR | `VAL:396-412` -> `VAL:434-450` |
| 231 | `EWAY_BILL_EXTENSION_WINDOW_CL | `VAL:421-430` -> `VAL:459-468` |
| 232 | `EWAY_BILL_EXTENSION_NOT_LATER | `VAL:436-448` -> `VAL:474-486` |
| 233 | `EWAY_BILL_NO_UNAPPLIED_EXTENS | `VAL:479-485` -> `VAL:517-523` |
| 234 | `EWAY_BILL_GOODS_ALREADY_MOVED | `VAL:535-541` -> `VAL:573-579` |
| 235 | `EWAY_BILL_SETTING_NOT_CONFIGU | `RULES:56` -> `RULES:71`; `RULES:256-259` -> `RULES:342-345`; `SVC:503-504` -> `SVC:516-517` |
| 236 | `EWAY_BILL_REQUIRED`, `EWAY_BI | `GUARD:36-37` -> `GUARD:41-42`; `GUARD:71-115` -> `GUARD:89-164` (re-read) |
| 239 | `COMPLIANCE_FILING_UNREADABLE` | `GW:458-467` -> `GW:464-473` |
| 250 |  | `SVC:1891-1893` -> `SVC:1904-1906` |
| 258 | `EWB-T2-03` | `ENT:95-99` -> `ENT:103-107` |
| 263 | `EWB-T2-08` | `MAP:229-238` -> `MAP:234-243`; `RULES:190-201` -> `RULES:261-272` |
| 265 | `EWB-T2-10` | `SVC:707` -> `SVC:720`; `SVC:748` -> `SVC:761`; `REPOI:284-288` -> `REPOI:324-328`; `QS:265-266` -> `QS:291-292` (re-read) |
| 275 | `EWC-T2-03` | `RULES:253-259` -> `RULES:339-345`; `RULES:190-201` -> `RULES:261-272` |
| 277 | `EWC-T2-05` | `CVIEW:63` -> `CVIEW:65`; `CREPOI:145-152` -> `CREPOI:156-163` |
| 287 | `EWB-T3-01` | `SVC:1691-1700` -> `SVC:1704-1713`; `RULES:91-93` -> `RULES:106-108`; `RULES:167-175` -> `RULES:238-246` |
| 288 | `EWB-T3-02` | `RULES:99-109` -> `RULES:114-124`; `RULES:185-201` -> `RULES:256-272`; `SVC:1646-1657` -> `SVC:1659-1670`; `VAL:367-375` -> `VAL:405-413`; `MAP:229-238` -> `MAP:234-243` |
| 289 | `EWB-T3-03` | `VAL:421-430` -> `VAL:459-468`; `RULES:177-183` -> `RULES:248-254`; `SVC:580-583` -> `SVC:593-596` |
| 290 | `EWB-T3-04` | `VAL:436-448` -> `VAL:474-486`; `SVC:588-589` -> `SVC:601-602` |
| 291 | `EWB-T3-05` | `VAL:201-208` -> `VAL:214-221`; `SVC:269-270` -> `SVC:272-273` |
| 292 | `EWB-T3-06` | `GUARD:119-127` -> `GUARD:168-175` (re-read); `RULES:70-88` -> `RULES:85-103`; `RULES:152` -> `RULES:223` |
| 293 | `EWB-T3-07` | `SVC:1673` -> `SVC:1686`; `RULES:124` -> `RULES:139` |
| 295 | `EWB-T3-09` | `MAP:240-245` -> `MAP:245-250`; `GUARD:112-115` -> `GUARD:136-139` (re-read); `VAL:273-277` -> `VAL:286-290` |
| 297 | `EWB-T3-11` | `SVC:1179-1180` -> `SVC:1192-1193` |
| 305 | `EWB-X-01` | `SVC:308-327` -> `SVC:311-330` |
| 306 | `EWB-X-02` | `SVC:1496-1498` -> `SVC:1509-1511` |
| 307 | `EWB-X-03` | `SVC:1554` -> `SVC:1567` |
| 308 | `EWB-X-04` | `SVC:1626-1629` -> `SVC:1639-1642` |
| 310 | `EWB-X-06` | `SVC:748` -> `SVC:761`; `DCREPOI:446-463` -> `DCREPOI:454-484` (re-read) |
| 311 | `EWB-X-07` | `REPOI:593-643` -> `REPOI:638-704` (re-read) |
| 312 | `EWB-X-08` | `SVC:1635-1639` -> `SVC:1648-1652` |
| 313 | `EWB-X-09` | `VAL:201` -> `VAL:204`; `REPOI:333` -> `REPOI:378` |
| 327 |  | `REPOI:150-157` -> `REPOI:175-182`; `REPOI:202-224` -> `REPOI:239-262` (re-read); `QS:163-170` -> `QS:164-174` (re-read); `QS:195-207` -> `QS:201-212` (re-read); `EXP:81-90` -> `EXP:81-92` (re-read); `QS:377-384` -> `QS:404-424` (re-read) |
| 328 |  | `EXP:123-127` -> `EXP:125-129`; `EXP:157-159` -> `EXP:159-163` (re-read) |
| 329 |  | `REPOI:229-242` -> `REPOI:269-282` (re-read); `REPOI:236-237` -> `REPOI:276-277`; `QS:185-186` -> `QS:190-191` (re-read) |
| 334 | Generate Part-A (Resume) | `ENT:95-99` -> `ENT:103-107` |
| 338 | Reconcile Extension | `REPOI:266-269` -> `REPOI:306-309`; `MAP:130` -> `MAP:135` |
| 339 | Close out unreadable filing | `REPOI:279-288` -> `REPOI:319-328` |
| 340 | Cancel | `MAP:222-238` -> `MAP:227-243` |
| 343 |  | `MAP:123-126` -> `MAP:128-131` |
| 351 |  | `QS:377-392` -> `QS:403-428` (re-read) |
| 352 |  | `CEXP:112-115` -> `CEXP:118-121`; `CEXP:142-144` -> `CEXP:148-150` |
| 353 |  | `CREPOI:118-123` -> `CREPOI:130-135` |
| 356 |  | `CVIEW:202-203` -> `CVIEW:205-206` |
| 357 |  | `CREPOI:139-144` -> `CREPOI:150-155`; `CVIEW:107` -> `CVIEW:110` |
| 388 | `OPEN-12` | `RULES:190-201` -> `RULES:261-272` |
| 391 | `OPEN-15` | `SVC:1423-1425` -> `SVC:1436-1438`; `GW:565` -> `GW:571`; `GW:678-686` -> `GW:684-692`; `GW:624-633` -> `GW:630-639` |
| 393 | `OPEN-17` | `RULES:140-143` -> `RULES:155-158` |
## Edit owed (classic, docs only)

1. Apply the map above to `warehouse-india/docs/contracts/eway-bill.contract.md` in one pass; move the header pin from `22184e07de` to the HEAD at that commit; add a `v6.37` changelog row; mark the `## 7` citations historical.
2. Re-read the 22 *(re-read)* ranges against the file once more at commit time.
3. Run the same carry-forward (`git diff -U0 <pinned> HEAD` per cited file) before the next F-batch lands, or cite by method name with the line as a hint, as v6.25.10 already did for cross-repo citations.
