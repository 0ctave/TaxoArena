# TaxoArena — Tuning Finalists & Architectural Report

## 1. Executive Summary & Pareto Ranking

| Rank | Run ID | Stage | Seed | Hard | Soft | Dom | Top-1 Acc | AnyMatch | ECE | Borderline | Bridge Ratio | Migration | DeltaRho | SmallLeaf | SrcBDepth2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | L9_005_seed42 | screen | 42 | PASSED | FAILED | 0 | 75.06% | 81.97% | 0.1352 | 0.4575 | 2.91% | 0.2342 | 0.0000 | 0.0155 | 0 |
| 2 | L9_004_seed42 | screen | 42 | PASSED | FAILED | 0 | 74.92% | 80.83% | 0.1465 | 0.3861 | 2.02% | 0.2389 | 0.0000 | 0.0238 | 0 |
| 3 | L9_003_seed42 | screen | 42 | PASSED | FAILED | 0 | 74.89% | 81.75% | 0.1409 | 0.4500 | 2.45% | 0.2372 | 0.0000 | 0.0156 | 0 |
| 4 | L9_009_seed42 | screen | 42 | PASSED | FAILED | 0 | 74.58% | 80.50% | 0.1416 | 0.3794 | 2.58% | 0.2397 | 0.0000 | 0.0164 | 0 |
| 5 | L9_002_seed42 | screen | 42 | PASSED | FAILED | 0 | 74.03% | 79.39% | 0.1415 | 0.3683 | 4.08% | 0.2317 | 0.0000 | 0.0164 | 0 |
| 6 | L9_007_seed42 | screen | 42 | PASSED | FAILED | 0 | 73.92% | 80.25% | 0.1401 | 0.4311 | 2.96% | 0.2350 | 0.0000 | 0.0080 | 0 |
| 7 | L9_006_seed42 | screen | 42 | PASSED | FAILED | 0 | 73.44% | 78.22% | 0.1451 | 0.3289 | 1.66% | 0.2400 | 0.0000 | 0.0000 | 0 |
| 8 | L9_008_seed42 | screen | 42 | PASSED | FAILED | 0 | 72.92% | 77.25% | 0.1487 | 0.3172 | 1.62% | 0.2406 | 0.0000 | 0.0000 | 0 |
| 9 | L9_001_seed42 | screen | 42 | PASSED | FAILED | 0 | 72.42% | 77.08% | 0.1416 | 0.3133 | 2.72% | 0.2453 | 0.0000 | 0.0000 | 0 |

## 2. Gate Failure Explanations (Top 10 Runs)

### 1. Run: L9_005_seed42
- **Soft Gate Failures**: BorderlineRate = 0.4575 outside band [0.2, 0.35]

### 2. Run: L9_004_seed42
- **Soft Gate Failures**: BorderlineRate = 0.3861 outside band [0.2, 0.35]

### 3. Run: L9_003_seed42
- **Soft Gate Failures**: BorderlineRate = 0.4500 outside band [0.2, 0.35]

### 4. Run: L9_009_seed42
- **Soft Gate Failures**: BorderlineRate = 0.3794 outside band [0.2, 0.35]

### 5. Run: L9_002_seed42
- **Soft Gate Failures**: BorderlineRate = 0.3683 outside band [0.2, 0.35]

### 6. Run: L9_007_seed42
- **Soft Gate Failures**: Top1Accuracy = 73.92% < 74.0%; BorderlineRate = 0.4311 outside band [0.2, 0.35]

### 7. Run: L9_006_seed42
- **Soft Gate Failures**: Top1Accuracy = 73.44% < 74.0%

### 8. Run: L9_008_seed42
- **Soft Gate Failures**: Top1Accuracy = 72.92% < 74.0%

### 9. Run: L9_001_seed42
- **Soft Gate Failures**: Top1Accuracy = 72.42% < 74.0%


## 3. Categorized Metric Summaries (Top 5 Finalists)

### Rank 1: L9_005_seed42

**Config Factors**: `assignmentCosineGap`=0.125, `deltaAssign`=1.5, `secondaryMassFloor`=2.0, `bridgeSupportRelFraction`=0.05

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.07694444444444444
- **SmallLeafFraction**: 0.015503875968992248
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=206, LeafCount=129, BridgeCount=6, BridgeRatio=0.0291, ResidualCount=1494

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.636737297144072
- **DendrogramPurity**: 0.005179195670094236
- **SphericalSilhouette**: 0.0970986821739101
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.06633906633906633
- **TotalDasguptaCost**: 5.1839857168999466E10
- **RoutingECE**: 0.135213602672641
- **BrierScore**: 0.4171463205046466

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7505555555555555%
- **AnyMatchAccuracy**: 0.8197222222222222%
- **MacroF1**: 0.7493255110048033
- **AvgMatchCount**: 1.8980555555555556
- **BorderlineRate**: 0.4575
- **CrossAnchorMigrationRate**: 0.23416666666666666

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 6
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.255813953488372
- **SoftDegreeMean**: 2.9963570127504555
- **EntropyGuardRate**: 0.3612629022465088
- **SoftEffSampleSize**: 4613.930103559459
- **SelectedNodeP10QueryCount**: 72.0
- **SelectedNodeLeafBalanceEntropy**: 4.804068963376003

#### F. Config Traceability
- **SHA256**: `6e03e8bf833c30b6c26d54d5f738b0f9f19bd408c036e01efb319436f297af5b`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 2: L9_004_seed42

