#!/bin/bash
W=/z/FAC/TUBerlin/THESIS/TaxoArena/.claude/worktrees/rp13-afu-run2
cd $W
T0=$(date +%s)
build() { # $1 toml name, $2 outdir
  mkdir -p $2; s=$(date +%s); echo "== $1 start $(date -Iseconds)"; tasklist | grep -i java || echo "no java"
  powershell -NoProfile -Command "cmd /c '.\gradlew.bat bootRun --console=plain -q --offline -PjvmThreads=12 --args=\"--config experiment_configs/union_af_route/AF-U/$1.toml\" > $2/build.log 2>&1'; exit \$LASTEXITCODE"
  echo "== $1 jvm rc=$? wall=$(( $(date +%s)-s ))s"
}
for m in gpqa musr math bbh mmlu_pro_lb; do
  build $m experiment_results/archv2/union_af_route/AF-U/$m
  python tools/analysis/union_af_route_ops.py --member $m; r=$?; echo "== $m ops rc=$r"
  if [ $r -ne 0 ] && [ $r -ne 3 ]; then echo "== STOP at $m"; exit 1; fi
done
echo "== members done total=$(( $(date +%s)-T0 ))s"
python tools/analysis/union_af_route_ops.py --fill; r=$?; echo "== fill rc=$r"; [ $r -ne 0 ] && exit 1
grep -c __SNAP_ experiment_configs/union_af_route/AF-U/graft_flatleaf.toml
build graft_flatleaf experiment_results/archv2/union_af_route/AF-U/graft_flatleaf
echo "== total=$(( $(date +%s)-T0 ))s"
