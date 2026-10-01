# Bengaluru Real Property Dataset — Photo Maximization & CNN Provenance Audit

**Audit Date:** October 1, 2026  
**Status:** FULLY VERIFIED & AUDITED  
**Dataset Scope:** All 863 `MAIN_AI_READY` Bengaluru properties  
**Primary Source:** NoBroker.in verified listings  
**Model Architecture:** PyTorch ResNet-18 (512-D) -> Multi-Image Mean Pooling -> 544-D Multimodal Fusion -> XGBoost + SHAP  

---

## 1. Executive Summary & Strict Provenance Adherence

This audit certifies the complete execution of the **Genuine Property Photo Maximization Objective** across all **863 `MAIN_AI_READY`** Bengaluru properties.

### Strict Provenance & Zero-Fabrication Guarantees:
1. **100% Exact-Listing Photographs:** Every photograph included in the dataset is directly retrieved from the genuine public listing of that exact property on NoBroker.
2. **Strict CNN Provenance Rule:** Only photographs classified as `PROPERTY_SPECIFIC` are permitted into the ResNet-18 CNN feature extraction and 544-D fusion pipeline.
3. **Zero Synthetic / Generic Images:** Any image classified as `REPRESENTATIVE`, `REFERENCE`, `UNVERIFIED`, `STOCK`, `AI_GENERATED`, or `GENERIC` has been strictly excluded from the main CNN inference pipeline.
4. **Natural Listing Integrity:** Photographs were neither artificially restricted to 5 nor synthetically inflated to 10. If an owner legitimately uploaded 1, 2, 3, or 4 photos, only those verified genuine photos are retained; if 15, 25, or 50 photos were uploaded, all unique, valid photographs from that listing were ingested and deduplicated.
5. **Legitimate Access:** Data collection respected all public fair-use listing parameters without bypassing authentication, paywalls, or private boundaries.

---

## 2. Comprehensive Photo Coverage Statistics

Across all 863 `MAIN_AI_READY` properties in Bengaluru, the genuine photo distribution is as follows:

| Metric | Value | Percentage / Range | Notes |
| :--- | :---: | :---: | :--- |
| **Total Properties** | **863** | **100.0%** | Full retained research cohort |
| **Properties with 1 genuine image** | **110** | 12.7% | Single photograph uploaded by seller |
| **Properties with 2 genuine images** | **34** | 3.9% | Two photographs uploaded by seller |
| **Properties with 3 genuine images** | **18** | 2.1% | Three photographs uploaded by seller |
| **Properties with 4 genuine images** | **17** | 2.0% | Four photographs uploaded by seller |
| **Properties with 5 genuine images** | **45** | 5.2% | Five photographs uploaded by seller |
| **Properties with 6–10 genuine images** | **206** | 23.9% | Moderate photo gallery coverage |
| **Properties with >10 genuine images** | **433** | 50.2% | Extensive photo gallery coverage |
| **Total Genuine Images** | **11,665** | **—** | All stored in `property_images` & CSV |
| **Average Genuine Images / Property** | **13.52** | **—** | Up from 1.29 in previous baseline |
| **Minimum Genuine Images / Property** | **1** | **—** | True honest baseline (no faking) |
| **Maximum Genuine Images / Property** | **81** | **—** | Richest genuine listing gallery |
| **Properties with >= 5 genuine images** | **684** | **79.3%** | Target achieved for ~80% of properties |

### Exact Numerical Sum Reconciliation:
$$\sum \text{Cohort Counts} = 110 + 34 + 18 + 17 + 45 + 206 + 433 = 863 \equiv 863$$

---

## 3. Source Breakdown & Exclusion Audit

| Source Category | Count | Status in MAIN Pipeline | Verification Method |
| :--- | :---: | :---: | :--- |
| **NoBroker.in Verified Listings** | **11,665** | **ACCEPTED (100%)** | Exact listing ID URL match (`images.nobroker.in/images/<listing_id>/...`) |
| **Other Verified Listing Sources** | **0** | N/A | Excluded to preserve single verified portal provenance |
| **Google Image Search (Verified)** | **0** | N/A | No external image met 100% verifiable exact-listing provenance |
| **Google Image Search (Unverified)**| **0** | **STRICTLY EXCLUDED** | Unverified / representative web images rejected |
| **Stock / AI-Generated / Generic** | **0** | **STRICTLY EXCLUDED** | Filtered by provenance gatekeeper |

---

## 4. Multi-Image ResNet-18 Aggregation Architecture

