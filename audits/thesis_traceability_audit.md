# Ma trận truy vết luận văn OBS/BHP → code, dữ liệu và kết quả

**Ngày kiểm toán:** 2026-07-26 (Asia/Saigon)  
**Phạm vi:** `thesis_requirements.md`, văn bản trích xuất từ DOCX/PDF, mã nguồn, cấu hình, raw trace, bảng và hình hiện có trong `work/obs_repro/`.  
**Ràng buộc:** báo cáo này **không sửa DOCX/PDF**.

## 1. Quy ước và ranh giới chỉnh sửa

### 1.1 Vùng luận văn

- **IMMUTABLE — phần mở đầu lõi:** lý do chọn đề tài, phạm vi OBS/BHP, mục tiêu tổng quát, năm mục tiêu cụ thể, đối tượng và phương pháp hai pha. Audit chỉ truy vết và nêu mức bằng chứng; không đề nghị thay đổi nội dung lõi này.
- **UPDATEABLE — phần thực nghiệm:** Chương 3, bảng/hình thực nghiệm, số liệu, cấu hình, mô tả seed, diễn giải cơ chế, kết luận thực nghiệm và giới hạn. Vùng này có thể được cập nhật **chỉ khi** artifact tái lập vượt gate tương ứng.
- **MIXED:** đóng góp/kết luận nhắc lại mục tiêu lõi nhưng chứa số liệu thực nghiệm. Câu mục tiêu là immutable; số liệu và mức suy luận là updateable.

### 1.2 Provenance

- `reported_target`: số hoặc kết luận chỉ được báo cáo trong luận văn/`thesis_requirements.md`.
- `reproduced_mvp`: số sinh từ artifact hiện có. Nhãn này gồm hai nhánh phải giữ tách biệt:\n  1. **Python MVP** — mô hình discrete-time trừu tượng, không phải NS-2/nOBS;
  2. **native reconstruction** — NS-2.35+nOBS theo cấu hình tái dựng công khai, không phải cấu hình gốc bit-for-bit.
- `assumption`: tham số được đặt vì tài liệu gốc không công bố hoặc không còn artifact gốc.

Không được trộn ba loại provenance trong cùng một kết luận định lượng.

### 1.3 Trạng thái

- **PASS:** artifact hiện có trực tiếp và tái kiểm được claim đúng theo phạm vi viết trong hàng.
- **PARTIAL:** có bằng chứng liên quan nhưng thiếu thành phần, khác protocol/config, hoặc chỉ hỗ trợ claim hẹp hơn.
- **FAIL:** thiếu bằng chứng bắt buộc, artifact mâu thuẫn claim, hoặc claim vượt quá mức suy luận cho phép.

## 2. Nguồn chuẩn và xung đột phiên bản

1. **Yêu cầu rút từ bản nguồn:** `thesis_requirements.md`, đọc từ `deliverables/LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.pdf`.
2. **Văn bản DOCX làm việc:** `docx_work/original.md`.
3. **Bản render hiện tại:** `docx_work/rendered/rendered.txt` và `docx_work/rendered/LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.pdf`.
4. **Bằng chứng native hiện tại:** `nobs/experiments/`.
5. **Bằng chứng UCI source-only:** `data/uci404/`.
6. **Python MVP cũ/độc lập:** `results/`, có manifest tự khai báo `classification=reproduced_mvp_with_explicit_assumptions` và `model=discrete-time shared reservation approximation; not NS-2/nOBS`.

Có xung đột quan trọng giữa các phiên bản:\n\n- `thesis_requirements.md` và phần tương ứng trong `docx_work/original.md` ghi mục tiêu cũ như S0/S1 `82,568/38,281`, giảm `53.6%`, burst `40,462/64,839`, loss khoảng `0.2%`, và các kết quả S2 cũ.
- `docx_work/rendered/rendered.txt` đã cập nhật Chương 3 theo ma trận native hiện có: S0/S1 `3,426/316.25`, giảm `90.77%`, offered bursts `2,304/8,056.125`, loss `0/1.199%`, S2 rate-limit `2,823.875`, S2 isolation `2,855.625`, tất cả `n=8`.
- Tuy vậy, bản render vẫn giữ một số claim ML/sweep cũ chưa được artifact hiện có tái tạo, gồm benchmark khoảng 1,300 cửa sổ/26 run, Bảng 3.4–3.5, và mô tả sweep khoảng 53,000→12,500 gói với điểm đảo chiều 40 Mb/s.

Do đó, **bản render hiện tại không phải một khối bằng chứng đồng nhất**; từng claim phải đi qua ma trận dưới đây.

## 3. Ma trận truy vết claim-by-claim

