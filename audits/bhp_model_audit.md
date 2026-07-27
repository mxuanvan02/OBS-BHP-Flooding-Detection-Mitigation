# Kiểm toán mô hình BHP flooding trên NS-2.35+nOBS

**Phạm vi kiểm toán:** `thesis_requirements.md`; nhánh chạy chính `nobs/experiments/{scenario.tcl,run_matrix.py,parse_trace.py}`; cấu hình `configs/full_400_rate40_8seed.json`; source nOBS/BHP trong cây build; các trace/audit hiện có. Không sửa source mô phỏng.

## Kết luận ngắn

Có **hai nhánh khác nhau** và hiện chưa được nối thành một thí nghiệm thống nhất:\n\n1. **Nhánh ma trận đang dùng để tạo số liệu:** 8 UDP/CBR đi qua burstifier nOBS, tạo **BHP hợp lệ đi kèm data burst thật**. Đây là *payload-driven valid-burst overload/resource contention*. Nó khá gần **xấp xỉ UDP steady-rate** được luận văn mô tả, nhưng không phải BHP giả/orphan theo nghĩa cơ chế tấn công trong tên luận văn.
2. **Nhánh C++ BHP trực tiếp:** đã có `Agent/BHPFlood`, `BhpGuard` và audit logger; nó tạo `PT_OP_BURST` không có payload và chặn trước scheduler. Tuy nhiên nhánh này chỉ xuất hiện trong scenario thử nghiệm riêng, không được `run_matrix.py`/`scenario.tcl` chính sử dụng, chưa đo tác động mạng, và lifecycle/telemetry còn thiếu. Chưa thể dùng nó để nâng claim của ma trận hiện tại thành “mô phỏng BHP flooding khép kín”.

Vì vậy, claim an toàn hiện tại là: **tái dựng được overload OBS bằng tải UDP sinh burst hợp lệ và hai oracle mitigation baselines; có prototype source-level cho control-only BHP/guard, mới ở mức smoke test.**

## 1. Cơ chế hiện tại thực sự mô phỏng gì?

- Tô-pô quang T 7 nút, route `0-1-2-3-4` và `5-6-2-3-4`; một wavelength/link, 400 Mb/s, JET, converter/FDL theo config.
- Hai TCP Reno/FTP hợp pháp, đều bị giới hạn access 3 Mb/s; một flow vào nút 0, một flow vào nút 5.
- S1 tạo 8 nguồn UDP/CBR, rate tham số là **mỗi attacker**, nhân hệ số seed chung `U[0.8,1.2]`; cấu hình ma trận hiện chọn 40 Mb/s/source.
- UDP được đưa vào `OpSRAgent`, sau đó burstifier gom payload và tạo cặp BHP + data burst. Vì có data thật tương ứng, reservation được sử dụng bởi chính data attacker; đây không phải control-only/orphan BHP.
- S2 rate-limit gắn stock NS-2 `TBF` vào **UDP payload path** sau đúng 0.25 s, CIR 4 Mb/s/source. S2 isolation đổi target UDP sang local `Null` sau đúng 0.25 s. Cả hai biết trước attacker và thời điểm hành động; không có observation/classifier/decision online.

**Bằng chứng source:** `scenario.tcl:289-316` tạo UDP/CBR; `:318-325` gắn TBF theo lịch; `:328-337` redirect theo lịch. `run_matrix.py` luôn gọi file này và parser hiện giả định mọi `OP_BURST` có cặp control/data dựa trên UID kề nhau.

### Kết quả trace hiện có không khớp các con số đích của luận văn

Ma trận cấu hình hiện tại hoàn tất 32/32 cell, nhưng mô hình cho hiệu ứng khác đáng kể (`analysis_configdriven_rate40_8seed_20260726_100244/scenario_summary.csv`):

| Chỉ số | S0 | S1 | Diễn giải |
|---|---:|---:|---|
| TCP legal packets | 3426.0 | 316.25 | giảm ~90.8%, không phải ~53.6% |
| offered bursts | 2304.0 | 8056.1 | tăng ~249.7%, không phải ~60.2% |
| burst-drop ratio | 0 | ~1.20% | tăng, không giữ gần ~0.2% |
| S2 rate-limit legal packets | 2823.9 | 82.4% S0 | phục hồi mạnh nhưng khác bảng luận văn |
| S2 isolation legal packets | 2855.6 | 83.4% S0 | không có hiện tượng 112.9% S0 |

Ma trận 12 Mb/s cũ gần như không làm giảm TCP. Điều này cho thấy kết luận định lượng phụ thuộc mạnh vào rate/config tái dựng; không được trình bày như reproduction của bảng luận văn.

## 2. Bằng chứng source và trace: nhánh direct-BHP hiện có

### Phần đã hiện thực

