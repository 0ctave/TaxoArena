# TaxoArena — Tuning Finalists & Architectural Report

## 1. Executive Summary & Pareto Ranking

| Rank | Run ID | Stage | Seed | Hard | Soft | Dom | Top-1 Acc | AnyMatch | ECE | Borderline | Bridge Ratio | Migration | DeltaRho | SmallLeaf | SrcBDepth2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | L9_006_seed42 | screen | 42 | FAILED | FAILED | 0 | 74.22% | 91.50% | 0.0960 | 1.0000 | 10.62% | 0.2578 | 0.0000 | 0.2958 | 0 |
| 2 | L9_001_seed42 | screen | 42 | FAILED | FAILED | 0 | 71.94% | 74.50% | 0.1738 | 0.2169 | 3.45% | 0.2292 | 0.0000 | 0.0000 | 0 |
| 3 | L9_004_seed42 | screen | 42 | FAILED | FAILED | 0 | 71.75% | 77.28% | 0.1426 | 0.3458 | 3.75% | 0.2436 | 0.0000 | 0.0000 | 0 |
| 4 | L9_009_seed42 | screen | 42 | FAILED | FAILED | 0 | 71.75% | 87.14% | 0.1009 | 0.9381 | 12.38% | 0.2761 | 0.0000 | 0.0879 | 0 |
| 5 | L9_007_seed42 | screen | 42 | FAILED | FAILED | 0 | 71.69% | 76.03% | 0.1512 | 0.2506 | 3.39% | 0.2461 | 0.0000 | 0.0000 | 0 |
| 6 | L9_008_seed42 | screen | 42 | FAILED | FAILED | 0 | 71.56% | 89.19% | 0.0926 | 0.9297 | 22.83% | 0.2806 | 0.0000 | 0.1340 | 0 |
| 7 | L9_003_seed42 | screen | 42 | FAILED | FAILED | 0 | 69.58% | 89.75% | 0.0597 | 0.9986 | 16.00% | 0.3042 | 0.0000 | 0.0968 | 0 |
| 8 | L9_005_seed42 | screen | 42 | FAILED | FAILED | 0 | 68.28% | 76.89% | 0.1535 | 0.5119 | 7.81% | 0.2553 | 0.0000 | 0.0000 | 0 |
| 9 | L9_002_seed42 | screen | 42 | FAILED | FAILED | 0 | 68.22% | 81.92% | 0.1054 | 0.7517 | 13.54% | 0.2692 | 0.0000 | 0.0488 | 0 |
| 10 | L9_001_seed42 | screen | 42 | FAILED | FAILED | 0 | 3.33% | 0.64% | 4.0000 | 0.7597 | 3.36% | 0.5894 | 0.0000 | 0.0000 | 4 |

## 2. Gate Failure Explanations (Top 10 Runs)

### 1. Run: L9_006_seed42
- **Hard Gate Failures**: DuplicateBridgeCount = 7 > 0; MaxAssignmentCapRate = 0.9944 > 0.2
- **Soft Gate Failures**: AvgMatchCount = 4.9914 outside band [1.0, 4.0]; BorderlineRate = 1.0000 outside band [0.2, 0.35]

### 2. Run: L9_001_seed42
- **Hard Gate Failures**: DuplicateBridgeCount = 2 > 0
- **Soft Gate Failures**: Top1Accuracy = 71.94% < 74.0%; RoutingECE = 0.1738 > 0.15

### 3. Run: L9_004_seed42
- **Hard Gate Failures**: DuplicateBridgeCount = 2 > 0
- **Soft Gate Failures**: Top1Accuracy = 71.75% < 74.0%

### 4. Run: L9_009_seed42
- **Hard Gate Failures**: DuplicateBridgeCount = 7 > 0; MaxAssignmentCapRate = 0.8192 > 0.2
- **Soft Gate Failures**: AvgMatchCount = 4.4958 outside band [1.0, 4.0]; Top1Accuracy = 71.75% < 74.0%; BorderlineRate = 0.9381 outside band [0.2, 0.35]

### 5. Run: L9_007_seed42
- **Hard Gate Failures**: DuplicateBridgeCount = 1 > 0
- **Soft Gate Failures**: Top1Accuracy = 71.69% < 74.0%; RoutingECE = 0.1512 > 0.15

### 6. Run: L9_008_seed42
- **Hard Gate Failures**: DuplicateBridgeCount = 11 > 0; MaxAssignmentCapRate = 0.7189 > 0.2
- **Soft Gate Failures**: AvgMatchCount = 4.2931 outside band [1.0, 4.0]; Top1Accuracy = 71.56% < 74.0%; BorderlineRate = 0.9297 outside band [0.2, 0.35]

