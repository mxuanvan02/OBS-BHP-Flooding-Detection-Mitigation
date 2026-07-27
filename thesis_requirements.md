# Yêu cầu tái lập mô phỏng OBS/BHP — đọc từ luận văn

**Nguồn đọc:** `deliverables/LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.pdf` (pdftotext -layout; 65 trang đánh số trong PDF) và DOCX cùng tên. Báo cáo này chỉ phân tích, không sửa luận văn.

## 1. Tóm tắt mục tiêu và phạm vi

Luận văn xây dựng cơ chế khép kín **phát hiện – ra quyết định – ứng phó** cho tấn công từ chối dịch vụ dạng **BHP flooding** trong mạng Optical Burst Switching (OBS), đặt tại nút biên (không đặt tại lõi vì lõi không có bộ đệm quang và phải xử lý trong khoảng offset rất ngắn). Hai pha thực nghiệm tách biệt:\n\n1. **Pha ML/benchmark:** so sánh Decision Tree, PSO–SVM, KNN, SVM-RBF và Naïve Bayes trên bộ `OBS-Network-DataSet`/UCI (“Burst Header Packet (BHP) flooding attack on OBS network”), rồi kiểm toán rò rỉ nhãn.
2. **Pha mô phỏng động:** NS-2 2.35 + mô-đun nOBS, tái tạo tác động chiếm dụng tài nguyên của BHP flood; sinh benchmark mức mạng không suy biến; thử cơ chế rate-limit/cách ly.

Mục tiêu đo lường: (i) tác động lên throughput hợp pháp, số burst và burst-loss; (ii) chất lượng phát hiện (accuracy, precision, recall, F1, MCC, balanced accuracy, latency); (iii) hiệu quả ứng phó.

## 2. Mô hình OBS/BHP cần tái tạo

- OBS tách BHP (control/header) và DB (data burst), BHP đi trước DB một **offset** để đặt trước tài nguyên/bước sóng tại các nút lõi.
- Tấn công luận văn mô hình hóa bằng các nguồn **UDP tốc độ ổn định**, gửi BHP/burst giả để chiếm reservation; đây là xấp xỉ hiệu ứng flooding, **chưa giả mạo header ở mức giao thức**.
- Tô-pô mô phỏng: **backbone quang hình chữ T, 7 nút (0…6)**; traffic vào qua 2 nút biên và ra tại một nút biên. Sơ đồ chi tiết/ma trận liên kết không được mô tả bằng văn bản đủ để tái tạo.
- Lưu lượng hợp pháp: nhiều luồng **TCP Reno**, truyền file. Có một luồng duy trì kết nối chung trong cả ba kịch bản để tránh lỗi nOBS khi burst generator rỗng.
- Các chi tiết OBS quan trọng (số bước sóng mỗi link, tốc độ link, buffer/queue, thuật toán assembly/scheduling, routing, offset/propagation, burst-size/time threshold) không được định lượng đầy đủ trong luận văn.

## 3. Kịch bản, công cụ và quy trình mô phỏng

### Kịch bản đối chứng

| ID | Hợp pháp | Tấn công | Phòng vệ |
|---|---|---|---|
| S0 nền | Có | Không | Không |
| S1 tấn công | Có | Có | Không |
| S2 ứng phó | Có | Có | Có (gáo token/cách ly) |

- Công cụ: **NS2 2.35 + nOBS**, chạy trong **Docker trên Ubuntu 18.04**, xuất dấu vết burst thật.
- Thời gian mỗi run: **5 s**.
- Lặp lại: **8 random seeds**; cường độ tấn công dao động khoảng **20%** giữa các seed. Giá trị seed cụ thể không công bố.
- S2/cách ly: chỉ còn **6/8 seed** do 2 run lỗi mô phỏng và bị loại; cần giữ nguyên thông tin loại trừ này khi tái lập, không gộp n=6 thành n=8.
- Sweep cường độ: **5–50 Mb/s**, đường cong tác động; khảo sát detection theo cường độ xuống tới **1 Mb/s** (mức “ẩn nhất” trong bảng), chưa tìm điểm gãy thấp hơn.

### Quy trình logic của cơ chế khép kín