| ID | Nguồn / vùng | Claim hoặc mục tiêu | Required evidence | Artifact hiện có và provenance | Trạng thái | Gap | Gate trước khi dùng như kết luận luận văn |
|---|---|---|---|---|---|---|---|
| T0 | Trang tên; IMMUTABLE | Tên đề tài chính xác phải truy được từ luận văn nguồn sang DOCX/PDF hiện tại. | Trang bìa/trang tên có text hoặc metadata title rõ ràng, nhất quán giữa source và bản render. | `docx_work/original.md` và `rendered.txt` bắt đầu từ lời cam đoan/mục lục; PDF source và render có trang 6–7 gần như trắng; DOCX core metadata không có title hữu dụng. Tên chỉ có thể suy từ filename/chủ đề. | **FAIL** | Không có chuỗi tên đề tài nguyên văn để đối chiếu; không nên tự dựng tên. | Cung cấp trang bìa hoặc tên đề tài chính thức từ hồ sơ luận văn; đối chiếu nguyên văn và lưu hash nguồn. |
| O0 | Mở đầu 1.1–1.2; IMMUTABLE | OBS tách BHP và DB; BHP đi trước theo offset; lõi không có bộ đệm quang nên BHP flooding là threat model hợp lý. | Văn bản nguồn, tài liệu tham khảo, và nếu claim thực nghiệm thì telemetry BHP/DB/reservation. | Claim khái niệm có trong `original.md`, `rendered.txt`, `thesis_requirements.md`; mã nOBS có đường burst/control thực. | **PASS** cho phạm vi/motivation; không phải PASS cho hiệu quả tấn công giả mạo | Audit này không tái thẩm định toàn bộ tài liệu tham khảo; valid-burst overload không đồng nghĩa forged/orphan BHP. | Giữ nguyên phần mở đầu; mọi kết quả thực nghiệm phải ghi rõ valid-burst UDP approximation hay direct forged-BHP. |
| O1 | Mở đầu 1.3; IMMUTABLE | Mục tiêu tổng quát: cơ chế khép kín phát hiện → quyết định → ứng phó tại edge, cân bằng chính xác và độ trễ, duy trì loss/throughput. | Telemetry online → model output → policy decision → actuator → feedback, có latency, false-positive và recovery logs. | Kiến trúc có trong luận văn; `scenario.tcl` chỉ hành động theo lịch và oracle attacker IDs; `PRACTICAL_UTILITY_GATE.md` và `CLAIM_EVIDENCE_UTILITY_MATRIX.csv` xác nhận chưa có online detector-actuator loop. | **PARTIAL** | Có kiến trúc và primitives, chưa có hệ thống khép kín. | PASS chỉ khi output từ telemetry thực sự điều khiển actuator có audit trail, rollback và fault tests, không dùng ID/timing oracle. |
| O2 | Mục tiêu 1; IMMUTABLE/MIXED | Phân tích BHP flooding và định lượng tác động lên burst loss và throughput. | S0/S1 paired runs, attack fidelity, raw trace, metric definitions, seed/config manifest, CI/effect estimate. | Native matrix 32/32 cell, raw trace và parser có đủ throughput/burst metrics; config/hash đầy đủ. Attack chính là UDP/CBR valid-burst overload. | **PARTIAL** | Định lượng được một cấu hình tái dựng, nhưng chưa đúng forged/orphan BHP và không khôi phục cấu hình gốc. | Dùng claim hẹp “valid-burst overload trong cấu hình tái dựng”; PASS BHP-flood fidelity cần direct control-only BHP, orphan evidence và matched causal contrast. |
| O3 | Mục tiêu 2; IMMUTABLE/MIXED | Xây dựng và so sánh DT, SVM/PSO-SVM, KNN, NB trên UCI theo accuracy/precision/recall/F1/latency. | UCI artifact nguyên gốc; preprocessing; folds/seeds; đủ 5 model; PSO search config; metric aggregation; latency hardware/protocol. | `data/uci404/pipeline.py`, `config.json`, official ARFF hash và outputs tái tạo 4 model: DecisionTree, SVM-RBF, KNN, GaussianNB; 25 fold-evaluations. PSO-SVM bị chặn; không benchmark latency. | **PARTIAL** | Thiếu PSO-SVM và latency; kết quả duplicate-group-aware khác Bảng 3.1 reported. | Chỉ công bố pipeline 4 model như audit mới. Muốn PASS mục tiêu nguyên văn cần artifact/config PSO-SVM và benchmark end-to-end latency có hardware/repetitions/percentiles. |
| O4 | Mục tiêu 3; IMMUTABLE/MIXED | Chọn model cân bằng hiệu quả phát hiện và độ nhẹ/độ trễ cho edge OBS. | Benchmark không rò rỉ trên features online, held-out run/topology; p99 feature+inference latency; CPU/RAM/model size; false-positive cost. | UCI audit có metric offline nhưng không timing; benchmark native network-window phù hợp chưa có; claim latency DT `0.006 ms`/phát hiện `0.10 s` là `reported_target`. | **FAIL** | Không có cùng pipeline/hardware để chứng minh Pareto choice; DT không vượt SVM trên bảng network-level được báo cáo. | PASS khi cùng online feature pipeline chứng minh model được chọn đạt detection, p99 latency, memory và FP-impact budgets định trước. |
| O5 | Mục tiêu 4; IMMUTABLE/MIXED | Tích hợp rate-limit/cách ly với detector thành quy trình khép kín. | Detector output và attribution gây ra action; policy state; action/recovery logs; no-oracle test. | `scenario.tcl` gắn TBF hoặc redirect nguồn đã biết sau `0.25 s`; không đọc classifier output. | **FAIL** | Đây là oracle action baseline, không phải integration detector-driven. | Detector-derived target/action phải lái real/emulated enforcement; thay scenario label/attacker registry không được quyết định action. |
| O6 | Mục tiêu 5; IMMUTABLE/MIXED | Mô phỏng NS2/nOBS và đánh giá cơ chế qua loss/throughput so với không bảo vệ. | Executable NS-2.35+nOBS; S0/S1/S2; raw traces; complete paired seeds; validated parser and statistics. | Native config-driven matrix có S0, S1, S2-rate-limit, S2-isolation; 32/32 thành công; trace reparse khớp retained metrics. | **PASS** cho **oracle mitigation experiment trong cấu hình tái dựng**; **PARTIAL** cho “cơ chế đề xuất” toàn phần | Không có detector-driven gate, original patch/config/seeds, hoặc exact thesis reproduction. | Luận văn phải giữ disclaimer oracle/fixed delay; PASS toàn mục tiêu chỉ khi O5 qua gate. |
| C1 | Nội dung nghiên cứu; IMMUTABLE | Tổng quan OBS, bảo mật, DoS/BHP, kỹ thuật phát hiện/ứng phó. | Chương 1–2 và references tương ứng. | `original.md`/`rendered.txt` có Chương 1–2 và bibliography. | **PASS** về presence/traceability | Chưa làm systematic literature verification hoặc kiểm DOI toàn bộ. | Không dùng PASS này để suy ra tính mới/hiệu quả thực nghiệm. |
| C2 | Phương pháp hai pha; IMMUTABLE | Pha UCI ML tách biệt pha mô phỏng động NS2/nOBS. | Hai code/data lineage độc lập, manifests và outputs riêng. | `data/uci404/` đọc official ARFF và tuyên bố không đọc `results/window_dataset.csv`; native nOBS nằm riêng. | **PASS** | Bảng 3.4 network-window được nêu như cầu nối nhưng artifact chuẩn chưa tương ứng. | Giữ lineage và manifests riêng; không ghép số từ Python MVP vào native NS2. |
| E1 | Chương 3.5–3.6; UPDATEABLE | Topology T 7 nút, 2 ingress/1 egress, TCP Reno, 8 UDP attackers, 5 s, 8 seeds, 400 Mb/s. | Versioned config chứa graph/routes/link/assembly/traffic/timing; source consumes config; tests. | `configs/full_400_rate40_8seed.json` khai báo nodes 0–6, links/routes, 2 legal Reno flows, 8 attackers, 5 s + 0.25 s drain, seeds 1–8, 400 Mb/s; `run_matrix.py`/`scenario.tcl`; 22 tests PASS. | **PASS** cho cấu hình tái dựng | Đây là `assumption`/reconstruction; topology và nhiều tham số gốc không được luận văn nguồn công bố đủ. | Luôn gọi là `nobs-explicit-topology-v1`, không là exact original topology, trừ khi có topology/config gốc. |
| E2 | Chương 3.6; UPDATEABLE | Ma trận native hiện tại hoàn tất và có provenance kiểm được. | Completion, manifest, per-run records, hashes, exit codes, independent trace reparse. | `completion.json`: 32 attempted/32 success/0 failed; `validation.json`: all traces reparsed and matched; `matrix_manifest.json` schema `nobs-configured-matrix-run-v1`, experiment `full-400mbps-rate40-8seed`. | **PASS** | Không có blocker nội bộ cho integrity của ma trận này. | Bảo toàn thư mục run, manifests, config và input hashes; thay bất kỳ input nào phải rerun/re-version. |
| E3 | Chương 3.6.1/Bảng 3.3 bản render; UPDATEABLE | Native S0→S1: legal packets 3426→316.25 (−90.77%); offered bursts 2304→8056.125 (+249.66%); loss 0→1.199%. | Raw trace-derived per-run metrics, n=8, paired summary/CI. | `analysis_configdriven.../scenario_summary.csv`, `paired_contrasts.csv`, `runs.csv`; numbers khớp `rendered.txt`. `reproduced_mvp` = native reconstruction. | **PASS** cho số hiện tại trong config hiện tại | Không khớp targets nguồn cũ; seed multipliers chỉ 0.80014–0.80107; generalization yếu. | Nêu rõ config, `n=8`, descriptive t-interval, narrow multiplier range và không suy rộng deployment. |
| E4 | `thesis_requirements.md`/bản nguồn cũ; UPDATEABLE | Targets cũ: S0/S1 82,568/38,281, −53.6%; bursts +60.2%; loss ~0.2%; Welch t=55.2. | Original raw 8-seed traces/config/statistics hoặc independent exact reproduction. | Chỉ là `reported_target`; native hiện tại cho effect khác; Python MVP cũng khác. | **FAIL** | Không có raw/config/seed manifest gốc; Welch test không thể kiểm độc lập. | Không trình bày là reproduced. Chỉ khôi phục nếu có repository, patch, configs, raw traces và exact analysis code gốc. |
| E5 | Chương 3.6.1 diễn giải; UPDATEABLE | Suy giảm do **reservation starvation**, không phải congestion/direct loss. | Reservation occupancy/failure telemetry, matched load controls, BHP↔data association, mediation/counterfactual test. | Parser có attempted/succeeded/failed control reservation và explicit drops; S1 loss tăng. Sweep cho suy giảm trước khi explicit drops lớn, nhưng không cô lập nguyên nhân. | **PARTIAL** | Association không chứng minh “sole causal mechanism”; attack valid bursts tự mang data. | Chỉ nói “phù hợp với cạnh tranh tài nguyên”. PASS causal claim cần reservation-specific intervention/telemetry phân biệt với ordinary offered load. |
| E6 | Chương 3.6.2/Hình 3.5; UPDATEABLE | Sweep 5–50 Mb/s cho legal throughput giảm khi attack load tăng. | Full rate×seed runs, retained traces/hashes, per-rate CIs, anomaly disclosure. | `sweep_analysis_20260726/`: 80/80 cells; legal mean 3449 tại 5 Mb/s và 178 tại 50 Mb/s; offered bursts tăng; explicit loss 0 ở 5–10 và 0.05244 tại 50. | **PASS** cho claim hướng tổng quát/hẹp trong cấu hình hiện tại | Response không đơn điệu: rebound tại 35 Mb/s; effective multiplier ~0.8; không khớp 53,000→12,500 hay anomaly 40 Mb/s/3 seed trong bản văn cũ. | Cập nhật hình/bảng theo retained source-only sweep; không smoothing; điều tra 30/35/40; không gọi endpoint difference là causal estimate. |
| E7 | Bản render mục 3.6.2; UPDATEABLE | Sweep cụ thể giảm ~53,000→12,500 packets, burst ~40,000→160,000 và đảo chiều 40 Mb/s trên 3 seed. | Raw sweep và summary tạo đúng các số/seed đó. | Không có artifact hiện tại khớp. Source-only sweep mới là 8 seed và số khác. | **FAIL** | Claim stale so với artifact hiện tại. | Thay bằng E6 hoặc cung cấp raw provenance riêng cho sweep cũ; không trộn hai sweep. |
| U1 | Chương 3.2; UPDATEABLE | UCI404 có 1,075 rows, 21 predictors, 4 classes, imbalance. | Official dataset hash/schema/profile. | `data/uci404/outputs/provenance.json`: 1,075 rows, 21 predictors, class counts 500/120/155/300; official ARFF SHA-256 `c573...69de`; 15 missing `Packet_lost`. | **PASS** | UCI page nói no missing nhưng ARFF có 15 `?`; phải giữ disclosure. | Hash-check input và công bố schema/missing handling. |
| U2 | Bảng 3.1; UPDATEABLE | Năm model có scores reported (DT/PSO-SVM 100%, v.v.) và point latency. | Original folds/code/config, exact preprocessing, PSO optimizer, latency benchmark protocol. | Source-only duplicate-aware pipeline cho 4 model với accuracy means DT 0.7523, SVM 0.7404, KNN 0.6492, GNB 0.6742; không PSO/latency. | **FAIL** cho exact Bảng 3.1; **PASS** cho audit 4-model mới nếu trình bày riêng | Protocol khác và artifacts gốc thiếu. | Không gắn numbers mới vào protocol cũ; ghi rõ StratifiedGroupKFold, 5 seeds, 25 evaluations và PSO blocker. |
| U3 | Chương 3.3.3/Đóng góp 1; UPDATEABLE | UCI bị “deterministic label leakage”; 12/21 single features gần hoàn hảo; Flood Status importance ~0.10. | Reproduction đúng split/protocol; label-construction provenance; single-feature and out-of-fold RF results. | Audit xác nhận 860 duplicate rows, 215 unique predictor vectors, policy/proxy risk. Nhưng best single feature `Flood Status` accuracy 0.7106; OOF importance 0.2177; không tái tạo 12/21 gần-perfect. | **PARTIAL** | Bằng chứng hỗ trợ benchmark-risk/target-policy leakage risk, không hỗ trợ exact `12/21` hoặc “deterministic” theo protocol mới. | Hạ claim thành “duplicate/dependence và target-policy/proxy risks”; exact claim chỉ PASS nếu code/folds gốc tái tạo và label provenance chứng minh post-label/action derivation. |
| U4 | Source-only UCI audit; UPDATEABLE | Pipeline UCI hiện tại tái lập, chống exact-duplicate crossing và có provenance. | Tests, config, outputs, manifest, file hashes. | 7/7 tests PASS; `config.json` seeds `17,42,73,101,2026`; outputs gồm fold metrics, summaries, figures, schema, provenance và SHA-256 manifest. | **PASS** | Không loại được dependence cao hơn vì UCI thiếu run/site/topology group IDs. | Giữ kết luận đúng phạm vi offline data-quality audit; không dùng làm deployment detector evidence. |
| N1 | Chương 3.6.3/Bảng 3.4; UPDATEABLE | Benchmark mức mạng khoảng 1,300 windows/26 independent runs, không feature đơn lẻ suy biến; SVM MCC 0.9805, DT 0.7611, NB 0.1009. | Dataset CSV + generator; source trace/run IDs; exact window/stride/features/labels; grouped split; model configs; raw folds. | Artifact đúng claim không có. `results/raw/window_dataset.csv` thuộc Python MVP lineage; manifest hiện ghi 320 rows, 16 source cells, 0.25 s, S0/S1. `results/tables/ml_results.csv` còn cho nhiều feature đơn lẻ và cả 4 model đạt 1.0, tức suy biến. `ml_fixed...` là một benchmark khác, không khớp Bảng 3.4. | **FAIL** | Claim trọng yếu nhất về detector không audit được và artifact hiện có còn phản chứng phiên bản cũ của dataset. | Publish/regenerate benchmark từ native traces với immutable run IDs, feature formulas, labels, leave-run/topology-out split và single-feature gate trước ML. |
| N2 | Chương 3.6.4/Bảng 3.5; UPDATEABLE | MCC theo attack rate 1–35 Mb/s; tại 1 Mb/s SVM 0.9368, DT 0.7397. | Per-rate native traces/windows, grouped folds, config and raw fold metrics. | Không có source-only artifact hiện tại khớp các mức và numbers này. Native S1 sweep là impact sweep, không detection sweep. | **FAIL** | Không thể nối Bảng 3.5 với raw data/code. | Regenerate detection-rate benchmark; giữ rate/run holdouts; report uncertainty và khảo sát dưới 1 Mb/s nếu claim limit. |
| M1 | Chương 3.5; UPDATEABLE | Closed-loop bốn trạng thái: allow/rate-limit/isolate/recover, feedback adaptation. | Online state machine; causally available features; model output; transition/action/recovery logs. | Chỉ có architecture prose; scenario có ba external modes và fixed scheduled action. | **FAIL** | Không có four-state transitions, recovery hoặc adaptive feedback. | Implement và test state machine; every transition/action auditable; no future/label/oracle input. |
| M2 | Chương 3.5; UPDATEABLE | RFC 2698 two-rate three-color/token bucket với PIR/CIR/**CBS/PBS**, color policy. | CIR, PIR, CBS, PBS, equations/color actions và matching implementation/tests. | Chỉ có CIR 4 Mb/s; stock NS-2 **single-rate** TBF, bucket `32,000 bits`, queue `0` trong current config. Source/manifest nói rõ thiếu PIR/**CBS/PBS**/color policy. | **FAIL** | Không được gọi stock TBF là RFC 2698 reproduction. | Cung cấp PIR/CIR/CBS/PBS và color semantics hoặc đổi claim thành single-rate drop policer. |
| M3 | Chương 3.5; UPDATEABLE | Graylist, exponential **backoff/hysteresis**, dual thresholds và monitored recovery. | State/config values, timers, transition tests, oscillation and recovery traces. | Không có implementation trong main matrix. | **FAIL** | Thiếu toàn bộ `/backoff/hysteresis` và recovery policy. | Implement/configure thresholds, timers, exponential backoff, hysteresis and restart consistency; test flapping/faults. |
| M4 | Chương 3.6.5/Bảng 3.6 bản render; UPDATEABLE | Rate-limit oracle hiện tại: S1 316.25 → S2 2823.875, 82.42% S0; paired recovery +2507.625 packets. | Paired n=8 raw traces, same config/load, CI and action definition. | Native `scenario_summary.csv` và `paired_contrasts.csv`; TBF attached after fixed 0.25 s to eight known attackers; lower CI of paired improvement >0. | **PASS** cho **oracle action effectiveness trong config này** | Không chứng minh detector safety/false positives; benign test chỉ gồm hai constant 3 Mb/s flows; per-attacker identity known. | Nêu rõ oracle/fixed delay; để claim safety cần benign bursty/high-rate/shared-identity and false-localization tests. |
| M5 | Chương 3.6.5/Bảng 3.6 bản render; UPDATEABLE | Isolation oracle hiện tại: S1 316.25 → S2 2855.625, 83.35% S0; paired recovery +2539.375 packets. | Paired n=8 raw traces; actual network enforcement semantics; all runs retained. | Native matrix 8/8 thành công; `scenario.tcl` redirects known attacker UDP target to local discard sink after fixed 0.25 s. | **PASS** cho **oracle redirect baseline**; **PARTIAL** nếu gọi là operational isolation | Redirect simulator target không phải production ACL/admission rule; no rollback/identity safety. | Không gọi là deployment isolation. PASS operational claim cần authenticated target, install/ack/TTL/rollback and shared `/NAT/customer` safety tests. |
| M6 | Requirements/bản cũ; UPDATEABLE | S2 cũ: rate-limit khoảng 52,244/53,078; isolation 93,238 n=6 hoặc 84,834 n=8, trên baseline. | Original raw runs, versioned exclusion rules/config, exact action/model gate. | Các variants này chỉ là `reported_target`; native current matrix cho số khác và không vượt baseline. Python MVP có n=6 nhưng là abstract model. | **FAIL** | Nhiều phiên bản số và n mâu thuẫn; không có lineage tái tạo từng variant. | Không dùng trong kết luận hiện tại; chỉ phục hồi nếu mỗi version có manifest/raw/config riêng và reason for supersession. |
| M7 | Chương 3.6.5; UPDATEABLE | Hai legal flows 3 Mb/s “được tha” chứng minh behavior-based detection/low false positives. | Classifier/localizer không dùng attacker labels; benign and attack share candidate identities; action logs; diverse benign traffic. | TBF/redirect được áp dụng trực tiếp lên agents đã khai báo attacker. Legal flows không nằm trong target list. | **FAIL** | Đây không phải false-positive test; là oracle source selection. | Blind target localization test; benign high-rate/bursty flows và mixed traffic cùng `/NAT/customer` identity; predeclared service-harm cap. |
| M8 | Timing claim; UPDATEABLE | Detection median `0.10 s` hoặc action delay/window `0.25 s` là phù hợp thời gian thực. | Timestamped telemetry→window close→features→inference→decision→install→ack; p50/p95/p99 under load; SLA. | Native matrix chỉ schedule action tại fixed `0.25 s`; không có classifier latency. UCI pipeline không timing. `0.10 s` chỉ reported. | **FAIL** | Window length/fixed schedule không phải measured upper bound; cũng không phải microsecond core offset. | Đặt edge SLA trước; đo end-to-end p99, dropped/late windows, actuator ack và fault delay. |
| B1 | Threat model; UPDATEABLE | Main experiment mô phỏng forged BHP flooding. | Control-only/orphan BHP reserves resources without data, end-to-end scheduler evidence and legitimate-impact contrast. | Main matrix dùng 8 UDP/CBR → valid BHP + real data bursts. `audits/bhp_model_audit.md` xác định đây là payload-driven valid-burst overload. | **FAIL** nếu gọi forged BHP; **PARTIAL** nếu gọi steady-rate approximation | Tên/threat model và implementation không đồng nhất. | Ghi rõ approximation. Muốn PASS forged claim: config-driven direct-BHP S0/S1/S2, orphan lifecycle/outcome logger và paired legal impact. |
| B2 | Direct-BHP prototype; UPDATEABLE | Có prototype tạo/guard control-only BHP native và chạy không crash. | Generator source, binary provenance, runtime logs, reject and admitted paths. | `VERIFY_2026-07-25.md`: forged pilot rc=0, `RUN_COMPLETE`, `admitted=0 dropped=200 quarantined=199`; admitted-path rc=0, `admitted=2 dropped=198 quarantined=197`; audit `observe=200 detect=2 act=200`. | **PASS** cho smoke/runtime scaffold; **PARTIAL** cho scientific attack experiment | Chưa nối vào main matrix; audit/lifecycle/end-to-end reservation và collateral effect chưa đầy đủ. | Clean source/build provenance; direct-BHP matrix; post-scheduler outcomes; same-ingress coexistence; parser supporting orphan controls. |
| D1 | Claim triển khai thực tế; MIXED | Detector-response loop sẵn sàng triển khai tại OBS edge. | Online feature contract, trusted identity/localization, p99 latency/resources, target API, safety, rollback/fault tests, relevant-environment pilot. | Không có production telemetry/API/hardware trial. Practical utility matrix đánh TRL 2–3 cho defense; UCI audit tooling cao hơn nhưng không phải defense. | **FAIL** | Simulation evidence không nâng thành deployment readiness. `/NAT/customer` aggregation có thể mở rộng blast radius từ source sang cả customer/ingress. | Shadow → mark/log → TTL policer → corroborated isolation; test identity spoofing, shared NAT/customer, capacity, partitions, restart and stale rules. |
| F1 | Hình 3.1–3.7; UPDATEABLE | Mỗi hình/bảng có lineage code→data→output rõ ràng. | Generator command/config, input hashes, output hash, table values matching figure. | UCI source-only figures có manifest/hashes; source-only S1 sweep có `s1_rate_response.png`. Top-level `results/figures/*.png` thuộc Python MVP. Figures nhúng trong DOCX không có manifest thống nhất nối với native matrix hiện tại. | **PARTIAL** | Mixed provenance; một số văn bản/hình vẫn mô tả benchmark/sweep stale. | Tạo manifest riêng cho từng figure/table, ghi generator/input/config SHA-256; regenerate only from approved source lineage. |

