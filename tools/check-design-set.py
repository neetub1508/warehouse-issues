#!/usr/bin/env python3
"""
Design-set integrity checker — Classic Warehouse.

`DECISIONS.md` §7 rule 3 is the whole reason this file exists:

    Every cross-reference must resolve. `FR-nnn` to a real requirement, `WH-SC-nnn` to a
    real scenario, a table name to a row in `DATA-MODEL.md`, an issue `#NN` to a row in
    `issues/CREATED.md`, a migration number to exactly one task inside its module's band.
    `tools/check-design-set.py` enforces all of it.

The design set is prose, but it is built from as if it were a schema. `DATA-MODEL.md` is the
migration authority, `## Scope` is the build list, and `FR-nnn` / `WH-SC-nnn` citations are the
acceptance contract. A dangling reference makes a live gap read as *closed*. The accounting
programme carried 25 dangling `FR` citations of which **19 resolved to a different real
requirement** — plausible, greppable, and wrong. A Flyway version claimed by two tasks is not a
lint warning, it is a boot failure.

Checks
   1  every FR-nnn cited anywhere resolves to a requirement in the FRD
   2  every WH-SC-nnn cited anywhere resolves to a scenario in the catalogue
   3  every whb_/wh_/wh3_/whin_/wha*_ table named in a task file appears in DATA-MODEL.md
   4  every Flyway version is claimed by exactly one task, inside its module's declared band
   5  every #NN issue cross-reference resolves to a row in issues/CREATED.md
   6  every task file carries the six required sections
   7  every finding id cited (round 1 C/T/E/F/S/P/G, round 2 Q/H/U/Y/Z/K/O/J) resolves to a
      real finding in its owning review
   8  every task in IMPLEMENTATION-PLAN.md §2 has a file, and every file is in the plan
   9  every task appears in exactly one phase epic's __TASKS__ / checklist region
  10  every FR-nnn is owned by exactly one task
  11  no id is used for two different kinds of thing
  12  every screen id (WS-nnn) cited resolves to BUILD-SPEC-SCREENS.md

Self-declared exemptions
  Some citations are *deliberately* unresolvable and reporting them buries the live defects and
  gets the check switched off. A forward reference to the next free id ("new ids continue from
  `WH-SC-301`") is the canonical case; so is a dated record that names a dropped id on purpose.

  Nothing is ever exempt **by path**. A document exempts itself, in the open, with an HTML
  comment, and every run — `--summary` included — prints how many mentions each declaration
  swallowed:

      <!-- check-design-set: <rule> file [ID ...] — why -->
      <!-- check-design-set: <rule> begin [ID ...] — why -->
      ...
      <!-- check-design-set: <rule> end -->

  `file` scopes the exemption to the whole document, `begin`/`end` to a region. Naming ids on the
  fence narrows it to exactly those, so one fence can cover a whole table while a *new* dangling
  id in that same table still fails. Rules: fr-citations (1) · scenario-citations (2) ·
  table-names (3) · flyway-band (4) · finding-citations (7) · id-collision (11) ·
  screen-citations (12).

  Three guard rails stop a declaration rotting into a blanket: an unterminated `begin` is itself a
  violation, a declaration that exempts nothing is reported as stale, and `--show-exempt` lists
  every exempted mention with its file:line and stated reason.

Usage
  tools/check-design-set.py                 full report, one line per violation
  tools/check-design-set.py --summary       counts only
  tools/check-design-set.py --check 4       run one check (repeatable)
  tools/check-design-set.py --show-exempt   list every exempted mention
  tools/check-design-set.py --root PATH     check a different checkout

Exit status: 0 clean, 1 violations found, 2 bad invocation or a missing authority file.
Python 3 standard library only, by design: the repo has no build tooling and CI must be able to
run this with a bare `python3`.
"""

import argparse
import os
import re
import sys

# --------------------------------------------------------------------------
# authorities — DECISIONS.md §6 names each of these
# --------------------------------------------------------------------------

FRD = "docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md"
SCENARIOS = "docs/SCENARIO-CATALOGUE.md"
DATA_MODEL = "docs/DATA-MODEL.md"
SCREENS = "docs/BUILD-SPEC-SCREENS.md"
PLAN = "docs/IMPLEMENTATION-PLAN.md"
DECISIONS = "docs/DECISIONS.md"
IRREVERSIBLE = "docs/IRREVERSIBLE.md"
ISSUE_MAP = "issues/CREATED.md"

REVIEWS = {
    "C": "docs/reviews/R1-codebase-reality.md",
    "T": "docs/reviews/R2-tier1-wms-audit.md",
    "E": "docs/reviews/R3-erp-midmarket-audit.md",
    "F": "docs/reviews/R4-fulfilment-3pl-audit.md",
    "S": "docs/reviews/R5-standards-industry-ops.md",
    "P": "docs/reviews/R6-prior-art-triage.md",
    "G": "docs/reviews/R7-logistics-supply-chain-seam.md",
    # round 2 — the eight orthogonal lenses. Prefixes were grep-verified free of the round-1
    # registers before allocation; `O-` is deliberately distinct from the `OD-n` open-decision
    # register, which FINDING_CITE_RE's letter-then-hyphen shape cannot match.
    "Q": "docs/reviews/R8-task-buildability-v1.md",
    "H": "docs/reviews/R9-task-buildability-v2-and-epics.md",
    "U": "docs/reviews/R10-operational-walkthrough.md",
    "Y": "docs/reviews/R11-exception-and-unhappy-paths.md",
    "Z": "docs/reviews/R12-lifecycle-and-data-migration.md",
    "K": "docs/reviews/R13-non-functional-and-operability.md",
    "O": "docs/reviews/R14-codebase-and-sibling-set-reverification.md",
    "J": "docs/reviews/R15-competitor-benchmark-r2.md",
    # round 3 — six orthogonal lenses. The single-letter space was exhausted at allocation time:
    # `M` alone was free (`R-1`…`R-5` are DATA-MODEL.md rounding rules, `V-3` and `W-n` are live
    # registers, `B-04` is a rack label in R2 and `N-045` a citation into the accounting set), so
    # round 3 takes a two-letter register. `RA`…`RF` were grep-verified free of the whole tree
    # before allocation and stay unambiguous under the same letter-then-hyphen rule that separates
    # `O-` from `OD-`.
    "RA": "docs/reviews/R16-role-and-persona-completeness.md",
    "RB": "docs/reviews/R17-screen-and-field-buildability.md",
    "RC": "docs/reviews/R18-reporting-and-analytics-completeness.md",
    "RD": "docs/reviews/R19-integration-device-and-channel-surface.md",
    "RE": "docs/reviews/R20-configuration-and-day-one-setup.md",
    "RF": "docs/reviews/R21-money-costing-and-billing.md",
}

