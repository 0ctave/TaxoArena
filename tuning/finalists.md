# TaxoArena — Tuning Finalists & Architectural Report

## 1. Executive Summary & Pareto Ranking

| Rank | Run ID | Stage | Seed | Hard | Soft | Dom | Top-1 Acc | AnyMatch | ECE | Borderline | Bridge Ratio | Migration | DeltaRho | SmallLeaf | SrcBDepth2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | L9_007_seed42 | screen | 42 | PASSED | PASSED | 0 | 74.14% | 77.26% | 0.1799 | 0.2514 | 1.30% | 0.2586 | 0.0000 | 0.0102 | 0 |
| 2 | L9_004_seed42 | screen | 42 | PASSED | PASSED | 0 | 73.91% | 77.12% | 0.2094 | 0.1551 | 0.00% | 0.2609 | 0.0000 | 0.0000 | 0 |
| 3 | L9_001_seed42 | screen | 42 | PASSED | PASSED | 0 | 73.74% | 77.09% | 0.1831 | 0.2467 | 0.00% | 0.2623 | 0.0000 | 0.0377 | 0 |
| 4 | L9_006_seed42 | screen | 42 | PASSED | PASSED | 0 | 73.74% | 74.44% | 0.2453 | 0.0583 | 0.70% | 0.2626 | 0.0000 | 0.0330 | 0 |
| 5 | L9_009_seed42 | screen | 42 | PASSED | PASSED | 0 | 73.66% | 74.19% | 0.2418 | 0.0631 | 0.00% | 0.2634 | 0.0000 | 0.0000 | 0 |
| 6 | L9_002_seed42 | screen | 42 | PASSED | PASSED | 0 | 73.55% | 75.36% | 0.2071 | 0.1462 | 0.60% | 0.2640 | 0.0000 | 0.0000 | 0 |
| 7 | L9_008_seed42 | screen | 42 | PASSED | PASSED | 0 | 73.27% | 75.08% | 0.2251 | 0.1060 | 0.00% | 0.2673 | 0.0000 | 0.0000 | 0 |
| 8 | L9_003_seed42 | screen | 42 | PASSED | PASSED | 0 | 73.02% | 73.69% | 0.2494 | 0.0446 | 0.00% | 0.2698 | 0.0000 | 0.0000 | 0 |
| 9 | L9_005_seed42 | screen | 42 | PASSED | PASSED | 0 | 72.71% | 74.16% | 0.2245 | 0.1373 | 0.00% | 0.2729 | 0.0000 | 0.0000 | 0 |

## 2. Gate Failure Explanations (Top 10 Runs)


## 3. Categorized Metric Summaries (Top 5 Finalists)

### Rank 1: L9_007_seed42

**Config Factors**: `proposalSeparationBar`=0.02, `descentMargin`=0.18, `minClusterSize`=35, `membershipFloor`=0.15

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.0
- **SmallLeafFraction**: 0.01020408163265306
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=154, LeafCount=98, BridgeCount=2, BridgeRatio=0.0130, ResidualCount=0

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7179942749975323
- **DendrogramPurity**: 0.4500522360001379
- **SphericalSilhouette**: 0.11110514422471811
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.07537688442211055
- **TotalDasguptaCost**: 6.5211647664279175E10
- **RoutingECE**: 0.17993674807095666
- **BrierScore**: 0.46760049726768455

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7413504464285714%
- **AnyMatchAccuracy**: 0.7726004464285714%
- **MacroF1**: 0.7221939276043496
- **AvgMatchCount**: 1.2974330357142858
- **BorderlineRate**: 0.2513950892857143
- **CrossAnchorMigrationRate**: 0.25864955357142855

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 2
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.13265306122449
- **SoftDegreeMean**: 2.183129855715871
- **EntropyGuardRate**: 0.41287458379578246
- **SoftEffSampleSize**: 3961.06698069313
- **SelectedNodeP10QueryCount**: 54.0
- **SelectedNodeLeafBalanceEntropy**: 4.42144548229063

#### F. Config Traceability
- **SHA256**: `b4dd7620014ec8f93f9a429affd041c7ad23326ae9966232b8deca41d5890755`
- **Hard Gates Passed**: True, **Soft Gates Passed**: True, **Dominance Count**: 0

---

### Rank 2: L9_004_seed42

**Config Factors**: `proposalSeparationBar`=0.03, `descentMargin`=0.12, `minClusterSize`=30, `membershipFloor`=0.15

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.0
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=61, LeafCount=41, BridgeCount=0, BridgeRatio=0.0000, ResidualCount=0

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7121652480797177
- **DendrogramPurity**: 0.4649903186690043
- **SphericalSilhouette**: 0.11678914041690334
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.19791666666666666
- **TotalDasguptaCost**: 6.5401715269084724E10
- **RoutingECE**: 0.20937275199167812
- **BrierScore**: 0.4780068586952213

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7391183035714286%
- **AnyMatchAccuracy**: 0.7712053571428571%
- **MacroF1**: 0.7196121880703664
- **AvgMatchCount**: 1.1721540178571428
- **BorderlineRate**: 0.15513392857142858
- **CrossAnchorMigrationRate**: 0.26088169642857145

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 0
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.4146341463414633
- **SoftDegreeMean**: 2.1097122302158273
- **EntropyGuardRate**: 0.3669064748201439
- **SoftEffSampleSize**: 3818.191154991826
- **SelectedNodeP10QueryCount**: 62.0
- **SelectedNodeLeafBalanceEntropy**: 3.484564334502518

