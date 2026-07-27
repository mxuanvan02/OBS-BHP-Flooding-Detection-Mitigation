# Kiểm toán artifact Machine Learning cho luận văn OBS/BHP

**Ngày kiểm toán:** 2026-07-26 (Asia/Saigon)  
**Phạm vi:** toàn bộ dataset, script, cấu hình, output và bằng chứng kiểm thử ML hiện có trong `work/obs_repro`, đối chiếu với `thesis_requirements.md`.  
**Nguyên tắc:** không sửa code; không coi dữ liệu synthetic là NS-2.35+nOBS; không suy diễn số liệu, PSO–SVM, detector online hoặc deployment artifact khi chưa có bằng chứng.

## 1. Kết luận điều hành

Hiện có bốn lớp bằng chứng phải được giữ tách biệt:\n\n1. **UCI404 official — nhánh ML canonical cho kiểm toán offline.** Pipeline đọc trực tiếp ARFF chính thức, khóa SHA-256, xử lý missing trong fold, nhóm 5 bản sao exact trước khi chia train/test, chạy bốn baseline cố định và xuất raw fold metrics, summary, provenance, manifest và hình. Nhánh này tái lập được và test pass, nhưng **không tái lập các con số ML của luận văn**, không có PSO–SVM, latency, prediction-level output, model deployable hay detector–actuator.
2. **Native NS-2.35+nOBS network windows — artifact thật nhưng benchmark thất bại ở non-degeneracy gate.** Dataset hiện có 320 cửa sổ từ 16 cell S0/S1, cân bằng 160/160 và chia nhóm theo seed. Cả bốn model và bảy feature đơn lẻ không bị loại đều đạt 1.0 trên mọi fold/metric. Nhãn đồng nhất với scenario và feature event-rate phân tách scenario hoàn hảo. Đây là bằng chứng benchmark suy biến, không phải bằng chứng detector tổng quát.
3. **Synthetic MVP — chỉ là approximation.** Dataset 600 cửa sổ từ discrete-time shared-resource simulator cho kết quả không hoàn hảo, nhưng không xuất phát từ NS-2.35+nOBS và không được dùng làm reproduction của benchmark mạng trong luận văn.
4. **Legacy GitHub/Orange/Weka/R — provenance tham khảo.** Có các biến thể dữ liệu và ảnh/workflow lịch sử. Một ARFF Weka đồng nhất về dataframe với official ARFF; CSV Random-Forest đồng nhất về giá trị sau chuẩn hóa header/encoding; `final_ml.csv` đã biến đổi và thay toàn bộ cột tương ứng `Packet_lost`. Không artifact legacy nào cung cấp đủ split, seed, prediction, PSO–SVM hoặc môi trường để làm ground truth cho luận văn.

**Verdict theo yêu cầu chính:**

- UCI404 leakage-aware baseline: **tái lập được, với protocol mới và kết luận hẹp hơn luận văn**.
- Claim “12/21 feature gần hoàn hảo” và RF importance khoảng 0.10: **không tái lập dưới protocol hiện tại**.
- PSO–SVM: **thiếu hoàn toàn implementation/config/artifact**.
- Benchmark mạng khoảng 1.300 windows/26 runs và kết quả Bảng 3.4–3.5: **không có artifact gốc; chưa tái lập**.
- Native benchmark 320 windows: **có thể tái chạy/kiểm tra nhưng không đạt non-degeneracy gate**.
- Inference latency, model size, end-to-end detection delay, false-positive cost, detector-to-actuator online: **chưa đo/chưa có**.

## 2. Phương pháp kiểm toán

Các bước đã thực hiện:\n\n- đọc `thesis_requirements.md`, pipeline/config/README/manifest/provenance;\n- crawl file liên quan UCI, window, ML model, metrics và experiment native;\n- tính/đối chiếu SHA-256 cho dataset và các bảng chính;
- parse schema, shape, missing, duplicate và class counts;
- so sánh dataframe các bản UCI official/legacy;
- kiểm tra model, hyperparameter, preprocessing và split trực tiếp từ source;
- kiểm tra output manifest UCI404: 11/11 file đúng size và SHA-256;
- chạy unittest UCI404 và native experiment;
- kiểm tra root test discovery và gọi trực tiếp hai test-function ML/plot do `pytest` không có trong môi trường;
- kiểm tra sự tồn tại của dependency lock/container và serialized model theo các pattern thông dụng.

Quy mô file theo nhóm đã kiểm kê:

| Nhóm | Số file | Tổng bytes | Ghi chú |
|---|---:|---:|---|
| UCI data | 2 | 367,480 | ZIP nguồn và ARFF giải nén |
| UCI pipeline/output | 18 | 451,360 | source, config, tests, CSV, JSON, PNG |
| Native nOBS experiments | 2,132 | 6,068,034,818 | gồm raw traces, run records, analysis, tests |
| MVP Python results | 13 | 332,408 | synthetic raw/tables/figures |

## 3. Inventory dataset

### 3.1 UCI404 official — canonical