**Config Factors**: `assignmentCosineGap`=0.125, `deltaAssign`=1.25, `secondaryMassFloor`=5.0, `bridgeSupportRelFraction`=0.03

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.05444444444444444
- **SmallLeafFraction**: 0.023809523809523808
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=198, LeafCount=126, BridgeCount=4, BridgeRatio=0.0202, ResidualCount=1323

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.6556869592824828
- **DendrogramPurity**: 0.003613025909198954
- **SphericalSilhouette**: 0.10213857490564031
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.06815222465174557
- **TotalDasguptaCost**: 5.2669302716349525E10
- **RoutingECE**: 0.14654584193340647
- **BrierScore**: 0.428207826402526

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7491666666666666%
- **AnyMatchAccuracy**: 0.8083333333333333%
- **MacroF1**: 0.7404599717929864
- **AvgMatchCount**: 1.7166666666666666
- **BorderlineRate**: 0.3861111111111111
- **CrossAnchorMigrationRate**: 0.2388888888888889

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 4
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.1825396825396823
- **SoftDegreeMean**: 2.88705035971223
- **EntropyGuardRate**: 0.4438848920863309
- **SoftEffSampleSize**: 4349.843758501106
- **SelectedNodeP10QueryCount**: 69.0
- **SelectedNodeLeafBalanceEntropy**: 4.794438543850006

#### F. Config Traceability
- **SHA256**: `95ebd645a9a2310209b635308a74d28729b25af2f006cb684650248caade4e81`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 3: L9_003_seed42

**Config Factors**: `assignmentCosineGap`=0.1, `deltaAssign`=1.5, `secondaryMassFloor`=5.0, `bridgeSupportRelFraction`=0.1

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.08277777777777778
- **SmallLeafFraction**: 0.015625
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=204, LeafCount=128, BridgeCount=5, BridgeRatio=0.0245, ResidualCount=1540

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.6354795201249379
- **DendrogramPurity**: 0.005099164170598338
- **SphericalSilhouette**: 0.09747618874271409
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.06339255499153976
- **TotalDasguptaCost**: 5.277466268895582E10
- **RoutingECE**: 0.14088919549444945
- **BrierScore**: 0.41960535053143005

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7488888888888889%
- **AnyMatchAccuracy**: 0.8175%
- **MacroF1**: 0.7444463703051298
- **AvgMatchCount**: 1.9055555555555554
- **BorderlineRate**: 0.45
- **CrossAnchorMigrationRate**: 0.23722222222222222

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 5
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.2421875
- **SoftDegreeMean**: 3.04320987654321
- **EntropyGuardRate**: 0.3617283950617284
- **SoftEffSampleSize**: 4600.646625484679
- **SelectedNodeP10QueryCount**: 72.0
- **SelectedNodeLeafBalanceEntropy**: 4.795530154617207

#### F. Config Traceability
- **SHA256**: `ecb00428df16a1c59f32f6cb7eb366c34de9e44bf0fe63e3d34c489aeb7a3085`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 4: L9_009_seed42

**Config Factors**: `assignmentCosineGap`=0.15, `deltaAssign`=1.25, `secondaryMassFloor`=2.0, `bridgeSupportRelFraction`=0.1

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.05388888888888889
- **SmallLeafFraction**: 0.01639344262295082
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=194, LeafCount=122, BridgeCount=5, BridgeRatio=0.0258, ResidualCount=1439

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.6553622725821896
- **DendrogramPurity**: 0.00366490077181327
- **SphericalSilhouette**: 0.10333623626431931
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.06927506775067752
- **TotalDasguptaCost**: 5.202694108705307E10
- **RoutingECE**: 0.14160486042601741
- **BrierScore**: 0.4288339848021315

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7458333333333333%
- **AnyMatchAccuracy**: 0.805%
- **MacroF1**: 0.7382651584339545
- **AvgMatchCount**: 1.7019444444444445
- **BorderlineRate**: 0.3794444444444444
- **CrossAnchorMigrationRate**: 0.23972222222222223

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 5
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.1885245901639343
- **SoftDegreeMean**: 2.887994143484627
- **EntropyGuardRate**: 0.42825768667642755
- **SoftEffSampleSize**: 4352.904993807259
- **SelectedNodeP10QueryCount**: 69.0
- **SelectedNodeLeafBalanceEntropy**: 4.763853382896569

#### F. Config Traceability
- **SHA256**: `69af462aee10ca4122798847fac9249c7eeec268cff4ec1c8b67d260f5e8045c`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 5: L9_002_seed42

**Config Factors**: `assignmentCosineGap`=0.1, `deltaAssign`=1.25, `secondaryMassFloor`=3.5, `bridgeSupportRelFraction`=0.05

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.050277777777777775
- **SmallLeafFraction**: 0.01639344262295082
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=196, LeafCount=122, BridgeCount=8, BridgeRatio=0.0408, ResidualCount=1369

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.6648778071334214
- **DendrogramPurity**: 0.0034369590245037144
- **SphericalSilhouette**: 0.10489311634635133
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.06933554627139014
- **TotalDasguptaCost**: 4.93527388130574E10
- **RoutingECE**: 0.14150830370767017
- **BrierScore**: 0.4332199887423979

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7402777777777778%
- **AnyMatchAccuracy**: 0.7938888888888889%
- **MacroF1**: 0.7397363359898106
- **AvgMatchCount**: 1.6502777777777777
- **BorderlineRate**: 0.36833333333333335
- **CrossAnchorMigrationRate**: 0.23166666666666666

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 8
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.2049180327868854
- **SoftDegreeMean**: 2.841628959276018
- **EntropyGuardRate**: 0.4306184012066365
- **SoftEffSampleSize**: 4308.716334239514
- **SelectedNodeP10QueryCount**: 70.0
- **SelectedNodeLeafBalanceEntropy**: 4.767636494628563

#### F. Config Traceability
- **SHA256**: `720cbba0b253cdabd79f4b1498342df38d59ab07eb49b6f3fa6162f7918eca02`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