1. Theo dõi đặc trưng theo nguồn trong cửa sổ thời gian: tốc độ phát BHP/control, tỷ lệ control không hợp lệ, packet-drop, bandwidth utilization.
2. Mô hình nhẹ (Decision Tree hoặc Naïve Bayes) phân loại 4 trạng thái.
3. Ánh xạ hành động: bình thường → cho qua; nghi ngờ → rate limit tạm thời bằng token bucket; xác định tấn công → cách ly (rate 0) với backoff tăng dần; hồi phục → danh sách phục hồi giám sát.
4. Đo lại throughput/burst loss để đóng vòng.

Thiết kế nêu **two-rate three-color marker/token bucket** theo RFC 2698, graylist, exponential backoff, dual threshold có hysteresis. Tuy nhiên không nêu công thức/cấu hình đầy đủ của token bucket, PIR/CIR, burst size, thời gian backoff, ngưỡng kép, điều kiện chuyển trạng thái.

## 4. Dữ liệu và thuật toán ML

### UCI phase

- 1.075 mẫu (văn bản có lúc gọi tập **UCI404**), **21 đặc trưng số**, nhãn 4 lớp, mất cân bằng.
- Chia tầng **5-fold stratified**; không chia theo nhóm node vì biến node chỉ có 2 giá trị và bị suy biến.
- Mô hình: Decision Tree; PSO–SVM; KNN; SVM với RBF; Naïve Bayes.
- Bảng 3.1 (mean±SD, nhưng không ghi rõ seed/fold/config): NB accuracy 70.0±1.8, precision 70.6±1.6, recall 77.8±1.2, F1 71.8±1.6, latency 0.020 ms; SVM 84.2±2.1 / 86.9±2.0 / 86.5±3.3 / 86.3±2.3, latency 0.219 ms; KNN 91.4±4.4 / 91.7±3.0 / 91.6±4.3 / 91.5±3.5, latency 2.644 ms; DT 100±0 trên mọi chỉ số, latency 0.006 ms; PSO-SVM 100±0, precision/recall/latency n/a.
- Kiểm toán leakage: single-feature DT cho thấy **12/21 features** gần như tự tách nhãn; Random Forest 200 cây permutation importance chỉ nổi bật feature “flooding state” khoảng 0.10, 18 feature gần 0. Kết luận UCI benchmark suy biến, nên không dùng accuracy UCI làm bằng chứng năng lực phát hiện.
- Tác giả chọn DT và NB theo độ nhẹ/giải thích/latency, nhưng việc chọn này cần được tái đánh giá trên benchmark không suy biến; trên benchmark mạng, SVM-RBF tốt hơn rõ rệt.

### Benchmark NS2 không suy biến

Ba lần thử: (1) detection theo nguồn, tốc độ cao → accuracy tuyệt đối do học nguồn/tốc độ; (2) low-rate attack → CV khoảng cách gói đơn lẻ gần như tách UDP/TCP; cả hai bị bác bỏ; (3) detection ở **mức mạng theo cửa sổ thời gian**, không đưa node ID vào feature, được chấp nhận.

- Khoảng **1.300 windows**; 26 lần chạy độc lập khi kiểm tra chéo (luận văn không cung cấp danh sách seed/cấu hình).
- Nhãn: cửa sổ mạng đang bị tấn công hay không; feature là thống kê tổng hợp toàn mạng.
- Kiểm tra chống suy biến: không feature đơn lẻ đạt ngưỡng suy biến.
- Bảng 3.4: SVM-RBF accuracy 0.9931, MCC 0.9805, balanced acc 0.9850, F1 0.9955; KNN 0.9569/0.8871/0.9627/0.9714; DT 0.9131/0.7611/0.8887/0.9430; NB 0.7415/0.1009/0.5357/0.8453.
- Bảng 3.5 MCC theo attack rate (Mb/s): 1: SVM 0.9368, DT 0.7397; 2: 0.9534/0.8839; 3: 0.9850/0.9455; 5: 0.9850/0.9801; 8–35: SVM 0.9867, DT 0.9733–0.9867.