| Artifact | Vai trò | SHA-256 / đặc điểm |
|---|---|---|
| `data/uci404/source/uci404.zip` | ZIP tải từ UCI | `b154f2018d24c0caff4b08daaea27784831529ecfbbc7e491bff7a2be9e4532e` |
| `data/uci404/extracted/OBS-Network-DataSet_2_Aug27.arff` | dataset canonical | `c573b83a9b8db30658be8dd53ef5769a94bc03a0695e78d6c130306c60cc69de` |
| UCI landing page | provenance | UCI ID 404, DOI `10.24432/C51C81` |

Schema official ARFF:

- 1,075 rows, 22 columns = 21 predictors + target `Class`;
- class counts: `NB-No Block=500`, `NB-Wait=300`, `No Block=155`, `Block=120`;
- 15 missing cells, tất cả tại `Packet_lost`;
- 860 exact duplicate rows;
- chỉ 215 unique full rows và 215 unique predictor vectors;
- nominal feature: `Node Status`; các predictor còn lại được pipeline xử lý như numeric;
- các feature đáng chú ý về leakage/causality: `Flood Status`, `Node Status`, `10-Run-*`, các rate/percentage được suy ra từ cùng phép đo dùng cho policy label.

Danh sách predictor được lưu đầy đủ trong `data/uci404/outputs/dataset_schema.csv`. Target là policy/state 4 lớp, không phải ground truth vật lý độc lập về forged-BHP.

### 3.2 UCI legacy/provenance

| Artifact | Shape | SHA-256 | Kết quả đối chiếu |
|---|---:|---|---|
| `artifacts/github/Classification-using-Weka--Burst-Header-Packet/Burst Header Packet.arff` | 1,075×22 | `56dc952fa719ae4e102b291773423b6c941ca880535319ff87fd463e377ad348` | Dataframe equal với official ARFF sau decode; khác bytes/metadata serialization. Có 860 duplicates và 15 missing `Packet_lost`. |
| `artifacts/github/Burst-Header-Packet-Flooding-Detection-using-Random-Forest/OBS-Network-DataSet_2_Aug27.csv` | 1,075×22 | `7a1a202d03c41e323d757523ff3f089268945d092472617f1b0953695dc48488` | Giá trị 22 cột đồng nhất sau chuẩn hóa spelling/whitespace/NBSP, quote quanh `P NB`, và xử lý literal `?`; không byte-identical. |
| `artifacts/github/Burst-Header-Packet/final_ml.csv` | 1,075×27 | `7722db041b8b3cb85902d7ccc4933c8945eff1cca60e4f4b00800b98dcc953ca` | Có index, `V1..V22` và 4 one-hot class columns. `V1..V13`, `V15..V19` map về dữ liệu official; `V20` mã hóa Node Status, `V21` bằng Flood Status, `V22` mã hóa Class; **toàn bộ 1,075 giá trị `V14` không bằng `Packet_lost` official**. Không dùng làm canonical. |
| `.../project_file.ows` | Orange workflow | — | Workflow/modeling recipe, không phải trained-model artifact; README nói RF 10 trees, min split 5, stratified 10-fold. Thiếu raw predictions/folds/environment. |

Các repository legacy có commit manifest trong `artifacts/github/INVENTORY.txt`; chúng cung cấp provenance lịch sử, không chứng minh protocol hay kết quả gốc của luận văn. Các ảnh confusion matrix/feature selection và file Excel Weka là derived presentation artifacts, không thay thế raw fold assignments/predictions.

### 3.3 Native NS-2.35+nOBS window dataset

Canonical native window artifact hiện có:

- `nobs/experiments/windows_fixed_20260726_014412.csv`
- duplicate byte-identical: `nobs/experiments/matrix_full_400_8seed_20260725_232912/analysis/window_dataset.csv`
- SHA-256 cả hai: `d55f8a2059d583c29f7169407ed74367a61fd13d488c3eb46c2fdb5dce1cc479`
- manifest: `windows_fixed_20260726_014412.manifest.json`.

Thiết kế thực tế:

- nguồn: `matrix_full_400_8seed_20260725_232912`;
- chỉ dùng S0 và S1, 8 seed × 2 scenario = 16 source cells;
- 5 s/cell, window 0.25 s, drain 0.25 s bị loại;
- 320 windows, 20 windows/cell;
- class balance `attack_label=0:160`, `1:160`;
- S0 luôn âm, S1 luôn dương vì `attack_start_s=0.1` và rule `end > attack_start_s` làm cả cửa sổ S1 đầu tiên dương;
- 146 duplicated model records sau khi bỏ scenario/seed/window IDs;
- source matrix manifest ghi nominal attack rate **12 Mb/s/source** cho mỗi seed. Không được suy rate 40 chỉ từ tên thư mục; `configs/full_400_rate40_8seed.json` thuộc design/config-driven run khác.