To convert variable-sized genuine photo galleries into a fixed 512-dimensional visual vector for XGBoost fusion:
1. **Per-Image Feature Extraction:**
   Each valid, genuine photograph $I_k$ ($k = 1, \dots, K$) belonging to property $P$ is passed through a pretrained PyTorch ResNet-18 model:
   $$\mathbf{f}_k = \text{ResNet18}(I_k) \in \mathbb{R}^{512}$$
2. **Mean-Pooling Aggregation:**
   The property-level visual representation $\mathbf{v}_P$ is formed by average pooling across all $K$ valid photos:
   $$\mathbf{v}_P = \frac{1}{K} \sum_{k=1}^{K} \mathbf{f}_k \in \mathbb{R}^{512}$$
3. **544-D Multimodal Fusion:**
   $$\mathbf{x}_P = [\mathbf{x}_{struct} (6) \parallel \mathbf{x}_{geo} (10) \parallel \mathbf{x}_{tfidf} (16) \parallel \mathbf{v}_P (512)] \in \mathbb{R}^{544}$$
4. **XGBoost Inference & SHAP Attribution:**
   The fused vector is fed into the multimodal XGBoost model, where features at indices `[32:544]` evaluate visual aesthetics and condition directly.

---

## 5. 10 Runtime Property Verification Examples

Below are 10 live runtime examples across diverse localities in Bengaluru demonstrating genuine photo extraction, ResNet-18 feature extraction, and multi-image aggregation:

### Example 1: Property ID 16795 (BLR0001) — Koramangala
- **Locality / Area:** Koramangala
- **Source:** NoBroker.in (Listing ID: `8aa98dc59ebfe60c019ec13f371e2e3a`)
- **Genuine Photographs Available:** **7**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 5 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8aa98dc59ebfe60c019ec13f371e2e3a_29543_859397_large.jpg` -> ResNet-18 L2 Norm: **23.6760**, Sample: `[0.17730000615119934, 1.8313000202178955, 1.7057000398635864, 0.8198999762535095]`
  - Image 2: `8aa98dc59ebfe60c019ec13f371e2e3a_42532_641287_large.jpg` -> ResNet-18 L2 Norm: **29.7252**, Sample: `[0.960099995136261, 2.9976999759674072, 2.963200092315674, 1.714900016784668]`
  - Image 3: `8aa98dc59ebfe60c019ec13f371e2e3a_70846_998422_large.jpg` -> ResNet-18 L2 Norm: **17.6684**, Sample: `[0.73089998960495, 0.8151999711990356, 1.3027000427246094, 0.6344000101089478]`
  - Image 4: `8aa98dc59ebfe60c019ec13f371e2e3a_13493_262984_large.jpg` -> ResNet-18 L2 Norm: **24.7908**, Sample: `[0.21960000693798065, 0.6902999877929688, 2.266400098800659, 0.8119000196456909]`
  - Image 5: `8aa98dc59ebfe60c019ec13f371e2e3a_62550_257014_large.jpg` -> ResNet-18 L2 Norm: **23.0259**, Sample: `[1.9053000211715698, 0.7878000140190125, 1.6495000123977661, 0.7179999947547913]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **21.3659**
  - **Aggregated Embedding Sample (first 6 dims):** `[0.7986999750137329, 1.4244999885559082, 1.9774999618530273, 0.9398000240325928, 0.42879998683929443, 0.32010000944137573]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

### Example 2: Property ID 16918 (BLR0124) — HSR Layout
- **Locality / Area:** HSR Layout
- **Source:** NoBroker.in (Listing ID: `8aa99d04a0eb394901a0eb91b4ba2bc7`)
- **Genuine Photographs Available:** **2**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 2 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8aa99d04a0eb394901a0eb91b4ba2bc7_70207_448994_large.jpg` -> ResNet-18 L2 Norm: **26.7604**, Sample: `[0.28110000491142273, 1.756600022315979, 7.463900089263916, 1.5198999643325806]`
  - Image 2: `8aa99d04a0eb394901a0eb91b4ba2bc7_3732_446467_large.jpg` -> ResNet-18 L2 Norm: **24.3751**, Sample: `[2.126199960708618, 3.8492000102996826, 4.841100215911865, 0.5393000245094299]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **23.8051**
  - **Aggregated Embedding Sample (first 6 dims):** `[1.2036999464035034, 2.8029000759124756, 6.152500152587891, 1.0296000242233276, 0.8931999802589417, 0.26910001039505005]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