- `op-bhp-flood-agent.cc:68-157` tạo trực tiếp control `PT_OP_BURST`, `burst_type=0`, khai báo `burst_size`, và gắn một descriptor phantom có `packet_num=0`; không cần UDP/CBR.
- `op-sragent.cc:543-547` gọi guard trước `LinkReservation_[slot_no].recv(...)` (`:591`), đúng vị trí admission trước reservation.
- `BhpObservation` không chứa nhãn attack/control-only; `BhpGuard` dùng token theo số BHP và claimed reservation cost, với trạng thái NORMAL/LIMITED/QUARANTINED.
- Smoke trace `bhp_verified_admit` có BHP trực tiếp UID 278/280 trên path 5→6→2; audit cho hai ALLOW, sau đó DROP/LIMITED và QUARANTINE. Đây là bằng chứng prototype generator/guard thực sự chạy trong binary.

### Giới hạn nghiêm trọng

1. **Không nằm trong experiment chính.** `scenario.tcl` chính không tạo `Agent/BHPFlood` hay bật guard. `bhp_control_scenario.tcl` là fixture hard-code; nhánh UDP bị vô hiệu bằng `if {0 && ...}` và S0/S1/S2 không còn khác nhau. Các thư mục `bhp_matrix_fix/{S0,S1,S2...}` đều báo cùng `admitted=0 dropped=200 quarantined=199`.
2. **Lifecycle control-only chưa được chứng minh nhất quán.** Source hiện tại có nhánh nhận diện phantom bằng `packet_num==0`, rồi free control/phantom ngay sau reservation ở first-link path (`op-sragent.cc:618-628`), hàm ý chỉ giữ reservation outgoing đầu tiên. Trái lại, trace `bhp_verified_admit/out.tr` cho UID direct-BHP 278/280 đi ít nhất `5→6→2`. Mâu thuẫn source/trace này (hoặc điều kiện `headeraddedfirsttime`, hoặc provenance binary/source) phải được giải quyết trước khi claim reservation end-to-end.
3. **Audit ghi ý định, chưa ghi sự thật scheduler.** `ACT reservation_attempted=1` được log trước khi gọi `LinkReservation_`; không có call site cho `log_outcome`, `log_legitimate_impact`, `register_legitimate_pair` hay `register_attack_generation` (hai hàm register còn là no-op). Vì thế chưa chứng minh accepted/rejected reservation, orphan outcome, collateral damage hay right-censoring bằng audit.
4. **Chưa có coexistence/collateral test.** Fixture direct-BHP đặt legal flow ở ingress 0, attacker/guard ở ingress 5; guard chưa xử lý legal và forged BHP chung một trusted attachment. Không đo false positive hay legitimate impact.
5. **Không phải detector/response của luận văn.** Guard là rule/token bucket 3 trạng thái, không phải classifier 4 trạng thái trên cửa sổ 0.25 s; không có invalid-control ratio, drop/utilization features, DT/NB/SVM, graylist, exponential backoff hay adaptive feedback. State được key theo một `bhp_guard_ingress_` cố định của node, chưa phải per-source trusted identity.
6. **Không có CIR 4 Mb/s/RFC2698 ở control path.** Guard dùng BHP-event/reservation-cost budget; CIR 4 Mb/s hiện chỉ thuộc TBF payload của nhánh cũ.
7. **Source-of-truth chưa sạch.** Overlay và cây build không đồng nhất: riêng `op-bhp-flood-agent.cc` khác ở `sched()`/`resched()`; `op-sragent.cc` cũng khác hash. Clean rebuild từ overlay hiện không được chứng minh tái tạo binary/trace đang kiểm toán.
8. **Parser hiện không chấp nhận orphan control.** `parse_trace.py` fail nếu có `OP_BURST` không ghép được thành cặp control/data, nên không thể dùng nguyên parser ma trận cho direct-BHP.

## 3. Thiếu gì để gọi là BHP flooding sát luận văn?

### Để sát **mô hình thực nghiệm được luận văn mô tả**

Nhánh UDP hiện tại đã đúng loại xấp xỉ broad-level, nhưng còn thiếu cấu hình gốc: topology/link/wavelength/assembly/offset, số flow/file, seed map và raw trace. Kết quả hiện không khớp hướng/độ lớn đầy đủ, nên chỉ được gọi là **reconstruction under explicit assumptions**.

### Để sát **cơ chế BHP flooding trong tên/threat model**

Cần control BHP khai báo reservation nhưng không có data tương ứng; control phải đi qua scheduler ở từng hop như BHP thật, đồng thời logger chứng minh `reservation accepted` và `data missing`. Prototype hiện mới đạt tạo control trực tiếp + guard ở ingress, chưa đạt end-to-end evidence.

### Để sát **đóng vòng phát hiện–ứng phó**

Cần observation online → detector/state → actuator trước reservation, không dựa scenario/attacker ID/thời điểm định sẵn; phải có attribution tin cậy, recovery/hysteresis, latency thực đo và legitimate-impact/false-positive accounting. Phần này chưa có trong bất kỳ ma trận nào.

