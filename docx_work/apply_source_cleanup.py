from pathlib import Path

p = Path('/home/hitokiri/.openclaw/workspace/work/BHP-Flooding-OBS-Thesis-Reproduction/docx_work/original.md')
s = p.read_text(encoding='utf-8')

replacements = [
("""Pha thứ nhất tập trung so sánh các mô hình học máy trên bộ dữ liệu
chuẩn, qua đó giải quyết mục tiêu thứ hai và thứ ba của đề tài. Ở pha
này, luận văn đánh giá năm mô hình học máy cổ điển trên bộ dữ liệu UCI
về tấn công ngập lụt gói điều khiển BHP, đồng thời kiểm định tính toàn
vẹn của chính bộ dữ liệu trước khi tin vào bất kỳ con số chính xác nào
mà nó tạo ra.""", """Pha thứ nhất tập trung kiểm toán và tái phân tích bộ dữ liệu UCI404 về BHP flooding. Luận văn chỉ tái phân tích bốn mô hình cơ sở có mã và đầu ra đầy đủ: DecisionTree, SVM-RBF, KNN và Gaussian Naïve Bayes. Nhánh PSO-SVM được giữ ở phần tổng quan đối chiếu vì repository hiện không có đủ artifact để tái lập. Trọng tâm của pha này không phải chọn một mô hình triển khai, mà là kiểm tra xem điểm số mô hình có bị chi phối bởi bản sao, giá trị thiếu hoặc các biến liên quan đến cơ chế tạo nhãn hay không."""),
("""Pha thứ hai chuyển sang mô phỏng động mạng OBS nhằm giải quyết mục tiêu
thứ tư và thứ năm. Ở pha này, luận văn dùng bộ công cụ NS2 kết hợp
mô-đun nOBS để tái tạo lại cuộc tấn công ngập lụt BHP một cách trung
thực, đo lường tác động thực tế của nó lên mạng, sinh ra một bộ dữ liệu
phát hiện không bị suy biến, và sau cùng thiết kế cơ chế ứng phó khép
kín đặt tại nút biên.""", """Pha thứ hai dùng môi trường NS-2.35 kết hợp mô-đun nOBS để đánh giá một đường xử lý BHP điều khiển trực tiếp tại nút biên. Ma trận thực nghiệm gồm bốn kịch bản S0, S1, S2-rate-limit và S2-isolation, với 8 hạt giống cho mỗi kịch bản, tổng cộng 32 lượt chạy. Pha này kiểm chứng tác động của BHP trực tiếp lên hai luồng TCP hợp lệ và hiệu quả của hai cấu hình kiểm soát trước khi đặt trước tài nguyên; không được gọi đây là một bộ phát hiện học máy trực tuyến hay một vòng khép kín ML hoàn chỉnh."""),
("""Bộ dữ liệu được sử dụng ở pha thứ nhất là tập \\\"OBS-Network-DataSet\\\"
công bố trên kho dữ liệu học máy UCI, gồm 1.075 mẫu với 21 đặc trưng số
và nhãn phân thành bốn lớp tương ứng với bốn trạng thái xử lý nguồn,
trong đó các lớp phân bố mất cân bằng. Đây chính là bộ dữ liệu được sử
dụng lặp lại trong hầu hết các nghiên cứu phát hiện tấn công ngập lụt
BHP, từ hướng cây quyết định, máy vector hỗ trợ kết hợp tối ưu bầy đàn,
học sâu, cho đến học bán giám sát. Xu hướng chung của các công trình này
là chạy đua theo độ chính xác, mỗi nghiên cứu lại bổ sung một mô hình
phức tạp hơn để nhích thêm vài phần trăm.""", """Bộ dữ liệu của pha thứ nhất là OBS-Network-DataSet, lấy từ UCI Machine Learning Repository, dataset ID 404: “Burst Header Packet (BHP) Flooding Attack on Optical Burst Switching (OBS) Network”. Trang nguồn chính thức là https://archive.ics.uci.edu/dataset/404/burst+header+packet+bhp+flooding+attack+on+optical+burst+switching+obs+network; tệp tải về là https://archive.ics.uci.edu/static/public/404/burst+header+packet+bhp+flooding+attack+on+optical+burst+switching+obs+network.zip, DOI 10.24432/C51C81. Artifact ARFF được dùng trong repository có SHA-256 c573b83a9b8db30658be8dd53ef5769a94bc03a0695e78d6c130306c60cc69de. Tệp có 1.075 dòng, 21 biến dự báo và nhãn Class bốn lớp; trong đó có 860 hàng lặp chính xác, chỉ 215 véc-tơ dự báo duy nhất và 15 ô thiếu ở Packet_lost. Vì vậy, kết quả dưới đây là tái phân tích nguồn UCI chính thức theo giao thức nhóm bản sao, không phải kết quả của một bộ dữ liệu mô phỏng mới."""),
("""Ở pha thứ nhất, luận văn huấn luyện và so sánh năm mô hình học máy gồm
cây quyết định, máy vector hỗ trợ kết hợp tối ưu bầy đàn, mô hình láng
giềng gần nhất, máy vector hỗ trợ với hàm nhân RBF, và mô hình Naïve
Bayes. Việc đánh giá được thực hiện theo phương pháp chia tầng năm phần,
trong đó dữ liệu được chia thành năm phần cân đối về tỷ lệ lớp rồi luân
phiên dùng làm tập kiểm tra. Luận văn không dùng cách chia theo nhóm nút
vì biến nút trong bộ dữ liệu chỉ nhận hai giá trị, khiến cách chia này
bị suy biến. Bốn chỉ số được dùng để đánh giá gồm độ chính xác, hệ số
tương quan Matthews, độ chính xác cân bằng và điểm F1 trung bình.""", """Pha này tái phân tích bốn mô hình cơ sở: DecisionTree, SVM-RBF, KNN và Gaussian Naïve Bayes. Đánh giá dùng StratifiedGroupKFold năm phần, lặp với các seed 17, 42, 73, 101 và 2026, tạo 25 lượt đánh giá cho mỗi mô hình. Nhóm được xác định bằng véc-tơ băm của toàn bộ 21 biến dự báo, nên năm bản sao của cùng một véc-tơ không bị chia sang cả tập huấn luyện và tập kiểm tra. Giá trị thiếu được điền trong từng tập huấn luyện; Node Status được mã hóa một-trong-K, còn các mô hình cần thiết được chuẩn hóa trong từng fold. Báo cáo dùng macro-F1, MCC, độ chính xác và độ chính xác cân bằng. PSO-SVM không được đưa vào bảng tái phân tích vì không có mã, cấu hình tối ưu và đầu ra đủ để kiểm tra."""),
("""### **3.3.2 Kết quả năm mô hình**""", """### **3.3.2 Kết quả tái phân tích bốn mô hình cơ sở**"""),
("""Bảng 3.1 trình bày kết quả chạy thật của năm mô hình theo phương pháp
chia tầng năm phần. Điều đáng chú ý là cây quyết định đạt độ chính xác
tuyệt đối trên toàn bộ các phần đánh giá. Trong nghiên cứu học máy, một
kết quả hoàn hảo như vậy không phải là dấu hiệu đáng mừng mà là tín hiệu
cảnh báo đầu tiên, buộc người nghiên cứu phải dừng lại để kiểm tra xem
mô hình có đang học một lối tắt nào đó hay không.""", """Bảng 3.1 trình bày kết quả trung bình của 25 lượt đánh giá cho mỗi mô hình theo giao thức nhóm bản sao. DecisionTree đạt macro-F1 0,8082 và MCC 0,6239; SVM-RBF đạt macro-F1 0,7680 và MCC 0,6095. Không mô hình nào đạt kết quả hoàn hảo. Chênh lệch so với các con số cũ cho thấy kết luận phụ thuộc mạnh vào cách chia dữ liệu và việc kiểm soát bản sao."""),
("""Kết quả cho thấy có tới mười hai trong số hai mươi mốt đặc trưng tự
mình đã đủ sức tách bốn lớp gần như hoàn hảo, thể hiện trên Hình 3.1.""", """Flood Status là đặc trưng đơn mạnh nhất, nhưng trong giao thức nhóm bản sao chỉ đạt độ chính xác trung bình 0,7106, macro-F1 0,7845 và MCC 0,5692; không có bằng chứng tái lập cho tuyên bố cũ rằng 12 trên 21 đặc trưng riêng lẻ đạt gần hoàn hảo. Kết quả đầy đủ được thể hiện trên Hình 3.1."""),
("""Phép đo này cho thấy chỉ riêng đặc trưng trạng thái ngập lụt có độ quan trọng đáng kể, đạt khoảng 0,10, trong khi
mười tám đặc trưng còn lại có độ quan trọng gần như bằng không.""", """Phép đo ngoài mẫu bằng rừng ngẫu nhiên 200 cây cho thấy Flood Status có mức giảm macro-F1 trung bình 0,2177 khi bị hoán vị; các biến còn lại gần 0 hoặc âm."""),
("""Bộ dữ liệu UCI404 bị suy biến
một cách tất định, nghĩa là nhãn của nó có thể được suy ra trực tiếp từ
một vài đặc trưng hậu nghiệm.""", """UCI404 có rủi ro nghiêm trọng về phụ thuộc do bản sao, biến hậu nghiệm và proxy/target-policy leakage. Tuy nhiên, các artifact hiện có hỗ trợ kết luận về rủi ro và sự phụ thuộc, không đủ để gọi toàn bộ bộ dữ liệu là suy biến tất định trong mọi giao thức."""),
("""### **3.5.2 Mô hình mạng và ba kịch bản**""", """### **3.5.2 Mô hình mạng và bốn kịch bản**"""),
("""Để đánh giá có đối chứng, luận văn thiết lập ba kịch bản. Kịch bản nền
không có tấn công và không có phòng vệ, dùng làm mốc so sánh. Kịch bản
tấn công có lưu lượng hợp pháp và nguồn tấn công nhưng chưa bật phòng
vệ, dùng để đo tác động thuần của tấn công. Kịch bản ứng phó có đầy đủ
lưu lượng hợp pháp, nguồn tấn công và cơ chế phòng vệ, dùng để đo hiệu
quả của cơ chế khép kín. Cấu trúc ba kịch bản này được tóm tắt trong
Bảng 3.2.

***Bảng 3.2. Ba kịch bản mô phỏng đối chứng.***""", """Ma trận mới có bốn kịch bản. S0 là nền: chỉ có hai luồng TCP hợp lệ, không có BHP trực tiếp. S1 là tải BHP trực tiếp không giới hạn thực tế: thêm tám nguồn BHP điều khiển không kèm chùm dữ liệu và dùng ngân sách đối chứng 1e9. S2-rate-limit giữ nguyên tải và seed của S1 nhưng bật giới hạn ngân sách; S2-isolation giữ nguyên tải và seed của S1 nhưng bật cấu hình cách ly. S0 dùng làm mốc nền, S1 đo tác động của BHP trực tiếp, còn hai S2 đo hiệu quả của hai cấu hình kiểm soát trước đặt trước tài nguyên. Cấu trúc bốn ô được tóm tắt trong Bảng 3.2.

***Bảng 3.2. Bốn kịch bản mô phỏng đối chứng.***"""),
("""Công cụ mô phỏng là NS2 phiên bản 2.35 kết hợp mô-đun nOBS \\[23\\] chạy
trong môi trường Docker trên nền Ubuntu 18.04, cho phép xuất ra dấu vết
burst thật. Mỗi kịch bản được chạy với thời gian mô phỏng năm giây và
được lặp lại trên tám hạt giống ngẫu nhiên, trong đó cường độ tấn công
được dao động khoảng hai mươi phần trăm để bảo đảm kết quả không phụ
thuộc vào một cấu hình may rủi.""", """Công cụ là NS-2 phiên bản 2.35 kết hợp mô-đun nOBS v2.1 trên môi trường Linux. Nguồn nOBS được giữ trong thư mục nobs/ của repository; kịch bản native là experiments/direct_bhp/scenario.tcl, cấu hình là experiments/direct_bhp/config.json và binary native được tạo từ archive NS-2.35 đã ghim hash. Ma trận gồm bốn kịch bản × tám seed cố định 101, 202, 303, 404, 505, 606, 707 và 808; mỗi lượt kéo dài 5 giây, tổng cộng 32 lượt. Tô-pô gồm bảy nút, liên kết quang 1000 Mb/s, hai luồng TCP hợp lệ và tám nguồn BHP trực tiếp. Tốc độ hiệu dụng của nguồn BHP thay đổi theo seed trong khoảng đã khai báo; các khoảng 95% chỉ là khoảng mô tả trên tám seed, không phải độ bất định tổng quát. Artifact native được lưu trong evidence/direct_bhp_matrix/ và được kiểm tra bằng validation.json và revalidation.json."""),
]

