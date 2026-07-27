# Thiết kế tối thiểu nhưng trung thực cho BHP flooding trên nOBS

## Trạng thái tài liệu

Đây là **audit source và đặc tả patch**, không phải kết quả thực nghiệm và không phải patch đã triển khai. Tài liệu không thay đổi `scenario.tcl`, parser, trace hiện có, hay tạo số liệu mới.

Source chuẩn để sửa là overlay tại `nobs/`; cây `nobs/build/ns-allinone-2.35/ns-2.35/` chỉ là cây build đã ghép với NS-2.35. Sáu file optical cốt lõi được kiểm tra trong hai cây hiện giống byte-for-byte.

## Kết luận bắt buộc về scenario hiện tại

### (1) UDP/CBR trước burstifier có mô hình đúng forged BHP flooding không?

**Không.**

Đường đi hiện tại là:

```text
Application/Traffic/CBR
  -> Agent/UDP
  -> OpSRAgent (gắn source route cho packet điện tử)
  -> OpClassifier
  -> BurstAgent::recv(packet không phải PT_OP_BURST)
  -> BurstAgent::burstsend()
  -> BHP hợp lệ + data burst tương ứng
  -> OpSRAgent::recv(PT_OP_BURST)
  -> OpSchedule::recv()/ScheduleBurst()
```

Bằng chứng source:

- `nobs/experiments/scenario.tcl:174-198` tạo payload UDP/CBR và trỏ UDP vào `OpSRAgent`.
- `optical/op-classifier.cc`, `OpClassifier::recv()`, nhánh packet không phải `PT_OP_BURST` tại khoảng dòng 176-188 chuyển packet sang `BurstAgent` khi bước kế tiếp đi vào optical core.
- `optical/op-burst_agent.cc`, `BurstAgent::recv()`, nhánh `ptype != PT_OP_BURST` tại khoảng dòng 246-428 gom payload theo ngưỡng số packet/kích thước/timeout.
- `BurstAgent::burstsend()` tại khoảng dòng 500-598 luôn gắn control packet với data burst qua `burstch->burst = p`, gửi control trước, rồi để `OpSRAgent` lập lịch data burst.
- `optical/op-sragent.cc`, `OpSRAgent::recv()`, khoảng dòng 529-575 lập reservation từ control rồi schedule cả control lẫn data burst.

Vì vậy lưu lượng tấn công hiện tại tạo **nhiều BHP hợp lệ do tải data lớn**, không tạo BHP giả/không có data. Nó có thể được gọi trung thực là *payload-driven burst/control-load overload* hoặc *resource starvation through valid bursts*, nhưng không phải *forged BHP flooding*.

### (2) TBF giữa UDP và OpSRAgent có phải BHP control-plane policing không?

**Không.**

- `scenario.tcl:203-210` gọi `$udp attach-tbf`.
- `tcl/lib/ns-agent.tcl`, `Agent instproc attach-tbf`, chỉ chèn TBF giữa target hiện tại của UDP và UDP.
- `adc/tbf.cc`, `TBF::recv()`, tính token bằng `hdr_cmn::size()` của packet đầu vào, queue/drop chính các packet đó.

Tại điểm này packet vẫn là UDP payload; BHP chưa được tạo. TBF đo **bit của data-plane payload**, có thể queue packet và chỉ gián tiếp làm giảm tần suất burstification. Nó không quan sát `burst_type == 0`, không đo BHP/s hay claimed reservation load, không nằm trước `OpSchedule::ScheduleBurst()`, và không có policy theo ingress control identity. Do đó đây không phải BHP control-plane policing.

### (3) Isolation bằng Tcl stop sau khoảng trễ cố định có phải closed-loop detector-actuator thực tế không?

**Không.**

`scenario.tcl:49-51, 213-216` tính thời điểm stop trực tiếp từ `attack_start + detect_delay` rồi gọi `$attack stop`. Không có observation, detector, quyết định online, hay feedback từ nOBS. Hành động biết trước ground truth và diễn ra tại application của attacker thay vì tại control ingress. Đây là **oracle-scheduled source shutdown**, không phải closed loop và không phải actuator có thể triển khai tại OBS node.

## Threat model được hỗ trợ

### Đối thủ