Schema 17 cột:\n\n- IDs/context: `scenario`, `seed`, `window_start`, `window_end`;
- target: `attack_label`;
- candidate model features: `legal_packets`, `legal_mbps`, `event_rate`, `enqueue_rate`, `dequeue_rate`, `receive_rate`, `drop_rate`, `optical_event_rate`, `optical_uid_rate`, `optical_mean_size_bytes`;
- direct leakage audit columns, bị loại khỏi model: `attacker_mbps`, `active_sources`.

`scenario` cũng bị loại khỏi model. Dù vậy, bảy feature đơn lẻ còn lại (`event_rate`, `enqueue_rate`, `dequeue_rate`, `receive_rate`, `optical_event_rate`, `optical_uid_rate`, `optical_mean_size_bytes`) đạt 1.0, nên việc loại ba direct columns không đủ làm benchmark có ý nghĩa.

### 3.4 Synthetic MVP window dataset

- `results/raw/window_dataset.csv`
- SHA-256: `a8481b523d1a2504b528524f65f120f939e5f05c07e11508f3fc3756638fc966`
- 600 rows, 12 columns;
- scenarios: S0 160, S1 160, S2 rate-limit 160, S2 isolation 120;
- seeds: `101,202,303,404,505,606,707,808`;
- class counts: 292/308;
- generator: root `simulator.py`/`run_all.py` theo `config/default.json`;
- provenance tự khai báo rõ: “discrete-time shared reservation approximation; not NS-2/nOBS”.

Dataset này hữu ích cho smoke test pipeline/plot, nhưng không được nhập chung với native traces hoặc dùng để xác nhận Bảng 3.4–3.5.

## 4. Inventory code, model và preprocessing

### 4.1 Official UCI404 pipeline

Files chính:

- `data/uci404/pipeline.py`
- `data/uci404/config.json`
- `data/uci404/README.md`
- `data/uci404/tests/test_pipeline.py`

Protocol:

- `StratifiedGroupKFold`, 5 folds;
- seeds `17, 42, 73, 101, 2026`, tổng 25 fold evaluations/model;
- group = hash của toàn bộ 21 predictor gốc, target excluded;
- exact copies không vượt train/test;
- numeric missing được median-impute chỉ từ training fold;
- `Node Status` most-frequent-impute + one-hot trong training fold;
- SVM-RBF, KNN, GaussianNB dùng standardization fitted trong training fold;
- DecisionTree không scale;
- không tuning, không nested CV.

Model/hyperparameter cố định:

| Model | Hyperparameter |
|---|---|
| DecisionTree | `criterion=gini`, `splitter=best`, `max_depth=None`, `min_samples_split=2`, `random_state=cv_seed` |
| SVM-RBF | `C=1.0`, `kernel=rbf`, `gamma=scale` |
| KNN | `n_neighbors=5`, `weights=uniform`, Minkowski `p=2` |
| GaussianNB | `var_smoothing=1e-9` |
| RF importance | 200 trees, gini, `max_features=sqrt`, seed 42, 10 permutation repeats, `f1_macro`, `n_jobs=1` |

Metrics: accuracy, balanced accuracy, macro precision, macro recall, macro F1 và multiclass MCC. Không có latency/resource/model-size benchmark.

### 4.2 Root/native network-window ML pipeline

Files:

- `ml_pipeline.py`
- `nobs/experiments/extract_windows.py`
- `tests/test_ml_and_plots.py`

Protocol:

- binary target `attack_label`;
- `GroupKFold` theo `seed`, tối đa 5 folds;
- loại `attacker_mbps`, `active_sources`, `scenario`; loại ID `seed`, `window_start`, `window_end`;
- drop rows missing ở feature/target/seed;
- SVM-RBF và KNN dùng `StandardScaler` trong sklearn pipeline;
- DecisionTree `max_depth=None`, `random_state=1729` mặc định CLI; GaussianNB default;
- models: DecisionTree, SVM-RBF C=1/gamma=scale, KNN k=5, GaussianNB;
- metrics nhị phân: accuracy, balanced accuracy, precision, recall, F1, MCC, `zero_division=0`;
- single-feature DecisionTree audit gồm cả direct columns bị loại để quyết định leakage có thể quan sát được.

Giới hạn protocol:

- grouping theo seed chặn window cùng seed qua train/test nhưng không có leave-rate/scenario/topology-out;
- nhãn hiện đồng nhất với scenario, không có benign high-load, mixed on/off periods hoặc low-rate hard negatives trong cùng run;
- nhiều feature đo dấu vết simulator/event volume, không chứng minh parity với telemetry deployable;
- `legal_packets/legal_mbps` là downstream outcome; tính khả dụng và độ trễ tại điểm ingress decision chưa được chứng minh;
- không tuning/nested CV/calibration/threshold selection;
- không lưu prediction-level output, confusion matrix per fold hoặc confidence interval.

### 4.3 Model persistence và environment

Không tìm thấy trained-model serialization với các đuôi `.pkl`, `.pickle`, `.joblib`, `.onnx`, `.pt`, `.pth`, `.h5`, `.sav`, `.model` trong các nhánh UCI404/native được kiểm tra. `project_file.ows` là workflow Orange, không phải final fitted model có provenance đầy đủ.