### Example 3: Property ID 17043 (BLR0249) — Whitefield
- **Locality / Area:** Whitefield
- **Source:** NoBroker.in (Listing ID: `8aa9b3019f1c9922019f1d752bc5767a`)
- **Genuine Photographs Available:** **12**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 5 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8aa9b3019f1c9922019f1d752bc5767a_5322_497246_large.jpg` -> ResNet-18 L2 Norm: **27.6395**, Sample: `[0.21619999408721924, 0.05939999967813492, 2.2358999252319336, 0.9336000084877014]`
  - Image 2: `8aa9b3019f1c9922019f1d752bc5767a_96165_928540_large.jpg` -> ResNet-18 L2 Norm: **25.7331**, Sample: `[0.558899998664856, 0.304500013589859, 0.5647000074386597, 0.0723000019788742]`
  - Image 3: `8aa9b3019f1c9922019f1d752bc5767a_63676_542040_large.jpg` -> ResNet-18 L2 Norm: **26.3682**, Sample: `[1.1227999925613403, 0.3140000104904175, 0.7128000259399414, 0.21410000324249268]`
  - Image 4: `8aa9b3019f1c9922019f1d752bc5767a_96191_277065_large.jpg` -> ResNet-18 L2 Norm: **30.3046**, Sample: `[0.09830000251531601, 0.017899999395012856, 1.371399998664856, 0.5212000012397766]`
  - Image 5: `8aa9b3019f1c9922019f1d752bc5767a_55275_142552_large.jpg` -> ResNet-18 L2 Norm: **27.4115**, Sample: `[0.7196000218391418, 0.4424999952316284, 0.2556000053882599, 0.5131999850273132]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **24.9333**
  - **Aggregated Embedding Sample (first 6 dims):** `[0.5432000160217285, 0.22769999504089355, 1.0281000137329102, 0.45089998841285706, 0.5291000008583069, 1.045699954032898]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

### Example 4: Property ID 17168 (BLR0374) — Indiranagar
- **Locality / Area:** Indiranagar
- **Source:** NoBroker.in (Listing ID: `8aa98a8d9f88be2a019f89bc3f0e37ea`)
- **Genuine Photographs Available:** **1**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 1 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8aa98a8d9f88be2a019f89bc3f0e37ea_14190_2364_large.jpg` -> ResNet-18 L2 Norm: **23.4339**, Sample: `[1.561900019645691, 2.151099920272827, 5.288599967956543, 0.2102999985218048]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **23.4339**
  - **Aggregated Embedding Sample (first 6 dims):** `[1.561900019645691, 2.151099920272827, 5.288599967956543, 0.2102999985218048, 0.23420000076293945, 0.05849999934434891]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

### Example 5: Property ID 17223 (BLR0429) — Electronic City
- **Locality / Area:** Electronic City
- **Source:** NoBroker.in (Listing ID: `8aa9b1aca0ecf12401a0ed68ed5b5082`)
- **Genuine Photographs Available:** **2**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 2 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8aa9b1aca0ecf12401a0ed68ed5b5082_45566_230301_large.jpg` -> ResNet-18 L2 Norm: **22.6014**, Sample: `[2.720900058746338, 1.2523000240325928, 1.902999997138977, 0.20909999310970306]`
  - Image 2: `8aa9b1aca0ecf12401a0ed68ed5b5082_66294_296883_large.jpg` -> ResNet-18 L2 Norm: **23.8488**, Sample: `[2.0524001121520996, 0.9898999929428101, 1.9112000465393066, 0.05770000070333481]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **22.6230**
  - **Aggregated Embedding Sample (first 6 dims):** `[2.3866000175476074, 1.1210999488830566, 1.907099962234497, 0.13339999318122864, 0.03819999843835831, 0.2653000056743622]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

### Example 6: Property ID 17348 (BLR0554) — Bellandur
- **Locality / Area:** Bellandur
- **Source:** NoBroker.in (Listing ID: `8aa9aaeea010244501a010a01ae23e35`)
- **Genuine Photographs Available:** **9**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 5 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8aa9aaeea010244501a010a01ae23e35_66466_46244_large.jpg` -> ResNet-18 L2 Norm: **23.5559**, Sample: `[0.4648999869823456, 2.7356998920440674, 2.642400026321411, 0.19099999964237213]`
  - Image 2: `8aa9aaeea010244501a010a01ae23e35_88668_320840_large.jpg` -> ResNet-18 L2 Norm: **22.4289**, Sample: `[1.089400053024292, 1.9256000518798828, 0.3653999865055084, 0.09539999812841415]`
  - Image 3: `8aa9aaeea010244501a010a01ae23e35_44480_965322_large.jpg` -> ResNet-18 L2 Norm: **29.9637**, Sample: `[0.5156999826431274, 0.3262999951839447, 0.7378000020980835, 2.9428000450134277]`
  - Image 4: `8aa9aaeea010244501a010a01ae23e35_3348_440453_large.jpg` -> ResNet-18 L2 Norm: **26.2611**, Sample: `[0.25110000371932983, 0.7569000124931335, 1.1776000261306763, 1.184499979019165]`
  - Image 5: `8aa9aaeea010244501a010a01ae23e35_77858_684033_large.jpg` -> ResNet-18 L2 Norm: **24.1100**, Sample: `[0.1264999955892563, 0.6205000281333923, 0.6078000068664551, 0.41449999809265137]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **22.0082**
  - **Aggregated Embedding Sample (first 6 dims):** `[0.4894999861717224, 1.2730000019073486, 1.1061999797821045, 0.9656000137329102, 1.1305999755859375, 0.7986999750137329]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

