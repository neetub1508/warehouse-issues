#!/usr/bin/env bash
#
# File the Classic Warehouse backlog on GitHub, in dependency order, wiring every cross-reference
# automatically — and afterwards keep GitHub a mirror of these files.
#
#   1. master epic
#   2. eight phase epics    (P0 P1 P2 P2-IN P3 P4 P5 P6 — each links back to the master)
#   3. 138 task issues      (each links back to its phase epic)
#   4. phase epics patched  with their real task checklists
#   5. master epic patched  with the real phase-epic numbers
#   6. issues/CREATED.md    written — the map tools/check-design-set.py check 5 resolves `#NN` against
#
# Placeholders substituted at creation time:
#   __MASTER__ __P0__ __P1__ __P2__ __P2IN__ __P3__ __P4__ __P5__ __P6__ __TASKS__
# which is why the .md files are **not valid issue bodies until this script runs**.
#
# `DECISIONS.md` §7 rule 5: the .md files in this repository are authoritative and GitHub is a
# mirror kept in sync mechanically. `--sync` pushes, `--check` fails CI on drift. Never edit an
# issue body in the GitHub UI.
#
# Requires: gh, authenticated with a token that has Issues: write on the repo.
#   gh auth login
#
# Usage:
#   ./create-issues.sh [--dry-run]            file the whole backlog (first run only)
#   ./create-issues.sh --sync    [--dry-run]  push every .md carrying an `issue: NN` line to its issue
#   ./create-issues.sh --check                diff each filed body against its .md; non-zero on drift
#
set -euo pipefail

REPO="${REPO:-neetub1508/warehouse-issues}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=0
MODE=create

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --sync)    MODE=sync ;;
    --check)   MODE=check ;;
    -h|--help) sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)         echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