Không tìm thấy dependency lock/environment/container ở root theo các pattern `requirements*.txt`, `environment*.yml|yaml`, `pyproject.toml`, `poetry.lock`, `uv.lock`, `Dockerfile*`. UCI provenance có snapshot version thực chạy:\n\n- Python 3.12.12;\n- NumPy 2.2.6;\n- pandas 2.3.3;\n- SciPy 1.16.2;\n- scikit-learn 1.7.2;\n- matplotlib 3.10.7.\n\nSnapshot version giúp giải thích run hiện tại nhưng chưa đủ để tái tạo môi trường sạch/độc lập.

## 5. Inventory output và kết quả thực có

### 5.1 UCI404 outputs

Thư mục: `data/uci404/outputs/`

- schema: `dataset_schema.csv` (22 rows);
- raw main folds: `raw/fold_metrics.csv` (100 rows = 4×25);
- raw single feature: `raw/single_feature_fold_metrics.csv` (525 rows = 21×25);
- raw RF OOF permutation: `raw/rf_oof_permutation_fold.csv` (105 rows = 21×5);
- summaries: `summary/model_summary.csv`, `single_feature_summary.csv`, `rf_permutation_importance_summary.csv`;
- figures: `model_macro_f1.png`, `single_feature_audit.png`, `rf_oof_permutation_importance.png`;
- provenance: `provenance.json`;
- integrity: `output_manifest.json`, 11/11 entries verified.

Main result dưới duplicate-group-aware protocol:

| Model | Accuracy | Balanced acc. | Macro precision | Macro recall | Macro F1 | MCC |
|---|---:|---:|---:|---:|---:|---:|
| DecisionTree | 0.7523 | 0.8171 | 0.8067 | 0.8171 | **0.8082** | 0.6239 |
| SVM-RBF | 0.7404 | 0.7748 | 0.7820 | 0.7748 | **0.7680** | 0.6095 |
| KNN | 0.6492 | 0.6734 | 0.6783 | 0.6734 | **0.6573** | 0.4750 |
| GaussianNB | 0.6742 | 0.7581 | 0.6874 | 0.7581 | **0.6838** | 0.5526 |

Leakage audit thực có:

- best single feature là `Flood Status`;
- mean accuracy 0.7106, macro F1 0.7845, MCC 0.5692;
- RF out-of-fold permutation importance của `Flood Status` = 0.2177;
- các feature còn lại có importance quanh 0 hoặc âm trong protocol này.

Diễn giải đúng: kết quả hỗ trợ cảnh báo duplicate/dependence và target-policy/proxy leakage; nó **không** tái lập “12/21 feature gần hoàn hảo” hay importance khoảng 0.10. Không được đổi protocol rồi so trực tiếp các số như cùng một thí nghiệm.

### 5.2 Native window outputs

- ML result canonical: `nobs/experiments/matrix_full_400_8seed_20260725_232912/analysis/ml_tables/ml_results.csv`;
- duplicate byte-identical: `results/tables/ml_fixed_20260726_014505/ml_results.csv`;
- SHA-256: `8c74d7863954c7dfd43ce8908938f8a92f75992cf6401969a80a7ea33d5130f4`;
- single feature: cùng hai thư mục, `single_feature_audit.csv`.

Kết quả:

- 4 models × 5 folds = 20 rows;
- DecisionTree, SVM-RBF, KNN, GaussianNB đều đạt accuracy, balanced accuracy, precision, recall, F1, MCC = **1.0 trong cả năm folds**;
- direct leaks `attacker_mbps`, `active_sources` = 1.0 và đã bị loại;
- bảy feature không bị loại vẫn đơn lẻ đạt 1.0;
- `drop_rate` hằng số, single-feature accuracy 0.5/MCC 0;
- `legal_packets` và `legal_mbps` trung bình accuracy 0.7125.

**Non-degeneracy verdict: FAIL.** Metric 1.0 ở đây là dấu hiệu scenario shortcut/simulator signature, không đáp ứng yêu cầu benchmark mạng không suy biến của `thesis_requirements.md`.

### 5.3 Synthetic outputs và name collision

- synthetic result: `results/tables/ml_results.csv`, SHA-256 `ad0e050fb0f58ed5cf095a2ea964e50b935681b8f095e7f052f4468eb6c84b5b`;
- native fixed result: `results/tables/ml_fixed_20260726_014505/ml_results.csv`, SHA-256 như trên.

Hai file cùng basename nhưng khác nguồn và không được trộn. Synthetic mean metrics:

| Model | Accuracy | MCC |
|---|---:|---:|
| DecisionTree | 0.8382 | 0.6807 |
| SVM-RBF | 0.8654 | 0.7618 |
| KNN | 0.8798 | 0.7637 |
| GaussianNB | 0.8654 | 0.7618 |

Các số này chỉ xác nhận pipeline chạy trên approximation; không thay thế native benchmark hoặc thesis tables.

## 6. Provenance native traces liên quan tới ML

Raw-trace corpora chính dưới `nobs/experiments/`:

| Run directory | Traces | Trace bytes | Metrics non-empty | Completion |
|---|---:|---:|---:|---|
| `matrix_8seed_20260725` | 32 | 36,551,104 | 32 | không có completion chuẩn trong inventory |
| `matrix_configdriven_rate40_8seed_20260726_095909` | 32 | 709,729,016 | 32 | 32/32 complete |
| `matrix_full_400_8seed_20260725_232912` | 32 | 385,849,758 | 32 | complete |
| `matrix_full_400_rate40_8seed_20260726_0942` | 32 | 721,201,664 | 32 | complete |
| `matrix_gate_400_2flows_20260725_232816` | 4 | 48,221,564 | 4 | complete |
| `matrix_gate_400_isolation_redirect_20260725_231750` | 4 | 125,622,754 | 3 | failed S2 isolation, rc=-11 |
| `matrix_gate_400_seed1_20260725_2315` | 4 | 125,602,274 | 3 | failed S2 isolation, rc=-11 |
| `matrix_gate_400_seed1_20260725_231515` | 4 | 125,602,274 | 3 | failed S2 isolation, rc=-11 |
| `pilots` | 4 | 6,193,987 | 4 | pilot, không completion chuẩn |
| `repro_5s_pilot_20260725` | 4 | 212,637,255 | 4 | pilot, không completion chuẩn |
| `sweep_s1_400_8seed_20260726_015037` | 80 | 3,536,658,763 | 80 | 80/80 complete |

Native provenance được snapshot bằng:

- `nobs/experiments/manifest.json`;
- `matrix_manifest.json`, `experiment_config.snapshot.json` hoặc `experiment_manifest.snapshot.json` trong từng run;
- binary SHA-256 `e2ff7127706c4e5f01891fc1915f013f3dd1a083fdec32252b4428ba94a76ba6`;
- `scenario.tcl` SHA-256 `e1643ec699b266c928d031633e5b93bafb9cf8fa97c79a91864dc32f53e04054`;
- `parse_trace.py` SHA-256 `9241b82b034b122b456c51267848b14a7541c10eacb6b01a9b4b394db5a2dbc1`.

`analysis_fixed_20260726_014410/validation.json` xác nhận 32/32 cells; sweep validation xác nhận 80/80 cells, raw trace/hash/accounting được kiểm tra. Tuy nhiên:\n\n- simulation manifest ghi rõ `status: reconstructed`/`reconstructed-assumption`;
- attack là UDP/CBR sinh BHP + data burst hợp lệ, không phải forged/orphan BHP packet-level;
- mitigation là oracle schedule với stock TBF hoặc redirect/stop, không dùng ML output;
- sweep attack multipliers thực tế chỉ 0.80014–0.80107, không hiện thực hóa rộng ±20%; 
- `sweep_analysis_20260726/CLAIM_GATE.md` chỉ hỗ trợ quan hệ tải danh định cao hơn với legal delivery thấp hơn trong cấu hình tái dựng;
- không có detector feature extraction/online decision/actuator acknowledgment trong raw benchmark.

## 7. Reproducibility gates đã chạy

| Gate | Kết quả | Diễn giải |
|---|---|---|
| `python3 -m unittest discover -s data/uci404/tests -v` | **7/7 pass** | hash blocking, schema/classes, duplicates grouping, split config, metric bounds, model fit, reduced end-to-end run |
| UCI `output_manifest.json` | **11/11 pass** | không size/hash mismatch |
| Native experiment unittest discovery | **22/22 pass** | parser, trace semantics, config/scenario fail-closed, real nOBS smoke, sweep CI/plot/validation |
| Root `python3 -m unittest discover -s tests -v` | **0 tests, exit 5** | file root dùng pytest-style functions, unittest discovery không nhận |
| `pytest` | **không chạy được** | `/media/ssd/conda/envs/ppis_env/bin/python3: No module named pytest` |
| Gọi trực tiếp hai root test functions với temporary directories | **2/2 pass** | ML output/leakage exclusion và PNG plot gate |

Các gate trên chứng minh code paths và retained artifacts nhất quán ở mức đã nêu. Chúng không khắc phục benchmark suy biến và không chứng minh thesis-reported results.

## 8. Đối chiếu `thesis_requirements.md`