- Đối thủ đã chiếm quyền hoặc giả mạo được burst-control producer **ở phía trước một trusted OBS enforcement ingress** đã được phép kết nối vào core; chính `OpSRAgent`/guard tại điểm enforcement vẫn được tin cậy.
- Đối thủ phát BHP đúng cú pháp, khai báo một data burst/reservation có kích thước và đích hợp lệ, nhưng không gửi data burst tương ứng.
- Mục tiêu là chiếm các khoảng reservation trong `OpSchedule`, làm BHP/burst hợp lệ bị từ chối hoặc tăng ảnh hưởng lên lưu lượng hợp lệ.
- Nhiều producer có thể cùng xuất hiện, nhưng policy tối thiểu quy trách nhiệm theo **trusted ingress attachment**, không tin trường `source` do BHP tự khai báo.

### Tài sản bảo vệ

- Admission/reservation tại `OpSRAgent` trước `LinkReservation_[slot_no].recv()`.
- Khả năng phục vụ của burst hợp lệ và tác động lên packet/byte hợp lệ đi kèm.
- Tính nhân quả và khả năng audit của observation → detection → decision → action.

### Ngoài phạm vi

- Mã hóa, xác thực BHP, key management và chống giả mạo ở mức giao thức thật.
- Đối thủ đã chiếm core node hoặc sửa code detector.
- Mô hình CPU/control-processor queue thực tế; nOBS hiện chủ yếu mô hình wavelength reservation, không mô hình năng lực xử lý BHP của controller.
- Xác định một user nằm sau cùng một ingress khi mọi BHP cùng đi qua một trusted attachment. Cơ chế tối thiểu cách ly ingress aggregate và phải đo collateral damage.

## Cơ chế tấn công source-level tối thiểu

### Không tạo packet type mới

Tái sử dụng `PT_OP_BURST` và `hdr_burst`, vì `OpSchedule::recv()` đã phân biệt control bằng `burst_type == 0` và dùng `burst_size`, route, lambda cùng timing để tạo reservation.

### `Agent/BHPFlood`

Thêm một agent C++ phát **control packet trực tiếp** vào `OpSRAgent` của optical ingress, không tạo UDP/TCP và không đi qua `BurstAgent::recv()`.

Mỗi lần `emit()`:

1. Allocate một `PT_OP_BURST` control packet và một descriptor data burst “phantom”.
2. Khởi tạo đầy đủ các trường mà `OpSRAgent`/`OpSchedule` đọc: `burst_type=0`, `burst_size`, `packet_num`, `source`, `destination`, `flow`, `first_link`, `lambda`, `delayedresv`, route-related state và common/IP header.
3. Gắn descriptor qua `control->burst` chỉ để thỏa invariant con trỏ cũ của nOBS.
4. Đánh dấu internal `control_only`; trường này chỉ điều khiển lifecycle, **không được đưa vào detector**.
5. Gửi control vào `OpSRAgent`. Tại ingress, agent thêm source route và control đi qua chính `LinkReservation_[slot_no].recv()` như BHP hợp lệ.
6. `OpSRAgent` không schedule phantom data khi `control_only` được bật. Reservation đã được tạo vẫn tồn tại đến hết khoảng mà BHP khai báo; không có data đến để sử dụng nó.
7. Khi control đến egress hoặc bị drop trước đó, giải phóng descriptor đúng một lần.

Đây là forged-BHP resource-reservation flooding: attack event là BHP, chi phí được gây ra tại reservation path, và không có payload traffic dùng làm proxy.

### Phạm vi diễn giải

Agent này mô hình một producer upstream bị chiếm quyền đi vào một enforcement ingress còn tin cậy, không mô hình việc attacker sửa chính guard và không mô hình một host Internet tùy ý có thể gửi BHP xuyên qua electronic access network. nOBS không có control-channel/authentication model đủ để tuyên bố các trường hợp đó.

## Closed-loop defense

### Vị trí bắt buộc

Guard chạy trong `OpSRAgent::recv()` cho `PT_OP_BURST && hdr_burst::burst_type == 0`, **ngay trước** lời gọi:

```cpp
LinkReservation_[slot_no].recv(packet, conversiontype_, 0)
```

Đây là điểm cuối cùng có thể drop/rate-limit một BHP mà chưa tạo reservation trên outgoing optical link. Bản tối thiểu chỉ bật guard tại trusted ingress (`headeraddedfirsttime == true`). Bật cùng actuator ở transit core cần thiết kế thêm xử lý data burst đã được schedule từ ingress và không còn là patch tối thiểu an toàn.

