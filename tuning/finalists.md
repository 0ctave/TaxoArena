# TaxoArena — Tuning Finalists & Architectural Report

## 1. Executive Summary & Pareto Ranking

| Rank | Run ID | Stage | Seed | Hard | Soft | Dom | Top-1 Acc | AnyMatch | ECE | Borderline | Bridge Ratio | Migration | DeltaRho | SmallLeaf | SrcBDepth2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | val_365af0c7_seed2048 | validate | 2048 | PASSED | FAILED | 1 | 75.94% | 77.47% | 0.2009 | 0.1028 | 0.95% | 0.2406 | 0.0000 | 0.0000 | 0 |
| 2 | val_82c0986d_seed2048 | validate | 2048 | PASSED | FAILED | 0 | 76.31% | 77.89% | 0.2018 | 0.1233 | 0.68% | 0.2369 | 0.0000 | 0.0000 | 0 |
| 3 | val_c0a0d68b_seed2048 | validate | 2048 | PASSED | FAILED | 0 | 75.72% | 77.31% | 0.2038 | 0.1083 | 0.00% | 0.2428 | 0.0000 | 0.0000 | 0 |
| 4 | L9_004_seed42 | screen | 42 | PASSED | FAILED | 0 | 75.56% | 76.93% | 0.2103 | 0.1217 | 1.88% | 0.2444 | 0.0000 | 0.0000 | 0 |
| 5 | val_365af0c7_seed137 | validate | 137 | PASSED | FAILED | 0 | 74.21% | 75.65% | 0.2058 | 0.1029 | 1.96% | 0.2418 | 0.0000 | 0.0000 | 0 |
| 6 | L9_005_seed42 | screen | 42 | PASSED | FAILED | 0 | 74.19% | 75.98% | 0.2237 | 0.1083 | 2.13% | 0.2581 | 0.0000 | 0.0000 | 0 |
| 7 | L9_007_seed42 | screen | 42 | PASSED | FAILED | 0 | 74.16% | 76.00% | 0.2108 | 0.1138 | 0.00% | 0.2584 | 0.0000 | 0.0000 | 0 |
| 8 | val_c0a0d68b_seed137 | validate | 137 | PASSED | FAILED | 0 | 74.07% | 75.74% | 0.1960 | 0.0960 | 2.04% | 0.2357 | 0.0000 | 0.0000 | 0 |
| 9 | L9_008_seed42 | screen | 42 | PASSED | FAILED | 0 | 73.91% | 75.47% | 0.1941 | 0.1378 | 3.77% | 0.2305 | 0.0000 | 0.1624 | 0 |
| 10 | L9_003_seed42 | screen | 42 | PASSED | FAILED | 0 | 73.66% | 75.17% | 0.2097 | 0.0999 | 1.98% | 0.2469 | 0.0000 | 0.0000 | 0 |

## 2. Gate Failure Explanations (Top 10 Runs)

### 1. Run: val_365af0c7_seed2048
- **Soft Gate Failures**: RoutingECE = 0.2009 > 0.15

### 2. Run: val_82c0986d_seed2048
- **Soft Gate Failures**: RoutingECE = 0.2018 > 0.15

### 3. Run: val_c0a0d68b_seed2048
- **Soft Gate Failures**: RoutingECE = 0.2038 > 0.15

### 4. Run: L9_004_seed42
- **Soft Gate Failures**: RoutingECE = 0.2103 > 0.15

### 5. Run: val_365af0c7_seed137
- **Soft Gate Failures**: RoutingECE = 0.2058 > 0.15

### 6. Run: L9_005_seed42
- **Soft Gate Failures**: RoutingECE = 0.2237 > 0.15

### 7. Run: L9_007_seed42
- **Soft Gate Failures**: RoutingECE = 0.2108 > 0.15

### 8. Run: val_c0a0d68b_seed137
- **Soft Gate Failures**: RoutingECE = 0.1960 > 0.15

### 9. Run: L9_008_seed42
- **Soft Gate Failures**: RoutingECE = 0.1941 > 0.15

### 10. Run: L9_003_seed42
- **Soft Gate Failures**: RoutingECE = 0.2097 > 0.15


## 3. Categorized Metric Summaries (Top 5 Finalists)

### Rank 1: val_365af0c7_seed2048

**Config Factors**: `deltaAssign`=0.003, `minClusterSize`=75, `secondaryMassFloor`=2.0, `bridgeSupportRelFraction`=0.05

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 2.777777777777778E-4
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=105, LeafCount=60, BridgeCount=1, BridgeRatio=0.0095, ResidualCount=826

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7289960740325294
- **DendrogramPurity**: 0.4684674062773342
- **SphericalSilhouette**: 0.1088319802575796
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.14457908163265304
- **TotalDasguptaCost**: 6.2678320464408905E10
- **RoutingECE**: 0.20093220591253047
- **BrierScore**: 0.4574524546363684

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7594444444444445%
- **AnyMatchAccuracy**: 0.7747222222222222%
- **MacroF1**: 0.748888821589377
- **AvgMatchCount**: 1.1225
- **BorderlineRate**: 0.10277777777777777
- **CrossAnchorMigrationRate**: 0.24055555555555555

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 1
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.85
- **SoftDegreeMean**: 2.191891891891892
- **EntropyGuardRate**: 0.8972972972972973
- **SoftEffSampleSize**: 3647.840109465606
- **SelectedNodeP10QueryCount**: 84.0
- **SelectedNodeLeafBalanceEntropy**: 3.9885418064843994

#### F. Config Traceability
- **SHA256**: `365af0c7679bcc99ecbc70baabb9de1bdd9960fce5cfa1399d5e52e003978331`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 1

---

### Rank 2: val_82c0986d_seed2048