| Requirement | Evidence hiện có | Status | Gap chính |
|---|---|---|---|
| Official UCI `OBS-Network-DataSet`, 1,075×21 + 4-class target | official ZIP/ARFF, hash, schema, provenance | **PASS** | Không có original thesis snapshot/split để chứng minh cùng preprocessing |
| 5-fold stratified UCI evaluation | 5-fold `StratifiedGroupKFold`, 5 seeds | **PARTIAL / protocol khác** | Luận văn không công bố fold assignment/seed; current grouping mạnh hơn simple stratified CV nên số không so trực tiếp |
| Decision Tree | fixed baseline, 25 folds, raw/summary | **PASS as baseline; FAIL exact thesis result** | Không có original tree config/split; current accuracy 0.7523, không phải 1.0 |
| SVM-RBF | C=1, gamma=scale baseline | **PASS as baseline; FAIL exact thesis result** | Không có original C/gamma/preprocessing |
| KNN | k=5 baseline | **PASS as baseline; FAIL exact thesis result** | Không có original k/metric/preprocessing |
| Naïve Bayes | GaussianNB baseline | **PASS as baseline; FAIL exact thesis result** | Luận văn không chỉ rõ NB variant/config |
| PSO–SVM | chỉ có thesis-reported claim | **FAIL / BLOCKED** | Thiếu source, swarm size, bounds, iterations, objective, preprocessing, seed, output |
| UCI accuracy/precision/recall/F1 mean±SD | macro fold metrics hiện có | **PARTIAL** | Protocol khác; không có original raw predictions/confusion matrices; latency không đo |
| UCI latency DT/NB/SVM/KNN | không có timing code/output | **FAIL** | Thiếu hardware, warmup, repetitions, percentiles, feature cost |
| Single-feature leakage audit “12/21 gần hoàn hảo” | 21-feature grouped audit; best `Flood Status` accuracy 0.7106/F1 0.7845 | **NOT REPRODUCED** | Cần original protocol/folds/code và định nghĩa threshold “gần hoàn hảo” |
| RF 200-tree permutation importance ~0.10 | OOF RF 200-tree importance; `Flood Status=0.2177` | **PARTIAL, exact claim not reproduced** | Protocol/scoring khác hoặc original unknown; correlated-feature effects |
| Hình UCI single feature/RF importance/model | ba PNG có manifest | **PASS for current protocol** | Không phải bit-for-bit thesis figures |
| NS-2.35+nOBS dynamic simulation | binary/source/config/traces, complete matrices/sweep | **PASS as reconstruction scaffold** | Không có original topology/config/raw runs; valid-burst overload, không forged BHP |
| Benchmark network-level không node ID | current model loại scenario/seed/time and has no node ID | **PARTIAL structural** | Event-rate signatures vẫn trivial; online feature causality chưa chứng minh |
| Khoảng 1,300 windows/26 independent runs | không có artifact | **FAIL** | Current native = 320 windows/16 cells; synthetic = 600 và không native |
| Window length/stride/label schema của benchmark gốc | current reconstruction định nghĩa 0.25 s, stride 0.25 s, design label | **FAIL exact / PASS reconstructed schema** | Không có original schema/label timing/alignment |
| Non-degeneracy: không single feature shortcut | 7 non-excluded features đạt 1.0 | **FAIL** | Cần hard negatives, mixed runs, nhiều rates/onsets/topologies và causal feature gate |
| Run-independent CV | GroupKFold theo seed | **PARTIAL** | Không leave-run/rate/scenario/topology-out; seed chưa tương đương independent topology/run |
| Bảng 3.4 SVM/KNN/DT/NB metrics | không có raw thesis benchmark | **FAIL** | Current native tất cả 1.0; không tương ứng số thesis |
| Bảng 3.5 MCC theo 1–35 Mb/s | native sweep không tạo ML window benchmark theo rate | **FAIL** | Không raw predictions/features/runs ở từng rate |
| Detection latency khoảng 0.25 s | 0.25 s chỉ là window/schedule parameter | **FAIL as measured latency** | Thiếu extraction+inference+decision+install/ack p50/p95/p99 |
| Detector chọn DT/NB theo lightweight/explainable | không có resource/latency benchmark | **FAIL deployment selection** | Cần model size, CPU/RSS, end-to-end utility và FP cost trên benchmark hợp lệ |
| Online four-state detector–actuator loop | không có integration | **FAIL** | Current native action biết attacker/scenario/time; không telemetry→model→policy |
| Rate-limit CIR 4 Mb/s | stock TBF reconstruction | **PARTIAL simulation primitive** | Không RFC2698 two-rate semantics, PIR/CBS/PBS/color, classifier trigger hoặc hardware API |
| Isolation | app redirect/stop theo oracle | **FAIL as network actuator** | Không ACL/policer install, source localization, TTL/rollback |
| Reproducible software environment | UCI version snapshot; native binary/source hashes | **PARTIAL** | Không lockfile/container hoàn chỉnh; pytest thiếu |
| Trained/deployable model | không tìm thấy | **FAIL** | Không final refit, serializer, preprocessor bundle, schema contract, inference API |
| Raw predictions/confusion matrices/CIs | fold-level aggregate metrics chủ yếu | **FAIL/PARTIAL** | Cần per-window/per-row prediction, score, fold/run ID, confusion và uncertainty |

## 9. Leakage và validity assessment

### 9.1 UCI404

Các loại rủi ro khác nhau cần phân biệt:\n\n1. **Exact duplicate leakage:** đã được xử lý bằng predictor-vector grouping. Simple random/stratified folds có thể đưa các bản sao của cùng observation qua train/test và làm score tăng giả.
2. **Dependence còn lại:** UCI không cung cấp run/site/topology/time group; 215 unique vectors chưa chắc độc lập.
3. **Target-construction leakage:** `Class` là policy/state label; `Flood Status`, `Node Status` và các `10-Run-*` có thể là input hậu xử lý hoặc proxy của cùng rule tạo target. Grouping duplicate không giải quyết leakage khái niệm này.
4. **Temporal/online leakage:** feature aggregate qua 10 runs hoặc feature status có thể không tồn tại tại thời điểm detector phải quyết định.
5. **Missing-data behavior:** official ARFF có 15 `?` dù UCI page hiện mô tả không missing; current fold-local imputation là hợp lý và được ghi provenance.