### Observation interface

Detector chỉ nhận một cấu trúc immutable `BhpObservation` gồm dữ liệu nhìn thấy tại control ingress:

- simulation/event time;
- trusted ingress ID do local `OpSRAgent` đóng dấu, không lấy identity từ trường source do packet khai báo;
- packet UID cho audit;
- destination/route class nhìn thấy;
- claimed `burst_size`, `packet_num`, và reservation cost suy ra từ header cùng `LINKSPEED`;
- BHP arrival count/rate và tổng claimed reservation load trong state online của chính ingress;
- kết quả kiểm tra cú pháp/range/route consistency của BHP.

Detector **không được đọc**:

- `control_only` hay nhãn legitimate/malicious;
- danh sách node attacker;
- `attack_start`, thời điểm dự kiến detect, scenario name;
- future event, delivered throughput, parser output hay kết quả cuối run;
- việc một data burst có xuất hiện trong tương lai hay không.

Việc “không thấy data sau BHP” không phù hợp cho actuator trước reservation nếu phải chờ đến tương lai. Có thể log nó làm outcome/forensics, nhưng không dùng cho quyết định admission hiện tại.

### Detector online

`BhpGuard` duy trì state riêng cho từng trusted ingress:

- admission profile theo số BHP event;
- profile theo tổng claimed reservation cost để một BHP khai báo cực lớn không né được giới hạn theo packet count;
- rolling/leaky state và hysteresis cấu hình ngoài source;
- state `NORMAL`, `LIMITED`, `QUARANTINED`.

Một transition xảy ra chỉ từ observation vừa đến và state quá khứ. Ngưỡng phải được cấu hình/calibrate từ clean workload và service policy; không hard-code để khớp bảng luận văn hoặc kết quả mong muốn.

### Decision và actuator

`BhpDecision` trả về một trong các action:

- `ALLOW`: cho BHP đi tiếp tới `LinkReservation_`;
- `DROP_OVER_PROFILE`: drop BHP hiện tại khi token/event hoặc reservation-cost budget không đủ; không queue BHP vì queue làm sai offset/timing của JET;
- `QUARANTINE_INGRESS`: drop mọi BHP mới từ trusted ingress trong hold-down được cấu hình;
- `RELEASE`: hết quarantine theo state machine/hysteresis, không theo Tcl oracle.

Khi drop tại ingress:

- không được gọi `LinkReservation_`;
- với control hợp lệ do `BurstAgent` tạo, phải giải phóng/trace data burst và các packet chứa trong đó để không tạo orphan hoặc leak;
- với forged `control_only`, giải phóng phantom descriptor;
- log action trước khi free packet.

Rate limit phải có đơn vị BHP event/reservation cost, không tái dùng stock `TBF` đo bit của UDP.

## Telemetry và tách ground truth khỏi detector

Thêm một logger append-only với schema versioned. Các record tối thiểu:

- `BHP_CREATE`: packet UID/burst ID, producer attachment, claimed reservation, và event time;
- `OBSERVE`: trusted ingress, observable fields, detector state trước observation;
- `DETECT`: first transition time, rule/profile bị vượt, state trước/sau;
- `DECIDE`: decision time, action được chọn, counters/budget chỉ từ quá khứ và hiện tại;
- `ACT`: action time, BHP UID, ingress, `reservation_attempted` và kết quả cleanup;
- `OUTCOME`: reservation accepted/rejected, control delivered, data arrived/missing, hoặc right-censored;
- `LEGIT_IMPACT`: BHP hợp lệ bị drop/delay, paired data-burst bytes/packet count bị suppress, và UID liên quan.

Để đo legitimate impact mà không làm rò nhãn vào detector:

- `BurstAgent::burstsend()` đăng ký mapping evaluation-only từ control UID sang paired legitimate data UID/count/bytes;
- `BHPFloodAgent::emit()` đăng ký mapping attack-generation riêng;
- `BhpGuard::observe()` chỉ nhận `BhpObservation`, API không chứa mapping/label;
- logger/evaluator join UID sau decision để tạo `LEGIT_IMPACT` và confusion accounting.

Phải log riêng:

```text
attack_emit_time
first_observation_time
first_detection_time
decision_time
action_time
```

Detection latency và actuation latency chỉ được tính từ các timestamp đã log, không gán sẵn một khoảng cố định.

## Exact files/classes/methods cần patch