**Thông tin thiếu về dataset:** file CSV/trace không kèm luận văn; tên/ý nghĩa chính xác của 21 UCI features không liệt kê; không có schema benchmark cửa sổ (window length, stride, timestamp alignment), công thức từng feature, cách gán nhãn, class balance, split độc lập theo run, preprocessing/normalization, xử lý missing/outlier, hyperparameters và phiên bản thư viện.

## 5. Kết quả mô phỏng phải khớp

### Tác động S0 vs S1 (8 seeds)

| Chỉ số | S0 | S1 | Thay đổi |
|---|---:|---:|---:|
| Throughput TCP hợp pháp (packets) | 82,568 | 38,281 | −53.6% |
| Byte hợp pháp | 85.8 MB | 39.8 MB | −53.7% |
| Burst gửi trên backbone | 40,462 | 64,839 | +60.2% |
| Burst loss | khoảng 0.2% | khoảng 0.2% | không đổi |

Báo cáo Welch t = **55.2** cho throughput/byte (bảng trình bày cột t không thật rõ; cần kiểm tra code/raw data trước khi diễn giải). Tác giả kết luận thiệt hại chủ yếu do reservation starvation, không phải link/burst loss tăng.

### S2 ứng phó (Bảng 3.6, 95% CI)

| Kịch bản | n | Throughput TCP | 95% CI | so S0 |
|---|---:|---:|---:|---:|
| S0 | 8 | 82,568 | n/a | 100% |
| S1 không phòng vệ | 8 | 38,281 | [36,387; 40,175] | −53.6% |
| S2 rate limit, CIR 4 Mb/s | 8 | 52,244 | [48,575; 55,913] | 63.3% |
| S2 cách ly | 6 | 93,238 | [83,147; 103,329] | 112.9% |

Rate limit phục hồi khoảng 31% phần throughput mất; cách ly vượt baseline nhẹ, được tác giả cảnh báo là phụ thuộc topo/tài nguyên/TCP và chưa được tổng quát hóa. Hai luồng hợp pháp 3 Mb/s dưới ngưỡng được pass ở mọi run; 8 nguồn tấn công khoảng 12 Mb/s bị xử lý. Ngưỡng rate-limit cam kết **CIR = 4 Mb/s**; độ trễ phát hiện khoảng **0.25 s**, lấy từ kích thước cửa sổ benchmark chứ không tối ưu riêng.

## 6. Công thức/định nghĩa cần dùng khi tái lập

Luận văn chủ yếu mô tả bằng lời, gần như không đưa phương trình triển khai. Các đại lượng tối thiểu nên định nghĩa rõ trong simulator/evaluator:

- `throughput_legal = số byte hoặc packet TCP hợp pháp nhận thành công / thời gian đo`; cần thống nhất bảng đang dùng packet hay byte.
- `burst_loss_rate = lost_bursts / offered_bursts` (luận văn chỉ báo “~0.2%”, không cho raw counts).
- `MCC = (TP*TN − FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))`.
- `balanced_accuracy = (TPR + TNR)/2` cho nhị phân (hoặc macro recall cho đa lớp).
- `precision = TP/(TP+FP)`, `recall = TP/(TP+FN)`, `F1 = 2PR/(P+R)`; cần biết macro/weighted/micro, luận văn không nói rõ.
- CI 95%: chưa nói dùng t-interval/bootstrap; 8 seed và S2 cách ly n=6 nên phải ghi rõ cách tính.
- Token bucket/two-rate marker cần ít nhất CIR, PIR, CBS/PBS, màu/điều kiện drop-mark; các giá trị này không có ngoài CIR 4 Mb/s ở S2.

## 7. Các bảng/hình cần tái tạo

- Hình 3.1: accuracy DT từng feature (UCI404).
- Hình 3.2: permutation importance RF 200 cây.
- Hình 3.3: kiến trúc closed-loop tại ingress edge.
- Hình 3.4: throughput S0/S1 trên 8 seed.
- Hình 3.5: sweep 5–50 Mb/s: legal throughput khoảng 53,000 → 12,500 packets; backbone burst khoảng 40,000 → 160,000; có đảo chiều nhất quán tại 40 Mb/s trên 3 seed, không smoothing.
- Hình 3.6: MCC theo độ ẩn (bảng 3.5).
- Hình 3.7: S0/S1/rate-limit/isolation với CI 95%.