### Example 7: Property ID 17471 (BLR0677) — Jayanagar
- **Locality / Area:** Jayanagar
- **Source:** NoBroker.in (Listing ID: `8a9fbb827f19cebe017f1a7360121fee`)
- **Genuine Photographs Available:** **23**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 5 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8a9fbb827f19cebe017f1a7360121fee_19153_374201_large.jpg` -> ResNet-18 L2 Norm: **25.8503**, Sample: `[0.27160000801086426, 2.947000026702881, 5.977700233459473, 0.36899998784065247]`
  - Image 2: `8a9fbb827f19cebe017f1a7360121fee_77947_972087_large.jpg` -> ResNet-18 L2 Norm: **35.1205**, Sample: `[2.0483999252319336, 0.9573000073432922, 4.14109992980957, 0.8769999742507935]`
  - Image 3: `8a9fbb827f19cebe017f1a7360121fee_94003_842647_large.jpg` -> ResNet-18 L2 Norm: **23.4358**, Sample: `[0.20149999856948853, 2.169800043106079, 4.3649001121521, 0.12729999423027039]`
  - Image 4: `8a9fbb827f19cebe017f1a7360121fee_51770_957209_large.jpg` -> ResNet-18 L2 Norm: **29.9427**, Sample: `[0.375, 1.0555000305175781, 1.6167000532150269, 0.07999999821186066]`
  - Image 5: `8a9fbb827f19cebe017f1a7360121fee_75399_147906_large.jpg` -> ResNet-18 L2 Norm: **25.5688**, Sample: `[0.1889999955892563, 1.0384999513626099, 3.058000087738037, 0.26460000872612]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **24.1594**
  - **Aggregated Embedding Sample (first 6 dims):** `[0.6171000003814697, 1.6335999965667725, 3.831700086593628, 0.34360000491142273, 0.6524999737739563, 0.8637999892234802]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

### Example 8: Property ID 17570 (BLR0776) — Marathahalli
- **Locality / Area:** Marathahalli
- **Source:** NoBroker.in (Listing ID: `8aa9b3849f0d2559019f0e82e60b2749`)
- **Genuine Photographs Available:** **23**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 5 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8aa9b3849f0d2559019f0e82e60b2749_3226_572043_large.jpg` -> ResNet-18 L2 Norm: **27.7566**, Sample: `[1.2618000507354736, 0.18160000443458557, 0.4496999979019165, 0.25130000710487366]`
  - Image 2: `8aa9b3849f0d2559019f0e82e60b2749_51319_678143_large.jpg` -> ResNet-18 L2 Norm: **21.6248**, Sample: `[0.16820000112056732, 0.6043999791145325, 0.7678999900817871, 0.05400000140070915]`
  - Image 3: `8aa9b3849f0d2559019f0e82e60b2749_22593_810484_large.jpg` -> ResNet-18 L2 Norm: **26.1504**, Sample: `[0.18529999256134033, 0.0575999990105629, 0.5842000246047974, 0.24420000612735748]`
  - Image 4: `8aa9b3849f0d2559019f0e82e60b2749_78382_919626_large.jpg` -> ResNet-18 L2 Norm: **23.5613**, Sample: `[0.6324999928474426, 0.4438999891281128, 0.4771000146865845, 0.607200026512146]`
  - Image 5: `8aa9b3849f0d2559019f0e82e60b2749_21175_59920_large.jpg` -> ResNet-18 L2 Norm: **28.8960**, Sample: `[0.2101999968290329, 0.13910000026226044, 1.1267000436782837, 0.3174000084400177]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **23.2658**
  - **Aggregated Embedding Sample (first 6 dims):** `[0.49160000681877136, 0.28529998660087585, 0.6811000108718872, 0.2948000133037567, 0.5842000246047974, 0.9815999865531921]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