# Each review anchors its findings differently. These are the *definition* anchors, not citations:
# a finding is defined where its register declares it, and nowhere else.
FINDING_DEF_RE = {
    "C": re.compile(r"^\|\s*\*\*C-(\d{3})\*\*\s*\|"),
    "T": re.compile(r"^###\s+T-(\d{3}[a-z]?)\s"),
    "E": re.compile(r"^\*\*E-(\d{3})\s*·"),
    "F": re.compile(r"^###\s+`F-(\d{3})`"),
    "S": re.compile(r"^\|\s*\*\*S-(\d{3})\*\*\s*\|"),
    "P": re.compile(r"^###\s+`P-(\d{3})`"),
    "G": re.compile(r"^\*\*`G-(\d{3})`\s*·"),
    # The eight round-2 lenses were authored against one shared brief and share one anchor.
    "Q": re.compile(r"^###\s+`Q-(\d{3})`"),
    "H": re.compile(r"^###\s+`H-(\d{3})`"),
    "U": re.compile(r"^###\s+`U-(\d{3})`"),
    "Y": re.compile(r"^###\s+`Y-(\d{3})`"),
    "Z": re.compile(r"^###\s+`Z-(\d{3})`"),
    "K": re.compile(r"^###\s+`K-(\d{3})`"),
    "O": re.compile(r"^###\s+`O-(\d{3})`"),
    "J": re.compile(r"^###\s+`J-(\d{3})`"),
    # The six round-3 lenses share one anchor, as round 2's eight do.
    "RA": re.compile(r"^###\s+`RA-(\d{3})`"),
    "RB": re.compile(r"^###\s+`RB-(\d{3})`"),
    "RC": re.compile(r"^###\s+`RC-(\d{3})`"),
    "RD": re.compile(r"^###\s+`RD-(\d{3})`"),
    "RE": re.compile(r"^###\s+`RE-(\d{3})`"),
    "RF": re.compile(r"^###\s+`RF-(\d{3})`"),
}
REVIEW_LABEL = {
    "C": "R1 codebase reality", "T": "R2 tier-1 WMS", "E": "R3 ERP / mid-market",
    "F": "R4 fulfilment / 3PL", "S": "R5 standards / statute", "P": "R6 prior art",
    "G": "R7 logistics seam",
    "Q": "R8 task buildability v1", "H": "R9 task buildability v2 / epics",
    "U": "R10 operational walkthrough", "Y": "R11 exception paths",
    "Z": "R12 lifecycle / data migration", "K": "R13 non-functional",
    "O": "R14 codebase / sibling re-verify", "J": "R15 competitor round 2",
    "RA": "R16 role & persona", "RB": "R17 screen & field buildability",
    "RC": "R18 reporting & analytics", "RD": "R19 integration, device & channel",
    "RE": "R20 configuration & day-1 setup", "RF": "R21 money, costing & billing",
}

# R1 §8's traps are a *second* register under the same `T-` prefix, separated from R2's findings
# by zero-padding alone. DECISIONS.md §7 rule 4a names this as a known hazard; check 11 asserts it
# stays separated and check 7 resolves each register against its own authority.
R1_TRAP_DEF_RE = re.compile(r"^\|\s*T-(\d{1,2})\s*\|")

# Flyway bands — DECISIONS.md §2 D-2. Disjoint and contiguous, unlike accounting's nested
# India carve-out. Every adapter shares one band, sub-allocated per adapter.
BANDS = {
    "warehouse-base": (500000, 509999),
    "warehouse": (510000, 519999),
    "warehouse-adapter": (520000, 529999),
    "warehouse-3pl": (530000, 539999),
    "warehouse-india": (540000, 549999),
}
# Named on a task header but carrying no band of their own. Declaring one of these alongside a
# banded module is normal (a task edits `platform` registries too); declaring *only* one of these
# while claiming a version is a defect, because no band authorises the number.
UNBANDED_MODULES = ("platform", "mobile", "logistics", "—", "-")

TASK_FILE_RE = re.compile(r"^p([0-6])(in)?-(\d{2})\.md$")
PHASE_EPIC = {
    "P0": "issues/01-EPIC-p0.md",
    "P1": "issues/02-EPIC-p1.md",
    "P2": "issues/03-EPIC-p2.md",
    "P2-IN": "issues/04-EPIC-p2in.md",
    "P3": "issues/05-EPIC-p3.md",
    "P4": "issues/06-EPIC-p4.md",
    "P5": "issues/07-EPIC-p5.md",
    "P6": "issues/08-EPIC-p6.md",
}

# --- citation and definition patterns -------------------------------------
FR_CITE_RE = re.compile(r"\bFR-(\d+)\b")
FR_DEF_RE = re.compile(r"^\|\s*\*\*FR-(\d{3})\*\*\s*\|")
SC_CITE_RE = re.compile(r"\bWH-SC-(\d+)\b")
SC_DEF_RE = re.compile(r"^\|\s*\*\*WH-SC-(\d{3})\*\*")
WS_CITE_RE = re.compile(r"\bWS-(\d+)\b")
WS_DEF_RE = re.compile(r"^\|\s*WS-(\d{3})\s*\|")
TABLE_RE = re.compile(r"\b(?:whb|wh3|whin|wha[a-z]|wh)_[a-z0-9_]+\b")
FINDING_CITE_RE = re.compile(r"\b(R[A-F]|[CTEFSPGQHUYZKOJ])-(\d{1,3}[a-z]?)\b(?!-\d)")
ISSUE_CITE_RE = re.compile(r"(?<![\w/#])#(\d{1,4})\b")
PR_REF_RE = re.compile(r"(?:\bPR|\bpull request)\s*#\d{1,4}\b", re.IGNORECASE)
ISSUE_MAP_ROW_RE = re.compile(r"^\|\s*#(\d+)\s*\|\s*`([^`]+)`")
VERSION_RE = re.compile(r"\bV(\d{6})\b")
VERSION_RANGE_RE = re.compile(r"V(\d{6})`?\s*[\u2013\u2014-]\s*`?V?(\d{6})")
TASK_ID_RE = re.compile(r"\bP([0-6])(?:-IN)?-(\d{2})\b")
PLAN_ROW_RE = re.compile(r"^\|\s*\*\*(P[0-6](?:-IN)?-\d{2})\*\*\s*\|")
EPIC_CHECK_RE = re.compile(r"^-\s*\[[ xX]\]\s*\**\s*`?\s*(P[0-6](?:-IN)?-\d{2})\b")
HEADING_RE = re.compile(r"^#{2,3}\s+(.*)$")

REQUIRED_SECTIONS = (
    "Scope", "Requirements closed", "Scenarios closed", "Closes", "Traps", "Acceptance",
)

CHECK_TITLES = {
    1: "FR-nnn citations resolve to the FRD",
    2: "WH-SC-nnn citations resolve to the scenario catalogue",
    3: "warehouse tables in task files appear in DATA-MODEL.md",
    4: "Flyway versions: claimed once, inside the module band",
    5: "#NN issue cross-references resolve to issues/CREATED.md",
    6: "task files carry the six required sections",
    7: "finding ids resolve to a real finding in their owning review",
    8: "IMPLEMENTATION-PLAN.md §2 and issues/ agree on the task list",
    9: "every task sits in exactly one phase epic's task region",
    10: "every FR-nnn is owned by exactly one task",
    11: "no id is used for two different kinds of thing",
    12: "WS-nnn citations resolve to BUILD-SPEC-SCREENS.md",
}

# rule name -> the check it exempts. A directive naming any other rule is a violation of the
# check it claims, so a typo cannot silently exempt nothing.
EXEMPT_RULES = {
    "fr-citations": 1,
    "scenario-citations": 2,
    "table-names": 3,
    "flyway-band": 4,
    "issue-citations": 5,
    "finding-citations": 7,
    "id-collision": 11,
    "screen-citations": 12,
}
# How a rule recognises the ids named on its own fence.
RULE_TOKEN_RE = {
    "fr-citations": re.compile(r"\bFR-\d+\b"),
    "scenario-citations": re.compile(r"\bWH-SC-\d+\b"),
    "table-names": TABLE_RE,
    "flyway-band": re.compile(r"\bV\d{6}\b"),
    "issue-citations": ISSUE_CITE_RE,
    "finding-citations": re.compile(r"\b(?:R[A-F]|[CTEFSPGQHUYZKOJ])-\d{1,3}[a-z]?\b"),
    "id-collision": re.compile(r"\b[A-Z][A-Z-]*-\d+[a-z]?\b"),
    "screen-citations": re.compile(r"\bWS-\d+\b"),
}

DIRECTIVE_RE = re.compile(
    r"<!--\s*check-design-set:\s*([a-z][a-z-]*)\s+(file|begin|end)\b(.*?)-->",
    re.IGNORECASE | re.DOTALL)