### 7. Run: L9_003_seed42
- **Hard Gate Failures**: DuplicateBridgeCount = 4 > 0; MaxAssignmentCapRate = 0.9847 > 0.2
- **Soft Gate Failures**: AvgMatchCount = 4.9678 outside band [1.0, 4.0]; Top1Accuracy = 69.58% < 74.0%; BorderlineRate = 0.9986 outside band [0.2, 0.35]; CrossAnchorMigrationRate = 0.3042 outside band [0.1, 0.3]

### 8. Run: L9_005_seed42
- **Hard Gate Failures**: DuplicateBridgeCount = 3 > 0
- **Soft Gate Failures**: Top1Accuracy = 68.28% < 74.0%; RoutingECE = 0.1535 > 0.15; BorderlineRate = 0.5119 outside band [0.2, 0.35]

### 9. Run: L9_002_seed42
- **Hard Gate Failures**: DuplicateBridgeCount = 6 > 0; MaxAssignmentCapRate = 0.4081 > 0.2
- **Soft Gate Failures**: Top1Accuracy = 68.22% < 74.0%; BorderlineRate = 0.7517 outside band [0.2, 0.35]

### 10. Run: L9_001_seed42
- **Hard Gate Failures**: MaxAssignmentCapRate = 1.2753 > 0.2
- **Soft Gate Failures**: AvgMatchCount = 0.1755 outside band [1.0, 4.0]; Top1Accuracy = 3.33% < 74.0%; RoutingECE = 4.0000 > 0.15; BorderlineRate = 0.7597 outside band [0.2, 0.35]; CrossAnchorMigrationRate = 0.5894 outside band [0.1, 0.3]; CanonicalAdaptedJaccard = 3913.2531 outside band [0.0, 1.0]


## 3. Categorized Metric Summaries (Top 5 Finalists)

### Rank 1: L9_006_seed42

**Config Factors**: `assignmentCosineGap`=0.15, `deltaAssign`=10.0, `minClusterSize`=50, `routingSoftmaxTau`=1.5

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 7 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.9944444444444445
- **SmallLeafFraction**: 0.29577464788732394
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=, LeafCount=142, BridgeCount=17, BridgeRatio=, ResidualCount=38075

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.6554596747427813
- **DendrogramPurity**: 0.0029357281234030277
- **SphericalSilhouette**: 0.0909173015703451
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.05633632544503883
- **TotalDasguptaCost**: 5.1909973387290985E10
- **RoutingECE**: 0.09604667943386835
- **BrierScore**: 0.41447434804959987

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7422222222222222%
- **AnyMatchAccuracy**: 0.915%
- **MacroF1**: 0.7302266400457543
- **AvgMatchCount**: 4.991388888888889
- **BorderlineRate**: 1.0
- **CrossAnchorMigrationRate**: 0.2577777777777778

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 17
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.4859154929577465
- **SoftDegreeMean**: 4.991388888888889
- **EntropyGuardRate**: 0.09111111111111111
- **SoftEffSampleSize**: 5652.079271631471
- **SelectedNodeP10QueryCount**: 76.0
- **SelectedNodeLeafBalanceEntropy**: 4.762532577844958

#### F. Config Traceability
- **SHA256**: `01db3dff686a689a1480ee0367fa3446f3cc8c5b915e62f7408959b69369255e`
- **Hard Gates Passed**: False, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 2: L9_001_seed42

**Config Factors**: `assignmentCosineGap`=0.1, `deltaAssign`=1.0, `minClusterSize`=50, `routingSoftmaxTau`=1.0

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 2 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.006111111111111111
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=, LeafCount=111, BridgeCount=4, BridgeRatio=, ResidualCount=680

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.713703624276217
- **DendrogramPurity**: 0.0026499871633004035
- **SphericalSilhouette**: 0.11343967115532162
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.07407407407407407
- **TotalDasguptaCost**: 4.673829454643108E10
- **RoutingECE**: 0.1738241250469722
- **BrierScore**: 0.4709445902576059

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7194444444444444%
- **AnyMatchAccuracy**: 0.745%
- **MacroF1**: 0.7239002632145344
- **AvgMatchCount**: 1.2491666666666668
- **BorderlineRate**: 0.21694444444444444
- **CrossAnchorMigrationRate**: 0.22916666666666666

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 4
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.2432432432432434
- **SoftDegreeMean**: 2.385403329065301
- **EntropyGuardRate**: 0.5685019206145967
- **SoftEffSampleSize**: 3921.4659218861957
- **SelectedNodeP10QueryCount**: 58.0
- **SelectedNodeLeafBalanceEntropy**: 4.670473010427459