## 4. Kết luận theo năm mục tiêu lõi

| Mục tiêu | Kết luận audit | Cách diễn đạt an toàn hiện tại |
|---|---|---|
| 1 — tác động BHP/DoS | **PARTIAL** | Native NS-2.35+nOBS reconstruction chứng minh valid-burst UDP overload làm giảm legal TCP và tăng offered/drop metrics trong cấu hình công bố; chưa chứng minh forged-BHP fidelity hoặc reservation starvation là nguyên nhân duy nhất. |
| 2 — so sánh ML | **PARTIAL** | Có audit source-only tái lập bốn baseline trên official UCI404 với duplicate-group-aware CV; PSO-SVM và latency chưa tái lập; Bảng 3.1 cũ không được xác nhận. |
| 3 — chọn model nhẹ | **FAIL** | Chưa có benchmark không suy biến, online-feature-valid và end-to-end latency/resource measurement để chọn model vận hành. |
| 4 — tích hợp closed loop | **FAIL** | Có architecture và action primitives, nhưng action vẫn theo lịch/oracle; thiếu detector output, attribution, four-state recovery, RFC2698 đầy đủ và `/backoff/hysteresis`. |
| 5 — mô phỏng/đánh giá ứng phó | **PASS** cho oracle mitigation matrix; **PARTIAL** toàn mục tiêu | 32/32 native cells và raw-trace reparse hỗ trợ hiệu quả của TBF/redirect baselines trong config hiện tại; không chứng minh detector-driven safety hoặc deployment. |

