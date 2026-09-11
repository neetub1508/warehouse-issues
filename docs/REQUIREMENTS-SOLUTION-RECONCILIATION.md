# Requirements solution reconciliation — 2026-09-11

Scope: warehouse requirements repository only; no application source review or implementation. Read/indexed all 203 Markdown sources and mapped all 152 open issues (143 tasks plus 9 epics) to their source Markdown. Existing rounds remain evidence; this pass targets unresolved decisions, contradictions and configuration completeness, not a new claim to have proved every workflow correct. No files/issues were deleted and no closed duplicate was reopened.

## Gaps and adopted solutions

| Gap in current design set | Solution now adopted | Validation |
|---|---|---|
| Review recommendations remained open/escalated in active decisions | Ten remaining warehouse-side OD answers adopted; integration dependencies become activation gates | Decision cells, task scope and contract agree |
| Settings seed list ended with an ellipsis; clients had no specified values or switch lifecycle | Typed catalogue, defaults, scoped inheritance, atomic revisions, audit and capability checks | CONFIG-CASE-01 through CONFIG-CASE-04 |
| Negative on-hand contradicted unconditional signed-available constraint | Separate signed balance from nonnegative ATP, retain reservation/serial guards | CONFIG-CASE-05 |
| Foreign cost currency/rate source unspecified | Base-valued posting, frozen original currency/rate evidence, no double conversion | CONFIG-CASE-06 |
| Tax engine conflicted with document handoff design | External provider/manual evidence modes, no silent zero tax or duplicate engine | CONFIG-CASE-09 |
| v1 label required later GS1 allocator/parser | Internal Code-128 default; optional GS1 after readiness; issued labels retain resolution | CONFIG-CASE-08 |
| Adopted value-conservation invariant still owed to authoritative tables | Add L-15 and I-21; VALUE_OFFSET seed and acceptance | CONFIG-CASE-10 |
| First-company periods/setup had no complete operator path | Idempotent first-day INSTALL walkthrough and task acceptance | CONFIG-CASE-01 |
| Registration/drop-shipment decisions remained questions | Guarded registration change and version-gated virtual drop shipment | CONFIG-CASE-11, CONFIG-CASE-12 |
| Design contract deferred answers until build | Preimplementation decision/acceptance contract; machine tests remain implementation work | contracts/README and owning tasks |

The built-in design checker is structural validation, not proof of runtime behavior. Provider credentials, company master data and validated jurisdiction profiles remain setup inputs; absent external capabilities remain explicit release dependencies. Historical mentions of 'owed' outside amended scope remain implementation obligations, not claims of completed software.

## Markdown source inventory

SHA-256 identifies each pre-amendment source. Unresolved-marker counts are search aids, not counts of live functional gaps; historical reviews intentionally retain questions.