### Canonical nOBS overlay

| File | Class/struct/method | Thay đổi dự kiến |
|---|---|---|
| `nobs/optical/op-burst_agent.h` | `hdr_burst` | Thêm lifecycle metadata tối thiểu cho `control_only`; metadata này không được lộ qua `BhpObservation`. Trusted ingress phải lấy từ cấu hình local của guard, không tin packet header. |
| `nobs/optical/op-burst_agent.h` | `BurstAgent` | Khai báo helper cleanup/telemetry cần dùng chung cho paired control/data. |
| `nobs/optical/op-burst_agent.cc` | `BurstAgent::burstsend()` | Đóng dấu trusted local ingress, đăng ký legitimate pair vào telemetry trước `send(pc, 0)`. |
| `nobs/optical/op-burst_agent.cc` | `BurstAgent::recv()` | Cleanup descriptor control-only khi control kết thúc tại egress; giữ nguyên deburstification của data thật. |
| `nobs/optical/op-sragent.h` | `OpSRAgent` | Sở hữu/configure `BhpGuard` và `BhpAuditLogger`; khai báo helper `admit_control()` và `discard_control_at_ingress()`. |
| `nobs/optical/op-sragent.cc` | `OpSRAgent::OpSRAgent()` / destructor | Khởi tạo/hủy guard, logger, node/attachment identity và counters với guard tắt mặc định. |
| `nobs/optical/op-sragent.cc` | `OpSRAgent::command()` | Thêm OTcl interface cấu hình local trusted-ingress ID, guard/profile/log path và query counters; không thêm Tcl command “detect now”. |
| `nobs/optical/op-sragent.cc` | `OpSRAgent::recv()` | Lấy trusted ingress từ local guard instance cho locally originated control; tạo observation; gọi guard trước `LinkReservation_[slot_no].recv()`; thực thi drop/quarantine; không schedule phantom data cho control-only; log decision/action/outcome. |
| `nobs/optical/op-bhp-flood-agent.h` | mới: `BHPFloodAgent`, timer | Khai báo direct BHP generator, `start()`, `stop()`, `emit()`, `command()`, lifecycle ownership. |
| `nobs/optical/op-bhp-flood-agent.cc` | mới: `Agent/BHPFlood` | Allocate/initialize forged control + phantom descriptor, schedule emit online, target `OpSRAgent`, và log attack generation. |
| `nobs/optical/op-bhp-guard.h` | mới: `BhpObservation`, `BhpDecision`, `BhpGuard` | API detector/actuator state, per-ingress budgets, state machine và invariant không nhận ground truth. |
| `nobs/optical/op-bhp-guard.cc` | mới | Implement observe/decide/state transition và parameter validation. |
| `nobs/optical/op-bhp-audit.h` | mới: `BhpAuditLogger` | Schema/version, UID registry evaluation-only, explicit detection/decision/action/impact methods. |
| `nobs/optical/op-bhp-audit.cc` | mới | Append-only logging, deterministic field order, flush/close, không gọi ngược vào detector. |

Không cần thêm packet type trong `common/packet.h`; dùng `PT_OP_BURST` hiện có để đi đúng path của nOBS.

### Build integration

| File | Thay đổi dự kiến |
|---|---|
| `nobs/patches/0003-nobs-deployable-bhp-control-path.patch` (file patch mới khi triển khai) | Patch `ns-2.35/Makefile.in` sau overlay để thêm object `op-bhp-flood-agent.o`, `op-bhp-guard.o`, `op-bhp-audit.o`; không sửa thủ công cây build rồi coi đó là source chuẩn. |
| `nobs/COMMANDS.md` | Ghi exact thứ tự apply overlay, build patch mới, compile và test để clean build tái tạo được. |
| `nobs/README.md` | Cập nhật danh sách optical object và interface OTcl. |

### Scenario sau khi patch được duyệt

Không sửa `nobs/experiments/scenario.tcl` hiện tại và không đổi nghĩa S0/S1/S2 cũ. Tạo **scenario mới** (ví dụ `scenario_deployable_bhp.tcl`) để:

- attach `Agent/BHPFlood` trực tiếp vào `src_agent_` của optical ingress bị chiếm quyền;
- bật `BhpGuard` tại cùng trusted ingress;
- cấu hình profile từ CLI/manifest, không hard-code oracle delay;
- không schedule `$attack stop` làm mitigation;
- lưu audit log riêng khỏi generic `trace-all`.