**Mục tiêu tổng quát:** **PARTIAL** ở mức simulation/reproducibility scaffold; **FAIL** nếu diễn giải là hệ thống khép kín đã được triển khai hoặc sẵn sàng thực tế.

## 5. Artifact integrity và gate đã chạy

### 5.1 Native NS-2.35+nOBS

- Experiment: `full-400mbps-rate40-8seed`.
- Run schema: `nobs-configured-matrix-run-v1`.
- Config schema: `nobs-matrix-experiment-v1`.
- Manifest timestamp: `2026-07-26T02:59:09.263340+00:00`.
- Completion: `32/32`, failures `0`.
- Validation: all raw traces independently reparsed and matched retained metrics.
- Test suite: **22/22 PASS**.
- Input SHA-256 verified:
  - `nobs/build/ns-allinone-2.35/ns-2.35/ns`: `e2ff7127706c5f01891fc1915f013f3dd1a083fdec32252b4428ba94a76ba6`
  - `nobs/experiments/parse_trace.py`: `9241b82b034b122b456c51267848b14a7541c10eacb6b01a9b4b394db5a2dbc1`
  - `nobs/experiments/scenario.tcl`: `69257782999285e483fc56ad7658b4a8bc9808bf06610df26bb87a64557c4699`
  - `nobs/experiments/configs/full_400_rate40_8seed.json`: `97dc476042c81804fc097ae1693611b7197e08876444c5d1afac1312c346a2fb`