# ---- the phase table -------------------------------------------------------
# Parallel arrays, in filing order. `p2in` is phase **P2-IN** and its epic is 04-EPIC-p2in.md —
# the one place where the file stem, the phase id and the placeholder all differ.
PHASES=(p0     p1     p2     p2in     p3     p4     p5     p6)
EPICNUM=(01    02     03     04       05     06     07     08)
PLACEHOLDER=(__P0__ __P1__ __P2__ __P2IN__ __P3__ __P4__ __P5__ __P6__)
PHASE_ID=(P0    P1     P2     P2-IN    P3     P4     P5     P6)
NPHASE=${#PHASES[@]}

epic_file() { echo "$DIR/${EPICNUM[$1]}-EPIC-${PHASES[$1]}.md"; }
master_file() { echo "$DIR/00-EPIC-master.md"; }

# `issues/` also holds DEFECTS-FOUND.md and this script's README, which are documents and not
# issues. An issue file is one that declares a TITLE.
is_issue_file() { grep -q '^TITLE: ' "$1"; }

title_of()  { sed -n 's/^TITLE: //p' "$1" | head -1; }
labels_of() { sed -n 's/^LABELS: //p' "$1" | head -1; }
issue_of()  { sed -n 's/^issue: *//p' "$1" | head -1; }
body_of()   { sed '1,/^---$/d' "$1"; }
short_of()  { title_of "$1" | sed 's/^\[Warehouse\] //'; }

# ---- preflight -------------------------------------------------------------
command -v gh >/dev/null || { echo "gh is not installed" >&2; exit 1; }
if [[ $DRY_RUN -eq 0 || $MODE == check ]]; then
  gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated. Run: gh auth login" >&2; exit 1; }
fi

# `__TASKS__` is replaced by a multi-line checklist. On a line with anything else — `## __TASKS__`
# is the shape that has actually occurred — the substitution corrupts the heading and leaves any
# hand-written checklist below it duplicated. Refuse rather than file a mangled epic.
# tools/check-design-set.py check 9 reports the same thing, so CI catches it before you get here.
assert_placeholder_lines() {
  local bad=0 f n line
  for ((i = 0; i < NPHASE; i++)); do
    f="$(epic_file "$i")"
    [[ -e "$f" ]] || { echo "MISSING epic: $f" >&2; bad=1; continue; }
    while IFS=: read -r n line; do
      [[ -z "$n" ]] && continue
      if [[ "$(echo "$line" | tr -d '[:space:]')" != "__TASKS__" ]]; then
        echo "REFUSING: $(basename "$f"):$n — \`__TASKS__\` shares its line with other content:" >&2
        echo "    $line" >&2
        bad=1
      fi
    done < <(grep -n '__TASKS__' "$f" || true)
  done
  if [[ $bad -ne 0 ]]; then
    echo >&2
    echo "  Put the placeholder alone on its own line, under a \`## Tasks\` heading, and delete any" >&2
    echo "  hand-written checklist beneath it — this script generates that list from the real issue" >&2
    echo "  numbers. See issues/README.md, 'The placeholder mechanism'." >&2
    exit 1
  fi
}

# ---- substitution ----------------------------------------------------------
# Placeholders inside a fenced code block are left alone. Two epics document a runnable command —
#   grep -h '^Part of __P0__' issues/p0-*.md
# — and substituting there would file an example that silently matches nothing. Same rule the
# checker uses: inside a fence it is a command, not a reference.
SUBST_KEYS=()
SUBST_VALS=()
TASKS_BLOCK=""

render() { # render <file> — the body with every placeholder resolved
  local file="$1" fenced=0 line i
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^[[:space:]]*'```' ]]; then
      fenced=$((1 - fenced)); printf '%s\n' "$line"; continue
    fi
    if [[ $fenced -eq 1 ]]; then printf '%s\n' "$line"; continue; fi
    if [[ "$(echo "$line" | tr -d '[:space:]')" == "__TASKS__" ]]; then
      printf '%s' "$TASKS_BLOCK"; continue
    fi
    for ((i = 0; i < ${#SUBST_KEYS[@]}; i++)); do
      line="${line//${SUBST_KEYS[$i]}/${SUBST_VALS[$i]}}"
    done
    printf '%s\n' "$line"
  done < <(body_of "$file")
}

set_subst() { # set_subst KEY=VAL ...
  SUBST_KEYS=(); SUBST_VALS=()
  local pair
  for pair in "$@"; do
    SUBST_KEYS[${#SUBST_KEYS[@]}]="${pair%%=*}"
    SUBST_VALS[${#SUBST_VALS[@]}]="${pair#*=}"
  done
}

# ---- labels ----------------------------------------------------------------
# Every label any issue file names must exist before the first create; there is no create-label
# step anywhere else. The colour is derived from the label name so re-runs are stable.
ensure_labels() {
  local all l colour n=0
  all=$(sed -n 's/^LABELS: //p' "$DIR"/*.md | tr ',' '\n' | sed 's/^ *//; s/ *$//' | sort -u)
  while IFS= read -r l; do
    [[ -z "$l" ]] && continue
    n=$((n + 1))
    colour=$(printf '%06x' $(( $(printf '%s' "$l" | cksum | cut -d' ' -f1) % 16777216 )))
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "    DRY: would ensure label '$l' (#$colour)"
      continue
    fi
    gh label create "$l" --repo "$REPO" --color "$colour" >/dev/null 2>&1 || true  # exists is fine
  done <<< "$all"
  echo "    $n label(s)"
}

# ---- create / patch --------------------------------------------------------
create() { # create <file> — echoes the new issue number on stdout, progress on stderr
  local file="$1"
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "    DRY: would create: $(title_of "$file")" >&2
    echo "0"; return
  fi
  local url
  url=$(render "$file" | gh issue create --repo "$REPO" \
        --title "$(title_of "$file")" \
        --label "$(labels_of "$file")" \
        --body-file -)
  echo "${url##*/}"
}

patch() { # patch <issue-number> <file>
  local num="$1" file="$2"
  if [[ $DRY_RUN -eq 1 ]]; then echo "    DRY: would patch #$num from $(basename "$file")" >&2; return; fi
  render "$file" | gh issue edit "$num" --repo "$REPO" --body-file - >/dev/null
}

# The `issue: NN` line is written back into the front matter so --sync and --check need no
# hand-keyed map of 147 numbers. It sits above the `---`, so it is never part of a body.
stamp_issue() { # stamp_issue <file> <number>
  local file="$1" num="$2" tmp
  [[ $DRY_RUN -eq 1 ]] && return
  [[ -n "$(issue_of "$file")" ]] && return
  tmp="$(mktemp)"
  awk -v num="$num" 'BEGIN{done=0} /^---$/ && !done {print "issue: " num; done=1} {print}' \
      "$file" > "$tmp"
  mv "$tmp" "$file"
}

# ---- sync and check --------------------------------------------------------
# The .md files are the single source of truth. Every file carrying an `issue: NN` line is in scope.

load_refs() {
  local i n
  n="$(issue_of "$(master_file)")"
  MASTER_REF="#${n:-__MASTER__}"
  EPIC_REF=()
  for ((i = 0; i < NPHASE; i++)); do
    n="$(issue_of "$(epic_file "$i")")"
    EPIC_REF[$i]="#${n:-${PLACEHOLDER[$i]}}"
  done
}

# bash 3.2 (the macOS default) has no `mapfile`, so the substitution arrays are set directly
# rather than round-tripped through a command substitution.
set_phase_subst() {
  local i
  SUBST_KEYS=("__MASTER__"); SUBST_VALS=("$MASTER_REF")
  for ((i = 0; i < NPHASE; i++)); do
    SUBST_KEYS[${#SUBST_KEYS[@]}]="${PLACEHOLDER[$i]}"
    SUBST_VALS[${#SUBST_VALS[@]}]="${EPIC_REF[$i]}"
  done
}

build_tasklist() { # build_tasklist <phase-index> -> TASKS_BLOCK
  local i="$1" f num
  TASKS_BLOCK=""
  for f in "$DIR"/${PHASES[$i]}-*.md; do
    [[ -e "$f" ]] || continue
    num="$(issue_of "$f")"
    if [[ -n "$num" ]]; then
      TASKS_BLOCK+="- [ ] #${num} · $(short_of "$f")"$'\n'
    else
      TASKS_BLOCK+="- [ ] $(short_of "$f")"$'\n'
    fi
  done
}

filed_body() { gh issue view "$1" --repo "$REPO" --json body --jq '.body' | tr -d '\r'; }

# Trailing blank lines are not content on either side; normalise both before diffing.
trim_tail() { awk '{ buf[NR] = $0 } END { last = NR; while (last > 0 && buf[last] ~ /^[[:space:]]*$/) last--; for (i = 1; i <= last; i++) print buf[i] }'; }

render_for_sync() { # render_for_sync <file>
  local f="$1" base i
  base="$(basename "$f")"
  set_phase_subst
  TASKS_BLOCK=""
  for ((i = 0; i < NPHASE; i++)); do
    if [[ "$base" == "${EPICNUM[$i]}-EPIC-${PHASES[$i]}.md" ]]; then
      build_tasklist "$i"
      break
    fi
  done
  render "$f"
}

sync_all() {
  local f num n=0
  for f in "$DIR"/*.md; do
    is_issue_file "$f" || continue
    num="$(issue_of "$f")"
    [[ -z "$num" ]] && continue
    n=$((n + 1))
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "DRY: would sync $(basename "$f") -> #$num"
      continue
    fi
    render_for_sync "$f" | gh issue edit "$num" --repo "$REPO" --body-file - >/dev/null
    echo "synced $(basename "$f") -> #$num"
  done
  echo "==> $n file(s) processed"
  if [[ $n -eq 0 ]]; then
    echo "    no file carries an \`issue: NN\` line — the backlog has not been filed yet" >&2
  fi
}

check_all() {
  local f num n=0 drift=0
  for f in "$DIR"/*.md; do
    is_issue_file "$f" || continue
    num="$(issue_of "$f")"
    [[ -z "$num" ]] && continue
    n=$((n + 1))
    if diff -q <(render_for_sync "$f" | trim_tail) <(filed_body "$num" | trim_tail) >/dev/null 2>&1
    then continue; fi
    drift=$((drift + 1))
    echo "DRIFT  $(basename "$f")  ->  #$num"
  done
  if [[ $n -eq 0 ]]; then
    echo "==> no file carries an \`issue: NN\` line — nothing filed, nothing to check"
    return 0
  fi
  if [[ $drift -eq 0 ]]; then
    echo "==> $n file(s) checked, no drift"
    return 0
  fi
  echo "==> $n file(s) checked, $drift drifted — the .md files win; run --sync" >&2
  return 1
}

assert_placeholder_lines

case "$MODE" in
  sync)  load_refs; sync_all; exit 0 ;;
  check) load_refs; if check_all; then exit 0; else exit 1; fi ;;
esac

# ---- refuse to double-file -------------------------------------------------
# A second create run would duplicate 147 issues and orphan every cross-reference in the first set.
if [[ $DRY_RUN -eq 0 ]]; then
  existing=$(gh issue list --repo "$REPO" --state all --limit 1 --json number --jq 'length' 2>/dev/null || echo 0)
  if [[ "$existing" != "0" ]]; then
    echo "REFUSING: $REPO already has issues." >&2
    echo "  Creating again would duplicate the backlog and orphan every cross-reference." >&2
    echo "  To update filed issues from these files:   $0 --sync" >&2
    echo "  To stand this backlog up elsewhere:        REPO=owner/other-repo $0" >&2
    exit 1
  fi
fi

TOTAL_TASKS=0
for ((i = 0; i < NPHASE; i++)); do
  for f in "$DIR"/${PHASES[$i]}-*.md; do
    [[ -e "$f" ]] && TOTAL_TASKS=$((TOTAL_TASKS + 1))
  done
done
echo "==> filing $((1 + NPHASE + TOTAL_TASKS)) issues into $REPO: 1 master + $NPHASE phase epics + $TOTAL_TASKS tasks"

echo "==> 0/6  labels"
ensure_labels

echo "==> 1/6  master epic"
set_subst; TASKS_BLOCK=""
MASTER=$(create "$(master_file)")
stamp_issue "$(master_file)" "$MASTER"
echo "    master epic = #$MASTER"

echo "==> 2/6  phase epics"
EPIC=()
for ((i = 0; i < NPHASE; i++)); do
  set_subst "__MASTER__=#$MASTER"; TASKS_BLOCK=""
  n=$(create "$(epic_file "$i")")
  EPIC[$i]=$n
  stamp_issue "$(epic_file "$i")" "$n"
  echo "    ${PHASE_ID[$i]} epic = #$n"
done

echo "==> 3/6  task issues"
for ((i = 0; i < NPHASE; i++)); do
  for f in "$DIR"/${PHASES[$i]}-*.md; do
    [[ -e "$f" ]] || continue
    set_subst "${PLACEHOLDER[$i]}=#${EPIC[$i]}"; TASKS_BLOCK=""
    n=$(create "$f")
    stamp_issue "$f" "$n"
    echo "    #$n  $(short_of "$f")"
  done
done

echo "==> 4/6  patch phase epics with their task checklists"
MASTER_REF="#$MASTER"
EPIC_REF=()
for ((i = 0; i < NPHASE; i++)); do EPIC_REF[$i]="#${EPIC[$i]}"; done
for ((i = 0; i < NPHASE; i++)); do
  build_tasklist "$i"
  set_phase_subst
  patch "${EPIC[$i]}" "$(epic_file "$i")"
  echo "    patched ${PHASE_ID[$i]} epic #${EPIC[$i]}"
done

echo "==> 5/6  patch master epic with the phase-epic numbers"
set_phase_subst; TASKS_BLOCK=""
patch "$MASTER" "$(master_file)"

echo "==> 6/6  write issues/CREATED.md"
if [[ $DRY_RUN -eq 1 ]]; then
  echo "    DRY: would write $DIR/CREATED.md"
else
  {
    echo "# Created issues"
    echo
    echo "Written by \`create-issues.sh\`. This is the map \`tools/check-design-set.py\` check 5"
    echo "resolves every \`#NN\` cross-reference against — do not hand-edit it."
    echo
    echo "| Issue | File | Title |"
    echo "|---|---|---|"
    echo "| #$MASTER | \`issues/00-EPIC-master.md\` | $(short_of "$(master_file)") |"
    for ((i = 0; i < NPHASE; i++)); do
      echo "| #${EPIC[$i]} | \`issues/${EPICNUM[$i]}-EPIC-${PHASES[$i]}.md\` | $(short_of "$(epic_file "$i")") |"
    done
    for ((i = 0; i < NPHASE; i++)); do
      for f in "$DIR"/${PHASES[$i]}-*.md; do
        [[ -e "$f" ]] || continue
        echo "| #$(issue_of "$f") | \`issues/$(basename "$f")\` | $(short_of "$f") |"
      done
    done
  } > "$DIR/CREATED.md"
  echo "    $DIR/CREATED.md"
fi

echo
echo "Done. Master epic: https://github.com/$REPO/issues/$MASTER"
echo "Next: python3 tools/check-design-set.py --check 5   # every #NN now has a row to resolve to"
