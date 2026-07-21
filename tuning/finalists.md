# TaxoArena — Tuning Finalists & Architectural Report

## 1. Executive Summary & Pareto Ranking

| Rank | Run ID | Stage | Seed | Hard | Soft | Dom | Top-1 Acc | AnyMatch | ECE | Borderline | Bridge Ratio | Migration | DeltaRho | SmallLeaf | SrcBDepth2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | L9_004_seed42 | screen | 42 | PASSED | FAILED | 0 | 74.86% | 81.11% | 0.1421 | 0.3839 | 0.00% | 0.2514 | 0.0000 | 0.0000 | 0 |
| 2 | L9_005_seed42 | screen | 42 | PASSED | FAILED | 0 | 73.92% | 79.89% | 0.1433 | 0.3253 | 1.22% | 0.2500 | 0.0000 | 0.0000 | 0 |
| 3 | L9_001_seed42 | screen | 42 | PASSED | FAILED | 0 | 73.42% | 76.11% | 0.1762 | 0.2169 | 2.15% | 0.2364 | 0.0000 | 0.0000 | 0 |
| 4 | L9_002_seed42 | screen | 42 | PASSED | FAILED | 0 | 71.92% | 79.69% | 0.1123 | 0.4961 | 2.36% | 0.2469 | 0.0000 | 0.0000 | 0 |
| 5 | L9_003_seed42 | screen | 42 | FAILED | FAILED | 0 | 66.17% | 84.78% | 0.0859 | 0.8303 | 9.41% | 0.3211 | 0.0000 | 0.0000 | 0 |

## 2. Gate Failure Explanations (Top 10 Runs)

### 1. Run: L9_004_seed42
- **Soft Gate Failures**: BorderlineRate = 0.3839 outside band [0.2, 0.35]

### 2. Run: L9_005_seed42
- **Soft Gate Failures**: Top1Accuracy = 73.92% < 74.0%

### 3. Run: L9_001_seed42
- **Soft Gate Failures**: Top1Accuracy = 73.42% < 74.0%; RoutingECE = 0.1762 > 0.15

### 4. Run: L9_002_seed42
- **Soft Gate Failures**: Top1Accuracy = 71.92% < 74.0%; BorderlineRate = 0.4961 outside band [0.2, 0.35]

### 5. Run: L9_003_seed42
- **Hard Gate Failures**: MaxAssignmentCapRate = 0.5597 > 0.2
- **Soft Gate Failures**: Top1Accuracy = 66.17% < 74.0%; BorderlineRate = 0.8303 outside band [0.2, 0.35]; CrossAnchorMigrationRate = 0.3211 outside band [0.1, 0.3]


## 3. Categorized Metric Summaries (Top 5 Finalists)

### Rank 1: L9_004_seed42

**Config Factors**: `assignmentCosineGap`=0.15, `deltaAssign`=1.0, `minClusterSize`=75, `routingSoftmaxTau`=2.0

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.03805555555555556
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=123, LeafCount=80, BridgeCount=0, BridgeRatio=0.0000, ResidualCount=1488

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.6403225806451613
- **DendrogramPurity**: 0.0018704615825372163
- **SphericalSilhouette**: 0.09299501794554449
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.10365661530705486
- **TotalDasguptaCost**: 5.443129368897255E10
- **RoutingECE**: 0.14210556626136026
- **BrierScore**: 0.42935664587522543

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7486111111111111%
- **AnyMatchAccuracy**: 0.8111111111111111%
- **MacroF1**: 0.731104127663532
- **AvgMatchCount**: 1.67
- **BorderlineRate**: 0.3838888888888889
- **CrossAnchorMigrationRate**: 0.2513888888888889

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 0
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.8375
- **SoftDegreeMean**: 2.7452966714905935
- **EntropyGuardRate**: 0.5463096960926194
- **SoftEffSampleSize**: 4254.943815657318
- **SelectedNodeP10QueryCount**: 106.0
- **SelectedNodeLeafBalanceEntropy**: 4.335820299212393

#### F. Config Traceability
- **SHA256**: `79e1dfb542e11250e3b81671d0ce3f967b18f34d13e75bd8c17e674307be8fb2`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 2: L9_005_seed42

**Config Factors**: `assignmentCosineGap`=0.15, `deltaAssign`=2.0, `minClusterSize`=100, `routingSoftmaxTau`=1.0

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.023333333333333334
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=82, LeafCount=55, BridgeCount=1, BridgeRatio=0.0122, ResidualCount=291

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.6490516100573445
- **DendrogramPurity**: 0.0019143091893285217
- **SphericalSilhouette**: 0.09600839815668767
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.1412639405204461
- **TotalDasguptaCost**: 5.2360071621928894E10
- **RoutingECE**: 0.14330560844856008
- **BrierScore**: 0.43711826354075195

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7391666666666666%
- **AnyMatchAccuracy**: 0.7988888888888889%
- **MacroF1**: 0.726727529474395
- **AvgMatchCount**: 1.5152777777777777
- **BorderlineRate**: 0.3252777777777778
- **CrossAnchorMigrationRate**: 0.25

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 1
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.381818181818182
- **SoftDegreeMean**: 2.6174210076857385
- **EntropyGuardRate**: 0.2237403928266439
- **SoftEffSampleSize**: 4297.165319744315
- **SelectedNodeP10QueryCount**: 135.0
- **SelectedNodeLeafBalanceEntropy**: 3.9662215629489

#### F. Config Traceability
- **SHA256**: `63862b01e84d2e67c133f0138ae9c5cbc00e540de8b7770183a40de7c567754d`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 3: L9_001_seed42