| Source | Lines | SHA-256 | Open/question marker lines |
|---|---:|---|---:|
| `README.md` | 117 | `765c68ee50746d2a06398663854a2ed0031d3c87da17951c200a44032357e47d` | 0 |
| `docs/BUILD-SPEC-SCREENS.md` | 2682 | `c2c0a047283df3621114f972f07eb77a4e7868f00169171c348d5a5a59be5565` | 5 |
| `docs/COEXISTENCE.md` | 770 | `3f58e262b8f24860409be4d2892471744f873b8bfcd1f91661b893160a934a2d` | 3 |
| `docs/COMPETITOR-BENCHMARK.md` | 1093 | `2b32c50bb34a42117037691ed0d5540ba78a20c1d2cc575a23c0397c3b2d5181` | 4 |
| `docs/DATA-MODEL.md` | 4670 | `ea11957f0230a3f650f2c3e6def6f728112f9a69e0b633feb0dc6f653ae1197c` | 4 |
| `docs/DECISIONS.md` | 670 | `71b306e60099450bd63a6f6615ec28067a41ca86fd3ac74436d7747098a7d873` | 19 |
| `docs/DESIGN-SET-DEFECTS.md` | 1974 | `3f3f0706fec2f167d44d433334f699b96b333ac99685cef9035f9628a2843bf2` | 10 |
| `docs/GAP-REGISTER-R2.md` | 427 | `248251eff3f643e49113131f7147ebf391b4188f0502aeaaad49620927c17d85` | 3 |
| `docs/GAP-REGISTER-R3.md` | 584 | `f2bfc394ddb8248c7156e095f796b63c6feda6b102c719d1a60255b27775f736` | 10 |
| `docs/GAP-REGISTER-R4.md` | 960 | `82f218bfd383980f7865f62537acc03d6012df8a2f37be2bee0697e7189677d7` | 1 |
| `docs/GAP-REGISTER.md` | 1302 | `3ab48dddea25c1ac004128d2b1012571305884ba56e9e3791e4498b728f9237d` | 4 |
| `docs/IMPLEMENTATION-PLAN.md` | 1794 | `b6e84f79aac89a172602c8e5530690a5077d4f1fc20860bc3cf47400978aa9eb` | 5 |
| `docs/INDIA-LOCALISATION-PACK.md` | 1405 | `cdea59146fadfde36442060c154d9937091ae5080c655e8127cb6e3cf7c92807` | 7 |
| `docs/IRREVERSIBLE.md` | 860 | `f3aa716849a454e953fed8656555ede791fc1516347e48bbad8f563e8001a75b` | 1 |
| `docs/MODULE-INTEGRATION.md` | 1216 | `1029e409d0e624521fcb194134a0ef789190a45f9c05c127f1f7f8fcf81b5a58` | 1 |
| `docs/OPEN-DECISIONS-RESOLVED.md` | 1118 | `4975f6010b4791da03eef200f3a53c1d44459d73c919e0978abc2e61bba7c659` | 22 |
| `docs/PLATFORM-DEPENDENCIES.md` | 983 | `f70b4037b82a4e7716b2125692bd170165c75df007ce67e9e9d447a9f78c9216` | 0 |
| `docs/PORT-AND-ADAPTER-CONTRACT.md` | 2137 | `775fc7ed86a0a9454766077ba9941ab003c250bfe030d4cdbdb63fa0195c80aa` | 5 |
| `docs/README.md` | 83 | `1687713983071b1770d1291c22bd4271c5bcd9e5adae5ca6ae5a8eafd30f8c05` | 0 |
| `docs/SCENARIO-CATALOGUE.md` | 771 | `88cd0a858e5eba5e02c939633c03f4fadfb6d6a0c0b4b50d2e37dbfdfe55dd01` | 3 |
| `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` | 1126 | `84fbc25ddde48b980c32104e5709aef9edb5e378203951bbbd6120e79cb971d5` | 1 |
| `docs/contracts/README.md` | 47 | `9bbf5cfda78a0e8fffe793e5161423d7fe3c22c0548c8dc12d4f9bbedc0b3296` | 0 |
| `docs/reviews/R1-codebase-reality.md` | 571 | `6d5e11e5ae6c43a5330637fc47bc4c09ad0c5d56828e7ee01c19756cbb6ac615` | 0 |
| `docs/reviews/R10-operational-walkthrough.md` | 642 | `99b9e41482be9b059ba57ec625f5a4911310ef135999a61107bd27f29d0dd448` | 0 |
| `docs/reviews/R11-exception-and-unhappy-paths.md` | 774 | `4b5a28d43ab734e9154c953a4d160bed28b4ca5625fe9d97ff505fc2bc645f27` | 3 |
| `docs/reviews/R12-lifecycle-and-data-migration.md` | 468 | `219232f5f4ac4681b0da496a01dd52c3bb2dfe51032257031c05b231f1b2b9b8` | 0 |
| `docs/reviews/R13-non-functional-and-operability.md` | 794 | `1c9f8eba86475163c2b818e27bdd5f2439a2a98c37cba252853f1d8f255ddee0` | 3 |
| `docs/reviews/R14-codebase-and-sibling-set-reverification.md` | 588 | `f0efdae65373f46d2b8204640973238e75d82a7629944d6492769fc3c28b0866` | 0 |
| `docs/reviews/R15-competitor-benchmark-r2.md` | 601 | `27f0add333104f5cf8cd0ea7f04ecfea0ff8fb237646fd17ef4586b55ff76842` | 2 |
| `docs/reviews/R16-role-and-persona-completeness.md` | 724 | `02715a1a003993522345dcfb50f50fbe0ee94af923674d629f6191e7b4a5600f` | 3 |
| `docs/reviews/R17-screen-and-field-buildability.md` | 676 | `2d5513b8cf035c643029b017572207d00ff87fbbcfe448328ce943ea70dcba3e` | 0 |
| `docs/reviews/R18-reporting-and-analytics-completeness.md` | 808 | `83302058b8449a856cce49eb5c1d7bbbd54b3114b8b254c6dedaa38e78386667` | 1 |
| `docs/reviews/R19-integration-device-and-channel-surface.md` | 852 | `f9ae364d3c7c2b629a3f917440519769962f45080f71178a8d16eadf410fd537` | 4 |
| `docs/reviews/R2-tier1-wms-audit.md` | 2165 | `8bbb18c07b44f7f3d12a8f7c1a1e6289427fe871bfd12cf80731e1c3bf1dd8ca` | 0 |
| `docs/reviews/R20-configuration-and-day-one-setup.md` | 702 | `3ed3c309032da3cdce433649b945b763d441a85b8f6d9c22ae0a1607642bf933` | 3 |
| `docs/reviews/R21-money-costing-and-billing.md` | 855 | `1a9a67262047ff024585a05f20a4acb129589bd2486b2e65998ef97e7bd10c7c` | 1 |
| `docs/reviews/R22-cardinality-and-junctions.md` | 1010 | `f22117b1b65406929747f04778f0173f570ff3ac2af9d75a3a7372d29e6190a4` | 2 |
| `docs/reviews/R23-platform-alignment.md` | 1074 | `616f055113c7c76d00c89af3cfe69df89d0554f47621a08234eb2364597d30e2` | 0 |
| `docs/reviews/R24-workflow-contract-completeness.md` | 337 | `5c81e6cc3e8119378de4c7585e4105b2870536bd50d639fbe7e7f4d49f43f617` | 1 |
| `docs/reviews/R25-competitor-gap-r3.md` | 670 | `f7d7e43a0e99d489cd618e6187b779f1ee97bc37bf7d271604ff017857aec1b3` | 0 |
| `docs/reviews/R26-extensibility-and-future-proofing.md` | 1042 | `b533ea9c7af076ccc1cb86430eff37909ee9d814e1cc33246df48ba69e62c76a` | 3 |
| `docs/reviews/R3-erp-midmarket-audit.md` | 1842 | `5fa41ec80d826b834ba16dbda9313616583b36ce40ea153ee3d77d017b88ae5f` | 0 |
| `docs/reviews/R4-fulfilment-3pl-audit.md` | 2691 | `e8dda0156129379660f6652d0dd772ac2d770d255d67527811fc3a52e4f54fc9` | 0 |
| `docs/reviews/R5-standards-industry-ops.md` | 1198 | `8689a0a78a6cc38fd95ac87ba8b1fb8745d975a5c96b2ce13496709fa9ce1327` | 1 |
| `docs/reviews/R6-prior-art-triage.md` | 1642 | `af413e59ce159c5256e1709cddccd675161f655de5bb26b116c265bf5278a5f2` | 3 |
| `docs/reviews/R7-logistics-supply-chain-seam.md` | 1647 | `28db7650c3a6d8eb4b78c1f65474ca4081299ade2b2273c0d2a5830d4f382964` | 2 |
| `docs/reviews/R8-task-buildability-v1.md` | 609 | `429c8244d70048c3980a1ceedb2e148bd2eab2d08400b7cd8343bf80d89970bb` | 0 |
| `docs/reviews/R9-task-buildability-v2-and-epics.md` | 832 | `bb83c2e9008c618594b2e6290a1329440b3d1549152761cbb1656d37636cd6ca` | 1 |
| `issues/00-EPIC-master.md` | 335 | `d7b75fb6dce3fb252880952c5cc469e1f8bbe0e7220eb85fe651c19268e1fd1b` | 1 |
| `issues/01-EPIC-p0.md` | 211 | `cd2abb701dfa692e9beb66b3b2cd5b09183f5507c0555c0a4df0c0d1fe6afa9a` | 0 |
| `issues/02-EPIC-p1.md` | 213 | `d392167c57df1219a4718afd1eea63dbd2733e37b7a676ca982bb7b9d61039b1` | 0 |
| `issues/03-EPIC-p2.md` | 287 | `1e4f019431b4c2108cf10db3e14dabf28c26245bef69c53aba623eb5ab896055` | 0 |
| `issues/04-EPIC-p2in.md` | 284 | `821a0eecd8167e3d0832dc511587a43fb6072fff65e1a0f65c91ac40af2df29a` | 0 |
| `issues/05-EPIC-p3.md` | 219 | `7ee8c146007f09e93f6c6b50d5352caf0ea78fd28434edbf2b02ca2f3e6ed1b9` | 0 |
| `issues/06-EPIC-p4.md` | 274 | `908dc1d5e277c993763faac00b8db9e21352c28f475d10e0a93b2b3e7ce0f41c` | 0 |
| `issues/07-EPIC-p5.md` | 257 | `6af2e998b7c4b44c78008217cf382a0779de0baca30bcda8389e7c7321973e88` | 0 |
| `issues/08-EPIC-p6.md` | 222 | `1c7888a41b8af89669af34222d3258afade3f2a125807c058c0cd4681ad9b09f` | 1 |
| `issues/CREATED.md` | 192 | `366b0a6e50bb02b8d838fc5c305e855aa199db3a59fa4048758a710ceb79dc14` | 0 |
| `issues/README.md` | 311 | `c0019b17d73f778012d0a9c7ce40bc5f435be6a6d9565efe62d8ea1450b54974` | 0 |
| `issues/p0-01.md` | 208 | `c0bc25a73c090c8a4e5e5507ba9fe4819ec342360c56441e499c2eaeeefe1664` | 0 |
| `issues/p0-02.md` | 328 | `da3bd117cf5f1fdd8aab73b747120857dd857478e2ffb5fb0efc3b0669bc4156` | 0 |
| `issues/p0-03.md` | 177 | `9253f343a9d137e00c44a8be386b6f74b3577a9068b1b737dbc0733fee2aeb0c` | 1 |
| `issues/p0-04.md` | 227 | `df4009fbd71f55348f52600a4e37e802eade4e9cbf4d2c54273f5feb71f7f793` | 0 |
| `issues/p0-05.md` | 161 | `4d5381ac05da9bc797fdbc8f63dd473f120749bc37978a85d33b69700cbb6faa` | 0 |
| `issues/p0-06.md` | 205 | `7982b98827e11a8e4b63933797207350a5571e3510d21ed57a8966622b5959cd` | 0 |
| `issues/p0-07.md` | 140 | `d176fc55d7946ff739025abe741877aeff11afcb4396f44e2b81558a9406c8a5` | 1 |
| `issues/p0-08.md` | 194 | `7df94a9603d69ec24d7ffd7aad52d5921428ee11d012e58c41637c63810bb1d7` | 0 |
| `issues/p0-09.md` | 135 | `7ad85725be3fa2428b416336181b46fb60866f63ff7ecf35be8793e0fcf6cd60` | 0 |
| `issues/p0-10.md` | 117 | `cb9179647e1087832b918b5ec7feb9622c3df5367bb8afb87830bde024903741` | 1 |
| `issues/p0-11.md` | 203 | `0155eabad77f2b1d30c73248d6c9668e5d0b12b127f9c64884b1f7911c2c1cd8` | 0 |
| `issues/p0-12.md` | 169 | `23307ac108270a49cb53e11458f378f581f1946c307a13a00c42876b5e1922e3` | 0 |
| `issues/p0-13.md` | 182 | `35657aea435a54d5bd04660265deca9c268ef6f1592cd7016be5850a3c57647a` | 2 |
| `issues/p0-14.md` | 123 | `4438291e1a1c4ee0c2908bb90c66bc55a8ed6288638994d3ab86d6541a21c1a8` | 0 |
| `issues/p0-15.md` | 186 | `ed86c46f4e659c769ade0b58630c3a5509e5e8cad22e20839a7f3e3ef434eafc` | 0 |
| `issues/p0-16.md` | 163 | `a891451aa889ebf85a57e9132f1aef546f7f6ce47b3aa98fb6a9684477b90d64` | 0 |
| `issues/p0-17.md` | 138 | `c2f66c1eb4c433a56b6ce25f70a394885b20fbc502f1575a71fb5ab25896139e` | 0 |
| `issues/p1-01.md` | 240 | `a3a1f812a5c99610b6a513aef0098be84260639377289e5fbfe73c326edffdf4` | 0 |
| `issues/p1-02.md` | 208 | `95bb8eeff9ee6ce5cd704b2f3050951de4ba1d7cb03f043183e2e92372facb4e` | 0 |
| `issues/p1-03.md` | 264 | `b9b710bfcbf4c8554e1c910bf597438055c53f1eed88676d6fde5b9ba86f32a6` | 0 |
| `issues/p1-04.md` | 148 | `238723864573545130c63294ad305d725297294f6348591caac878a779999702` | 0 |
| `issues/p1-05.md` | 417 | `fe2defff3c3c194101b5df2b5dfe353b01ebff2768db033aa5307a43f45e3e28` | 0 |
| `issues/p1-06.md` | 126 | `45bb2e71849fe7d5ef1858aff9a9efb4bf2c0492a0cac0747234ea4adea9f0de` | 0 |
| `issues/p1-07.md` | 182 | `625834df648f211d3430fb16c06d9953fcc9107f25e9b1c3a75631e206609580` | 0 |
| `issues/p1-08.md` | 152 | `eba69b6265cc3bc40c31ccef5b0b6be0169d101fb3dc30a181ab6fb69e4a0847` | 0 |
| `issues/p1-09.md` | 144 | `c9863c4df3249639ca738a5e33f418d571460bf95302b521091373613788b9ab` | 0 |
| `issues/p1-10.md` | 131 | `dfbcfbf47dad1f2edaaf84f1a05590ee5699a2ba85f2d8869dd27d17be4e9fac` | 0 |
| `issues/p1-11.md` | 116 | `65d9183693bca4ac9b00aadf1bd05dc14b1a09e036aed157274fed786241b74b` | 0 |
| `issues/p1-12.md` | 147 | `0f90da4861e2a0cad85bf1e3cbfe75cbd8184aca55012aafc45df83436883045` | 0 |
| `issues/p1-13.md` | 179 | `446d44e657e8dd15d68b9229d101fb3ee7e90b326cc09f38dae3eb4628b1a61b` | 0 |
| `issues/p1-14.md` | 165 | `c5faca67bb48685136280156172ac8c0877d4f25b883e32456d0587ad5d723e0` | 0 |
| `issues/p1-15.md` | 128 | `9c879dd7e92df13a7b5f3147066ca0ba9c630821acd5f3ef509f173a1daab681` | 0 |
| `issues/p1-16.md` | 110 | `76e21e6355d475d3ee5a66a8d3dc3981c8c6113fc85dd06d6220119345cd5027` | 0 |
| `issues/p1-17.md` | 225 | `fb5addbf09773bc21d9b8028d25513afcce596abaff81d8687520a85802cff43` | 0 |
| `issues/p1-18.md` | 186 | `dda436a9239bcd141f66e70d50d619accdda4b9108bdacf9ecbb2bc7b02838f4` | 0 |
| `issues/p1-19.md` | 173 | `97e8d9f4c397a9717491d20df4760fd35f003fd7056fe2cee9866a5c0a642dc3` | 0 |
| `issues/p1-20.md` | 148 | `9af577890b827905d8166c81fdd90bd2aab5766c206eb084a3e59490bd33fa55` | 0 |
| `issues/p1-21.md` | 86 | `3a047a38c929da5e2ceffd1c0c4710500c2db54d0458d20d5a8960e2ac6f78ca` | 0 |
| `issues/p2-01.md` | 166 | `b77dcdc277bf97d194b5f79371f107349d8580dfdda6f415fc97fc86504925e8` | 0 |
| `issues/p2-02.md` | 265 | `ff44a2c4cc37d33a5678f34b79f39742e2fe57fc7ff69759a1ea39a3ddafbd90` | 0 |
| `issues/p2-03.md` | 114 | `fae05d28fb80723c40b54beb6360783ee337b968469ff7c5c0a1e4e6e91cfc21` | 0 |
| `issues/p2-04.md` | 216 | `fb547ee7afe8a3d2b8228f7df20d940977419c7dcebd9f326a7591b614eee314` | 0 |
| `issues/p2-05.md` | 141 | `6ae1d40f735065fdba4656af254bdf0c013ba6918c2e531af7f50e8cb5f57fe2` | 0 |
| `issues/p2-06.md` | 99 | `e7c3ffceb8fe71b1c7fc952dfbaaf46ad96884379cd5912731a70916fb18e8f8` | 1 |
| `issues/p2-07.md` | 168 | `e6bf4bc508c1d6681b4d125b29b0ffb8da4d0d37ec0d4fd63053119ef06ed520` | 0 |
| `issues/p2-08.md` | 146 | `ea8f13f07f1ce22ddb0a3eafd6c598c3b4c3658f02f8c2b0ba8548fc9643f5b4` | 0 |
| `issues/p2-09.md` | 140 | `817d51146d719f9e1997c67c25d46e62a0cba97f35fba67a94d4c5abaf2ccc00` | 0 |
| `issues/p2-10.md` | 150 | `5cda7a382ecf81445875abfba59e7925832ce1cfcde82af8e153bd39467526a6` | 0 |
| `issues/p2-11.md` | 105 | `ef7a1b5c273c8a41580470e1b6de577abf7e9b07b517732b17f8c525b1794052` | 0 |
| `issues/p2-12.md` | 192 | `452a68ce74edb52eafa0cfc201daf1ebffac9f77eb7449351051bbbea3bd5e29` | 0 |
| `issues/p2-13.md` | 145 | `675562ebc3a62283e0f621079e770775d0a4a13dbb7a1118eafc421e48322988` | 0 |
| `issues/p2-14.md` | 161 | `be8b40577070fb256616bc3f1527a20a9d31a616cf5c0a79759d7be8e9f4c4b8` | 0 |
| `issues/p2-15.md` | 165 | `9f3a1cbc9a9d7225f6f1e8718bbd9a894277d93ff3284da8cfcefe0485ea54a4` | 0 |
| `issues/p2-16.md` | 210 | `4f1ebb0a14ed65686cfa851839d60ab9bb531f85aeaa3f2da3e4c4c54bf54dc0` | 0 |
| `issues/p2-17.md` | 146 | `e5ef4f7c982ec99a0449a112272e0537b8abc05ea31cfacfa383b839493970e4` | 0 |
| `issues/p2-18.md` | 169 | `a4891267510da1e4d0e664ec0b81719a5861c1837551721b79f280820c84091a` | 0 |
| `issues/p2-19.md` | 126 | `a0c18ed4d1d5b8e496675c6e1828182a506cff9dd51b6f543d669889f9b8987d` | 0 |
| `issues/p2-20.md` | 119 | `6efe356e0db570b4c89ba2f2846af81f305edce616deed1cef3e91b31b7a3c41` | 0 |
| `issues/p2-21.md` | 134 | `4306fae51635eeed49fee67032c08e6a0c69e1871b8e479a19e0470a8c0d9e1c` | 0 |
| `issues/p2-22.md` | 94 | `cd0be6c0f2f3e713cba7fc04939d7bb3536cbdd41d240e11adb2ebb555ee191e` | 0 |
| `issues/p2-23.md` | 145 | `496a79b52971a7e3c3db7e51e49d24390d28efb4789ac89447da9fcb12221da0` | 0 |
| `issues/p2-24.md` | 124 | `7086da9af54d77a5c098d25664fc90f71e45f5f303f092df3a69d5a290d4c3f6` | 0 |
| `issues/p2-25.md` | 207 | `9c791cdbc3cb8bfc3ed53158500f26fc5c49a5f5c73629f6aa76e097e6919081` | 0 |
| `issues/p2-26.md` | 133 | `dc5c64660b5a63fed73e6e7ac9007ce6a14008e821c975d4c1bda91230463aec` | 0 |
| `issues/p2-27.md` | 138 | `4f7fc0b846ef6d5ec3030d111a211b842fa26ed23e42f6f7eb175816c0855e92` | 1 |
| `issues/p2-28.md` | 122 | `100f3c8357eeab982d17c2a5b629148cc8adcc98e397afcff8216a7ef00971c6` | 0 |
| `issues/p2-29.md` | 172 | `97ad617557ff068c13284e102f27d77a5281f8a91cf409d231e8b4af44feee9c` | 0 |
| `issues/p2in-01.md` | 238 | `df2794122105ef21ca3557fb36cc7c0f2bcd2b56d13bedf81362f6e4d62bc4e2` | 0 |
| `issues/p2in-02.md` | 133 | `957cc9044af213f61bb4ff3192fdf11374ee2b1e45b8c607594e3bfbe0e974ae` | 0 |
| `issues/p2in-03.md` | 170 | `3de27f48798368e6b5fef27f0d3805c5c8a765e884e2fe032c8fdd5dd49719c9` | 0 |
| `issues/p2in-04.md` | 212 | `5da587c66dd603f21e221350478dedd98771b73b6975c3fab9b66fe5c69f5b64` | 0 |
| `issues/p3-01.md` | 122 | `8a85d9433517d859f76e5efeeb9e50a759cf8b31f301e04631dcdce412b03efe` | 0 |
| `issues/p3-02.md` | 86 | `d7c59d7ae104ffb95482dedd0ba198a306645ae161a9f402b1ac2011a967bfa1` | 0 |
| `issues/p3-03.md` | 79 | `1850fbb30dd5cf9763442b7547638b80e939a08c473c7dc2e2d04e78c667e6b3` | 0 |
| `issues/p3-04.md` | 137 | `1125d354dbbd902edef5fe7ed1b9810f7497ab0306be4afcc13c82ca7782ac4f` | 0 |
| `issues/p3-05.md` | 104 | `441fda5385879443145ce4ba6fa13168184f3b7ec5cc5ac1c181e08af8249b1c` | 0 |
| `issues/p3-06.md` | 93 | `dbfcb8070f28aafbfaf0a2693cb5f73e24c1b5126c87943bbb38743872d2811a` | 0 |
| `issues/p3-07.md` | 98 | `271d59ad8ef98efd29177f815f8dbe7c33ebd7b4f82cea9154e4278408d40f63` | 0 |
| `issues/p3-08.md` | 90 | `cf267fdfb86d7336893879e82fa603442591ebad33a01347b5f76c711afeda64` | 0 |
| `issues/p3-09.md` | 87 | `a98b7c9fa9564234181578f9bdcbdc7dd3137bdfa2a5459bbcec403e79690e16` | 0 |
| `issues/p3-10.md` | 81 | `fbf2740c8228d44b80bc345a78ddbbbc7cf9cf006d801496067659414212a499` | 0 |
| `issues/p3-11.md` | 122 | `87cb14535f3d4728529f0f4f844ab456e7604707402429efacbde24db3298a0a` | 0 |
| `issues/p3-12.md` | 101 | `bb9877d106c83df79a21ef4e2566bc70fb01f5c40482a70b04915338c77ccca3` | 0 |
| `issues/p3-13.md` | 88 | `525a5b214a11a3bc0ec7c3cb336f35f3f3d5220cbd4ab2f2821c87c2a8cd5015` | 0 |
| `issues/p3-14.md` | 71 | `6177d9d966a5f56b243ea6eb8189cee9d9772b937e50d6ea4e0c522448ee7148` | 0 |
| `issues/p3-15.md` | 86 | `1ce2c70a143ce8d650ab2a958f7d278310ccd77cc17943a8cb46f7267369ab9f` | 0 |
| `issues/p3-16.md` | 122 | `e9942579aeeeb76104c14223f26afc7b0584bca3240b1882e426653b60af7a59` | 2 |
| `issues/p3-17.md` | 95 | `bfc8c50d9e1c8dc682ef2ed9ea017fc2fee3e65c629ec4ee0048038e5ee24f5a` | 0 |
| `issues/p3-18.md` | 110 | `54a91ca1ee433c178d84e0eb3f035124a723bd94435a56bbe95bf6a0e2c6dbca` | 1 |
| `issues/p3-19.md` | 87 | `ae118e21507d385026e4ac4fa73f7b9459a7508be1e5e4cde84d453604dd336b` | 0 |
| `issues/p3-20.md` | 114 | `a5d2041af496e087be8167288c4e46932994ade0e360ea0c38e35493d6014da9` | 0 |
| `issues/p3-21.md` | 88 | `d9b7e6ad46686a4b870012b46f838e8c941b2f52ac6155996e2e693616b40110` | 0 |
| `issues/p3-22.md` | 112 | `a3eec8f4c76cd52d0e7beb20cda479d697378522ed9667549464f3101a985eb7` | 0 |
| `issues/p3-23.md` | 83 | `9835c3a96b73b0b1f25aa4199f119ab675fce2782138fff31ed3b296b997826f` | 0 |
| `issues/p3-24.md` | 91 | `77e6c3b5f2ae7a5b4aeabd3454fe9d422822eb6599f1435806cdf1de9970f70b` | 0 |
| `issues/p4-01.md` | 144 | `d0eeda5a75645763364d1328d371b63f37b754a12d6cfe49f961e04f13c10e70` | 2 |
| `issues/p4-02.md` | 123 | `0b40099d1f8824b51b4c7673bd738fc7eee7b5ce47453fc400afc5486902247b` | 0 |
| `issues/p4-03.md` | 129 | `1d1e3ea6ac68aa504c28aaf49b6eb81ec3d0c82db39b7c335efbbac9267594a4` | 0 |
| `issues/p4-04.md` | 115 | `0fd8cc48c5471dce173a1a735875f8a477cf63cd7a328c8398131f50dfdcc153` | 0 |
| `issues/p4-05.md` | 119 | `5dcc6daf3e077b21c999d4d6626a3c475270c5bad833677296bb8df4c0895ca8` | 0 |
| `issues/p4-06.md` | 112 | `5a961093576c16359de169d43f36a26b2df60a87423f1f646c9f105baa7e2251` | 0 |
| `issues/p4-07.md` | 138 | `bbeac60a135d52075a2a9668a646fc3c0b1f911f8cdcbb2bdf7199f8017c2e7e` | 0 |
| `issues/p4-08.md` | 92 | `63c8cf37e8084af97e50edc37ce13e4bf653e6fa00242c5430d5ef1d3db3c458` | 0 |
| `issues/p4-09.md` | 131 | `4761937318a35253e15b9060791b25bfae968ac0d64df842d3c943db04d07b8d` | 1 |
| `issues/p4-10.md` | 128 | `74657555031090eca9bac23107a32d269c475cab6b2aa1a84065e451a32451a3` | 0 |
| `issues/p4-11.md` | 101 | `5f4c310811ce84f10caab34928ae98bea9b1aed3343f17b5c7a18614024060d5` | 0 |
| `issues/p4-12.md` | 128 | `38875f260586c758c1446167d1c6e63e542d656622cf824062a2e5f664693dd4` | 0 |
| `issues/p4-13.md` | 103 | `d0cea54bdc2a403222730b7e0e26b47ca2826aae9e79f29a93c1674ac0855ebe` | 0 |
| `issues/p5-01.md` | 124 | `95820549d139ec45a33887f098651710ca2490b59707531efb7e915177049b09` | 0 |
| `issues/p5-02.md` | 94 | `ed9ef83bee5394c890ff15530463e11179e46c47975a2e015d79303aaae47952` | 0 |
| `issues/p5-03.md` | 97 | `73a8614db4ba114e1987b852c9abd3033561d6ed0045fb7ca0c4a74e542394ed` | 0 |
| `issues/p5-04.md` | 74 | `9bb1dbc5b71de884caa5cdb6861097b7a4669975acc78ffec34d477acea959b1` | 0 |
| `issues/p5-05.md` | 104 | `b4e4ebb5916c8502f9a5d40d6b9483cecc9afd39c191687d6c018e3162a401c1` | 0 |
| `issues/p5-06.md` | 69 | `146cb98736861d988a837d153404f97d77baf406bbfeb391989a45cfe3e72eb8` | 0 |
| `issues/p5-07.md` | 78 | `5e7d684957663cdd92176ffa35bff243c4d1bb4954647fb857c20c111bc817e6` | 0 |
| `issues/p5-08.md` | 156 | `f0a4731b8264f20b2c1afc262f47ea5bb64f4e2f0b76aca7563c5f7afa71ed0c` | 0 |
| `issues/p5-09.md` | 114 | `23b1c43e1c445617ff42ffca87761bb18277bd8f376664b28307ec9e6931f93f` | 1 |
| `issues/p5-10.md` | 84 | `47320afa8b1d3bf4fbc31e2669d2dadabb91804d315ea689035c69e6a61edb51` | 0 |
| `issues/p5-11.md` | 102 | `6470586b120c9563edcae336a060a2779ada6db3eab1e8a99c3630fb3c2a1b74` | 0 |
| `issues/p5-12.md` | 81 | `c3e20eb539adec0d57729f900d973b77b25688b177ecd5810d390fb2072622af` | 0 |
| `issues/p5-13.md` | 91 | `c21be151f45d613f1f54d800932cd6595c82effba9f48de2e31164be1c754b3e` | 0 |
| `issues/p5-14.md` | 75 | `5ac0ccaaaca63b05af8f91781e76965b9bbb060514a8acf74980f2cfb88b9a8c` | 0 |
| `issues/p5-15.md` | 75 | `fb7c764cdfed81b892c50ef871c9296e4b2b95584703e31fc97fcce10e1cb759` | 0 |
| `issues/p5-16.md` | 86 | `a058cfa128cd3237e3782d700a84e2c45b5d7730da1b1f2019e0d6b18de4c9f8` | 0 |
| `issues/p5-17.md` | 73 | `2df58f3cefa0ce2ae04cfdfcbae044df782c7a9d0ce240238c5e180d2be2a1bc` | 0 |
| `issues/p5-18.md` | 92 | `68e8894ee8f4bc8df3e76dda1d72304be289f36f7ee05a9810edf0f345b2db6b` | 0 |
| `issues/p5-19.md` | 89 | `807edfc1729e91b7caa90cce5350f4271a95420709780ad3f85cd28ca0e897a5` | 0 |
| `issues/p5-20.md` | 89 | `ab81b1d037bd79af71424fe84bced681e5d2e2893c7a84bc77437bb5630100f7` | 0 |
| `issues/p5-21.md` | 138 | `ceb7235c8f37b727a549f4a4eb37ac9556bf75da2fee9af1f84c4ade60ce3a09` | 0 |
| `issues/p5-22.md` | 97 | `c1bffce33d21b111293e56df38748ca299f95016c877985c622df6770b401406` | 0 |
| `issues/p5-23.md` | 83 | `4ca0c668ff7f51841ef9754d07564a1e664d075d8fdbcdf5d370ce0c4c26a799` | 0 |
| `issues/p6-01.md` | 114 | `e5d5eff4a231683bcc80bc9204b479763cbdd625b4f90e2cba4f8c59d0cee5f3` | 0 |
| `issues/p6-02.md` | 85 | `4611215cb97fa3fc49ab5ac2a4bdf058f179830533095f79833a1dd97cf41948` | 0 |
| `issues/p6-03.md` | 84 | `a2d9c6c76ef37f57176ca915da62609af9e79f05500417fd0a948dff61625a53` | 0 |
| `issues/p6-04.md` | 103 | `ab755122c53a314b0f94f192af39b670b21219c29019614293c896945935e165` | 0 |
| `issues/p6-05.md` | 80 | `6c3c30cb0cf0acb18f02075bb52dc0cb50583b87127383445f460242c1d1dc32` | 0 |
| `issues/p6-06.md` | 90 | `e495acee02763aab3aa11bcd74cd4c37ce023c7376fc72bb1376230a0976c3db` | 0 |
| `issues/p6-07.md` | 95 | `8bf131b022afb45b0229705d0ea7143fcf3dd247aaf83abbbb9def847b67950f` | 0 |
| `issues/p6-08.md` | 224 | `a44358e69d5a05638c3f83ef41adacc5a68bc19f1c3414fae5168c01c12d31b5` | 0 |
| `issues/p6-09.md` | 85 | `4437f477c0d5fd0a142fd5a50a706c35af79cb946452b70f7d6c4101efe6e706` | 0 |
| `issues/p6-10.md` | 99 | `3cde600d70d69496a1601ecca92ba87a603aa532c2992ad5ec02fe023d0d0e83` | 0 |
| `issues/p6-11.md` | 91 | `ee607faa4618007abe657604d03511cab3bd6e139c88d3c2408e5919678f3dd8` | 0 |
| `issues/p6-12.md` | 78 | `5fa2075855bbd0061942d2b77893c2a9ab51409df3512639d771920ddfffc45e` | 0 |
| `tools/README.md` | 372 | `50077203d108e64af668b474f90dfaaecbe34aabc85c39f4b601b7e5a471a635` | 0 |