#### F. Config Traceability
- **SHA256**: `5674a7e6903dcc17dbe56204dbc9ea0db89c55fd85bd60aaf39b826f8e57afb7`
- **Hard Gates Passed**: False, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 3: L9_004_seed42

**Config Factors**: `assignmentCosineGap`=0.15, `deltaAssign`=1.0, `minClusterSize`=75, `routingSoftmaxTau`=2.0

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 2 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.03166666666666667
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=, LeafCount=76, BridgeCount=3, BridgeRatio=, ResidualCount=1346

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.6449621837781448
- **DendrogramPurity**: 0.0022173397605049217
- **SphericalSilhouette**: 0.09325238493796345
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.10865008941691062
- **TotalDasguptaCost**: 4.792758763262902E10
- **RoutingECE**: 0.14263098326778675
- **BrierScore**: 0.45427851725814067

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7175%
- **AnyMatchAccuracy**: 0.7727777777777778%
- **MacroF1**: 0.7150531265005947
- **AvgMatchCount**: 1.5569444444444445
- **BorderlineRate**: 0.3458333333333333
- **CrossAnchorMigrationRate**: 0.2436111111111111

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 3
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.789473684210526
- **SoftDegreeMean**: 2.7228915662650603
- **EntropyGuardRate**: 0.5622489959839357
- **SoftEffSampleSize**: 4152.850468536112
- **SelectedNodeP10QueryCount**: 93.0
- **SelectedNodeLeafBalanceEntropy**: 4.285545265657962

#### F. Config Traceability
- **SHA256**: `79e1dfb542e11250e3b81671d0ce3f967b18f34d13e75bd8c17e674307be8fb2`
- **Hard Gates Passed**: False, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 4: L9_009_seed42

**Config Factors**: `assignmentCosineGap`=0.2, `deltaAssign`=10.0, `minClusterSize`=75, `routingSoftmaxTau`=1.0

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 7 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.8191666666666667
- **SmallLeafFraction**: 0.08791208791208792
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=, LeafCount=91, BridgeCount=13, BridgeRatio=, ResidualCount=4176

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.5913339857591199
- **DendrogramPurity**: 0.0039718305678530415
- **SphericalSilhouette**: 0.07481494365227401
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.07228915662650602
- **TotalDasguptaCost**: 5.027218001688225E10
- **RoutingECE**: 0.10093649400210158
- **BrierScore**: 0.45768229992877013

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7175%
- **AnyMatchAccuracy**: 0.8713888888888889%
- **MacroF1**: 0.6982453746819773
- **AvgMatchCount**: 4.495833333333334
- **BorderlineRate**: 0.9380555555555555
- **CrossAnchorMigrationRate**: 0.2761111111111111

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 13
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.087912087912088
- **SoftDegreeMean**: 4.73349126443589
- **EntropyGuardRate**: 0.04234527687296417
- **SoftEffSampleSize**: 5034.768454309423
- **SelectedNodeP10QueryCount**: 131.0
- **SelectedNodeLeafBalanceEntropy**: 4.380611803621784

#### F. Config Traceability
- **SHA256**: `28140cd35981029f4a43060b631a0a877655a2572ed4eacd305a0bc9c61ff042`
- **Hard Gates Passed**: False, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 5: L9_007_seed42

**Config Factors**: `assignmentCosineGap`=0.2, `deltaAssign`=1.0, `minClusterSize`=100, `routingSoftmaxTau`=1.5

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 1 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.009722222222222222
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=, LeafCount=56, BridgeCount=2, BridgeRatio=, ResidualCount=600

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.673967396739674
- **DendrogramPurity**: 0.002039854630851975
- **SphericalSilhouette**: 0.09580917598886912
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.14455825864276567
- **TotalDasguptaCost**: 4.8303908332064835E10
- **RoutingECE**: 0.1511776217807998
- **BrierScore**: 0.46532751256440147

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7169444444444445%
- **AnyMatchAccuracy**: 0.7602777777777778%
- **MacroF1**: 0.7157789017474352
- **AvgMatchCount**: 1.3269444444444445
- **BorderlineRate**: 0.25055555555555553
- **CrossAnchorMigrationRate**: 0.2461111111111111

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 2
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.4464285714285716
- **SoftDegreeMean**: 2.4523281596452327
- **EntropyGuardRate**: 0.5776053215077606
- **SoftEffSampleSize**: 3975.8362522879293
- **SelectedNodeP10QueryCount**: 120.0
- **SelectedNodeLeafBalanceEntropy**: 3.989119738581531

#### F. Config Traceability
- **SHA256**: `f6a990eabea2739aaa76ff9501eef405203bb62b2153df814565e040b4fa1432`
- **Hard Gates Passed**: False, **Soft Gates Passed**: False, **Dominance Count**: 0

---