### 5.2 UCI404 source-only

- Official ARFF SHA-256: `c573b83a9b8db30658be8dd53ef5769a94bc03a0695e78d6c130306c60cc69de`.
- Rows/predictors/classes: `1,075 / 21 / 4`.
- Exact duplicate rows/unique predictor vectors: `860 / 215`.
- Missing: `15` cells in `Packet_lost`.
- Fixed CV seeds: `17, 42, 73, 101, 2026`.
- Test suite: **7/7 PASS**.
- Key hashes:
  - `data/uci404/config.json`: `80bb3a5c838eca5463b78377804ce7ce6d7bd1bd3dacc3d8f9679f9e8ee317ac`
  - `data/uci404/pipeline.py`: `92b86001e02b4ab949a0d356127f578ae96e5ca7515ec0dcf943b24263d5a03f`
  - `data/uci404/outputs/provenance.json`: `b96ad3909055546fa295485d27ef9936487ab6b80fd0b74a63cdf89a79e391ba`
  - `data/uci404/outputs/output_manifest.json`: `6981436209b215dac1b219cdb1bbd3535025d063385b10167bf3fa67e12f091a`

### 5.3 Working-tree state

`git status --short` trả về:

```text
?? work/obs_repro/
```

Toàn bộ package kiểm toán/tái dựng hiện **untracked** trong repository cha. SHA-256 giúp kiểm tra file cụ thể nhưng chưa thay thế version-control provenance. Không có DOCX/PDF nào bị sửa bởi audit này.