## Open issue coverage

| Issue | Source of truth | State |
|---|---|---|
| #1 | `issues/00-EPIC-master.md` | open; existing task retained |
| #3 | `issues/01-EPIC-p0.md` | open; existing task retained |
| #4 | `issues/02-EPIC-p1.md` | open; existing task retained |
| #5 | `issues/03-EPIC-p2.md` | open; existing task retained |
| #6 | `issues/04-EPIC-p2in.md` | open; existing task retained |
| #7 | `issues/05-EPIC-p3.md` | open; existing task retained |
| #8 | `issues/06-EPIC-p4.md` | open; existing task retained |
| #10 | `issues/07-EPIC-p5.md` | open; existing task retained |
| #11 | `issues/08-EPIC-p6.md` | open; existing task retained |
| #12 | `issues/p3-01.md` | open; existing task retained |
| #13 | `issues/p1-01.md` | open; existing task retained |
| #14 | `issues/p3-02.md` | open; existing task retained |
| #15 | `issues/p0-01.md` | open; existing task retained |
| #16 | `issues/p4-01.md` | open; solution/acceptance amended |
| #17 | `issues/p5-01.md` | open; existing task retained |
| #18 | `issues/p2-01.md` | open; existing task retained |
| #19 | `issues/p3-03.md` | open; existing task retained |
| #20 | `issues/p1-02.md` | open; existing task retained |
| #21 | `issues/p5-02.md` | open; existing task retained |
| #22 | `issues/p4-02.md` | open; existing task retained |
| #23 | `issues/p3-04.md` | open; existing task retained |
| #24 | `issues/p2-02.md` | open; existing task retained |
| #25 | `issues/p0-02.md` | open; solution/acceptance amended |
| #26 | `issues/p5-03.md` | open; existing task retained |
| #27 | `issues/p4-03.md` | open; existing task retained |
| #28 | `issues/p3-05.md` | open; existing task retained |
| #29 | `issues/p2-03.md` | open; existing task retained |
| #30 | `issues/p5-04.md` | open; existing task retained |
| #31 | `issues/p3-06.md` | open; existing task retained |
| #32 | `issues/p4-04.md` | open; existing task retained |
| #33 | `issues/p1-03.md` | open; solution/acceptance amended |
| #34 | `issues/p0-03.md` | open; solution/acceptance amended |
| #35 | `issues/p5-05.md` | open; existing task retained |
| #36 | `issues/p3-07.md` | open; existing task retained |
| #37 | `issues/p2-04.md` | open; existing task retained |
| #38 | `issues/p4-05.md` | open; existing task retained |
| #39 | `issues/p5-06.md` | open; existing task retained |
| #40 | `issues/p1-04.md` | open; solution/acceptance amended |
| #41 | `issues/p3-08.md` | open; existing task retained |
| #42 | `issues/p2-05.md` | open; solution/acceptance amended |
| #43 | `issues/p0-04.md` | open; existing task retained |
| #44 | `issues/p5-07.md` | open; existing task retained |
| #45 | `issues/p4-06.md` | open; existing task retained |
| #46 | `issues/p3-09.md` | open; existing task retained |
| #47 | `issues/p2-06.md` | open; existing task retained |
| #48 | `issues/p5-08.md` | open; existing task retained |
| #49 | `issues/p0-05.md` | open; existing task retained |
| #50 | `issues/p3-10.md` | open; existing task retained |
| #51 | `issues/p4-07.md` | open; existing task retained |
| #52 | `issues/p5-09.md` | open; solution/acceptance amended |
| #53 | `issues/p2-07.md` | open; existing task retained |
| #54 | `issues/p1-05.md` | open; solution/acceptance amended |
| #55 | `issues/p4-08.md` | open; existing task retained |
| #56 | `issues/p0-06.md` | open; existing task retained |
| #57 | `issues/p3-11.md` | open; existing task retained |
| #58 | `issues/p5-10.md` | open; existing task retained |
| #59 | `issues/p2-08.md` | open; existing task retained |
| #60 | `issues/p1-06.md` | open; existing task retained |
| #61 | `issues/p3-12.md` | open; existing task retained |
| #62 | `issues/p5-11.md` | open; existing task retained |
| #63 | `issues/p0-07.md` | open; solution/acceptance amended |
| #64 | `issues/p4-09.md` | open; existing task retained |
| #65 | `issues/p2-09.md` | open; existing task retained |
| #66 | `issues/p3-13.md` | open; existing task retained |
| #67 | `issues/p5-12.md` | open; existing task retained |
| #68 | `issues/p4-10.md` | open; existing task retained |
| #69 | `issues/p3-14.md` | open; existing task retained |
| #70 | `issues/p1-07.md` | open; existing task retained |
| #71 | `issues/p0-08.md` | open; solution/acceptance amended |
| #72 | `issues/p5-13.md` | open; existing task retained |
| #73 | `issues/p2-10.md` | open; existing task retained |
| #74 | `issues/p3-15.md` | open; existing task retained |
| #75 | `issues/p4-11.md` | open; existing task retained |
| #76 | `issues/p5-14.md` | open; existing task retained |
| #77 | `issues/p0-09.md` | open; solution/acceptance amended |
| #78 | `issues/p1-08.md` | open; existing task retained |
| #79 | `issues/p2-11.md` | open; existing task retained |
| #80 | `issues/p3-16.md` | open; existing task retained |
| #81 | `issues/p5-15.md` | open; existing task retained |
| #82 | `issues/p4-12.md` | open; existing task retained |
| #83 | `issues/p0-10.md` | open; solution/acceptance amended |
| #84 | `issues/p1-09.md` | open; existing task retained |
| #85 | `issues/p3-17.md` | open; existing task retained |
| #86 | `issues/p5-16.md` | open; existing task retained |
| #87 | `issues/p2-12.md` | open; existing task retained |
| #88 | `issues/p4-13.md` | open; solution/acceptance amended |
| #89 | `issues/p0-11.md` | open; solution/acceptance amended |
| #90 | `issues/p3-18.md` | open; solution/acceptance amended |
| #91 | `issues/p5-17.md` | open; existing task retained |
| #92 | `issues/p1-10.md` | open; existing task retained |
| #93 | `issues/p2-13.md` | open; existing task retained |
| #94 | `issues/p6-01.md` | open; existing task retained |
| #95 | `issues/p3-19.md` | open; existing task retained |
| #96 | `issues/p5-18.md` | open; existing task retained |
| #97 | `issues/p0-12.md` | open; existing task retained |
| #98 | `issues/p1-11.md` | open; solution/acceptance amended |
| #99 | `issues/p6-02.md` | open; existing task retained |
| #100 | `issues/p2-14.md` | open; solution/acceptance amended |
| #101 | `issues/p5-19.md` | open; existing task retained |
| #102 | `issues/p3-20.md` | open; existing task retained |
| #103 | `issues/p6-03.md` | open; existing task retained |
| #104 | `issues/p0-13.md` | open; existing task retained |
| #105 | `issues/p1-12.md` | open; solution/acceptance amended |
| #106 | `issues/p2-15.md` | open; existing task retained |
| #107 | `issues/p5-20.md` | open; existing task retained |
| #108 | `issues/p3-21.md` | open; existing task retained |
| #109 | `issues/p6-04.md` | open; existing task retained |
| #110 | `issues/p0-14.md` | open; solution/acceptance amended |
| #111 | `issues/p3-22.md` | open; existing task retained |
| #112 | `issues/p6-05.md` | open; existing task retained |
| #113 | `issues/p1-13.md` | open; existing task retained |
| #114 | `issues/p5-21.md` | open; existing task retained |
| #115 | `issues/p2-16.md` | open; solution/acceptance amended |
| #116 | `issues/p3-23.md` | open; existing task retained |
| #117 | `issues/p0-15.md` | open; solution/acceptance amended |
| #118 | `issues/p6-06.md` | open; solution/acceptance amended |
| #119 | `issues/p5-22.md` | open; solution/acceptance amended |
| #120 | `issues/p1-14.md` | open; existing task retained |
| #121 | `issues/p3-24.md` | open; solution/acceptance amended |
| #122 | `issues/p6-07.md` | open; existing task retained |
| #123 | `issues/p5-23.md` | open; existing task retained |
| #124 | `issues/p0-16.md` | open; solution/acceptance amended |
| #125 | `issues/p2-17.md` | open; solution/acceptance amended |
| #126 | `issues/p1-15.md` | open; existing task retained |
| #127 | `issues/p0-17.md` | open; solution/acceptance amended |
| #128 | `issues/p2-18.md` | open; solution/acceptance amended |
| #129 | `issues/p1-16.md` | open; existing task retained |
| #130 | `issues/p2in-01.md` | open; existing task retained |
| #131 | `issues/p6-08.md` | open; solution/acceptance amended |
| #132 | `issues/p2-19.md` | open; existing task retained |
| #133 | `issues/p1-17.md` | open; existing task retained |
| #134 | `issues/p6-09.md` | open; solution/acceptance amended |
| #135 | `issues/p2in-02.md` | open; existing task retained |
| #136 | `issues/p2-20.md` | open; existing task retained |
| #137 | `issues/p1-18.md` | open; solution/acceptance amended |
| #138 | `issues/p6-10.md` | open; existing task retained |
| #139 | `issues/p1-19.md` | open; existing task retained |
| #140 | `issues/p2in-03.md` | open; existing task retained |
| #141 | `issues/p2-21.md` | open; existing task retained |
| #142 | `issues/p6-11.md` | open; existing task retained |
| #143 | `issues/p2-22.md` | open; existing task retained |
| #144 | `issues/p6-12.md` | open; existing task retained |
| #145 | `issues/p1-20.md` | open; solution/acceptance amended |
| #146 | `issues/p2-23.md` | open; solution/acceptance amended |
| #147 | `issues/p2in-04.md` | open; existing task retained |
| #148 | `issues/p1-21.md` | open; existing task retained |
| #149 | `issues/p2-24.md` | open; existing task retained |
| #150 | `issues/p2-25.md` | open; solution/acceptance amended |
| #151 | `issues/p2-26.md` | open; existing task retained |
| #152 | `issues/p2-27.md` | open; existing task retained |
| #153 | `issues/p2-28.md` | open; solution/acceptance amended |
| #154 | `issues/p2-29.md` | open; existing task retained |