Parser hiện tại không được dùng để suy ra detection/action mới; audit log mới phải có schema và test riêng. Task này không sửa scenario hay parser.

## OTcl/source interfaces đề xuất

### Generator

```text
Agent/BHPFlood set destination_ <optical-egress>
Agent/BHPFlood set claimedBurstBytes_ <policy/test input>
Agent/BHPFlood set interval_ <input>
Agent/BHPFlood set trustedAttachment_ <ingress attachment>
$generator target $ingress_src_agent
$generator start
$generator stop
$generator emit
```

`stop` chỉ quản lý workload generator trong test; defense không được gọi nó. Actuator luôn nằm trong `OpSRAgent` control path.

### Guard

```text
$ingress_src_agent bhp-guard-enable <boolean>
$ingress_src_agent bhp-guard-profile <profile object/config>
$ingress_src_agent bhp-guard-log <path>
$ingress_src_agent bhp-guard-reset
$ingress_src_agent bhp-guard-counters
```

Profile phải validate rate/capacity/hold-down/hysteresis và fail closed với giá trị không hợp lệ. `reset` chỉ dành cho setup giữa run, không được schedule như một oracle action.

### C++ contract

```cpp
BhpDecision BhpGuard::observe(const BhpObservation& event);
void OpSRAgent::apply_bhp_decision(Packet* control,
                                   const BhpObservation& event,
                                   const BhpDecision& decision);
void BhpAuditLogger::log_detection(...);
void BhpAuditLogger::log_decision(...);
void BhpAuditLogger::log_action(...);
void BhpAuditLogger::log_legitimate_impact(...);
```

`BhpObservation` không có field ground-truth. Đây phải là compile-time/API boundary, không chỉ là convention.

## Pass/fail tests

### Source/unit tests

| Test | PASS | FAIL |
|---|---|---|
| Direct generation | Một `emit()` đi vào `OpSRAgent` dưới dạng `PT_OP_BURST`, `burst_type=0`, không tạo UDP/TCP event và không gọi nhánh payload của `BurstAgent::recv()`. | Cần UDP/CBR để sinh control hoặc data burst phantom được transmit. |
| Reservation semantics | Với guard tắt, forged control gọi đúng `OpSchedule::ScheduleBurst()` và tạo reservation theo claimed header; không có matching data arrival. | Chỉ chiếm electronic queue/link hoặc không đi qua scheduler reservation. |
| Guard placement | Với action drop tại ingress, `LinkReservation_` không được gọi cho UID đó và không có reservation mới. | Guard chạy sau reservation hoặc chỉ dừng generator. |
| Observable-only detector | Mock `BhpObservation` đủ để tái lập decision; thay đổi ground-truth registry, scenario name hay attack schedule không đổi decision. | Detector đọc `control_only`, attacker list, attack start hoặc future data outcome. |
| Trusted attribution | Sửa claimed BHP source không chuyển state sang bucket khác; trusted ingress attachment vẫn là key. | Spoof source né được profile/quarantine. |
| Policer units | Admission thay đổi theo BHP event/reservation cost, không theo kích thước UDP hay data packet trước burstifier. | Tái dùng stock TBF ở UDP path. |
| Causal timestamps | `observation <= detection <= decision <= action` cho mỗi transition/action, và mỗi action tham chiếu UID đã observe. | Timestamp được gán trước hoặc action không có observation. |
| Cleanup | Drop ingress giải phóng control, phantom/paired burst và inner packet đúng một lần; sanitizer/valgrind không báo leak/double-free trong fixture. | Orphan event, use-after-free, leak hoặc double-free. |
| Quarantine state | Chỉ observation online làm state transition; BHP trong quarantine bị chặn trước reservation; release theo policy state. | Tcl gọi detect/isolate hoặc timer dựa trên attack start. |
| Evaluation isolation | Legitimate/attack mapping chỉ được logger join sau decision; guard API không có nhãn. | Ground truth xuất hiện trong detector input. |

### Integration tests