## 8. Blocker đối với tái lập đầy đủ

1. **Thiếu mã nguồn/topology script/config nOBS và Dockerfile**; không thể biết patch nOBS, trace format hay cách tích hợp detector/rate limiter.
2. **Thiếu random seeds cụ thể**, phân phối dao động ±20%, seed-to-run mapping và raw per-run outputs.
3. Thiếu topo T đầy đủ (edge/link/route), link rate/delay, số wavelength, wavelength conversion, scheduling/reservation, queue/buffer, assembly threshold, offset.
4. Thiếu traffic generator config: số TCP/file size/start time/packet size/rate/route; số nguồn UDP, packet size, start/stop, chính xác rate và cách biến thành BHP/DB.
5. Thiếu định nghĩa/công thức và giá trị của cửa sổ detection, stride, feature schema, label rule; thiếu file benchmark ~1,300 windows và raw traces.
6. Thiếu ML preprocessing, hyperparameters (DT depth/criterion, NB variant, KNN k, RBF C/gamma, PSO swarm/iterations/objective), software versions và latency benchmark hardware.
7. Thiếu cấu hình đầy đủ token bucket (PIR, CBS/PBS), graylist/backoff/hysteresis, state transition và chính sách phục hồi; chỉ biết CIR 4 Mb/s, detect delay ~0.25 s.
8. Thiếu cách tính CI/Welch test, raw samples và lý do/tiêu chí loại 2 seed lỗi ở isolation.
9. S2 “cách ly” vượt baseline 112.9% có nguy cơ phụ thuộc setup; cần tái kiểm chứng nhiều topo/traffic trước khi coi là kết quả tổng quát.
10. Tấn công là UDP steady-rate approximation, **không phải BHP header spoofing thật**; tái lập chỉ chứng minh reservation/resource starvation ở mức mô hình.

## 9. Simulator tối thiểu được khuyến nghị

### MVP để kiểm tra các claim định lượng chính

Dùng **NS-2.35 + nOBS đúng phiên bản/patch của luận văn** (ưu tiên container Ubuntu 18.04) với một discrete-event model gồm:\n\n- topo T 7 node, nhiều wavelength/link và OBS one-way reservation;\n- ingress burst assembly + BHP đi trước offset; core scheduler không buffer quang;\n- 2–3 TCP Reno legal flows (trong đó 2 flow 3 Mb/s persistent nếu muốn kiểm tra false-positive claim), 8 UDP steady-rate attacker khoảng 12 Mb/s;
- S0/S1/S2, 5 s/run, 8 seed; lưu per-run throughput legal, bytes, offered/sent/lost bursts, event timestamps;
- detector baseline window 0.25 s ở ingress; trước mắt dùng rule rate > 4 Mb/s để tái tạo S2 (chưa cần ML), sau đó cắm DT/NB;
- rate-limit CIR 4 Mb/s và hard isolation rate 0; mọi tham số còn thiếu phải để trong config và ghi là giả định.

### Gate kiểm chứng

1. Trước hết chạy S0/S1 và yêu cầu hướng tác động: throughput legal giảm khoảng 53.6%, burst sent tăng khoảng 60%, burst loss gần như không đổi.
2. Chạy S2 rate-limit và isolation; không kỳ vọng khớp 112.9% nếu chưa có đúng topo/resource/TCP config.
3. Chạy sweep 5–50 Mb/s và kiểm tra tính đơn điệu/điểm bất thường 40 Mb/s.
4. Xuất trace window-level; kiểm tra single-feature accuracy không suy biến trước khi huấn luyện classifier.
5. Chỉ sau khi raw metrics khớp mới so sánh ML; báo cáo n riêng, seed, CI method, và mọi run bị loại.

**Kết luận thực dụng:** luận văn cung cấp đủ mục tiêu, cấu trúc thí nghiệm và các con số đích để xây một MVP, nhưng **chưa đủ đặc tả để tái lập bit-for-bit hoặc tái tạo chắc chắn các bảng kết quả**. Artifact bắt buộc cần xin thêm là repository mã nguồn + nOBS patch + Dockerfile + topology/traffic configs + UCI/raw NS2 dataset + seed manifest.