Kết luận được hỗ trợ là: **UCI404 không nên là bằng chứng duy nhất cho detector deployment vì duplicate/dependence và target-policy/proxy risks.** Chưa đủ bằng chứng để gọi label “deterministically leaked” theo nghĩa toán học cho 12/21 feature dưới mọi protocol.

### 9.2 Native windows

Shortcut chính:

- label = scenario trong retained dataset;
- S0 và S1 có toàn bộ window thuộc hai lớp khác nhau, không có benign high-load hay attack-off windows bên trong S1 để phá shortcut;
- event-count/rate features ghi trực tiếp simulator workload signature;
- source runs dùng cùng topology, traffic family, attack timing và nominal design;
- bảy single features đạt perfect held-seed classification;
- direct attacker features đã bị loại nhưng các proxy gần trực tiếp vẫn còn;
- downstream legal-delivery feature có nguy cơ observation/action mismatch.

Do đó held-seed GroupKFold không đủ. Benchmark cần chứng minh generalization qua rate, onset, attacker count, benign load, scenario, topology và traffic process, đồng thời mọi feature phải có telemetry contract online.

## 10. Cái gì thực sự tái lập được

### Tái lập được từ artifact hiện có

- tải/kiểm tra exact official UCI404 bằng SHA-256;
- schema, class counts, missing và duplicate audit;
- duplicate-group-aware 5×5-fold evaluation cho DT/SVM-RBF/KNN/GaussianNB;
- single-feature audit toàn bộ 21 predictor;
- RF 200-tree OOF permutation importance;
- CSV summary/raw fold, provenance, manifest và ba PNG;
- extraction 0.25 s windows từ retained native S0/S1 traces theo schema hiện tại;
- held-seed ML evaluation của current native windows;
- kết luận fail non-degeneracy từ perfect single-feature/model scores;
- native matrix/sweep trace validation trong đúng reconstructed configuration;
- smoke test synthetic pipeline/plots, nếu ghi rõ approximation.

### Không tái lập được từ artifact hiện có

- exact UCI tables của luận văn;
- PSO–SVM;
- original fold assignments, seeds và preprocessing;
- original ~1,300-window/26-run network benchmark;
- Bảng 3.4 và MCC-by-rate Bảng 3.5;
- original single-feature “12/21” và exact RF ~0.10;
- inference latency 0.006/0.020/0.219/2.644 ms;
- model deployability hoặc final trained model;
- detector-driven four-state mitigation loop;
- source localization và false-positive blast radius;
- forged/orphan BHP detection từ current valid-burst traces;
- bit-for-bit NS-2.35+nOBS thesis reproduction;
- exact thesis S0/S1/S2 effect sizes.

## 11. Kế hoạch đóng gap thực tế

### P0 — Chốt claim và nguồn ground truth

1. Xin/khôi phục repository luận văn gốc: UCI notebook/script, PSO–SVM implementation, fold/seed list, network-window CSV, raw traces, feature dictionary, confusion matrices, latency logs, nOBS config và run-exclusion record.
2. Nếu không thu được, đánh dấu mọi exact thesis metric là **reported-only** và định nghĩa study mới là reconstruction, không gọi là reproduction bit-for-bit.
3. Quyết định rõ threat model: valid UDP/CBR-generated bursts hay forged/orphan BHP; giữ hai benchmark riêng nếu cần cả hai.

### P1 — Làm benchmark native không suy biến

1. Tạo independent run matrix có:
   - benign low/high/flash load;
   - attack rates ít nhất 1, 2, 3, 5, 8 và dải 5–50 Mb/s;
   - nhiều attacker counts và distributed sub-threshold conditions;
   - randomized attack onset/offset và attack-free periods trong cùng run;
   - nhiều legal transport profiles, seeds và topology/resource settings;
   - S0/S1 load-matched controls để tách protocol/simulator signature khỏi attack semantics.
2. Cửa sổ phải có manifest: length, stride, event-time alignment, partial-window rule, label rule, right-censor handling và source run ID.
3. Chỉ dùng feature có causal online telemetry contract; loại future/downstream feature nếu không có latency-aligned observation.
4. Predeclare non-degeneracy gate, ví dụ: không feature đơn lẻ hoặc scenario proxy đạt gần-perfect held-domain performance; kiểm tra duplicate và mutual dependence trước training.
5. Split theo independent run; bổ sung leave-seed-out, leave-rate-out, leave-scenario/traffic-out và leave-topology-out. Không chọn model/hyperparameter trên test domains.

### P2 — Hoàn thiện model evaluation