class Violation:
    def __init__(self, check, path, line, message):
        self.check = check
        self.path = path
        self.line = line
        self.message = message

    def render(self):
        return "%s:%d: [check-%d] %s" % (self.path, self.line, self.check, self.message)

    def key(self):
        return (self.path, self.line, self.message)


# --------------------------------------------------------------------------
# repository access
# --------------------------------------------------------------------------

def die(message):
    sys.stderr.write("check-design-set: %s\n" % message)
    sys.exit(2)


_CACHE = {}


def read_lines(root, relpath):
    key = (root, relpath)
    if key in _CACHE:
        return _CACHE[key]
    full = os.path.join(root, relpath)
    if not os.path.exists(full):
        die("missing authority file: %s" % relpath)
    with open(full, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    _CACHE[key] = lines
    return lines


def exists(root, relpath):
    return os.path.exists(os.path.join(root, relpath))


# `tools/` holds this checker and its documentation, not the design set. It is skipped so the
# directive examples in tools/README.md stay examples: a checker must not be able to exempt itself.
SKIP_DIRS = (".git", ".github", "node_modules", "tools")


def markdown_files(root):
    """Every design-set .md file, repo-relative, sorted. `anywhere` means anywhere."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".md"):
                found.append(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(found)


def task_files(root):
    issues = os.path.join(root, "issues")
    if not os.path.isdir(issues):
        die("missing issues/ directory")
    out = sorted(n for n in os.listdir(issues) if TASK_FILE_RE.match(n))
    if not out:
        die("no task files (issues/pN-nn.md) found — the parser is out of date")
    return [os.path.join("issues", n) for n in out]


def task_id(relpath):
    """issues/p2in-03.md -> P2-IN-03 ; issues/p0-02.md -> P0-02"""
    m = TASK_FILE_RE.match(os.path.basename(relpath))
    return "P%s%s-%s" % (m.group(1), "-IN" if m.group(2) else "", m.group(3))


def phase_of(task):
    return task.rsplit("-", 1)[0]


def strip_code(text):
    """Drop inline code spans so `#77` in prose is not read as issue #77."""
    return re.sub(r"`[^`]*`", " ", text)


def iter_lines(lines):
    """Yield (lineno, text, in_code_block) for every line.

    A citation inside a fenced block is a command or an example, not a reference. There is exactly
    one copy of this walker and every citation check uses it.
    """
    fenced = False
    for lineno, text in enumerate(lines, 1):
        if text.lstrip().startswith("```"):
            fenced = not fenced
            yield lineno, text, True
            continue
        yield lineno, text, fenced


def defined_ints(lines, pattern):
    out = set()
    for line in lines:
        m = pattern.match(line)
        if m:
            out.add(int(m.group(1)))
    return out


def collapse(values):
    """[1,2,3,7] -> [(1,3),(7,7)] so a 50-version range is one violation line."""
    runs = []
    for v in sorted(values):
        if runs and v == runs[-1][1] + 1:
            runs[-1][1] = v
        else:
            runs.append([v, v])
    return [(lo, hi) for lo, hi in runs]


def span(lo, hi):
    return "V%d" % lo if lo == hi else "V%d-V%d" % (lo, hi)


# --------------------------------------------------------------------------
# the exemption engine — one grammar, seven rules, nothing exempt by path
# --------------------------------------------------------------------------

class ExemptionLedger:
    """What the checks chose not to report, and on whose authority.

    A silent exemption is how a checker rots, so every count here is printed on every run —
    `--summary` included — and a declaration that suppresses nothing is called out so a stale
    fence gets removed instead of quietly widening.
    """

    def __init__(self):
        self.by_rule = {}          # rule -> mentions swallowed
        self.sources = {}          # (rule, path, anchor) -> count
        self.mentions = []         # (path, lineno, token, rule, reason)
        self.declarations = []     # (rule, path, lineno, reason)

    def record(self, path, lineno, token, rule, anchor, reason):
        self.by_rule[rule] = self.by_rule.get(rule, 0) + 1
        key = (rule, path, anchor)
        self.sources[key] = self.sources.get(key, 0) + 1
        self.mentions.append((path, lineno, token, rule, reason))

    def declare(self, rule, path, lineno, reason):
        self.declarations.append((rule, path, lineno, reason))

    def total_for(self, check):
        rules = [r for r, c in EXEMPT_RULES.items() if c == check]
        return sum(self.by_rule.get(r, 0) for r in rules) + self.by_rule.get(
            "code-block/%d" % check, 0)

    def stale(self, check):
        """Declarations for this check that exempted nothing — remove them."""
        used = set(self.sources)
        out = []
        for rule, path, lineno, reason in self.declarations:
            if EXEMPT_RULES.get(rule) != check:
                continue
            if (rule, path, lineno) not in used:
                out.append((rule, path, lineno, reason))
        return sorted(out, key=lambda d: (d[1], d[2]))

    def summary_line(self, check):
        parts = []
        for rule in sorted(EXEMPT_RULES):
            if EXEMPT_RULES[rule] != check:
                continue
            count = self.by_rule.get(rule, 0)
            if not count:
                continue
            anchors = len([1 for (r, _p, _a) in self.sources if r == rule])
            wheres = len(set(p for (r, p, _a) in self.sources if r == rule))
            parts.append("%s %d (%d declaration%s in %d file%s)"
                         % (rule, count, anchors, "" if anchors == 1 else "s",
                            wheres, "" if wheres == 1 else "s"))
        blocks = self.by_rule.get("code-block/%d" % check, 0)
        if blocks:
            parts.append("code-block %d" % blocks)
        if not parts:
            return "exempt 0 mentions — nothing declares an exemption for this check"
        total = self.total_for(check)
        return ("exempt %d mention%s — %s"
                % (total, "" if total == 1 else "s", " · ".join(parts)))

    def sources_for(self, check):
        out = []
        for (rule, path, anchor), count in self.sources.items():
            if EXEMPT_RULES.get(rule) == check:
                out.append((path, anchor, rule, count))
        return sorted(out)


class FileExemptions:
    """The directives one file declares, parsed once and shared by every check."""

    def __init__(self, lines):
        self.file_scope = {}   # rule -> (lineno, ids or None, reason)
        self.regions = {}      # rule -> [(begin, end, ids or None, reason)]
        self.errors = []       # (lineno, rule, message)
        self.declaration_lines = set()
        open_at = {}
        for lineno, text, in_code in iter_lines(lines):
            if in_code:
                continue
            for m in DIRECTIVE_RE.finditer(text):
                rule, scope, body = m.group(1).lower(), m.group(2).lower(), m.group(3)
                self.declaration_lines.add(lineno)
                if rule not in EXEMPT_RULES:
                    self.errors.append((lineno, rule,
                                        "unknown exemption rule `%s` — known rules are %s"
                                        % (rule, ", ".join(sorted(EXEMPT_RULES)))))
                    continue
                ids, reason = self._split(rule, body)
                if scope == "file":
                    if rule in self.file_scope:
                        self.errors.append((lineno, rule,
                                            "a second `%s file` declaration; the first is at line %d"
                                            % (rule, self.file_scope[rule][0])))
                    else:
                        self.file_scope[rule] = (lineno, ids, reason)
                elif scope == "begin":
                    if rule in open_at:
                        self.errors.append((lineno, rule,
                                            "a `%s begin` fence is already open at line %d — "
                                            "nested fences are not allowed" % (rule, open_at[rule][0])))
                    else:
                        open_at[rule] = (lineno, ids, reason)
                else:  # end
                    if rule not in open_at:
                        self.errors.append((lineno, rule,
                                            "`%s end` with no matching `begin`" % rule))
                    else:
                        begin, ids0, reason0 = open_at.pop(rule)
                        self.regions.setdefault(rule, []).append((begin, lineno, ids0, reason0))
        for rule, (begin, _ids, _reason) in open_at.items():
            self.errors.append((begin, rule,
                                "`%s begin` is never closed — an unterminated fence would exempt "
                                "the rest of the file" % rule))

    @staticmethod
    def _split(rule, body):
        token_re = RULE_TOKEN_RE[rule]
        ids = set(m.group(0) for m in token_re.finditer(body))
        reason = token_re.sub(" ", body)
        reason = reason.replace("`", " ").strip(" -–—\t")
        reason = re.sub(r"\s+", " ", reason) or "no reason given"
        if ids:
            reason = "%s [%s]" % (reason, " ".join(sorted(ids)))
        return (ids or None), reason

    def declared(self, ledger, path):
        for rule, (lineno, _ids, reason) in self.file_scope.items():
            ledger.declare(rule, path, lineno, reason)
        for rule, regions in self.regions.items():
            for begin, _end, _ids, reason in regions:
                ledger.declare(rule, path, begin, reason)

    def cover(self, rule, lineno, token):
        """(anchor, reason) if this rule exempts `token` at `lineno`, else None."""
        got = self.file_scope.get(rule)
        if got is not None:
            anchor, ids, reason = got
            if ids is None or token in ids:
                return anchor, reason
        for begin, end, ids, reason in self.regions.get(rule, ()):
            if begin <= lineno <= end and (ids is None or token in ids):
                return begin, reason
        return None


class DirectiveIndex:
    """Every design-set file's directives, parsed once, before any check runs.

    Parsing is global rather than per check so a malformed fence is reported exactly once and
    wherever it sits — including in a document that the check it names does not otherwise scan. A
    directive that does not parse is a build failure in its own right: an unterminated fence would
    otherwise exempt the rest of a file silently.
    """

    def __init__(self, root, files, ledger):
        self.root = root
        self.ledger = ledger
        self.by_path = {}
        self.errors = []
        for path in files:
            fe = FileExemptions(read_lines(root, path))
            fe.declared(ledger, path)
            self.by_path[path] = fe
            for lineno, rule, message in fe.errors:
                self.errors.append((path, lineno, rule, message))
        self.errors.sort()

    def get(self, path):
        if path not in self.by_path:
            fe = FileExemptions(read_lines(self.root, path))
            fe.declared(self.ledger, path)
            self.by_path[path] = fe
        return self.by_path[path]


class Scanner:
    """Walks a file set once, applying one rule's exemptions as it goes."""

    def __init__(self, root, files, ledger, directives):
        self.root = root
        self.files = files
        self.ledger = ledger
        self.directives = directives

    def exemptions(self, path):
        return self.directives.get(path)

    def scan(self, check, rule, token_re, is_bad, message):
        """Report every match of `token_re` that `is_bad` rejects and no directive covers."""
        out = []
        for path in self.files:
            fe = self.exemptions(path)
            for lineno, text, in_code in iter_lines(read_lines(self.root, path)):
                if lineno in fe.declaration_lines:
                    continue  # an id named on a fence is the fence's scope, not a citation
                for m in token_re.finditer(text):
                    token = m.group(0)
                    if not is_bad(m):
                        continue
                    if in_code:
                        self.ledger.record(path, lineno, token, "code-block/%d" % check, 0,
                                           "inside a fenced code block")
                        continue
                    cover = fe.cover(rule, lineno, token)
                    if cover is not None:
                        self.ledger.record(path, lineno, token, rule, cover[0], cover[1])
                        continue
                    out.append(Violation(check, path, lineno, message(m)))
        return sorted(out, key=lambda v: v.key())


# --------------------------------------------------------------------------
# check 1 / 2 / 12 — citation resolution against a single authority
# --------------------------------------------------------------------------

def check_fr(root, scanner):
    defined = defined_ints(read_lines(root, FRD), FR_DEF_RE)
    if not defined:
        die("no FR definitions found in %s — the parser is out of date" % FRD)
    out = scanner.scan(
        1, "fr-citations", FR_CITE_RE,
        lambda m: int(m.group(1)) not in defined,
        lambda m: "FR-%03d is cited but not defined in %s" % (int(m.group(1)), FRD))
    return sorted(out, key=lambda v: v.key())


def check_scenarios(root, scanner):
    defined = defined_ints(read_lines(root, SCENARIOS), SC_DEF_RE)
    if not defined:
        die("no WH-SC definitions found in %s — the parser is out of date" % SCENARIOS)
    out = scanner.scan(
        2, "scenario-citations", SC_CITE_RE,
        lambda m: int(m.group(1)) not in defined,
        lambda m: "WH-SC-%03d is cited but not defined in %s" % (int(m.group(1)), SCENARIOS))
    return sorted(out, key=lambda v: v.key())


def check_screens(root, scanner):
    defined = defined_ints(read_lines(root, SCREENS), WS_DEF_RE)
    if not defined:
        die("no WS definitions found in %s — the parser is out of date" % SCREENS)
    out = scanner.scan(
        12, "screen-citations", WS_CITE_RE,
        lambda m: int(m.group(1)) not in defined,
        lambda m: "WS-%03d is cited but has no row in %s §1" % (int(m.group(1)), SCREENS))
    return sorted(out, key=lambda v: v.key())


# --------------------------------------------------------------------------
# check 3 — tables named by tasks exist in the data model
# --------------------------------------------------------------------------

def check_tables(root, ledger, directives):
    known = set()
    for line in read_lines(root, DATA_MODEL):
        known.update(TABLE_RE.findall(line))
    if not known:
        die("no warehouse tables found in %s — the parser is out of date" % DATA_MODEL)
    files = task_files(root)
    scanner = Scanner(root, files, ledger, directives)
    out = []

    def bad(m):
        # `wh_orders:edit_after_release` is a permission string, not a table name.
        rest = m.string[m.end():]
        if rest.startswith(":"):
            return False
        return m.group(0) not in known

    out += scanner.scan(
        3, "table-names", TABLE_RE, bad,
        lambda m: "table `%s` is named here but absent from %s" % (m.group(0), DATA_MODEL))
    return sorted(out, key=lambda v: v.key())


# --------------------------------------------------------------------------
# check 4 — Flyway version ownership and bands
# --------------------------------------------------------------------------

def header_line(lines):
    """The `Part of … · Module … · Migrations … · Screens …` front-matter line of a task."""
    for lineno, text in enumerate(lines, 1):
        if text.startswith("Part of"):
            return lineno, text
    return None, None


MODULE_TOKEN_RE = re.compile(
    r"`(warehouse-adapter-[a-z-]+|warehouse-base|warehouse-3pl|warehouse-india|warehouse"
    r"|platform|mobile|logistics|[—-])`")


def declared_modules(header, at):
    """(banded modules, unbanded module names) named before the Migrations field."""
    modules, unbanded = set(), set()
    for m in MODULE_TOKEN_RE.finditer(header[:at]):
        name = m.group(1)
        if name.startswith("warehouse-adapter-"):
            modules.add("warehouse-adapter")
        elif name in BANDS:
            modules.add(name)
        elif name in UNBANDED_MODULES:
            unbanded.add(name)
        else:                       # unreachable while MODULE_TOKEN_RE lists the known names
            unbanded.add(name)
    return modules, unbanded


def migrations_field(header):
    """The Migrations field, bounded so a parenthetical after it is not read as a claim.

    `Migrations **—** (`whad_oem_orders` … already exist at `V520012`)` claims nothing: only the
    **bold** runs inside the field are claims, which is what the task files actually mean.
    """
    at = header.find("Migration")
    if at < 0:
        return None, None
    field = header[at:]
    cut = field.find("Screens")
    if cut >= 0:
        field = field[:cut]
    return at, field


def declared_versions(field):
    claims = set()
    for bold in re.finditer(r"\*\*(.+?)\*\*", field):
        seg = bold.group(1)
        for m in VERSION_RANGE_RE.finditer(seg):
            lo, hi = int(m.group(1)), int(m.group(2))
            if 0 <= hi - lo <= 5000:
                claims.update(range(lo, hi + 1))
            seg = seg.replace(m.group(0), " ")
        claims.update(int(m.group(1)) for m in VERSION_RE.finditer(seg))
    return claims


def check_flyway(root, ledger, directives):
    out, owners, offenders = [], {}, {}
    files = task_files(root)
    scanner = Scanner(root, files, ledger, directives)

    def flag(path, line, reason, version):
        offenders.setdefault((path, line, reason), []).append(version)

    for path in files:
        lines = read_lines(root, path)
        fe = scanner.exemptions(path)
        lineno, header = header_line(lines)
        if header is None:
            out.append(Violation(4, path, 1,
                                 "no `Part of …` header line — module and migrations undeclared"))
            continue
        at, field = migrations_field(header)
        if at is None:
            out.append(Violation(4, path, lineno,
                                 "the header line declares no `Migrations` field"))
            continue
        modules, unbanded = declared_modules(header, at)
        for version in sorted(declared_versions(field)):
            owners.setdefault(version, []).append((path, lineno))
            if any(BANDS[m][0] <= version <= BANDS[m][1] for m in modules):
                continue
            token = "V%d" % version
            cover = fe.cover("flyway-band", lineno, token)
            if cover is not None:
                ledger.record(path, lineno, token, "flyway-band", cover[0], cover[1])
                continue
            if not modules:
                flag(path, lineno,
                     "claimed but the header declares no banded module%s"
                     % ((" (found %s)" % ", ".join(sorted(unbanded))) if unbanded else ""),
                     version)
            else:
                flag(path, lineno,
                     "outside the band of its declared module%s: %s"
                     % ("s" if len(modules) > 1 else "",
                        ", ".join("%s V%d-V%d" % (m, BANDS[m][0], BANDS[m][1])
                                  for m in sorted(modules))),
                     version)

    for (path, lineno, reason), versions in offenders.items():
        for lo, hi in collapse(versions):
            out.append(Violation(4, path, lineno, "%s is %s" % (span(lo, hi), reason)))

    dupes = {}
    for version, claimants in owners.items():
        if len(claimants) > 1:
            for path, lineno in claimants[1:]:
                dupes.setdefault((path, lineno, tuple(claimants)), []).append(version)
    for (path, lineno, claimants), versions in dupes.items():
        who = ", ".join("%s:%d" % (p, l) for p, l in claimants)
        for lo, hi in collapse(versions):
            out.append(Violation(
                4, path, lineno,
                "%s is claimed by %d tasks (%s) — duplicate Flyway version, boot failure"
                % (span(lo, hi), len(claimants), who)))
    return sorted(out, key=lambda v: v.key())


def flyway_advisory(root):
    """Versions cited in a task *body* that no task header claims. Never fails the build — a body
    routinely cites a version another task owns — but a version claimed by nobody is a migration
    that has been designed and not assigned."""
    claimed = set()
    for path in task_files(root):
        _lineno, header = header_line(read_lines(root, path))
        if header:
            at, field = migrations_field(header)
            if at is not None:
                claimed.update(declared_versions(field))
    notes = set()
    for path in task_files(root):
        lines = read_lines(root, path)
        hdr_lineno, _ = header_line(lines)
        for lineno, text, in_code in iter_lines(lines):
            if lineno == hdr_lineno or in_code:
                continue
            # A range in a body is a band or a reserved gap being described, not a claim on a
            # file — `V500064`-`V500199` is "the next free block", not a migration anyone owns.
            body = VERSION_RANGE_RE.sub(" ", text)
            for m in VERSION_RE.finditer(body):
                v = int(m.group(1))
                if 500000 <= v <= 549999 and v not in claimed:
                    notes.add("%s:%d: V%d is cited but no task header claims it" % (path, lineno, v))
    return sorted(notes)


# --------------------------------------------------------------------------
# check 5 — issue cross-references
# --------------------------------------------------------------------------

def issue_map(root):
    mapping = {}
    for line in read_lines(root, ISSUE_MAP):
        m = ISSUE_MAP_ROW_RE.match(line)
        if m:
            mapping[int(m.group(1))] = m.group(2)
    if not mapping:
        die("no issue rows found in %s — the parser is out of date" % ISSUE_MAP)
    return mapping


def check_issue_refs(root, files, ledger, directives):
    """Skips cleanly, with a count, until the backlog is filed and CREATED.md exists.

    `#NN` is also how English writes an ordinal — *Refusal #2*, *Adapter #2*, *ship-blocker #2*,
    *the most important row in this table is #263* — and how markdown writes an in-page anchor
    (`[§9](#9--…)`). A design set that argues in prose therefore carries far more `#NN` tokens than
    it carries issue references, which is why this check answers to the `issue-citations` rule like
    every other check answers to its own: a document exempts itself, in the open, naming the ids.
    """
    if not exists(root, ISSUE_MAP):
        pending = 0
        for path in files:
            for lineno, text, in_code in iter_lines(read_lines(root, path)):
                if in_code:
                    continue
                scan = PR_REF_RE.sub(" ", strip_code(text))
                pending += len(ISSUE_CITE_RE.findall(scan))
        return [], ("%s does not exist yet — the backlog is unfiled. %d bare `#NN` mention%s "
                    "will become check-5 subjects the moment it does; most are document row "
                    "numbers, not issues. See tools/README.md."
                    % (ISSUE_MAP, pending, "" if pending == 1 else "s"))
    mapping = issue_map(root)
    scanner = Scanner(root, files, ledger, directives)
    out = []
    for path in files:
        fe = scanner.exemptions(path)
        for lineno, text, in_code in iter_lines(read_lines(root, path)):
            if lineno in fe.declaration_lines:
                continue  # an id named on a fence is the fence's scope, not a citation
            scan = PR_REF_RE.sub(" ", strip_code(text))
            for m in ISSUE_CITE_RE.finditer(scan):
                num = int(m.group(1))
                if num in mapping:
                    continue
                token = "#%d" % num
                if in_code:
                    ledger.record(path, lineno, token, "code-block/5", 0,
                                  "inside a fenced code block")
                    continue
                cover = fe.cover("issue-citations", lineno, token)
                if cover is not None:
                    ledger.record(path, lineno, token, "issue-citations", cover[0], cover[1])
                    continue
                out.append(Violation(
                    5, path, lineno,
                    "#%d is referenced but has no row in %s "
                    "(a cross-repo issue must be written owner/repo#%d)" % (num, ISSUE_MAP, num)))
    return sorted(out, key=lambda v: v.key()), None


# --------------------------------------------------------------------------
# check 6 — the six sections every task file must carry
# --------------------------------------------------------------------------

def check_sections(root):
    out = []
    for path in task_files(root):
        headings = []
        for _lineno, text, in_code in iter_lines(read_lines(root, path)):
            if in_code:
                continue
            m = HEADING_RE.match(text)
            if m:
                headings.append(m.group(1).strip())
        for want in REQUIRED_SECTIONS:
            hit = any(h == want or any(h.startswith(want + sep)
                                       for sep in (" ", "\u2014", "\u2013", ":", "-"))
                      for h in headings)
            if not hit:
                out.append(Violation(6, path, 1,
                                     "no `## %s` section — the task is not buildable from its file"
                                     % want))
    return sorted(out, key=lambda v: v.key())


# --------------------------------------------------------------------------
# check 7 — finding ids resolve, each against its own register
# --------------------------------------------------------------------------

def finding_registers(root):
    """{prefix: (set of ids, authority path, label)} plus the R1 §8 trap register."""
    reg = {}
    for prefix, path in sorted(REVIEWS.items()):
        ids = set()
        for line in read_lines(root, path):
            m = FINDING_DEF_RE[prefix].match(line)
            if m:
                ids.add(m.group(1))
        if not ids:
            die("no %s-nnn findings found in %s — the parser is out of date" % (prefix, path))
        reg[prefix] = (ids, path, REVIEW_LABEL[prefix])
    traps = set()
    for line in read_lines(root, REVIEWS["C"]):
        m = R1_TRAP_DEF_RE.match(line)
        if m:
            traps.add(m.group(1).lstrip("0") or "0")
    if not traps:
        die("no R1 §8 traps found in %s — the parser is out of date" % REVIEWS["C"])
    return reg, traps


def check_findings(root, scanner):
    reg, traps = finding_registers(root)

    def bad(m):
        prefix, num = m.group(1), m.group(2)
        if prefix == "T" and len(num) <= 2:
            return num.lstrip("0") not in traps
        if len(num) < 3:
            return True   # only `T-n` has a second, unpadded register
        return num not in reg[prefix][0]

    def message(m):
        prefix, num = m.group(1), m.group(2)
        if prefix == "T" and len(num) <= 2:
            return ("T-%s is cited as an R1 §8 trap but §8 defines only T-1…T-%d "
                    "(R2's findings are the zero-padded T-001…T-097)"
                    % (num, max(int(t) for t in traps)))
        if len(num) < 3:
            return ("%s is not a finding id — %s findings are three-digit (%s-001 …), and only "
                    "`T-n` has a second register" % (m.group(0), prefix, prefix))
        ids, path, label = reg[prefix]
        tail = ("" if prefix != "T" else
                " — an R2 capability-matrix row number reads exactly like a finding id, "
                "DECISIONS.md \u00a77 rule 4a")
        return ("%s is cited but not defined in %s (%s, %d findings)%s"
                % (m.group(0), path, label, len(ids), tail))

    out = scanner.scan(7, "finding-citations", FINDING_CITE_RE, bad, message)
    return sorted(out, key=lambda v: v.key())


# --------------------------------------------------------------------------
# check 8 — the plan's task list and the files agree
# --------------------------------------------------------------------------

def plan_rows(root):
    """{task id: (lineno, cells)} for every §2 task row."""
    lines = read_lines(root, PLAN)
    start = end = None
    for lineno, text in enumerate(lines, 1):
        if re.match(r"^##\s+2\.\s", text):
            start = lineno
        elif start and re.match(r"^##\s+3\.\s", text):
            end = lineno
            break
    if start is None:
        die("no `## 2. …` task-list section found in %s — the parser is out of date" % PLAN)
    end = end or len(lines) + 1
    rows = {}
    for lineno in range(start, end):
        text = lines[lineno - 1]
        m = PLAN_ROW_RE.match(text)
        if not m:
            continue
        cells = [c.strip() for c in text.strip().strip("|").split("|")]
        rows.setdefault(m.group(1), []).append((lineno, cells))
    if not rows:
        die("no task rows found in %s §2 — the parser is out of date" % PLAN)
    return rows, start


def check_plan(root):
    rows, section = plan_rows(root)
    files = {task_id(p): p for p in task_files(root)}
    out = []
    for task in sorted(set(rows) - set(files)):
        stem = task.lower().replace("-in-", "in-").replace("-", "-", 1)
        out.append(Violation(8, PLAN, rows[task][0][0],
                             "%s is listed in the plan but `issues/%s.md` does not exist"
                             % (task, stem)))
    for task in sorted(set(files) - set(rows)):
        out.append(Violation(8, files[task], 1,
                             "%s has a task file but no row in %s §2 — the plan is the build list"
                             % (task, PLAN)))
    for task, hits in sorted(rows.items()):
        if len(hits) > 1:
            for lineno, _cells in hits[1:]:
                out.append(Violation(8, PLAN, lineno,
                                     "%s has %d rows in §2; a task is listed once"
                                     % (task, len(hits))))
    return sorted(out, key=lambda v: v.key())


# --------------------------------------------------------------------------
# check 9 — every task sits in exactly one phase epic
# --------------------------------------------------------------------------

def check_epics(root):
    out = []
    files = {task_id(p): p for p in task_files(root)}
    by_phase = {}
    for task in files:
        by_phase.setdefault(phase_of(task), set()).add(task)

    listed = {}       # task -> [(epic, lineno)]
    for phase, epic in sorted(PHASE_EPIC.items()):
        if not exists(root, epic):
            out.append(Violation(9, "issues/", 1,
                                 "%s is missing — phase %s has no epic" % (epic, phase)))
            continue
        lines = read_lines(root, epic)
        placeholder, inline = [], []
        checklist = {}
        for lineno, text, in_code in iter_lines(lines):
            if in_code:
                continue
            if "__TASKS__" in text:
                if text.strip() == "__TASKS__":
                    placeholder.append(lineno)
                else:
                    inline.append((lineno, text.strip()))
            m = EPIC_CHECK_RE.match(text)
            if m:
                checklist.setdefault(m.group(1), []).append(lineno)
        for lineno, text in inline:
            out.append(Violation(
                9, epic, lineno,
                "`__TASKS__` shares its line with other content (`%s`) — create-issues.sh "
                "substitutes a multi-line checklist here and corrupts the heading; put the "
                "placeholder alone on its own line under a `## Tasks` heading"
                % (text[:48] + ("…" if len(text) > 48 else ""))))
        if not placeholder and not inline and not checklist:
            out.append(Violation(9, epic, 1,
                                 "no `__TASKS__` placeholder and no task checklist — phase %s's "
                                 "tasks are listed nowhere" % phase))
        for task, hits in sorted(checklist.items()):
            for lineno in hits:
                listed.setdefault(task, []).append((epic, lineno))
            if len(hits) > 1:
                out.append(Violation(9, epic, hits[1],
                                     "%s is listed %d times in this epic" % (task, len(hits))))
        if checklist:
            for task in sorted(by_phase.get(phase, ())):
                if task not in checklist:
                    out.append(Violation(9, epic, 1,
                                         "%s belongs to phase %s but is absent from this epic's "
                                         "checklist" % (task, phase)))

    for task, where in sorted(listed.items()):
        if task not in files:
            epic, lineno = where[0]
            out.append(Violation(9, epic, lineno,
                                 "%s is on this checklist but has no task file" % task))
            continue
        epics = sorted(set(e for e, _l in where))
        if len(epics) > 1:
            epic, lineno = where[-1]
            out.append(Violation(9, epic, lineno,
                                 "%s is listed by %d epics (%s) — a task belongs to one phase"
                                 % (task, len(epics), ", ".join(epics))))
        elif epics[0] != PHASE_EPIC.get(phase_of(task)):
            epic, lineno = where[0]
            out.append(Violation(9, epic, lineno,
                                 "%s is phase %s but is listed by %s"
                                 % (task, phase_of(task), epic)))
    return sorted(out, key=lambda v: v.key())


# --------------------------------------------------------------------------
# check 10 — every FR is owned by exactly one task
# --------------------------------------------------------------------------

def expand_frs(text):
    """`FR-371…FR-374` is four requirements, not two. Ranges first, then singletons."""
    out, rest = set(), text
    for m in re.finditer(r"FR-(\d{3})\s*(?:…|\.\.\.|–|—)\s*`?FR-(\d{3})", text):
        lo, hi = int(m.group(1)), int(m.group(2))
        if 0 <= hi - lo <= 200:
            out.update(range(lo, hi + 1))
        rest = rest.replace(m.group(0), " ")
    out.update(int(m.group(1)) for m in FR_CITE_RE.finditer(rest))
    return out


def requirements_block(lines):
    """The id list under `## Requirements closed` — the first paragraph, ids only.

    Prose after the blank line ("`FR-137` is multi-phase; `P5-09` builds the behaviour") is a
    cross-reference, not a claim of ownership, and must not be read as one. A first paragraph that
    opens in bold ("**None.** Deliberate") is a stated non-claim.
    """
    para, on, stated_none = [], False, False
    for lineno, text, in_code in iter_lines(lines):
        if in_code:
            continue
        m = HEADING_RE.match(text)
        if m:
            if m.group(1).strip().startswith("Requirements closed"):
                on = True
                continue
            if on:
                break
        if on:
            if not text.strip():
                break
            if text.lstrip().startswith("**"):
                if re.match(r"\*\*None\b", text.lstrip()):
                    stated_none = True
                break
            para.append((lineno, text))
    return para, stated_none


def check_ownership(root):
    defined = defined_ints(read_lines(root, FRD), FR_DEF_RE)
    rows, _section = plan_rows(root)
    out = []
    owned = {}
    for task, hits in sorted(rows.items()):
        lineno, cells = hits[0]
        if len(cells) < 6:
            out.append(Violation(10, PLAN, lineno,
                                 "%s's §2 row has %d cells; the `Closes` column is column 6"
                                 % (task, len(cells))))
            continue
        for fr in expand_frs(cells[5]):
            owned.setdefault(fr, []).append((task, lineno))

    for fr in sorted(defined - set(owned)):
        out.append(Violation(10, PLAN, _section,
                             "FR-%03d is defined in the FRD but no §2 task row closes it — "
                             "an unowned requirement is a gap that reads as covered" % fr))
    for fr in sorted(set(owned) - defined):
        task, lineno = owned[fr][0]
        out.append(Violation(10, PLAN, lineno,
                             "FR-%03d is claimed by %s but is not defined in %s" % (fr, task, FRD)))
    for fr, claims in sorted(owned.items()):
        if len(claims) > 1:
            task, lineno = claims[-1]
            out.append(Violation(
                10, PLAN, lineno,
                "FR-%03d is closed by %d tasks (%s) — plan §2 says every FR is owned by exactly one"
                % (fr, len(claims), ", ".join(t for t, _l in claims))))

    # The other direction: a task file claiming a requirement its plan row does not assign it.
    for path in task_files(root):
        task = task_id(path)
        block, stated_none = requirements_block(read_lines(root, path))
        if stated_none:
            block = []
        elif not block:
            out.append(Violation(10, path, 1,
                                 "%s has no id list under `## Requirements closed`" % task))
            continue
        anchor = block[0][0] if block else 1
        claimed = expand_frs(" ".join(t for _l, t in block))
        assigned = set(fr for fr, cl in owned.items() if any(t == task for t, _l in cl))
        extra = sorted(claimed - assigned)
        missing = sorted(assigned - claimed)
        if extra:
            out.append(Violation(
                10, path, block[0][0],
                "%s claims %s, which %s §2's `Closes` column does not assign to it"
                % (task, " ".join("FR-%03d" % v for v in extra), PLAN)))
        if missing:
            out.append(Violation(
                10, path, block[0][0],
                "%s §2 assigns %s to %s but the task file does not list %s"
                % (PLAN, " ".join("FR-%03d" % v for v in missing), task,
                   "it" if len(missing) == 1 else "them")))
    return sorted(out, key=lambda v: v.key())


# --------------------------------------------------------------------------
# check 11 — the id-collision guard
# --------------------------------------------------------------------------

def id_registers(root):
    """[(label, kind, authority, {token: first lineno}, probe prefix)] for every register the
    checker itself resolves. If it can resolve it, DECISIONS.md §6 must declare it."""
    reg = []

    def table(path, pattern, fmt, label, kind, probe):
        found = {}
        for lineno, text in enumerate(read_lines(root, path), 1):
            m = pattern.match(text)
            if m:
                found.setdefault(fmt(m), lineno)
        reg.append((label, kind, path, found, probe))

    table(FRD, FR_DEF_RE, lambda m: "FR-%03d" % int(m.group(1)),
          "requirements", "requirement", "FR-")
    table(SCENARIOS, SC_DEF_RE, lambda m: "WH-SC-%03d" % int(m.group(1)),
          "scenarios", "scenario", "WH-SC-")
    table(SCREENS, WS_DEF_RE, lambda m: "WS-%03d" % int(m.group(1)),
          "screens", "screen", "WS-")
    table(DATA_MODEL, re.compile(r"^\|\s*\*\*I-(\d{1,2})\*\*\s*\|"),
          lambda m: "I-%s" % m.group(1), "enforceable constraints", "constraint", "I-")
    table(IRREVERSIBLE, re.compile(r"^\|\s*\*\*`?IRR-(\d{2})`?\*\*\s*\|"),
          lambda m: "IRR-%s" % m.group(1), "irreversible rows", "irreversible row", "IRR-")
    table(DECISIONS, re.compile(r"^###\s+D-(\d{1,2})\s*[\u00b7:.]"),
          lambda m: "D-%s" % m.group(1), "decisions", "decision", "D-")
    table(DECISIONS, re.compile(r"^\|\s*\*\*OD-(\d{1,2})\*\*\s*\|"),
          lambda m: "OD-%s" % m.group(1), "open decisions", "open decision", "OD-")
    table(DECISIONS, re.compile(r"^\|\s*\*\*L-(\d{1,2})\*\*\s*\|"),
          lambda m: "L-%s" % m.group(1), "invariants", "invariant", "L-")
    for prefix, path in sorted(REVIEWS.items()):
        table(path, FINDING_DEF_RE[prefix], lambda m, p=prefix: "%s-%s" % (p, m.group(1)),
              "findings — %s" % REVIEW_LABEL[prefix], "finding", "%s-" % prefix)
    table(REVIEWS["C"], R1_TRAP_DEF_RE, lambda m: "T-%s" % m.group(1),
          "R1 §8 traps", "trap", "T-")
    tasks = {}
    for path in task_files(root):
        tasks[task_id(path)] = 1
    reg.append(("tasks", "task", "issues/pN-nn.md", tasks, "P"))
    return reg


def namespace_rows(root):
    """DECISIONS.md §6's table: [(lineno, namespace cell, authority cell)]."""
    lines = read_lines(root, DECISIONS)
    start = end = None
    for lineno, text in enumerate(lines, 1):
        if re.match(r"^##\s+6\.\s", text):
            start = lineno
        elif start and re.match(r"^##\s+7\.\s", text):
            end = lineno
            break
    if start is None:
        die("no `## 6. Id namespaces` section in %s — the parser is out of date" % DECISIONS)
    end = end or len(lines) + 1
    rows = []
    for lineno in range(start, end):
        cells = [c.strip() for c in lines[lineno - 1].strip().strip("|").split("|")]
        if len(cells) >= 3:
            rows.append((lineno, cells[1], cells[2]))
    return rows, start


AUTHORITY_STEM = {
    "docs/reviews/R1-codebase-reality.md": "R1",
    "docs/reviews/R2-tier1-wms-audit.md": "R2",
    "docs/reviews/R3-erp-midmarket-audit.md": "R3",
    "docs/reviews/R4-fulfilment-3pl-audit.md": "R4",
    "docs/reviews/R5-standards-industry-ops.md": "R5",
    "docs/reviews/R6-prior-art-triage.md": "R6",
    "docs/reviews/R7-logistics-supply-chain-seam.md": "R7",
    "docs/reviews/R8-task-buildability-v1.md": "R8",
    "docs/reviews/R9-task-buildability-v2-and-epics.md": "R9",
    "docs/reviews/R10-operational-walkthrough.md": "R10",
    "docs/reviews/R11-exception-and-unhappy-paths.md": "R11",
    "docs/reviews/R12-lifecycle-and-data-migration.md": "R12",
    "docs/reviews/R13-non-functional-and-operability.md": "R13",
    "docs/reviews/R14-codebase-and-sibling-set-reverification.md": "R14",
    "docs/reviews/R15-competitor-benchmark-r2.md": "R15",
    "docs/reviews/R16-role-and-persona-completeness.md": "R16",
    "docs/reviews/R17-screen-and-field-buildability.md": "R17",
    "docs/reviews/R18-reporting-and-analytics-completeness.md": "R18",
    "docs/reviews/R19-integration-device-and-channel-surface.md": "R19",
    "docs/reviews/R20-configuration-and-day-one-setup.md": "R20",
    "docs/reviews/R21-money-costing-and-billing.md": "R21",
}


def check_id_collisions(root, scanner):
    """Two things, both of which the accounting programme paid for.

    (a) A literal id defined by two registers. The known hazards are stated in the brief: R1 §6's
        traps are `T-1`…`T-18` and R2's findings are `T-001`…`T-097`, and R2's capability-matrix
        row numbers read like finding ids. Whether the two `T-` registers stay separated is
        asserted here; a matrix row copied as `T-244` is caught by check 7.
    (b) A register the checker can resolve that DECISIONS.md §6 does not declare. §6 is what a
        later author reads before choosing an id; a register missing from it is the next collision.
    """
    reg = id_registers(root)
    out = []

    # --- (a) literal collisions ------------------------------------------
    where = {}
    for label, kind, path, tokens, _probe in reg:
        for token, lineno in tokens.items():
            where.setdefault(token, []).append((label, kind, path, lineno))
    colliding = {t: v for t, v in where.items() if len(v) > 1}

    mentions = {}
    if colliding:
        for path in scanner.files:
            fe = scanner.exemptions(path)
            for lineno, text, in_code in iter_lines(read_lines(root, path)):
                if in_code or lineno in fe.declaration_lines:
                    continue
                for m in RULE_TOKEN_RE["id-collision"].finditer(text):
                    token = m.group(0)
                    if token not in colliding:
                        continue
                    if fe.cover("id-collision", lineno, token) is not None:
                        cover = fe.cover("id-collision", lineno, token)
                        scanner.ledger.record(path, lineno, token, "id-collision",
                                              cover[0], cover[1])
                        continue
                    mentions.setdefault(token, []).append((path, lineno))

    for token in sorted(colliding):
        owners = colliding[token]
        cites = mentions.get(token, [])
        anchor_path, anchor_line = owners[0][2], owners[0][3]
        sites = ", ".join("%s:%d" % (p, l) for p, l in cites[:3])
        out.append(Violation(
            11, anchor_path, anchor_line,
            "`%s` is defined by %d registers — %s — so %d mention%s of it across the design set "
            "cannot be told apart by shape%s"
            % (token, len(owners),
               " and ".join("%s (%s)" % (lab, pth) for lab, _k, pth, _l in owners),
               len(cites), "" if len(cites) == 1 else "s",
               (": %s%s" % (sites, ", …" if len(cites) > 3 else "")) if cites else "")))

    # --- (b) registers missing from DECISIONS.md §6 -----------------------
    rows, section = namespace_rows(root)
    for label, _kind, path, tokens, probe in reg:
        if not tokens:
            continue
        stem = AUTHORITY_STEM.get(path, os.path.basename(path))
        hit = False
        for _lineno, namespace, authority in rows:
            if probe not in namespace:
                continue
            # `| Invariants | **`L-1` … `L-14`** | this file |` — DECISIONS.md cites itself that way
            self_ref = "this file" in authority.lower() and path == DECISIONS
            if self_ref or stem in authority or stem in namespace:
                hit = True
                break
        if not hit:
            out.append(Violation(
                11, DECISIONS, section,
                "§6 declares no namespace for the %s register (`%s…`, %d ids, authority %s) — "
                "§6 is what the next author reads before choosing an id"
                % (label, probe, len(tokens), path)))
    return sorted(out, key=lambda v: v.key())


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def run(root, selected):
    files = markdown_files(root)
    ledger = ExemptionLedger()
    directives = DirectiveIndex(root, files, ledger)
    scanner = Scanner(root, files, ledger, directives)
    results, notes = {}, {}
    if 1 in selected:
        results[1] = check_fr(root, scanner)
    if 2 in selected:
        results[2] = check_scenarios(root, scanner)
    if 3 in selected:
        results[3] = check_tables(root, ledger, directives)
    if 4 in selected:
        results[4] = check_flyway(root, ledger, directives)
    if 5 in selected:
        results[5], note = check_issue_refs(root, files, ledger, directives)
        if note:
            notes[5] = note
    if 6 in selected:
        results[6] = check_sections(root)
    if 7 in selected:
        results[7] = check_findings(root, scanner)
    if 8 in selected:
        results[8] = check_plan(root)
    if 9 in selected:
        results[9] = check_epics(root)
    if 10 in selected:
        results[10] = check_ownership(root)
    if 11 in selected:
        results[11] = check_id_collisions(root, scanner)
    if 12 in selected:
        results[12] = check_screens(root, scanner)
    return results, ledger, notes, directives


def main():
    parser = argparse.ArgumentParser(
        description="Design-set integrity checker for the Classic Warehouse design set.")
    parser.add_argument("--summary", action="store_true", help="print counts only")
    parser.add_argument("--check", type=int, action="append", choices=sorted(CHECK_TITLES),
                        metavar="N", help="run only this check (repeatable, 1-12)")
    parser.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        help="repository root (default: the checkout this script lives in)")
    parser.add_argument("--no-advisory", action="store_true",
                        help="suppress the non-failing advisory notes")
    parser.add_argument("--show-exempt", action="store_true",
                        help="list every mention an exemption swallowed, file:line, with its rule")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        die("--root is not a directory: %s" % root)
    if not os.path.isdir(os.path.join(root, "docs")):
        die("%s does not look like the design set — no docs/ directory" % root)

    selected = set(args.check) if args.check else set(CHECK_TITLES)
    results, ledger, notes, directives = run(root, selected)

    total = len(directives.errors)
    if directives.errors:
        print("directive FAIL %4d  exemption directives that do not parse"
              % len(directives.errors))
        for path, lineno, _rule, message in directives.errors:
            print("  %s:%d: [directive] %s" % (path, lineno, message))
    for check in sorted(results):
        found = results[check]
        total += len(found)
        print("check-%-2d %-4s %4d  %s"
              % (check, "FAIL" if found else "pass", len(found), CHECK_TITLES[check]))
        if not args.summary:
            for violation in found:
                print("  " + violation.render())
        if check in notes:
            print("        note: %s" % notes[check])
        # An exemption nobody can see is an exemption nobody maintains: this prints on every run.
        if any(c == check for c in EXEMPT_RULES.values()):
            print("        %s" % ledger.summary_line(check))
            if not args.summary:
                for path, anchor, rule, count in ledger.sources_for(check):
                    print("          %s:%d: [%s] exempts %d mention%s"
                          % (path, anchor, rule, count, "" if count == 1 else "s"))
            for rule, path, lineno, reason in ledger.stale(check):
                print("          %s:%d: stale [%s] declaration — it exempts nothing, remove it: %s"
                      % (path, lineno, rule, reason))
            if args.show_exempt:
                for path, lineno, token, rule, reason in sorted(ledger.mentions):
                    if EXEMPT_RULES.get(rule) == check or rule == "code-block/%d" % check:
                        print("          %s:%d: %s exempt [%s] %s"
                              % (path, lineno, token, rule, reason))

    if not args.summary and 4 in selected and not args.no_advisory:
        advisory = flyway_advisory(root)
        if advisory:
            print("\nadvisory (%d, does not fail the build) — a version cited by a task body that "
                  "no task header claims:" % len(advisory))
            for note in advisory:
                print("  " + note)

    print("\n%d violation%s across %d check%s"
          % (total, "" if total == 1 else "s", len(results), "" if len(results) == 1 else "s"))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