#### F. Config Traceability
- **SHA256**: `c80b154abf94363f91258d2fd6c9ed1c89d2ae7152ba3e720dbb13e9323a29f8`
- **Hard Gates Passed**: True, **Soft Gates Passed**: True, **Dominance Count**: 0

---

### Rank 3: L9_001_seed42

**Config Factors**: `proposalSeparationBar`=0.01, `descentMargin`=0.06, `minClusterSize`=25, `membershipFloor`=0.15

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.0
- **SmallLeafFraction**: 0.03773584905660377
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=158, LeafCount=106, BridgeCount=0, BridgeRatio=0.0000, ResidualCount=0

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7162832209440698
- **DendrogramPurity**: 0.46819382026332473
- **SphericalSilhouette**: 0.11275018644624756
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.06813654618473897
- **TotalDasguptaCost**: 6.569351800898109E10
- **RoutingECE**: 0.18314280871691443
- **BrierScore**: 0.47473299762053867

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7374441964285714%
- **AnyMatchAccuracy**: 0.7709263392857143%
- **MacroF1**: 0.7188127480190353
- **AvgMatchCount**: 1.291015625
- **BorderlineRate**: 0.24665178571428573
- **CrossAnchorMigrationRate**: 0.2622767857142857

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 0
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.0
- **SoftDegreeMean**: 2.180995475113122
- **EntropyGuardRate**: 0.40497737556561086
- **SoftEffSampleSize**: 3959.585057370448
- **SelectedNodeP10QueryCount**: 35.0
- **SelectedNodeLeafBalanceEntropy**: 4.437886804283561

#### F. Config Traceability
- **SHA256**: `a37411017ba0facaa247a72dc0edc9f2e9faa8572244ce10507e2fac9ff3e63e`
- **Hard Gates Passed**: True, **Soft Gates Passed**: True, **Dominance Count**: 0

---

### Rank 4: L9_006_seed42

**Config Factors**: `proposalSeparationBar`=0.02, `descentMargin`=0.12, `minClusterSize`=25, `membershipFloor`=0.35

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.0
- **SmallLeafFraction**: 0.03296703296703297
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=143, LeafCount=91, BridgeCount=1, BridgeRatio=0.0070, ResidualCount=0

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7407067462138596
- **DendrogramPurity**: 0.46518207933913847
- **SphericalSilhouette**: 0.12705232378050332
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.07575757575757576
- **TotalDasguptaCost**: 6.5133489174202484E10
- **RoutingECE**: 0.24525028359603607
- **BrierScore**: 0.5133756645013124

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7374441964285714%
- **AnyMatchAccuracy**: 0.7444196428571429%
- **MacroF1**: 0.7190740224853622
- **AvgMatchCount**: 1.0583147321428572
- **BorderlineRate**: 0.058314732142857144
- **CrossAnchorMigrationRate**: 0.26255580357142855

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 1
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.120879120879121
- **SoftDegreeMean**: 2.0
- **EntropyGuardRate**: 1.0
- **SoftEffSampleSize**: 3584.0
- **SelectedNodeP10QueryCount**: 32.0
- **SelectedNodeLeafBalanceEntropy**: 4.2217077238705425

#### F. Config Traceability
- **SHA256**: `1d72fb3e00ecc14eebc6e767611f2d3fb1ecb3a7d372f7081994162a1716f344`
- **Hard Gates Passed**: True, **Soft Gates Passed**: True, **Dominance Count**: 0

---

### Rank 5: L9_009_seed42

**Config Factors**: `proposalSeparationBar`=0.01, `descentMargin`=0.18, `minClusterSize`=30, `membershipFloor`=0.35

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.0
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=137, LeafCount=91, BridgeCount=0, BridgeRatio=0.0000, ResidualCount=0

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.742369020501139
- **DendrogramPurity**: 0.469451573551495
- **SphericalSilhouette**: 0.1220153749649325
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.08823529411764706
- **TotalDasguptaCost**: 6.5074964121319084E10
- **RoutingECE**: 0.24177028238003268
- **BrierScore**: 0.5123678034572813

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7366071428571429%
- **AnyMatchAccuracy**: 0.7419084821428571%
- **MacroF1**: 0.7182913460539396
- **AvgMatchCount**: 1.0630580357142858
- **BorderlineRate**: 0.06305803571428571
- **CrossAnchorMigrationRate**: 0.26339285714285715

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 0
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.923076923076923
- **SoftDegreeMean**: 2.0
- **EntropyGuardRate**: 1.0
- **SoftEffSampleSize**: 3584.0
- **SelectedNodeP10QueryCount**: 43.0
- **SelectedNodeLeafBalanceEntropy**: 4.3046320061912695

#### F. Config Traceability
- **SHA256**: `09a131552ae56771be9910af551b6966119726b855c1ba0b04bafdcc99fecd3e`
- **Hard Gates Passed**: True, **Soft Gates Passed**: True, **Dominance Count**: 0

---