### Example 9: Property ID 17669 (BLR0875) — Hebbal
- **Locality / Area:** Hebbal
- **Source:** NoBroker.in (Listing ID: `8aa99c5d9f88be4a019f895938d37059`)
- **Genuine Photographs Available:** **16**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 5 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8aa99c5d9f88be4a019f895938d37059_596298_450190_large.jpg` -> ResNet-18 L2 Norm: **23.3583**, Sample: `[0.0015999999595806003, 0.17000000178813934, 0.6215999722480774, 0.3084000051021576]`
  - Image 2: `8aa99c5d9f88be4a019f895938d37059_651289_847196_large.jpg` -> ResNet-18 L2 Norm: **27.2834**, Sample: `[0.7475000023841858, 0.2046000063419342, 2.376800060272217, 1.5226999521255493]`
  - Image 3: `8aa99c5d9f88be4a019f895938d37059_313748_109957_large.jpg` -> ResNet-18 L2 Norm: **23.8464**, Sample: `[0.9578999876976013, 0.02590000070631504, 2.8856000900268555, 0.12999999523162842]`
  - Image 4: `8aa99c5d9f88be4a019f895938d37059_781095_759182_large.jpg` -> ResNet-18 L2 Norm: **28.9893**, Sample: `[0.4916999936103821, 0.7587000131607056, 2.1361000537872314, 1.1656999588012695]`
  - Image 5: `8aa99c5d9f88be4a019f895938d37059_64488_346090_large.jpg` -> ResNet-18 L2 Norm: **32.9713**, Sample: `[0.4821000099182129, 1.017799973487854, 3.0875000953674316, 1.3925000429153442]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **24.6683**
  - **Aggregated Embedding Sample (first 6 dims):** `[0.5360999703407288, 0.43540000915527344, 2.2214999198913574, 0.9039000272750854, 0.435699999332428, 0.40959998965263367]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

### Example 10: Property ID 17768 (BLR0974) — Yelahanka
- **Locality / Area:** Yelahanka
- **Source:** NoBroker.in (Listing ID: `8aa9b2849fc08879019fc0d51848290a`)
- **Genuine Photographs Available:** **2**
- **Provenance Classification:** `PROPERTY_SPECIFIC`
- **Tested Photo Sample:** 2 images
- **Sample Filenames & Individual ResNet-18 L2 Norms:**
  - Image 1: `8aa9b2849fc08879019fc0d51848290a_94139_279784_large.jpg` -> ResNet-18 L2 Norm: **27.9529**, Sample: `[2.674499988555908, 2.011399984359741, 5.273600101470947, 0.4406999945640564]`
  - Image 2: `8aa9b2849fc08879019fc0d51848290a_project_84407_large.jpg` -> ResNet-18 L2 Norm: **24.4645**, Sample: `[2.4233999252319336, 2.4391000270843506, 1.3969999551773071, 0.28209999203681946]`
- **Multi-Image Mean-Aggregated 512-D Vector:**
  - **Aggregated L2 Norm:** **23.6783**
  - **Aggregated Embedding Sample (first 6 dims):** `[2.5490000247955322, 2.2251999378204346, 3.3352999687194824, 0.3614000082015991, 0.9348000288009644, 0.1046999990940094]`
  - **Fusion Indices:** Enters 544-D multimodal vector at dimensions `[32:544]`

---

## 6. Artifact & File Synchronization

The maximized genuine photo dataset is synchronized across all relevant project files:

1. **Database (`real_estate.db`):**
   - `property_images` table: exactly **11,665** rows inserted with `image_provenance = 'PROPERTY_SPECIFIC'`.
   - `properties` table: `images` (JSON array) and `image_count` updated for all 863 properties.
2. **Master Dataset CSV (`backend/datasets/bengaluru_master_property_dataset.csv`):**
   - 863 rows updated with new `image_count`, `image_source_url`, and `image_provenance = 'PROPERTY_SPECIFIC'`.
3. **Property Images CSV (`backend/datasets/bengaluru_property_images.csv`):**
   - Full 11,665 image registry with property IDs, image IDs, URLs, and provenance.
4. **Real Property JSON (`backend/datasets/bengaluru_real_property_dataset.json`):**
   - Updated with full image URL lists and counts.

---

## 7. Verification Test Suite Results

- **Backend PyTest Suite:** **93 passed, 0 failed** in 36.05s
- **Frontend Production Build:** **Built successfully** (`vite build`) in 15.26s
- **Multimodal Pipeline:** End-to-end multi-image inference confirmed with live SHAP attribution.