## 6. Unresolved

1. **Tên đề tài chính thức:** không có text trang tên trong các extraction/PDF pages đã kiểm; cần bản bìa hoặc hồ sơ chính thức.
2. **Original experiment package:** thiếu repository gốc, exact nOBS patch, Dockerfile Ubuntu 18.04, topology/traffic Tcl, seed manifest, raw traces và analysis scripts tạo các số `82,568/38,281`, Welch `55.2`, Bảng 3.1, Bảng 3.4–3.5.
3. **Version authority:** cần chỉ định bản nào là nguồn chuẩn cho số liệu—`thesis_requirements.md`/source PDF cũ, `original.md`, hay `rendered.txt` mới. Hiện bản render mới chỉ cập nhật một phần Chương 3.
4. **Attack semantics:** cần quyết định và ghi tách biệt giữa (a) UDP steady-rate valid-burst overload và (b) forged/orphan control-only BHP. Không được dùng kết quả nhánh (a) để chứng minh fidelity nhánh (b).
5. **Causal mechanism:** chưa tách reservation starvation khỏi ordinary offered-load contention, explicit drop và protocol/TCP dynamics.
6. **Network-window benchmark:** thiếu artifact chuẩn cho ~1,300 windows/26 runs, exact features, labels, class balance, grouping, preprocessing và raw fold metrics. Dataset Python MVP hiện có không hỗ trợ claim không suy biến.
7. **Low-rate detection:** không có raw/code tái tạo MCC tại 1–35 Mb/s; chưa xác định detection break point dưới 1 Mb/s.
8. **PSO-SVM:** thiếu optimizer source/config (swarm, bounds, iterations, objective, preprocessing, seeds); không được bịa reproduction.
9. **Latency:** `0.10 s` và `0.25 s` chưa phải end-to-end measured p99; thiếu feature extraction, inference, controller, install/ack và rollback timings.
10. **RFC2698:** thiếu PIR và **CBS/PBS**, color policy và matching implementation; current TBF là single-rate policer.
11. **Policy state:** thiếu graylist, `/backoff/hysteresis`, dual thresholds, monitored recovery và restart consistency.
12. **Identity/localization:** accepted detector được mô tả ở network-window level nhưng mitigation là per source. Chưa có trusted localizer; shared `/NAT/customer` có thể làm blast radius thành cả customer/ingress.
13. **Safety:** chưa test benign high-rate/bursty traffic, mixed legitimate+attack identity, spoofing, distributed subthreshold attackers, stale rule, controller partition, table exhaustion hoặc failed rollback.
14. **Production actuator:** chưa chỉ định device/API/capacity; simulator redirect không phải operational isolation.
15. **Generalization:** native evidence chỉ từ một topology, 400 Mb/s, one wavelength/link, 5 s, 8 seeds với effective multiplier rất hẹp; chưa có multi-topology/traffic/device validation.
16. **Sweep anomaly:** cần điều tra rebound tại 35 Mb/s trong source-only sweep; không được giữ mô tả anomaly 40 Mb/s/3-seed nếu không có lineage riêng.
17. **Figure lineage:** cần regenerate và manifest từng Bảng/Hình 3.1–3.7 từ nguồn được duyệt; hiện có sự trộn giữa reported targets, Python MVP và native reconstruction.
18. **Version control:** package `work/obs_repro/` còn untracked; cần commit/tag hoặc immutable archive manifest trước khi coi là release evidence.

## 7. Quyết định audit cuối

- **Được hỗ trợ:** scaffold NS-2.35+nOBS chạy được; native valid-burst overload matrix hoàn tất và tái parse; oracle rate-limit/redirect làm giảm attack load và phục hồi legal TCP trong cấu hình hiện tại; official UCI404 có audit source-only, duplicate-aware, có provenance.
- **Chỉ hỗ trợ một phần:** mục tiêu đo impact, tính rủi ro/suy biến của UCI, kiến trúc edge closed-loop, direct-BHP smoke path.
- **Chưa được hỗ trợ:** exact source-thesis targets; exact `12/21` deterministic leakage claim; benchmark 1,300-window/26-run và low-rate MCC; model-selection/deployment latency; detector-driven closed loop; RFC2698 đầy đủ với `/CBS/PBS`; graylist `/backoff/hysteresis`; safe per-source action qua `/NAT/customer`; deployment readiness.

**Gate tổng:** package hiện tại đạt mức **reproducible reconstruction and audit scaffold**, không đạt gate “exact thesis reproduction” và không đạt gate “practically deployable detector-response system”.