| Test | PASS | FAIL |
|---|---|---|
| Regression | Build mới chạy được example và scenario cũ với guard/generator tắt; semantics control/data hiện có không đổi ngoài telemetry được tắt mặc định. | Patch làm thay đổi baseline reservation/delivery hoặc yêu cầu sửa parser cũ. |
| Forged flood, guard off | Audit log có `BHP_CREATE`, `OBSERVE`, reservation outcome; forged controls không có matching data; legitimate impact có thể quan sát dưới contention. | Chỉ thấy UDP load hoặc không có reservation-side effect. |
| Forged flood, guard on | Detection phát sinh từ event stream, action xuất hiện tại ingress trước reservation, và log đủ detection/decision/action time. | Detection time bằng hằng số Tcl hoặc source app bị stop. |
| Legitimate coexistence | BHP hợp lệ và forged BHP cùng qua một ingress; mọi BHP hợp lệ bị policy chặn đều có `LEGIT_IMPACT` với paired UID/count/bytes. | Chỉ báo attack drop mà bỏ qua collateral damage. |
| No-attack profile | Clean workload theo profile không tạo action ngoài policy; mọi false action (nếu fixture cố tình tạo) được log và test so với SLO cấu hình. | Claim “không false positive” mà không có log/criterion. |
| Malformed BHP | Header/range/route không hợp lệ bị drop trước scheduler và ghi reason cụ thể. | Crash, out-of-bounds, hoặc malformed BHP tạo reservation. |
| Right-censoring | BHP/data còn in flight khi simulation kết thúc được ghi `right_censored`, không tự gán delivered/missing. | Event chưa hoàn tất bị gọi là loss/attack thành công. |
| Determinism | Cùng input/seed/profile cho cùng chuỗi audit decision/action và schema-valid log. | Decision phụ thuộc parser hậu kỳ hoặc state không khởi tạo. |

Không đặt pass threshold bằng số tùy ý trong source. Test fixture có thể chọn input rõ ràng dưới/trên profile đã truyền vào; tiêu chí nghiên cứu phải được khai báo trước trong manifest/SLO, không fit sau khi xem kết quả.

## Hạn chế nOBS và alternative

### Khi nOBS vẫn dùng được

nOBS đủ để mô hình **reservation exhaustion do forged control** nếu patch direct generator giữ đúng các invariant con trỏ/lifecycle, control đi qua `OpSRAgent`/`OpSchedule`, và data phantom không được schedule. Claim khi đó chỉ nên là hiệu quả của admission policing đối với wavelength-reservation path trong simulator.

Một overload tương đương không cần direct forged generator mà nOBS vốn hỗ trợ là cấu hình burstifier tạo rất nhiều **BHP hợp lệ** từ nhiều burst nhỏ/timeout ngắn. Đây chỉ được gọi là *valid-BHP control-load/resource overload*, không được đổi nhãn thành forged BHP attack.

### Khi phải chuyển mô hình

Không dùng nOBS để claim deployability nếu câu hỏi nghiên cứu cần một trong các thuộc tính sau mà không patch/validate được:

- control packet đi trên channel/queue riêng và có bandwidth/CPU/service time hữu hạn;
- BHP authentication, port identity hoặc anti-spoofing thực;
- control processor saturation thay vì wavelength reservation exhaustion;
- cancellation/rollback reservation khi data không tới;
- multi-tenant identity đáng tin phía sau cùng ingress;
- actuator tương tác với switch/controller thật.

Alternative trung thực là một discrete-event model chuyên biệt (NS-3/OMNeT++ custom hoặc simulator nhỏ đã kiểm chứng) với các entity tách biệt:

```text
BHP producer -> authenticated control ingress -> finite control queue/server
             -> online detector -> policer/quarantine -> reservation table
Data burst   -> optical fabric using reservation table
```

Model thay thế phải giữ cùng observation API và audit schema, có unit test cho reservation/cancellation/queueing. Nếu mục tiêu là “deployable” theo nghĩa vận hành, bổ sung prototype control-ingress policer trên controller/software switch hoặc replay harness; nOBS chỉ cung cấp evidence về cơ chế, không đủ làm evidence triển khai thực tế.

## Gate trước khi gọi là deployable

Chỉ bỏ nhãn “integration experiment” khi đồng thời chứng minh được:

- attack được tạo trực tiếp ở control path hoặc được gọi đúng là valid-control overload;
- detector không dùng oracle/ground truth/future outcome;
- action chạy trước reservation trên trusted ingress;
- log có detection time, decision, action và legitimate impact;
- regression, cleanup, attribution, malformed-input và causality tests pass;
- claim được giới hạn theo đúng những gì nOBS mô hình, không suy rộng sang authentication/CPU/controller thực.