## 4. Thay đổi code tối thiểu có thể triển khai

Theo thứ tự ưu tiên:
1. **Chốt source chuẩn:** đồng bộ các file BHP/`op-sragent` giữa overlay và build; tạo clean-build gate và hash manifest. Không chạy nghiên cứu từ cây build sửa tay.
2. **Tạo scenario direct-BHP riêng, config-driven:** S0 legal only; S1 legal + `Agent/BHPFlood`, guard off; S2 cùng traffic, guard on. Không tái định nghĩa nghĩa của `scenario.tcl` payload hiện tại.
3. **Sửa lifecycle control-only:** BHP phải được forward và reserve trên từng hop; tuyệt đối không schedule phantom data; cleanup đúng một lần tại egress/drop/end-run. Dùng metadata lifecycle tường minh, không suy control-only từ `packet_num==0`; metadata không được đưa vào detector.
4. **Sửa audit theo hậu quả thật:** log ACT sau decision nhưng log OUTCOME sau `LinkReservation_`; ghi result, hop, UID, reservation interval; đăng ký legitimate control/data pair và attack generation; ghi `LEGIT_IMPACT` và right-censored.
5. **Attribution/enforcement tối thiểu:** key policy theo trusted ingress attachment (không theo source field tự khai báo); cho legitimate và attack cùng attachment trong test. Nếu mục tiêu luận văn giữ “per-source”, cần thêm trusted per-source/tenant handle hoặc hạ claim xuống ingress-aggregate defense.
6. **Actuator tối thiểu:** giữ policer theo BHP events + claimed reservation cost trước scheduler; quarantine có hold-down/release online. Chưa gọi nó là RFC2698/CIR 4 Mb/s nếu chưa định nghĩa mapping và PIR/CBS/PBS.
7. **Parser/evaluator mới:** đọc audit schema cho direct control; không ép control/data pairing; join ground truth sau decision. Giữ parser cũ chỉ cho valid-burst branch.
8. **ML là bước sau:** trước mắt rule detector cho causal baseline. Chỉ cắm DT/NB/SVM khi đã định nghĩa được feature cửa sổ online và split theo independent run; không dùng UCI label-leaky model làm actuator.

## 5. Test/gate đề xuất

- **Build/provenance:** clean overlay+patch build tạo binary hash xác định; fixture cũ chạy không đổi khi BHP feature tắt.
- **Direct-generation unit:** một `emit()` tạo đúng một control `PT_OP_BURST`, không UDP/TCP và không data event.
- **End-to-end reservation:** guard off, cùng UID tạo accepted reservation trên mọi hop của route; không có matching data; reservation tự hết đúng thời gian khai báo.
- **Guard placement:** với DROP, UID không xuất hiện trong scheduler/outgoing reservation; audit không được ghi “attempted/accepted” trước call thật.
- **Causality/no oracle:** `observe <= detect <= decide <= act`; thay scenario label, attacker registry hay future data outcome không làm đổi decision.
- **Attribution:** spoof `hdr_burst.source` không chuyển budget; trusted attachment mới là key.
- **Coexistence:** legal + forged BHP chung attachment; mọi legal drop có UID/bytes/packets và false-positive rate.
- **Lifecycle safety:** ASan/Valgrind hoặc equivalent fixture cho leak/double-free/use-after-free; stop/end-run ghi right-censored.
- **Parser/schema:** audit schema validation; control-only không làm parser fail; mỗi action join được observation và outcome.
- **Research matrix:** 5 s, 8 seed paired, sweep rate/claimed size/BHP rate; báo n thật, CI method và exclusion. Gate đầu tiên là S1 gây giảm legal throughput do reservation contention; không ép khớp 53.6% nếu thiếu config gốc.
- **Defense utility:** S2 giảm admitted malicious reservation cost và phục hồi legal throughput, đồng thời collateral/latency/overhead dưới SLO khai báo trước; không chấp nhận profile được fit sau khi xem test.

## Câu hỏi unresolved

1. Luận văn muốn giữ threat model **UDP steady-rate sinh valid bursts** hay nâng lên **forged/orphan BHP**? Hai mô hình phải được báo cáo tách biệt.
2. BHP giả phải chiếm reservation ở mọi core hop hay chỉ cần chứng minh starvation tại ingress outgoing link?
3. Đơn vị policy chính là BHP/s, claimed reservation-seconds, hay CIR payload 4 Mb/s; mapping giữa chúng là gì?
4. “Per-source” có trusted identity nào trong nOBS, hay defense thực tế chỉ có thể cách ly cả ingress/customer aggregate?
5. Có repository/config/seed/raw trace gốc để hiệu chỉnh topo và kiểm chứng các mốc −53.6%, +60.2%, ~0.2% loss không?
6. Cần tái hiện architecture 4-state/ML trong NS-2, hay chỉ cần rule-based causal guard làm baseline rồi đánh giá ML offline từ audit windows?