1. Lưu per-sample prediction, decision score/probability, true label, fold, run, seed, rate, scenario và feature-schema hash.
2. Xuất confusion matrix per fold/domain; accuracy, balanced accuracy, precision, recall, F1, MCC; nêu rõ binary/macro/weighted.
3. Dùng nested CV hoặc validation-only tuning; công bố search space và seed.
4. Nếu giữ PSO–SVM, predeclare swarm size, bounds C/gamma, iterations, objective, inner folds, stopping rule và seed; so với grid/random-search budget tương đương. Nếu không, bỏ claim PSO–SVM thay vì dựng số.
5. Báo confidence intervals phù hợp với independent run, không coi hàng nghìn windows tương quan là independent samples.

### P3 — Đo deployment utility

1. Bundle final model + preprocessor + schema/version/hash; có load/predict smoke test và backward-compatibility test.
2. Pin dependencies bằng lockfile và cung cấp container/clean environment recipe.
3. Đo end-to-end latency: window close → export → preprocessing → inference → policy → actuator install/ack; báo p50/p95/p99 dưới source/load concurrency đại diện.
4. Đo model/preprocessor bytes, CPU, peak RSS, telemetry bandwidth, cold start và many-source scaling.
5. Đo false-positive cost trên benign high-load/bursty/shared-identity traffic; predeclare rollback/TTL gate.

### P4 — Nối detector với actuator có bằng chứng

1. ML output phải trực tiếp điều khiển action trong emulation/simulation, không dùng scenario-known attacker IDs hay fixed schedule.
2. Có trusted attribution/localization trước rate-limit/isolation.
3. Nếu claim RFC2698, phải chứng minh `/configuration/raw`, PIR/CIR, CBS/PBS, color/action semantics; stock single-rate TBF không đủ.
4. Nếu claim isolation, phải có rule install/ack, scope, TTL, rollback và stale-rule tests; app stop/redirect không phải network isolation.
5. Đo closed-loop effectiveness và collateral harm bằng paired independent runs; không gọi 0.25 s window là measured detection upper bound.

## 12. Reporting rules nên áp dụng

- Luôn ghi rõ artifact source: official UCI, native trace, synthetic hoặc legacy.
- Không dùng basename `ml_results.csv` nếu không kèm full path/source hash.
- Không trình bày native 1.0 như thành tích; ghi “failed non-degeneracy gate”.
- Không so current grouped UCI metrics trực tiếp với thesis simple/unknown split như cùng protocol.
- Không gọi UDP/CBR valid-burst load là forged-BHP packet-level.
- Không gọi fixed TBF/app redirect là detector-driven online actuator.
- Không tuyên bố practical deployment từ latency/model/resource chưa đo.
- Khi trích native effect, ghi đúng analysis directory; không trộn `analysis_fixed_20260726_014410` với `analysis_configdriven_rate40_8seed_20260726_100244`.

## Unresolved

1. Chưa có artifact gốc cho PSO–SVM: source, swarm, bounds, iterations, objective, preprocessing, seeds và raw output.
2. Chưa có original UCI fold assignments/seeds/config, prediction-level output, confusion matrices hoặc latency benchmark hardware.
3. Chưa xác minh được provenance tạo target `Class`, `Flood Status`, `Node Status` và `10-Run-*`; vì vậy target-construction leakage vẫn là rủi ro, chưa phải định lý deterministic leakage.
4. Chưa có CSV/raw traces/schema của benchmark khoảng 1,300 windows/26 runs hoặc bằng chứng cho Bảng 3.4–3.5.
5. Native 320-window benchmark suy biến: label đồng nhất scenario và bảy feature đơn lẻ đạt 1.0.
6. Chưa có benign high-load controls, mixed attack on/off windows, leave-rate/scenario/topology-out hoặc source-localization target.
7. Current native attack path là UDP/CBR sinh valid BHP+data burst; chưa có packet-level forged/orphan-BHP evidence cho benchmark ML.
8. Chưa có dependency lock/container đầy đủ; `pytest` không được cài; root unittest discovery báo `NO TESTS RAN` và exit code 5.
9. Chưa có serialized trained model, final refit protocol, inference API hoặc online feature schema contract.
10. Chưa đo preprocessing/inference/end-to-end latency, model size, CPU/RSS, telemetry overhead hoặc false-positive cost.
11. Chưa có detector-to-actuator online path; rate-limit/isolation hiện là oracle schedule.
12. Semantics actuator `/configuration/raw` và `/CBS/PBS/color`, cùng PIR/CBS/PBS/color policy của RFC2698, chưa được chứng minh; stock TBF không đủ.
13. Isolation hiện là application redirect/stop, chưa phải authenticated device/network rule với install acknowledgment, TTL và rollback.
14. Sweep multipliers chỉ 0.80014–0.80107, không hiện thực hóa intended ±20% variation; cần giải thích RNG/design trước khi dùng seed diversity làm bằng chứng.
15. Thiếu topology/config/raw artifacts gốc nên không thể xác nhận exact thesis S0/S1/S2 effects hoặc bit-for-bit NS-2.35+nOBS reproduction.