for old, new in replacements:
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'Expected exactly one match, got {n}: {old[:100]!r}')
    s = s.replace(old, new, 1)

# These are short, unambiguous stale claims elsewhere in the manuscript.
short = {
    'Bảng 3.1. Kết quả năm mô hình học máy trên bộ dữ liệu UCI404 (chia tầng năm phần).': 'Bảng 3.1. Kết quả tái phân tích bốn mô hình cơ sở trên UCI404 bằng StratifiedGroupKFold (25 lượt đánh giá/mô hình).',
    'Bảng 3.4. Năng lực phát hiện trên benchmark mức mạng không suy biến.': 'Bảng 3.4. Trạng thái bằng chứng của bộ chuẩn đánh giá theo cửa sổ.',
    'Bảng 3.5. Hệ số tương quan Matthews theo cường độ tấn công.': 'Bảng 3.5. Trạng thái bằng chứng cho đường cong phát hiện theo cường độ tấn công.',
    'Đóng góp ở đây không phải là một thuật toán học máy mới, mà gồm ba điểm.': 'Đóng góp ở đây không phải là một thuật toán học máy mới, mà là một quy trình kiểm toán dữ liệu và kiểm chứng native có ranh giới bằng chứng rõ ràng.',
    'Luận văn đã hoàn thành đầy đủ năm mục tiêu cụ thể đặt ra trong đề cương nghiên cứu.': 'Luận văn hoàn thành các mục tiêu trong phạm vi dữ liệu, mã nguồn và artifact đã kiểm chứng; những nhánh chưa đủ bằng chứng được nêu rõ là giới hạn.',
}
for old, new in short.items():
    s = s.replace(old, new)

p.write_text(s, encoding='utf-8')
print(f'updated {p}')