**Config Factors**: `assignmentCosineGap`=0.1, `deltaAssign`=1.0, `minClusterSize`=50, `routingSoftmaxTau`=1.0

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.006111111111111111
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=186, LeafCount=115, BridgeCount=4, BridgeRatio=0.0215, ResidualCount=637

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.7107541462396996
- **DendrogramPurity**: 0.002513522484100761
- **SphericalSilhouette**: 0.11286658168799303
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.07450980392156863
- **TotalDasguptaCost**: 4.941174390981244E10
- **RoutingECE**: 0.17624564452657498
- **BrierScore**: 0.4640678858595744

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7341666666666666%
- **AnyMatchAccuracy**: 0.7611111111111111%
- **MacroF1**: 0.7289925358171324
- **AvgMatchCount**: 1.28
- **BorderlineRate**: 0.21694444444444444
- **CrossAnchorMigrationRate**: 0.2363888888888889

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 4
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 3.208695652173913
- **SoftDegreeMean**: 2.4263764404609476
- **EntropyGuardRate**: 0.5633802816901409
- **SoftEffSampleSize**: 3931.4816306138628
- **SelectedNodeP10QueryCount**: 57.0
- **SelectedNodeLeafBalanceEntropy**: 4.706554051524791

#### F. Config Traceability
- **SHA256**: `5674a7e6903dcc17dbe56204dbc9ea0db89c55fd85bd60aaf39b826f8e57afb7`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 4: L9_002_seed42

**Config Factors**: `assignmentCosineGap`=0.1, `deltaAssign`=2.0, `minClusterSize`=75, `routingSoftmaxTau`=1.5

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.09083333333333334
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=127, LeafCount=78, BridgeCount=3, BridgeRatio=0.0236, ResidualCount=1511

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.5983567596930808
- **DendrogramPurity**: 0.0021923207061732702
- **SphericalSilhouette**: 0.0863092898717221
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.10705243879447332
- **TotalDasguptaCost**: 4.861751968400927E10
- **RoutingECE**: 0.1123413243525715
- **BrierScore**: 0.4472197945796155

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.7191666666666666%
- **AnyMatchAccuracy**: 0.7969444444444445%
- **MacroF1**: 0.7146139114944567
- **AvgMatchCount**: 1.976388888888889
- **BorderlineRate**: 0.4961111111111111
- **CrossAnchorMigrationRate**: 0.24694444444444444

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 3
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.9358974358974357
- **SoftDegreeMean**: 3.036394176931691
- **EntropyGuardRate**: 0.24356103023516237
- **SoftEffSampleSize**: 4722.898084144068
- **SelectedNodeP10QueryCount**: 121.0
- **SelectedNodeLeafBalanceEntropy**: 4.3092408813650085

#### F. Config Traceability
- **SHA256**: `43e711a5394be66544e471e862f7b77972f4784108379fb8f2bf2a82d22fe4d9`
- **Hard Gates Passed**: True, **Soft Gates Passed**: False, **Dominance Count**: 0

---

### Rank 5: L9_003_seed42

**Config Factors**: `assignmentCosineGap`=0.1, `deltaAssign`=4.0, `minClusterSize`=100, `routingSoftmaxTau`=2.0

#### A. Structural Integrity (Hard Gates)
- **Acyclic**: true
- **RootReachable**: true
- **OrphanCount**: 0
- **DuplicateBridgeCount**: 0 *(excl. empty child sets)*
- **MaxAssignmentCapRate**: 0.5597222222222222
- **SmallLeafFraction**: 0.0
- **SelectedNodeStarvedLeafFraction**: 0.0
- **SourceBPerAnchorMean**: 0.0
- **Topology Counts**: TotalNodes=85, LeafCount=51, BridgeCount=8, BridgeRatio=0.0941, ResidualCount=2123

#### B. Taxonomy Quality (Pareto Objectives)
- **WeightedLeafPurity**: 0.5410740453409189
- **DendrogramPurity**: 0.001544165995574299
- **SphericalSilhouette**: 0.0740330184047154
- **DeltaRhoTotal**: 0.0
- **CanonicalAdaptedJaccard**: 0.13297872340425532
- **TotalDasguptaCost**: 4.772169633523554E10
- **RoutingECE**: 0.0859117812781644
- **BrierScore**: 0.5092008590064431

#### C. Routing & Arena Performance (Soft Gates)
- **Top1Accuracy**: 0.6616666666666666%
- **AnyMatchAccuracy**: 0.8477777777777777%
- **MacroF1**: 0.6453813317275848
- **AvgMatchCount**: 3.7316666666666665
- **BorderlineRate**: 0.8302777777777778
- **CrossAnchorMigrationRate**: 0.3211111111111111

#### D. Bridge & Cross-Domain Diagnostics
- **SourceA_Count**: 8
- **SourceB_Count**: 0
- **SourceBDepth2Count**: 0
- **SourceBPerAnchorMean**: 0.0
- **RhoCanonicalHard**: 0.0, **RhoAdaptedHard**: 0.0, **RhoAdaptedSoft**: 0.0
- **DeltaRhoGeom**: 0.0, **DeltaRhoSoft**: 0.0

#### E. Distributional / Balance Diagnostics
- **NormalisedSackinIndex**: 2.7254901960784315
- **SoftDegreeMean**: 4.3108062897290065
- **EntropyGuardRate**: 0.11876881900301103
- **SoftEffSampleSize**: 5493.745367164563
- **SelectedNodeP10QueryCount**: 208.0
- **SelectedNodeLeafBalanceEntropy**: 3.799885167925952

#### F. Config Traceability
- **SHA256**: `1e94b4f12562fecb3b4f4545167117206729f1e21c1419e6eb662b79372d8ebe`
- **Hard Gates Passed**: False, **Soft Gates Passed**: False, **Dominance Count**: 0

---