**Config Factors**: `deltaAssign`=0.0015, `minClusterSize`=50, `secondaryMassFloor`=5.0, `bridgeSupportRelFraction`=0.05

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 2.777777777777778E-4
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=146, LeafCount=91, BridgeCount=1, BridgeRatio=0.0068, ResidualCount=663

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7425212431614481
- **DendrogramPurity**: 0.4788911096061479
- **SphericalSilhouette**: 0.10464010094590868
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.097799511002445
- **TotalDasguptaCost**: 6.274051944253647E10
- **RoutingECE**: 0.20179333081999573
- **BrierScore**: 0.45179636030670517

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7630555555555556%
- **AnyMatchAccuracy**: 0.7788888888888889%
- **MacroF1**: 0.757044084529845
- **AvgMatchCount**: 1.146111111111111
- **BorderlineRate**: 0.12333333333333334
- **CrossAnchorMigrationRate**: 0.23694444444444446

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 1
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.956043956043956
- **SoftDegreeMean**: 2.184684684684685
- **EntropyGuardRate**: 0.8896396396396397
- **SoftEffSampleSize**: 3659.558953554894
- **SelectedNodeP10QueryCount**: 57.0
- **SelectedNodeLeafBalanceEntropy**: 4.435206278092548

#### F. Config Traceability
- **SHA256**: `82c0986dc6b96524cbf345ba8d2616c535e5cdfc87f6429a89c98f84935fd984`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 3: val_c0a0d68b_seed2048

**Config Factors**: `deltaAssign`=0.0015, `minClusterSize`=75, `secondaryMassFloor`=3.5, `bridgeSupportRelFraction`=0.1

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 2.777777777777778E-4
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=101, LeafCount=62, BridgeCount=0, BridgeRatio=0.0000, ResidualCount=621

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7382290934645116
- **DendrogramPurity**: 0.47618392029810447
- **SphericalSilhouette**: 0.10476154552634931
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.141399416909621
- **TotalDasguptaCost**: 6.214540428094315E10
- **RoutingECE**: 0.20381383721848695
- **BrierScore**: 0.4625931483716876

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7572222222222222%
- **AnyMatchAccuracy**: 0.7730555555555556%
- **MacroF1**: 0.7471932975049794
- **AvgMatchCount**: 1.1275
- **BorderlineRate**: 0.10833333333333334
- **CrossAnchorMigrationRate**: 0.2427777777777778

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 0
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.7419354838709675
- **SoftDegreeMean**: 2.1769230769230767
- **EntropyGuardRate**: 0.9
- **SoftEffSampleSize**: 3649.2712546696207
- **SelectedNodeP10QueryCount**: 81.0
- **SelectedNodeLeafBalanceEntropy**: 4.035899967064877

#### F. Config Traceability
- **SHA256**: `c0a0d68b0906a3606fcaa874da23d3658816bd8b800797cc68f831394d7f1110`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 4: L9_004_seed42

**Config Factors**: `deltaAssign`=0.0015, `minClusterSize`=50, `secondaryMassFloor`=5.0, `bridgeSupportRelFraction`=0.05

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.0011160714285714285
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=160, LeafCount=98, BridgeCount=3, BridgeRatio=0.0188, ResidualCount=787

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7476483567529904
- **DendrogramPurity**: 0.4402598469480136
- **SphericalSilhouette**: 0.1089540050891341
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.08964504089573572
- **TotalDasguptaCost**: 6.189816566446237E10
- **RoutingECE**: 0.21029955172588352
- **BrierScore**: 0.4658762659389504

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7555803571428571%
- **AnyMatchAccuracy**: 0.7692522321428571%
- **MacroF1**: 0.7458536384944707
- **AvgMatchCount**: 1.1431361607142858
- **BorderlineRate**: 0.12165178571428571
- **CrossAnchorMigrationRate**: 0.24441964285714285

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 3
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.122448979591837
- **SoftDegreeMean**: 2.176605504587156
- **EntropyGuardRate**: 0.9013761467889908
- **SoftEffSampleSize**: 3640.1045041759658
- **SelectedNodeP10QueryCount**: 57.0
- **SelectedNodeLeafBalanceEntropy**: 4.521382254351018

#### F. Config Traceability
- **SHA256**: `82c0986dc6b96524cbf345ba8d2616c535e5cdfc87f6429a89c98f84935fd984`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 5: val_365af0c7_seed137

**Config Factors**: `deltaAssign`=0.003, `minClusterSize`=75, `secondaryMassFloor`=2.0, `bridgeSupportRelFraction`=0.05

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 2.782415136338342E-4
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=102, LeafCount=62, BridgeCount=2, BridgeRatio=0.0196, ResidualCount=711

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7210404624277457
- **DendrogramPurity**: 0.46369639746119606
- **SphericalSilhouette**: 0.10646712295571663
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.14100982162081588
- **TotalDasguptaCost**: 5.672976002889536E10
- **RoutingECE**: 0.20579750614994677
- **BrierScore**: 0.47416455344082736

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7420701168614358%
- **AnyMatchAccuracy**: 0.7565386755703951%
- **MacroF1**: 0.7333825295827083
- **AvgMatchCount**: 1.1085141903171953
- **BorderlineRate**: 0.10294936004451864
- **CrossAnchorMigrationRate**: 0.2417918753478019

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 2
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.6774193548387095
- **SoftDegreeMean**: 2.210810810810811
- **EntropyGuardRate**: 0.9
- **SoftEffSampleSize**: 3647.3401512321443
- **SelectedNodeP10QueryCount**: 89.0
- **SelectedNodeLeafBalanceEntropy**: 4.046202422422495

#### F. Config Traceability
- **SHA256**: `365af0c7679bcc99ecbc70baabb9de1bdd9960fce5cfa1399d5e52e003978331`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

