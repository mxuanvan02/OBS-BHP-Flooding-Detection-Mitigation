**LỜI CAM ĐOAN**

Tôi xin cam đoan luận văn này là công trình nghiên cứu của riêng tôi.
Các số liệu, kết quả thực nghiệm và phân tích trong luận văn được trình
bày trung thực; các nguồn tài liệu tham khảo được trích dẫn theo đúng
quy định.

Học viên thực hiện

Nguyễn Quang Tín

**LỜI CẢM ƠN**

Tôi xin chân thành cảm ơn người hướng dẫn khoa học, quý thầy cô, gia
đình và bạn bè đã hỗ trợ, góp ý và tạo điều kiện trong quá trình thực
hiện luận văn.

**MỤC LỤC**

**DANH MỤC BẢNG**

Bảng 1.1. So sánh chuyển mạch chùm quang với chuyển mạch kênh quang và
chuyển mạch gói quang. 16

Bảng 2.1. Tổng hợp các nghiên cứu tiêu biểu về phát hiện và đối phó tấn
công ngập lụt BHP. 36

Bảng 3.1. Kết quả năm mô hình học máy trên bộ dữ liệu UCI404 (chia tầng
năm phần). 43

Bảng 3.2. Ba kịch bản mô phỏng đối chứng. 47

Bảng 3.3. Tác động của tấn công lên các chỉ số mạng (tám hạt giống). 47

Bảng 3.4. Năng lực phát hiện trên benchmark mức mạng không suy biến. 50

Bảng 3.5. Hệ số tương quan Matthews theo cường độ tấn công. 50

Bảng 3.6. Thông lượng hợp pháp theo kịch bản (khoảng tin cậy 95%). 52

**DANH MỤC HÌNH**

Hình 1.1. Sự phát triển của các phương pháp truyền thông quang 12

Hình 1.2. Kiến trúc mạng chuyển mạch kênh quang 14

Hình 1.3. Kiến trúc và sơ đồ chức năng của mạng OBS 18

Hình 1.4. Cấu trúc nút biên vào OBS 19

Hình 1.5. Cấu trúc nút lõi OBS 20

Hình 1.6. Tập hợp chùm và tách chùm 21

Hình 1.7. Tập hợp chùm theo ngưỡng thời gian 21

Hình 1.8. Tập hợp chùm theo ngưỡng kích thước (số gói tối đa) 21

Hình 1.9. Tập hợp chùm theo ngưỡng thời gian và ngưỡng độ dài chùm 23

Hình 1.10. Quá trình đặt trước tức thời và sau một thời gian trễ 24

Hình 2.1. Cơ chế tấn công ngập lụt gói điều khiển BHP trong mạng OBS. 31

Hình 2.2. Phân loại các kỹ thuật phát hiện và ứng phó tấn công DoS trong
mạng OBS. 38

Hình 3.1. Phép thử từng đặc trưng đơn lẻ trên bộ dữ liệu UCI404. 43

Hình 3.2. Độ quan trọng hoán vị tính trên rừng ngẫu nhiên đối với bộ dữ
liệu UCI404. 44

Hình 3.3. Kiến trúc cơ chế phát hiện--ứng phó khép kín đặt tại nút biên
vào mạng OBS. 52

Hình 3.4. Tác động của tấn công ngập lụt BHP lên thông lượng hợp pháp
(tám hạt giống). 48

Hình 3.5. Đường cong tác động theo cường độ tấn công. 49

Hình 3.6. Đường cong khả năng phát hiện theo độ ẩn của tấn công. 50

Hình 3.7. Hiệu quả của cơ chế ứng phó khép kín (tám hạt giống, khoảng
tin cậy 95%). 53

# **MỞ ĐẦU**

**1.1. Lý do chọn đề tài**

Hơn 20 năm kể từ khi Internet chính thức gia nhập vào Việt Nam, công
nghệ này đã tác động mạnh mẽ đến mọi lĩnh vực của đời sống, từ kinh tế,
giáo dục đến khoa học -- kỹ thuật. Nhu cầu trao đổi, chia sẻ thông tin
của con người ngày càng lớn đã thúc đẩy tốc độ phát triển nhanh chóng
của hạ tầng mạng Internet, đặc biệt trong những năm gần đây.

Song song với đó, sự bùng nổ của các dịch vụ truyền thông mới không chỉ
gia tăng về số lượng mà còn đòi hỏi chất lượng ngày càng cao. Điều này
đặt ra yêu cầu tất yếu về việc mở rộng băng thông, nâng cao khả năng
truyền dẫn dữ liệu để đáp ứng nhu cầu của mạng thế hệ mới.

Một trong những công nghệ truyền thông được quan tâm hàng đầu hiện nay
là mạng quang nhờ vào các ưu điểm nổi bật: tốc độ truyền dữ liệu rất
cao, dung lượng băng thông tiềm năng lớn, và tỷ lệ lỗi tín hiệu thấp. Sự
ra đời và phát triển của công nghệ ghép kênh theo bước sóng WDM
(Wavelength Division Multiplexing) đã mang đến giải pháp kịp thời, giải
quyết được bài toán băng thông Internet hiện tại, đồng thời mở ra hướng
phát triển cho tương lai.

Trong số các mô hình truyền thông quang, mạng chuyển mạch chùm quang
(Optical Burst Switching -- OBS) nổi bật nhờ cơ chế truyền tải đặc
trưng: phần gói điều khiển BHP (Burst Header Packet) tách biệt hoàn toàn
với phần chùm dữ liệu DB (Data Burst). Gói BHP được gửi đi trước một
khoảng thời gian offset đủ để đặt trước tài nguyên và cấu hình chuyển
mạch tại các nút trung gian trên đường truyền từ nguồn đến đích. OBS
dành riêng một số kênh bước sóng cho BHP và các kênh còn lại cho DB, đảm
bảo tính linh hoạt và hiệu quả của việc truyền dữ liệu.

Tuy nhiên, chính đặc điểm tách rời giữa BHP và DB cùng việc OBS không sử
dụng bộ đệm quang tại nút lõi đã tạo ra một thách thức bảo mật: nếu gói
BHP bị giả mạo hoặc bị khai thác để đặt trước tài nguyên một cách bất
hợp pháp, hiệu suất mạng sẽ bị suy giảm nghiêm trọng. Điều này đặc biệt
nguy hiểm trong các cuộc tấn công từ chối dịch vụ (DoS), khi kẻ tấn công
gửi lượng lớn BHP giả nhằm chiếm dụng tài nguyên, làm tăng tỷ lệ mất
chùm và giảm chất lượng dịch vụ.

Do đó, việc nghiên cứu kỹ thuật phát hiện và ứng phó tấn công DoS trong
mạng OBS là cần thiết và cấp bách, góp phần đảm bảo tính ổn định, an
toàn và hiệu quả cho các hệ thống mạng quang thế hệ mới.

**1.2. Tổng quan tài liệu**

Mạng chuyển mạch chùm quang (Optical Burst Switching -- OBS) là một
trong những kiến trúc truyền dẫn hứa hẹn cho mạng lõi tốc độ cao nhờ khả
năng tận dụng băng thông linh hoạt và giảm yêu cầu phần cứng so với OPS
hoặc OCS. Trong OBS, gói điều khiển (Burst Header Packet -- BHP) được
gửi trước chùm dữ liệu (Data Burst -- DB) một khoảng thời gian offset để
đặt trước tài nguyên và cấu hình chuyển mạch trên các nút lõi. Tuy
nhiên, đặc điểm tách rời giữa BHP và DB khiến OBS dễ bị khai thác trong
tấn công từ chối dịch vụ (DoS), đặc biệt là tấn công ngập lụt BHP (BHP
flooding), khi kẻ tấn công gửi lượng lớn BHP giả mạo nhằm chiếm dụng tài
nguyên quang mà không có dữ liệu thực đi kèm, dẫn đến giảm hiệu suất
mạng, tăng tỷ lệ mất chùm và suy giảm chất lượng dịch vụ \[2\].

Hiện nay đã có nhiều nghiên cứu về kỹ thuật phát hiện tấn công đã được
đề xuất theo các hướng tiếp cận khác nhau bao gồm:

Mô hình học máy dựa trên luật cây quyết định: Rajab, Huang và
Al-Shargabi (2018) đề xuất phương pháp học luật từ cây quyết định
(decision tree rule learning), kết hợp đánh giá và lựa chọn các đặc
trưng quan trọng nhất từ lưu lượng BHP để phân loại luồng thành hợp lệ
hoặc tấn công. Việc rút gọn đặc trưng vừa hạn chế quá khớp vừa tăng tốc
độ dự đoán, phù hợp với môi trường yêu cầu xử lý thời gian thực \[18\].

Máy vector hỗ trợ kết hợp tối ưu hóa bầy đàn (PSO--SVM): Liu, Liao và
Shi (2021) áp dụng Support Vector Machine (SVM) để phát hiện tấn công,
đồng thời dùng Particle Swarm Optimization (PSO) để tối ưu tham số cho
SVM. Mô hình PSO--SVM đạt độ chính xác và tỷ lệ phát hiện cao hơn đáng
kể so với SVM truyền thống khi thử nghiệm trên dữ liệu BHP flooding
\[19\].

Hướng học bán giám sát và học sâu: Hossain và Haque (2019) sử dụng thuật
toán K-Means bán giám sát để phát hiện và ngăn chặn tấn công BHP
flooding khi nhãn dữ liệu hạn chế \[21\]; Hossain, Haque và Dewan (2021)
tiếp tục phân tích so sánh nhiều thuật toán học bán giám sát trên cùng
bài toán \[25\]; Seddik, Kadri và Bouarouguene (2021) kết hợp tối ưu hóa
đàn kiến (Ant Colony Optimization) với học máy để nâng cao độ chính xác
phát hiện \[37\]. Các hướng này có khả năng tự trích xuất đặc trưng và
phát hiện mẫu tấn công phức tạp, nhưng đòi hỏi lượng dữ liệu và tài
nguyên xử lý lớn hơn các mô hình truyền thống.

Bên cạnh các phương pháp phát hiện, nhiều nghiên cứu cũng tập trung vào
việc đề xuất cơ chế ứng phó để giảm thiểu tác động của tấn công sau khi
đã được phát hiện. Các hướng tiếp cận phổ biến gồm:

Giới hạn tốc độ (Rate Limiting) hoặc cách ly nguồn nghi ngờ: Hệ thống
tạm thời giảm tốc độ xử lý hoặc chặn các luồng đến từ nguồn bị nghi ngờ
tấn công. Cách này phản ứng nhanh, giảm tức thì lưu lượng tấn công,
nhưng có thể ảnh hưởng tới luồng hợp lệ nếu tỷ lệ cảnh báo sai cao.

Điều chỉnh định tuyến hoặc phân bổ lại tài nguyên: Khi phát hiện tấn
công, hệ thống có thể đổi đường đi của chùm dữ liệu hoặc ưu tiên tài
nguyên cho các luồng hợp lệ. Hướng tiếp cận này thường được khuyến nghị
tích hợp trực tiếp với khối phát hiện để tăng khả năng phản ứng kịp
thời.

Tuy nhiên với các nghiên cứu hiện tại cho thấy một số hạn chế đáng chú
ý:

Phụ thuộc vào dữ liệu mô phỏng, chưa kiểm chứng trên dữ liệu thực tế
hoặc nhiều kịch bản mạng khác nhau.

Tách biệt phát hiện và ứng phó, thiếu các cơ chế tích hợp khép kín từ
phát hiện, ra quyết định, thực hiện phản ứng.

Chưa tối ưu cân bằng giữa hiệu suất phát hiện và độ nhẹ mô hình, đặc
biệt quan trọng trong môi trường OBS vốn yêu cầu độ trễ thấp.

Ít khai thác đặc trưng tầng quang để bổ sung cho dữ liệu điều khiển,
trong khi đây có thể là nguồn thông tin giàu giá trị giúp tăng độ chính
xác phát hiện.

**1.3. Mục tiêu nghiên cứu**

**Mục tiêu tổng quát: Nghiên cứu và đề xuất một cơ chế tích hợp khép kín
phát hiện -- ra quyết định -- ứng phó tấn công DoS (cụ thể là tấn công
ngập lụt gói điều khiển BHP) trong mạng chuyển mạch chùm quang OBS, cân
bằng giữa độ chính xác phát hiện và độ trễ xử lý, nhằm duy trì tỷ lệ mất
chùm và thông lượng ở mức chấp nhận được khi mạng bị tấn công.**

**Mục tiêu cụ thể:**

\(1\) Phân tích cơ chế tấn công DoS/BHP flooding và định lượng ảnh hưởng
của nó đến tỷ lệ mất chùm và thông lượng trong mạng OBS.

\(2\) Xây dựng và so sánh các mô hình học máy phát hiện tấn công (cây
quyết định, SVM và PSO--SVM, KNN, Naïve Bayes) trên bộ dữ liệu BHP
flooding công khai theo các chỉ số độ chính xác, precision, recall, F1
và độ trễ suy luận.

\(3\) Lựa chọn mô hình cân bằng giữa hiệu quả phát hiện và độ nhẹ (độ
trễ thấp), phù hợp với ràng buộc xử lý thời gian thực tại nút OBS.

\(4\) Đề xuất và tích hợp cơ chế ứng phó (giới hạn tốc độ, cách ly nguồn
nghi ngờ) gắn trực tiếp với khối phát hiện thành một quy trình khép kín.

\(5\) Mô phỏng kịch bản tấn công bằng NS2/OMNeT++ và đánh giá hiệu quả
của cơ chế đề xuất qua tỷ lệ mất chùm và thông lượng, so với trường hợp
không có cơ chế bảo vệ.

**1.4. Đối tượng nghiên cứu**

Mạng chuyển mạch chùm quang (OBS).

Các hình thức tấn công DoS vào kênh điều khiển.

Kỹ thuật phát hiện và ứng phó tấn công.

**1.5. Phương pháp nghiên cứu**

Nghiên cứu lý thuyết: Tổng hợp tài liệu, phân tích kiến trúc và đặc điểm
bảo mật của mạng OBS, cơ chế tấn công DoS/BHP flooding và các thuật toán
phát hiện, ứng phó.

Để bảo đảm tính so sánh được và tính khả thi, luận văn tách quá trình
thực nghiệm thành hai pha với hai nguồn dữ liệu khác nhau:

Pha 1 -- Phát hiện tấn công: Huấn luyện và đánh giá các mô hình học máy
trên bộ dữ liệu BHP flooding công khai (tập dữ liệu OBS-Network/"Burst
Header Packet (BHP) flooding attack on OBS network" trên UCI Machine
Learning Repository). Việc dùng bộ dữ liệu chuẩn này cho phép so sánh
trực tiếp và công bằng với các kết quả đã công bố trong phần tổng quan.

Pha 2 -- Ứng phó tấn công: Mô phỏng kịch bản tấn công và cơ chế ứng phó
bằng NS2 (kèm OBS module) hoặc OMNeT++ để quan sát diễn biến tài nguyên
theo thời gian, do phần đánh giá ứng phó cần các chỉ số động (tỷ lệ mất
chùm, thông lượng) mà bộ dữ liệu tĩnh ở Pha 1 không cung cấp.

Đánh giá hiệu quả: Pha 1 dùng các chỉ số độ chính xác, precision,
recall, F1 và độ trễ suy luận; Pha 2 dùng tỷ lệ mất chùm và thông lượng,
đối chiếu giữa trường hợp có và không có cơ chế bảo vệ đề xuất.

**1.6. Phạm vi nghiên cứu**

Tập trung vào tấn công DoS vào kênh điều khiển của OBS và kỹ thuật phát
hiện + ứng phó ở lớp điều khiển, không nghiên cứu sâu các lớp vật lý và
ứng dụng.

**2. NỘI DUNG NGHIÊN CỨU VÀ BỐ CỤC DỰ KIẾN**

**2.1. Nội dung nghiên cứu**

Tổng quan về OBS và đặc điểm bảo mật.

Phân tích cơ chế và tác động của DoS trong OBS.

Nghiên cứu, lựa chọn và cải tiến thuật toán phát hiện.

Đề xuất cơ chế ứng phó giảm thiểu tác hại.

Mô phỏng và đánh giá.

**2.2. Bố cục dự kiến**

Phần mở đầu:

Chương 1: Tổng quan về mạng OBS và bảo mật.

Chương 2: Một số phương pháp tấn công DoS và các kỹ thuật phát hiện, ứng
phó tấn công.

Chương 3: Mô phỏng và phân tích kết quả.

Kết luận và hướng phát triển.

# **Chương 1. TỔNG QUAN VỀ MẠNG CHUYỂN MẠCH CHÙM QUANG VÀ BẢO MẬT**

## 1.1. Tóm lược về lịch sử phát triển của truyền thông quang

Trong những thập kỷ gần đây, sự phát triển nhanh chóng của mạng truyền
thông cùng với sự bùng nổ của các dịch vụ internet yêu cầu băng thông
lớn như truyền hình internet (IPTV), video theo yêu cầu (VoD), điện
thoại internet (VoIP) và các ứng dụng đa phương tiện đã làm gia tăng
đáng kể lưu lượng truyền tải trên mạng. Trong khi đó, khả năng khai thác
của cáp đồng đã đạt đến giới hạn về dung lượng và hiệu năng, không còn
đáp ứng được yêu cầu ngày càng cao của người dùng.

Trước thực trạng đó, mạng sợi quang \[1\] đã được công nhận là giải pháp
truyền dẫn hiệu quả nhờ khả năng hỗ trợ băng thông rất lớn, suy hao tín
hiệu thấp và tỷ lệ lỗi bit nhỏ, phù hợp cho các hệ thống mạng hiện tại
và tương lai. Điều đó là do, theo lý thuyết mỗi sợi quang có thể hỗ trợ
băng thông cực lớn lến đến 50Tbps. Ngoài ra việc sản xuất sợi quang có
chi phí và độ lỗi bit thấp (khoảng $10^{- 2}$dB). Mặc khác, mất mát tín
hiệu truyền trên sợi quang thấp hơn nhiều so với cáp đồng, nên rất thuận
tiện trong vấn đề bảo mật. Một mạng toàn quang, trong đó dữ liệu được
vận chuyển hoàn toàn trong miền quang, còn gói tin điều khiển được xử lý
trong miền điện, là mục tiêu hướng tới trong tương lai gần mà có thể xây
dựng được.

Sự phát triển của mạng quang được chia thành 3 giai đoạn chính. Thế hệ
đầu tiên của các kiến trúc mạng quang bao gồm các liên kết WDM
điểm-nối-điểm (*point-to-point WDM links*). Với cấu trúc mạng bao gồm
nhiều liên kết điểm-nối-điểm mà tại đó tín hiệu (lưu lượng) đến tại một
nút được chuyển đổi từ quang sang điện (*optics to electronics - EO*),
được xử lý trong miền điện và được chuyển đổi ngược lại từ điện sang
quang (*electronics to optics - EO*) trước khi đi đến nút khác. Việc
trích (tách) (*dropping*) và chèn (*adding*) lưu lượng tại các nút trong
mạng do đó phải gánh chịu thêm độ phức tạp của chuyển mạch và chi phí xử
lý điện tử, đặc biệt nếu phần lớn các lưu lượng chỉ chuyển tiếp qua các
nút này. Để giảm thiểu chi phí mạng, các thiết bị toàn quang
(*all-optical*) có thể được sử dụng. Hình 1.1 cho thấy sự phát triển của
các phương pháp truyền thông quang khác nhau.

![](media/image1.png){width="3.7498458005249344in"
height="2.902600612423447in"}

***Hình 1.1. Sự phát triển của các phương pháp truyền thông quang***

Kiến trúc mạng quang thế hệ thứ hai dựa trên các bộ ghép/tách bước sóng
tại các bộ (*Wavelength Add-Drop Multiplexers - WADM*) \[1\]. Các bộ
WADM cho phép thêm hoặc tách lưu lượng tại các nút mạng, trong khi các
bước sóng còn lại được truyền tiếp mà không cần xử lý. Do lưu lượng
chuyển tiếp thường chiếm ưu thế, việc sử dụng WADM giúp giảm chi phí
triển khai mạng. Kiến trúc này chủ yếu được áp dụng trong các mạng WDM
hình vòng (*ring networks)*, hướng tới triển khai tại các khu vực đô
thị.

Việc xây dựng một mạng quang theo kiến trúc hình lưới (mesh), sử dụng
các sợi quang hỗ trợ đa bước sóng cùng với các thiết bị kết nối sợi
quang phù hợp, là yêu cầu tất yếu. Kiến trúc mạng quang thế hệ thứ ba
được phát triển dựa trên các thiết bị kết nối toàn quang, bao gồm ba
nhóm chính: bộ chia hình sao thụ động (*passive star couplers*), bộ định
tuyến thụ động (*passive routers*) và bộ chuyển mạch chủ động (*active
switches*). Bộ chia hình sao thụ động hoạt động như một thiết bị phát
sóng, trong đó tín hiệu đến tại một cổng vào trên một bước sóng bất kỳ
được phân chia đều về mặt công suất đến tất cả các cổng ra. Bộ định
tuyến thụ động cho phép định tuyến riêng biệt từng bước sóng từ sợi
quang vào sang sợi quang ra tương ứng trên cùng bước sóng; do là thiết
bị tĩnh, cấu hình tuyến của bộ định tuyến thụ động là cố định. Ngược
lại, bộ chuyển mạch chủ động có khả năng định tuyến các bước sóng giữa
các sợi quang vào và ra, hỗ trợ nhiều kết nối đồng thời, đồng thời cho
phép tái cấu hình linh hoạt nhằm thay đổi mô hình kết nối. Trong các
mạng quang thế hệ thứ ba, dữ liệu có thể được chuyển tiếp qua các nút
trung gian mà không cần thực hiện chuyển đổi quang--điện--quang
(*Optical--Electrical--Optical, OEO*), từ đó làm giảm đáng kể chi phí
liên quan đến việc triển khai các khối chuyển mạch và định tuyến điện tử
tốc độ cao tại mỗi nút mạng.

Các hệ thống toàn quang đang nổi lên được kỳ vọng sẽ cung cấp các kết
nối chuyển mạch kênh quang (*optical circuit switching -- OCS*), hay còn
gọi là các đường quang (*lightpaths*), giữa các bộ định tuyến biên thông
qua một mạng lõi quang \[1\]. Tuy nhiên, do các kết nối OCS có tính chất
tương đối tĩnh, chúng không thích nghi hiệu quả với đặc tính lưu lượng
dạng burst của Internet. Về mặt lý tưởng, để đạt được mức sử dụng tối ưu
của mạng lõi quang, các nút mạng cần được trang bị khả năng chuyển mạch
gói quang (*optical packet switching -- OPS*) \[5\]. Mặc dù vậy, do
những hạn chế hiện tại về công nghệ, OPS vẫn chưa khả thi để triển khai
rộng rãi trong tương lai gần.

Một giải pháp thay thế khả thi trong ngắn hạn cho chuyển mạch kênh toàn
quang và chuyển mạch gói quang là chuyển mạch chùm quang (*optical burst
switching -- OBS*) \[2\], \[4\]. Trong OBS, các gói tin được gom nhóm
thành các đơn vị truyền dẫn gọi là chùm quang (*bursts*), sau đó được
chuyển mạch hoàn toàn trong miền quang bên trong mạng lõi. Nhờ cho phép
mức độ ghép kênh cao hơn, mạng OBS tỏ ra phù hợp hơn với việc xử lý lưu
lượng có tính chất *bursty* so với mạng OCS. Đồng thời, OBS ít bị ràng
buộc bởi các hạn chế công nghệ như trong trường hợp chuyển mạch gói
quang (OPS).

## 1.2. Các mô hình chuyển mạch quang 

Chuyển mạch quang có thể được chia thành loại: chuyển mạch kênh quang
\[1\], chuyển mạch gói quang \[5\] và chuyển mạch chùm quang \[2\],
\[4\]. Mỗi mô hình này sẽ được mô tả chi tiết trong các mục ngay sau:

### 1.2.1. Chuyển mạch kênh quang 

Trong chuyển mạch kênh quang một đường quang (*lightpath*) được thiết
lập giữa cặp nút nguồn - đích trước khi truyền dữ liệu (Hình 1.2). Như
vậy các nút trung gian do đó không cần thực hiện những công việc phức
tạp như xử lý phần điều khiển (*header*) hay lưu tạm (*buffering*) phần
dữ liệu. Một lightpath sẽ cung cấp một kết nối mà nó có thể đi qua nhiều
liên kết quang trong chuyển mạch kênh quang. hả năng chuyển đổi bước
sóng của mỗi nút quang sẽ cho phép các liên kết quang nối tiếp nhau mang
các bước sóng khác nhau.

![](media/image2.png){width="4.975436351706037in"
height="3.0745220909886264in"}

***Hình 1.2. Kiến trúc mạng chuyển mạch kênh quang***

Trong chuyển mạch kênh quang, băng thông được cấp phát theo cơ chế tĩnh,
do đó khó thích ứng với đặc tính lưu lượng biến thiên liên tục của mạng
Internet. Với số lượng bước sóng hữu hạn, chỉ có một số lượng giới hạn
các đường quang (*lightpaths*) có thể được thiết lập đồng thời. Khi lưu
lượng thay đổi theo thời gian nhưng được truyền trên các *lightpath*
tĩnh, hiệu quả sử dụng băng thông bị suy giảm đáng kể. Để đáp ứng nhu
cầu băng thông ngày càng cao trong các mạng đô thị và mạng diện rộng,
các cơ chế truyền tải cần hỗ trợ khả năng dự trữ tài nguyên đồng thời
thích ứng với sự đột biến của lưu lượng. Tuy nhiên, việc thiết lập các
đường quang theo cơ chế động làm cho trạng thái mạng thay đổi liên tục,
gây khó khăn trong quá trình cập nhật và quản lý thông tin trạng thái.
Bên cạnh đó, trong chuyển mạch kênh quang, quá trình đặt trước tài
nguyên thường được thực hiện theo cơ chế hai chiều, trong đó nguồn gửi
yêu cầu thiết lập đường quang và đích phản hồi xác nhận khi kết nối đã
được thiết lập với dung lượng không xác định trước. Cơ chế này dẫn đến
việc sử dụng băng thông kém hiệu quả.

### 1.2.2. Chuyển mạch gói quang

Chuyển mạch gói quang (*optical packet switching -- OPS*) là một mô hình
chuyển mạch cho phép thực hiện việc chuyển mạch và định tuyến các gói IP
trực tiếp trong miền quang, không yêu cầu chuyển đổi sang miền điện tử
tại mỗi nút mạng. Một nút OPS được trang bị ma trận chuyển mạch
(*switching fabric*) có khả năng tái cấu hình theo từng gói tin. Các gói
quang được truyền đi kèm với phần điều khiển (*header*) mà không cần
thiết lập trước khi đi vào mạng. Tại mỗi nút lõi, gói tin được lưu tạm
thời trong bộ đệm quang, trong khi phần điều khiển được chuyển đổi từ
quang sang điện để xử lý trong miền điện. Dựa trên thông tin điều khiển
này, ma trận chuyển mạch được cấu hình nhằm chuyển gói quang từ cổng vào
sang cổng ra tương ứng, sau đó gói tin được truyền tiếp ngay lập tức đến
nút kế tiếp.

Do tài nguyên mạng không được đặt trước, các gói quang có thể xảy ra
tranh chấp tại cùng một cổng ra, dẫn đến hiện tượng mất gói. Việc thiếu
các công nghệ đệm quang hiệu quả càng làm trầm trọng thêm vấn đề tranh
chấp trong chuyển mạch gói quang so với các hệ thống chuyển mạch gói
điện tử truyền thống, nơi mà công nghệ đệm điện tử đã được phát triển
hoàn thiện. Hiện nay, đệm quang chủ yếu được thực hiện thông qua các
đường trễ sợi quang (*Fiber Delay Lines -- FDL*), tuy nhiên phương pháp
này chỉ cho phép lưu giữ gói quang trong những khoảng thời gian xác
định, phụ thuộc vào cấu hình các đường trễ theo dạng nối tiếp hoặc song
song. Hơn nữa, dung lượng của bộ đệm quang bị giới hạn bởi không gian
vật lý; chẳng hạn, để trì hoãn một gói quang trong khoảng 5 micro giây,
cần đến chiều dài sợi quang lên tới hàng cây số (km) \[5\]. Do những hạn
chế này, các nút chuyển mạch gói quang tỏ ra kém hiệu quả trong việc xử
lý tải cao hoặc lưu lượng có tính chất *bursty*.

Bên cạnh đó, việc triển khai thực tế chuyển mạch gói quang đòi hỏi thời
gian chuyển mạch cực nhanh, trong khi các thiết bị chuyển mạch quang
hiện nay chủ yếu dựa trên công nghệ vi cơ điện tử
(*micro-electro-mechanical systems -- MEMS*) với thời gian chuyển mạch
vào khoảng 1 ms \[5\]. Mặc dù các bộ chuyển mạch sử dụng khuếch đại bán
dẫn quang (*Semiconductor Optical Amplifier -- SOA*) có thể đạt thời
gian chuyển mạch ngắn hơn đáng kể (khoảng 1 ns), song chi phí cao và
kiến trúc chuyển mạch dựa trên các bộ chia quang gây tổn thất lớn điện
năng . Ngoài ra, các vấn đề liên quan đến việc trích xuất phần điều
khiển và thực hiện chuyển mạch trong miền quang cũng làm gia tăng độ
phức tạp, khiến việc triển khai chuyển mạch gói quang trở nên khó khăn
hơn trong tương lai gần.

Để tránh yêu cầu về đệm quang và chuyển mạch cực nhanh, đồng thời vẫn
duy trì khả năng chuyển mạch hoàn toàn trong miền quang, mô hình chuyển
mạch chùm quang (*optical burst switching -- OBS*) đã được đề xuất. OBS
được xem là một giải pháp khả thi cho các mạng toàn quang, do cung cấp
sự cân bằng giữa mức độ thô của chuyển mạch kênh quang và mức độ mịn của
chuyển mạch gói quang. Thông qua việc chuyển mạch dữ liệu ở mức chùm,
OBS kết hợp được tính trong suốt của chuyển mạch kênh quang với khả năng
ghép kênh hiệu quả của chuyển mạch gói quang.

### 1.2.3. Chuyển mạch chùm quang

Chuyển mạch chùm quang lần đầu được đề xuất vào khoảng năm 1980. Tuy
nhiên, kỹ thuật này không đạt được thành công trong các mạng chuyển mạch
điện tử do yêu cầu triển khai phức tạp và không mang lại lợi thế rõ rệt
so với chuyển mạch gói truyền thống. Trong mạng quang, tồn tại sự khác
biệt đáng kể giữa năng lực truyền dẫn trong miền quang và khả năng xử lý
trong miền điện tử; bên cạnh đó, việc sử dụng bộ nhớ truy cập ngẫu nhiên
trong miền quang hiện vẫn chưa khả thi, dẫn đến không thể lưu giữ dữ
liệu chờ xử lý trực tiếp trong miền quang. Chuyển mạch chùm quang được
đề xuất lại vào cuối năm 1990 và nó trở thành một công nghệ hứa hẹn có
thể tận dụng được những ưu điểm của chuyển mạch kênh quang, chuyển mạch
gói quang và khắc phục những những bất lợi về kỹ thuật hiện tại.

Trong chuyển mạch chùm quang, các gói dữ liệu điện tử, chẳng hạn như gói
IP, tế bào ATM hoặc khung Ethernet, được tập hợp thành các đơn vị truyền
dẫn có kích thước lớn hơn, gọi là các chùm quang (*bursts*). Các chùm
quang này sau đó được chuyển mạch và truyền dẫn hoàn toàn trong mạng lõi
quang. Nhờ khả năng ghép kênh hiệu quả hơn, chuyển mạch chùm quang tỏ ra
phù hợp hơn trong việc xử lý lưu lượng có tính chất *bursty* so với
chuyển mạch kênh quang. Đồng thời, chuyển mạch chùm quang ít chịu các
ràng buộc về mặt công nghệ hơn so với chuyển mạch gói quang.

Một so sánh về các kỹ thuật chuyển mạch quang được tóm tắt trong Bảng
1.1 cho thấy những lợi thế của chuyển mạch chùm quang so với chuyển mạch
kênh quang và chuyển mạch gói quang.

***Bảng 1.1. So sánh chuyển mạch chùm quang với chuyển mạch kênh quang
và chuyển mạch gói quang.***

  -------------------------------------------------------------------------
  **Loại       **Khả năng   **Mức trễ** **Đệm      **Xử lý/đồng  **Khả năng
  chuyển       tận dụng                 quang**    bộ gói điều   thích ứng
  mạch**       băng thông**                        khiển**       với tải
                                                                 lưu lượng
                                                                 và lỗi**
  ------------ ------------ ----------- ---------- ------------- ----------
  OCS          Thấp         Cao         Không      Thấp          Thấp

  OPS          Cao          Thấp        Yêu cầu    Cao           Cao

  OBS          Cao          Thấp        Không      Thấp          Cao
  -------------------------------------------------------------------------

## 1.3. Mạng chuyển mạch chùm quang

Mạng chuyển mạch chùm quang (OBS) được xem là một trong những công nghệ
tiềm năng cho mạng Internet toàn quang thế hệ tiếp theo, nhờ sở hữu
nhiều đặc tính và ưu thế vượt trội so với các mô hình chuyển mạch quang
hiện có. Mạng OBS cung cấp một giải pháp cho phép truyền tải lưu lượng
trực tiếp trên hạ tầng WDM mà không yêu cầu sử dụng bộ đệm quang. Công
nghệ này áp dụng cơ chế đặt trước tài nguyên theo hướng một chiều kết
hợp với quá trình truyền dẫn tức thời, trong đó chùm dữ liệu được gửi đi
ngay sau gói điều khiển tương ứng mà không cần chờ phản hồi hay báo nhận
từ nút đích.

Mạng chuyển mạch chùm quang coi lớp quang thuần túy như một môi trường
truyền dẫn trong suốt đối với các ứng dụng. Tuy nhiên, cho đến nay vẫn
chưa tồn tại một định nghĩa thống nhất và đầy đủ cho khái niệm chuyển
mạch chùm quang trong các nghiên cứu hiện hành.

Một số đặc trưng của mạng chuyển mạch chùm quang:

-   *Tách biệt giữa kênh truyền gói điều khiển và kênh truyền chùm*: gói
    điều khiển được truyền trên một kênh riêng biệt.

-   *Dành riêng một chiều: tài nguyên được cấp phát theo kiểu dành riêng
    một chiều, nghĩa là nút nguồn không cần đợi thông tin phản hồi từ
    nút đích trước khi nó bắt đầu truyền chùm.*

-   *Độ dài chùm thay đổi được*: kích thước của chùm có thể thay đổi
    được theo yêu cầu.

-   *Không cần bộ đệm quang*: nút trung gian trong mạng quang không yêu
    cầu phải có bộ đệm quang. Các chùm đi qua các nút trung gian không
    chịu bất kỳ một sự trì hoãn nào.

Vì vậy mạng OBS kết hợp được những ưu điểm của mạng OCS và mạng OPS,
trong khi khắc phục được những thiếu sót của chúng. Một so sánh ngắn
giữa mạng OBS so với 2 mạng OCS và OPS dựa trên các yếu tố hiệu năng
dưới đây \[4\]:

-   Sử dụng băng thông (*Bandwidth utilization*): Mạng OCS có mức độ sử
    dụng băng thông sợi quang thấp nhất. Băng thông được thiết lập cho
    một đường quang giữa một cặp nút, trong trường hợp không được khai
    thác hết, phần băng thông này cũng không thể được sử dụng cho các
    luồng lưu lượng khác. Mạng OCS không hỗ trợ chuyển mạch lưu lượng
    với độ mịn (*granularity*) nhỏ hơn một bước sóng. Ngược lại, mạng
    OPS và OBS cho phép lưu lượng giữa nhiều cặp nút đầu--cuối cùng chia
    sẻ băng thông trên một liên kết thông qua kỹ thuật ghép kênh thống
    kê.

-   Độ trễ thiết lập thấp (Setup delay): mạng OBS sử dụng sơ đồ báo hiệu
    một chiều để đặt trước tài nguyên trên hành trình trước khi chùm
    được truyền Độ trễ thiết lập này là rất ngắn, không giống như mạng
    OCS trong đó các thông điệp báo hiệu được trao đổi giữa nút nguồn và
    đích để thiết lập (setup) và gỡ bỏ (release) các đường quang.

-   Tốc độ chuyển mạch (*Switching speed*): mạng OPS yêu cầu các thiết
    bị chuyển mạch tốc độ rất cao để chuyển mạch các gói quang có kích
    thước nhỏ. Ngược lại, chuyển mạch trong mạng OCS là nhanh hơn. Hơn
    nữa, đường quang thường được thiết lập cho thời gian dài hơn và do
    đó thời gian cấu hình của các thiết bị chuyển mạch có thể dài hơn.
    Trong trường hợp mạng OBS, thiết bị chuyển mạch có tốc độ trung bình
    do kích thước của các chùm quang lớn hơn so với các gói dữ liệu
    quang.

-   Độ phức tạp về xử lý (*Processing complexity*): Trong mạng OPS, bởi
    vì thông tin điều khiển chứa trong các gói quang, nên độ phức tạp về
    xử lý là rất cao, vì phần điều khiển phải được chiết xuất từ mỗi gói
    và xử lý trong miền điện tử. Trong mạng OCS, bởi vì đường quang được
    thiết lập trong một thời gian dài, độ phức tạp là tương đối thấp khi
    so sánh với mạng OPS và OBS. Vì kích thước các chùm là lớn hơn (được
    tạo từ nhiều gói tin IP) so với các gói tin quang, độ phức tạp xử lý
    của mạng OBS là giữa OCS và OPS.

-   Tính thích nghi của lưu lượng (*traffic adaptivity*): mạng OCS không
    thích nghi với sự biến thiên lưu lượng bursty do độ trễ thiết lập
    cao và việc sử dụng chuyển mạch bước sóng.

### 1.3.1. Kiến trúc mạng chuyển mạch chùm quang

Một mạng OBS bao gồm các nút chuyển mạch chùm quang (nút OBS) được kết
nối với nhau thông qua các sợi quang \[3\], \[4\]. Mỗi sợi quang có khả
năng hỗ trợ nhiều kênh đa bước sóng. Như mô tả trong Hình 1.3, mạng OBS
có hai kiểu nút: nút biên và nút lõi. Trong đó, nút biên được xem là
giao diện giữa miền điện và miền quang, và được phân chia thành hai loại
là nút biên vào và nút biên ra. Nút biên vào thực hiện tập hợp các gói
điện tử (chẳng hạn như các gói IP) có cùng đích đến thành một đơn vị
truyền dẫn lớn, được gọi là chùm quang (hay chùm). Các hoạt động tiếp
theo bao gồm định tuyến, cấp phát bước sóng và lập lịch cho chùm trên
một kênh dữ liệu tại cổng ra. Chùm sau đó được truyền qua mạng OBS và
cuối cùng được tách thành các gói tại nút biên ra để gửi tới đích tương
ứng. Nút lõi được trang bị một ma trận chuyển mạch quang nhằm thực hiện
chức năng chuyển tiếp các chùm đến nút kế tiếp.

Một nút OBS bao gồm 2 phần: quang và điện. Phần quang là các bộ
ghép/tách bước sóng (*multiplexer/demultiplexer*) và ma trận chuyển mạch
quang. Phần điện gồm các mô-đun vào/ra, lập lịch và điều khiển định
tuyến. Đơn vị chuyển mạch quang điều khiển các chùm từ một cổng vào và
ra một cổng tương ứng tuỳ theo đích đến của chùm.

![](media/image3.png){width="5.1952482502187225in"
height="2.782661854768154in"}

***Hình 1.3. Kiến trúc và sơ đồ chức năng của mạng OBS***

#### 1.3.1.1. Nút biên

Việc liên kết các mạng biên với mạng OBS được thực hiện bởi các nút biên
mạng OBS. Mạng biên có thể kể đến như mạng IP, ATM, SONET/SDH. Một nút
biên OBS có thể là nút biên vào hoặc nút biên ra. Nút biên vào (ingress)
chịu trách nhiệm biến đổi các gói tin từ mạng biên thành định dạng dữ
liệu truyền trong mạng OBS, nghĩa là tập hợp các gói tin điện tử đến từ
nhiều nguồn khác nhau vào trong một chùm tùy theo từng đích đến của
chúng. Chùm sau đó được truyền trong môi trường toàn quang qua các bộ
định tuyến mà không cần bất kỳ lưu tạm nào tại những nút trung gian. Nút
biên ra tiếp nhận chùm, tách chùm thành những gói tin ban đầu và chuyển
chúng tới đích. Cấu trúc một nút biên có thể mô tả trong Hình 1.4.

![](media/image4.png){width="4.165606955380578in"
height="2.7269849081364828in"}

***Hình 1.4. Cấu trúc nút biên vào OBS***

Tương ứng với mỗi chùm một gói điều khiển được tạo ra mang các thông tin
điều khiển như chiều dài chùm, thời điểm đến của chùm, địa chỉ nút đích.
Gói điều khiển được gửi trên kênh điều khiển có bước sóng dành riêng đến
các nút trung gian để lập lịch đặt trước tài nguyên. Bộ lập lịch chùm
(*Scheduler*) thực hiện lập lịch chùm trên các kênh dữ liệu ra. Sự phân
chia xử lý này làm cho kênh điều khiển có thể hoạt động ở tốc độ bit
thấp hơn nhiều so với kênh dữ liệu nên có thể sử dụng các phương pháp
điều khiển khác nhau.

Một số giải thuật tập hợp chùm đã được đề xuất như sau:

-   Giải thuật dựa trên ngưỡng thời gian (timer-based): xác định ngưỡng
    thời gian tối đa để sinh chùm.

-   Giải thuật dựa trên ngưỡng độ dài chùm (length-based): chỉ rõ độ dài
    tối đa của mỗi chùm

-   Giải thuật lai (hybrid): dựa trên cả ngưỡng thời gian và ngưỡng độ
    dài.

Một yêu cầu đặt ra là phải tính toán khoảng thời gian *offset* như thế
nào để không quá dài hoặc quá ngắn nhằm tránh trường hợp chùm được tạo
ra và gởi đi khi chưa đặt trước được kênh bước sóng tại các nút trong
gian và khi đó chùm sẽ bị hủy.

#### 1.3.1.2. Nút lõi

Chuyển mạch và chuyển tiếp (bypass) các chùm là được thực hiện bởi các
nút (Hình 1.5). Các khối chức năng của nút bao gồm: giao diện vào, bộ
điều khiển chuyển mạch, bộ chuyển mạch quang và giao diện ra.

![](media/image5.png){width="4.855790682414698in"
height="2.8939435695538056in"}

***Hình 1.5. Cấu trúc nút lõi OBS***

Chức năng chính của giao diện vào là chọn lựa các kênh dữ liệu và điều
khiển. Mỗi kênh điều khiển được kết nối với một bộ tiếp nhận chùm. Bộ
tiếp nhận chùm khôi phục lại thông tin điều khiển từ các gói điều khiển,
chuyển đổi thành dạng điện và chuyển xuống bộ điều khiển chuyển mạch.
Đồng thời các chùm trên các bước sóng vào được tách kênh và phân phối
đến ma trận (*fabric*) chuyển mạch quang.

Bộ điều khiển chuyển mạch xử lý gói điều khiển, cụ thể là thực hiện tìm
kiếm và lập lịch tài nguyên cho chùm dữ liệu tương ứng. Lập lịch được
thực hiện bằng cách cấu hình ma trận chuyển mạch thích hợp và xử lý
tranh chấp. Bộ điều khiển chịu trách nhiệm cập nhật thông tin cho gói
điều khiển, gửi các tín hiệu điều khiển trong khoảng thời gian thích hợp
đến ma trận chuyển mạch và các thành phần khác để điều khiển các chùm.

Bộ chuyển mạch được xây dựng với ma trận chuyển mạch và các bộ phận
chuyên dụng khác. Ma trận chuyển mạch có thể được đặc trưng bởi chế độ
thực hiện (không đồng bộ/đồng bộ), kích thước, thời gian chuyển mạch và
các khối bên trong. Kích thước của ma trận chuyển mạch sẽ là
$(N \times W) \times (N \times W)$ nếu $N$ là số cổng vào/ra, $W\ $là số
bước sóng trên mỗi cổng. Các thành phần khác có thể được tìm thấy trong
chuyển mạch quang, ví dụ: chuyển đổi bước sóng, đường trễ sợi quang,
chúng được sử dụng cho cơ chế xử lý tranh chấp.

Giao diện ra thực hiện cập nhật thông tin điều khiển, ghép kênh WDM cho
các kênh điều khiển và dữ liệu và các điều kiện cho tín hiệu vào.

### 1.3.2. Các hoạt động bên trong mạng OBS

Các hoạt động bên trong một mạng OBS bao gồm: tập hợp chùm, báo hiệu,
lập lịch và giải quyết tranh chấp. Mỗi hoạt động đều đóng vai trò quan
trọng và tác động trực tiếp đến hiệu quả hoạt động của mạng OBS. \[32\],
\[35\]

#### 1.3.2.1. Tập hợp chùm

Tập hợp chùm là quá trình tập hợp các gói tin điện tử và đóng gói thành
chùm tại nút biên vào của mạng OBS. Tất cả gói đến sẽ chuyển đến hàng
đợi tùy theo đích của chúng như được mô tả trong Hình 1.6. Một giá trị
ngưỡng được sử dụng như một giới hạn để quyết định khi nào sinh ra một
chùm và gửi vào trong mạng.

![](media/image6.png){width="5.459095581802274in"
height="2.0523698600174978in"}

***Hình 1.6. Tập hợp chùm và tách chùm***

Hiện có nhiều kỹ thuật tập hợp chùm được đề xuất trong đó hai kỹ thuật
được quan tâm nhất là tập hợp chùm dựa vào ngưỡng thời gian
(*timer-based*) như Hình 1.7 và dựa vào ngưỡng độ dài (*length-based*)
như Hình 1.8. \[34\]

![](media/image7.png){width="5.229896106736658in"
height="1.8544258530183726in"}

***Hình 1.7. Tập hợp chùm theo ngưỡng thời gian***

Trong phương pháp tập hợp chùm dựa vào ngưỡng thời gian \[6\], một chùm
được sinh ra và được gửi vào trong mạng theo từng chu kỳ thời gian, đúng
bằng thời gian đã được xác định mà không quan tâm đến kích thước chùm
sinh ra dài hay ngắn. Chiều dài chùm sẽ biến đổi tuỳ theo tốc độ đến của
gói, trong những khoảng thời gian bằng nhau.

Đối với phương pháp tập hợp chùm dựa vào ngưỡng độ dài chùm \[6\], một
giới hạn về số lượng gói tin tối đa chứa trong mỗi chùm hoặc về kích
thước chùm tính theo bytes, trong trường hợp các gói tin đến có kích
thước thay đổi, được sử dụng như là điều kiện để sinh ra chùm. Vì vậy,
các chùm được tạo ra có kích thước bằng nhau.

![](media/image8.png){width="5.896655730533683in"
height="2.0211154855643043in"}

***Hình 1.8. Tập hợp chùm theo ngưỡng kích thước (số gói tối đa)***

Vấn đề quan trọng được đặt ra ở đây là làm thế nào để chọn một giá trị
ngưỡng thời gian hoặc ngưỡng độ dài tối ưu nhằm để giảm số lượng gói tin
điện tử bị mất khi có tranh chấp xảy ra, cũng như tăng hiệu suất sử dụng
mạng OBS. Rõ ràng nếu giá trị ngưỡng thời gian quá thấp, chiều dài chùm
sinh ra sẽ ngắn và số lượng chùm di chuyển trong mạng sẽ tăng lên, dẫn
đến tình trạng số lượng tranh chấp trong mạng cao, nhưng số lương gói
tin mất trung bình trong mỗi chùm lại thấp. Thêm vào đó, số lượng chùm
nhiều sẽ gây ra áp lực lên tốc độ xử lý các gói điều khiển phải nhanh
mới hiệu quả. Ngược lại nếu giá trị ngưỡng thời gian lớn, độ dài của
chùm tăng lên và số lượng chùm di chuyển trong mạng là giảm, do đó giảm
được số lượng tranh chấp trong mạng so với trường hợp chùm ngắn, nhưng
số lượng gói tin mất trung bình trên mỗi chùm mất là cao. Tóm lại, cần
xác định độ dài chùm tối ưu để tăng hiệu quả của một mạng OBS. \[33\]

Trong trường hợp các gói điện tử bị giới hạn về chất lượng dịch vụ
(*Quality of Service*), như ràng buộc về độ trễ, tập hợp chùm theo
ngưỡng thời gian sẽ được chọn, trong đó giá trị ngưỡng được chọn được
dựa trên yêu cầu độ trễ của các gói điện tử. Trong trường hợp không bắt
buộc về độ trễ, việc thiết lập chùm theo ngưỡng độ dài tỏ ra hợp lý hơn
vì các chùm có kích thước cố định sẽ giúp giảm bớt khả năng mất chùm do
xung đột.

Do thực tế lưu lượng trong mạng Internet hiện nay thay đổi thường xuyên
nên phương pháp tập hợp chùm tốt nhất là kết hợp vừa dựa trên ngưỡng
thời gian và vừa ngưỡng độ dài \[6\].

Hình 1.9 mô tả ảnh hưởng của kỹ thuật tập hợp chùm dựa trên ngưỡng thời
gian và ngưỡng độ dài đối với chùm sinh ra.

![](media/image9.png){width="3.8963768591426073in"
height="2.68787510936133in"}

***Hình 1.9. Tập hợp chùm theo ngưỡng thời gian và ngưỡng độ dài chùm***

#### 1.3.2.2. Báo hiệu

Trong mạng OBS khi một gói điều khiển đến tại một nút lõi, quá trình báo
hiệu bắt đầu được thực hiện để lập lịch tài nguyên và cấu hình ma trận
chuyển mạch sao cho phù hợp với chùm theo sau của nó. Tiến trình báo
hiệu trong mạng OBS được thực hiện bởi các gói điều khiển, mà chúng được
truyền trên một kênh bước sóng độc lập với các chùm.

Có nhiều phương thức báo hiệu tùy thuộc vào cách thức thực hiện và thời
điểm mà tài nguyên được đặt trước. Chúng ta có thể chia các loại phương
thức báo hiệu như sau \[3\] :

-   Theo hướng: đặt trước tài nguyên một chiều, hai chiều hay kết hợp.

-   Theo vị trí: đặt trước bắt đầu từ nguồn, từ đích hoặc từ nút trung
    gian.

-   Khi tài nguyên không sẵn sàng: đặt trước bền vững hay không bền
    vững.

-   Theo thời gian: đặt trước tài nguyên tức thời hoặc sau một thời gian
    trễ.

-   Giải phóng tài nguyên: Tường minh hoặc ngầm định.

-   Theo cách tính toán: Tập trung hoặc phân tán.

-   Báo hiệu một chiều, hai chiều hay hỗn hợp.

a)  *Báo hiệu một chiều, hai chiều, hỗn hợp*

Đối với báo hiệu một chiều, nút nguồn gửi đi một gói điều khiển yêu cầu
mỗi nút trên cùng một tuyến cấp phát tài nguyên cần thiết cho chùm dữ
liệu và cấu hình chuyển mạch quang tương ứng. Sau đó nguồn sẽ gửi chùm
dữ liệu đi mà không cần chờ tín hiệu ACK (*Acknowledge*) từ nút trung
gian hay nút đích trả lời về. Vì không cần tín hiệu ACK nên chùm dữ liệu
có thể gửi đi sớm hơn và giảm độ trễ truyền dẫn đầu -- cuối
(*end-to-end*).

Báo hiệu hai chiều cũng tương tự như báo hiệu một chiều. Tuy nhiên, nút
nguồn chờ nhận được tín hiệu ACK phản hồi sau đó mới quyết định có
truyền chùm đi hay không. Như vậy, nếu việc đặt trước tài nguyên thất
bại tại một nút trung gian nào đó thì các đặt trước trước đó sẽ phải hủy
bỏ và thực hiện lại từ đầu. Vì vậy, báo hiệu hai chiều tăng độ trễ
truyền dẫn đầu -- cuối.

Phương pháp báo hiệu hỗn hợp đưa ra giải pháp cân bằng giữa báo hiệu một
chiều và hai chiều. Trong phương pháp này, việc đặt trước từ nút nguồn
tới các nút trung gian được xác nhận bằng tín hiệu ACK. Vị trí của nút
được chỉ định làm nút trung gian sẽ quyết định khả năng mất hay độ trễ
của chùm dữ liệu.

b)  *Đặt trước tài nguyên bắt đầu từ nguồn, từ đích hoặc từ nút trung
    gian*

Trong đặt trước từ nguồn (Source Initiated Reservation - SIR), tài
nguyên được đặt trước trong khi gói điều khiển đi từ nguồn đến đích. Nếu
quá trình đặt trước thành công, một tín hiệu ACK được gửi ngược từ đích
về nguồn chỉ định bước sóng mà chùm dữ liệu sẽ được truyền đi. Ngược
lại, trong đặt trước từ đích (*Destination Initiated Reservation -
DIR*), nguồn gửi một yêu cầu đặt trước tài nguyên đến nút đích. Dựa vào
thông tin bước sóng khả dụng trên mỗi liên kết dọc theo tuyến đường, nút
đích sẽ chọn một bước sóng khả dụng với khoảng thời gian phù hợp (nếu
tồn tại) và gửi yêu cầu đặt trước trở về nút nguồn. Nguyên nhân chính
gây ra tắc nghẽn (hoặc mất dữ liệu) trong SIR là vì thiếu tài nguyên
rỗi, trong khi đối với DIR là do thông tin hết hạn.

Đặt trước tại nút trung gian (*Intermediate Node Initiated Reservation-
INI*): đặt trước tài nguyên này giống như DIR từ nguồn đến một vài nút
trung gian và giống như SIR từ nút trung gian đến nút đích.

c)  *Đặt trước tức thời hay đặt trước sau một thời gian trễ*

Dựa trên khoảng thời gian giữa gói điều khiển và chùm đến, tài nguyên có
thể được đặt trước tức thời hoặc sau một khoảng thời gian trễ (Hình
1.10). Trong kỹ thuật đặt trước tức thời, tài nguyên sẽ được đặt trước
ngay khi gói điều khiển đến các nút. Ngược lại, đối với kỹ thuật đặt
trước sau khoảng thời gian trễ, tài nguyên được đặt trước dựa trên thời
gian thực tế mà chùm dữ liệu đến tại nút đó. Nhìn chung, đặt trước tức
thời đơn giản nhưng dễ tạo ra tắc nghẽn lớn, ảnh hưởng đến hiệu quả sử
dụng băng thông trên toàn mạng.

![](media/image10.png){width="5.834146981627296in"
height="1.375191382327209in"}

***Hình 1.10. Quá trình đặt trước tức thời và sau một thời gian trễ***

d)  *Giải phóng tài nguyên tường minh hoặc ngầm định*

Giải phóng tài nguyên có thể thực hiện bằng hai cách là tường minh hoăc
ngầm định (Hình 1.10). Trong giải phóng tường minh, tài nguyên được giải
phóng bởi một gói điều khiển theo ngay sau chùm dữ liệu từ nguồn đến.
Ngược lại trong giải phóng ngầm định, gói BCP (*Burst Control Packet*)
phải mang thêm thông tin như là độ dài chùm và thời gian bù đắp để tại
các nút sẽ biết khi nào tài nguyên cần được giải phóng. Trong hai phương
pháp thì phương pháp giải phóng tường minh phức tạp hơn, vì nó chiếm
dụng băng thông và làm tăng số lượng gói thông báo ở trong mạng.

#### 1.3.2.3. Lập lịch chùm

Khi gói điều khiển của chùm đến tại các nút lõi mạng, dựa vào thông tin
trên gói điều khiển lúc này một giải thuật lập lịch sẽ được gọi để tìm
kênh ra khả dụng lập lịch cho chùm đến của nó. Mục đích chính của giải
thuật lập lịch là tìm kiếm được kênh khả dụng để lập lịch chùm đến và
sắp xếp tối ưu các chùm lên các kênh bước sóng ra nhằm tối ưu băng thông
sử dụng, giảm số chùm bị rơi, giảm tắc nghẽn và tăng hiệu năng hoạt động
của mạng.

Các giải thuật lập lịch trên mạng OBS có thể được chia thành các nhóm:
lập lịch trực tiếp, lập lịch trực tiếp kết hợp và lập lịch nhóm. Chi
tiết về các nhóm giải thuật này sẽ được trình bày trong các phần sau.
\[36\]

#### 1.3.2.4. Định tuyến

Định tuyến để chỉ sự lựa chọn đường đi cho một kết nối để thực hiện việc
gửi dữ liệu. Định tuyến chỉ ra hướng dịch chuyển của các gói tin (dữ
liệu), từ nguồn đến đích và qua các nút trung gian; thiết bị chuyên dùng
cho việc định tuyến là bộ định tuyến (*router*). Quá trình định tuyến
chỉ hướng đi thường dựa vào bảng định tuyến, bảng chứa các lộ trình tốt
nhất đến các đích khác nhau trên mạng. Vì vậy việc xây dựng bảng đinh
tuyến, được tổ chức trong bộ nhớ của bộ định tuyến, trở nên vô cùng quan
trọng cho hiệu quả của việc định tuyến. \[31\]

Trong mạng quang, các nút biên liên lạc với nhau qua các kênh quang gọi
là các lightpath. Lightpath là một đường đi của tín hiệu ánh sáng từ
nguồn đến đích và qua các nút trung gian. Trong mạng quang không sử dụng
bộ chuyển đổi bước sóng, lightpath phải sử dụng cùng một bước sóng từ
nguồn đến đích. Khi có yêu cầu thiết lập một kết nối, bộ định tuyến bước
sóng (Wavelength Router) phải sử dụng một giải thuật được chọn từ trước
để xác định một cổng ra và bước sóng tương ứng. Sự lựa chọn bước sóng
đóng vai trò rất quan trọng đối với xác suất tắc nghẽn trên toàn mạng
sau này. Vì vậy một bộ định tuyến bước sóng phải tìm ra lightpath và
thực hiện gán bước sóng sao cho xác suất tắc nghẽn là tối thiểu. Đây là
loại bài toán quan trọng trong việc thiết kế các mạng toàn quang.

-   Bài toán định tuyến và cấp phát bước sóng (Routing and Assignment
    Wavelength, RWA) được chia làm hai loại \[7\]:

-   Bài toán định tuyến và cấp phát bước sóng dành cho lưu lượng mạng cố
    định (*static traffic*).

-   Bài toán định tuyến và cấp phát bước sóng dành cho lưu lượng mạng
    thay đổi (*dynamic traffic*).

## 1.4. Tổng quan về bảo mật trong mạng chuyển mạch chùm quang 

Trong mạng chuyển mạch chùm quang (OBS), bảo mật là một trong những
thách thức quan trọng. Do đặc điểm vận hành của mạng OBS, trong đó gói
điều khiển và chùm dữ liệu được tách rời, mạng này dễ bị tấn công từ
chối dịch vụ và tấn công ngập lụt. Những cuộc tấn công này có thể làm
giảm hiệu suất mạng, gây mất dữ liệu và ảnh hưởng đến chất lượng dịch
vụ.

### 1.4.1. Đặc điểm bảo mật của mạng chùm quang

Mạng chuyển mạch chùm quang (Optical Burst Switching -- OBS) có các đặc
tính bảo mật đặc thù do kiến trúc và cơ chế truyền dẫn khác biệt so với
mạng chuyển mạch gói IP truyền thống. Trong OBS, sự tách biệt giữa mặt
phẳng điều khiển và mặt phẳng dữ liệu, với gói tiêu đề chùm (Burst
Header Packet -- BHP) được truyền trước để đặt trước tài nguyên mạng,
khiến mặt phẳng điều khiển trở thành mục tiêu dễ bị tấn công. Các cuộc
tấn công nhắm vào BHP có thể gây gián đoạn nghiêm trọng hoạt động mạng
mà không cần truy cập trực tiếp vào tải dữ liệu quang.

Hơn nữa, các mạng OBS thường hoạt động mà không có cơ chế xác nhận như
ACK hoặc NAK trong quá trình truyền dữ liệu theo cụm. Việc thiếu phản
hồi làm phức tạp việc phát hiện các hành vi bất thường và hạn chế khả
năng phục hồi của mạng sau các cuộc tấn công độc hại hoặc lỗi truyền
dẫn. Do đó, các cuộc tấn công từ chối dịch vụ (DoS) có thể được thực
hiện một cách lén lút trong khi vẫn gây ra sự suy giảm nghiêm trọng về
hiệu suất mạng.

Một đặc điểm bảo mật quan trọng khác của mạng OBS là yêu cầu về thời
gian nghiêm ngặt để xử lý các gói tin BHP tại các nút lõi. Vì các gói
tin BHP phải được xử lý trong khoảng thời gian cực ngắn, việc triển khai
các cơ chế bảo mật đòi hỏi nhiều tài nguyên tính toán như mã hóa mạnh
hoặc các giao thức xác thực phức tạp thường không khả thi. Hạn chế này
làm tăng tính dễ bị tổn thương của mạng OBS trước các cuộc tấn công tốc
độ cao, đặc biệt là các cuộc tấn công làm ngập gói tin BHP.

### 1.4.2. Lỗ hổng bảo mật do kiến trúc tách điều khiển và dữ liệu trong mạng OBS.

Một lỗ hổng quan trọng xuất phát từ việc thiếu sự ràng buộc chặt chẽ
giữa BHP và chùm dữ liệu tương ứng. Kẻ tấn công có thể phát sinh các BHP
giả mạo hoặc phát lại (*replay*) nhằm chiếm giữ tài nguyên chuyển mạch
và bước sóng một cách trái phép, dẫn đến hiện tượng cạn kiệt tài nguyên
và gián đoạn dịch vụ. Do chùm dữ liệu được gửi đi mà không có cơ chế xác
nhận đặt trước tài nguyên, các yêu cầu đặt trước không hợp lệ vẫn có thể
tồn tại đủ lâu để gây ra mất chùm và tắc nghẽn mạng nghiêm trọng \[3\].

Bên cạnh đó, kiến trúc tách điều khiển -- dữ liệu làm gia tăng đáng kể
hiệu quả của các cuộc tấn công từ chối dịch vụ (*Denial-of-Service --
DoS*) nhắm vào mặt phẳng điều khiển. Bằng cách phát tán một số lượng lớn
BHP bất thường hoặc độc hại, kẻ tấn công có thể làm quá tải khối xử lý
điều khiển tại các nút lõi OBS, từ đó ngăn cản các yêu cầu thiết lập
chùm hợp lệ. Các cuộc tấn công này, điển hình là tấn công BHP flooding,
có chi phí thực hiện thấp nhưng gây tác động lan rộng trên toàn mạng
\[8\].

Ngoài ra, sự thiếu vắng các cơ chế xác thực và kiểm tra chéo giữa hai
mặt phẳng càng làm trầm trọng thêm các lỗ hổng bảo mật. Các nút lõi OBS
thường chuyển tiếp chùm dữ liệu dựa hoàn toàn vào thông tin đã được xử
lý từ BHP trước đó, với khả năng rất hạn chế trong việc xác minh tính
hợp lệ của các yêu cầu đặt trước theo thời gian thực. Điều này khiến các
sai lệch giữa thông tin điều khiển và trạng thái truyền dữ liệu thực tế
khó bị phát hiện và xử lý kịp thời \[3\], \[8\].

Tóm lại, mặc dù kiến trúc tách biệt mặt phẳng điều khiển và dữ liệu cho
phép mạng OBS đạt được tốc độ truyền dẫn rất cao, nó đồng thời làm suy
yếu mức độ bảo mật tổng thể của hệ thống bằng cách tập trung niềm tin và
chức năng quan trọng vào mặt phẳng điều khiển. Do đó, việc bảo vệ mặt
phẳng điều khiển, đặc biệt là các gói BHP, thông qua các cơ chế xác thực
nhẹ, phát hiện bất thường và phân tích lưu lượng điều khiển, được xem là
hướng tiếp cận cần thiết trong các nghiên cứu bảo mật mạng OBS hiện nay
\[8\], \[9\].

### 1.4.3. Hạn chế của các cơ chế bảo mật truyền thống trong mạng OBS

Các cơ chế bảo mật truyền thống, vốn được thiết kế cho mạng chuyển mạch
gói hoặc chuyển mạch kênh, bộc lộ nhiều hạn chế khi áp dụng vào mạng
chuyển mạch chùm quang (*Optical Burst Switching -- OBS*). Do kiến trúc
tách biệt giữa mặt phẳng điều khiển và mặt phẳng dữ liệu, các gói điều
khiển chùm (*Burst Header Packet -- BHP*) phải được xử lý trong thời
gian rất ngắn tại các nút lõi. Điều này khiến việc triển khai các cơ chế
bảo mật dựa trên xác thực mạnh, mã hóa hoặc kiểm soát truy cập phức tạp
trở nên không khả thi, bởi chúng làm gia tăng độ trễ xử lý và ảnh hưởng
trực tiếp đến hiệu năng truyền dẫn của mạng OBS \[8\].

Bên cạnh đó, các phương pháp bảo mật dựa trên cơ chế phản hồi như xác
nhận (ACK/NAK), kiểm tra sâu nội dung gói tin hoặc tường lửa truyền
thống không phù hợp với đặc thù truyền dẫn hoàn toàn quang của OBS. Việc
thiếu bộ đệm quang tại các nút lõi và khả năng giám sát lưu lượng theo
thời gian thực khiến các cơ chế này không thể phát hiện và ngăn chặn kịp
thời các hành vi tấn công tinh vi, đặc biệt là các cuộc tấn công từ chối
dịch vụ nhắm vào mặt phẳng điều khiển như BHP flooding \[8\], \[9\].

Ngoài ra, các cơ chế bảo mật truyền thống thường dựa trên giả định về
mức độ tin cậy cao giữa các nút mạng, trong khi OBS lại rất nhạy cảm với
các tấn công từ bên trong. Khi một nút mạng bị xâm nhập, các BHP giả mạo
có thể được phát tán rộng rãi, dẫn đến hiện tượng chiếm dụng tài nguyên
và suy giảm nghiêm trọng chất lượng dịch vụ trên toàn mạng. Do đó, nhiều
nghiên cứu đã chỉ ra rằng các phương pháp bảo mật truyền thống không đủ
hiệu quả để bảo vệ mạng OBS trước các mối đe dọa hiện đại, và cần đến
các hướng tiếp cận mới dựa trên phân tích lưu lượng điều khiển và phát
hiện bất thường \[8\], \[9\], \[15\].

## 1.5. Các cách thức tấn công trong mạng OBS

Do đặc thù kiến trúc tách biệt giữa mặt phẳng điều khiển và mặt phẳng dữ
liệu, mạng chuyển mạch chùm quang phải đối mặt với nhiều phương thức tấn
công khác nhau, trong đó các cuộc tấn công nhắm vào mặt phẳng điều khiển
được xem là nguy hiểm nhất. Các nghiên cứu cho thấy rằng việc thao túng
các gói điều khiển chùm (Burst Header Packet -- BHP) có thể gây ra hậu
quả nghiêm trọng đối với hiệu năng và độ ổn định của toàn mạng, ngay cả
khi kẻ tấn công không truy cập trực tiếp vào nội dung dữ liệu quang.
Hiện nay đã phát hiện có nhiều phương pháp tấn công phổ biến:

*- Tấn công từ chối dịch vụ (DoS) trong OBS*: Tấn công từ chối dịch vụ
nhằm mục đích làm cạn kiệt tài nguyên mạng, khiến hệ thống không thể
phục vụ các yêu cầu hợp pháp. Hiện có các phương thức tấn công DoS phổ
biến bao gồm: Tấn công ngập lụt gói điều khiển (BHP Flooding Attack);
Tấn công giả mạo đường truyền (*Link Fabrication Attack*); Tấn công làm
gián đoạn đặt trước tài nguyên (*Resource Reservation Attack*); Tấn công
làm tràn bộ đệm hàng đợi (*Queue Overload Attack*)

\- *Tấn công ngập lụt (Flooding Attacks) trong OBS*: Tấn công ngập lụt
là một dạng đặc biệt của tấn công từ chối dịch vụ, trong đó kẻ tấn công
gửi một lượng lớn gói dữ liệu hoặc tín hiệu giả để làm cạn kiệt tài
nguyên hệ thống. Trong OBS, các loại tấn công ngập lụt phổ biến bao gồm:
Ngập lụt gói điều khiển (*BHP Flooding*); Ngập lụt chùm dữ liệu (*Data
Burst Flooding*); Ngập lụt tín hiệu báo hiệu (*Control Signaling
Flooding*).

Tấn công từ chối dịch vụ và tấn công ngập lụt trong mạng OBS là những
thách thức nghiêm trọng đối với bảo mật mạng. Những cuộc tấn công này
không chỉ làm giảm hiệu suất của hệ thống mà còn có thể gây gián đoạn
toàn bộ dịch vụ. Do đó, cần có các biện pháp bảo vệ hiệu quả để phát
hiện sớm và ngăn chặn những cuộc tấn công này nhằm đảm bảo sự ổn định và
hiệu quả của mạng OBS.

# **CHƯƠNG 2. TẤN CÔNG TỪ CHỐI DỊCH VỤ (DoS) VÀ KỸ THUẬT PHÁT HIỆN, ỨNG PHÓ**

## **2.1 Tấn công DoS trong mạng OBS**

### **2.1.1 Tổng quan về tấn công từ chối dịch vụ DoS**

*a) Khái niệm:* Tấn công từ chối dịch vụ và các dạng tấn công ngập lụt
được xem là những mối đe dọa nghiêm trọng đối với hạ tầng mạng hiện đại,
đặc biệt trong các hệ thống yêu cầu truyền tải dữ liệu tốc độ cao như
mạng chuyển mạch chùm quang OBS. Mục tiêu chính của các cuộc tấn công
này là làm gián đoạn hoặc suy giảm khả năng hoạt động bình thường của hệ
thống bằng cách khai thác những điểm yếu trong cơ chế quản lý tài nguyên
và quá trình định tuyến dữ liệu, từ đó gây ảnh hưởng đáng kể đến chất
lượng dịch vụ của mạng.

*b) Tấn công DoS trong mạng OBS:* Denial-of-Service attack (DoS) là hình
thức tấn công nhằm làm cạn kiệt tài nguyên của mạng, hệ thống hoặc ứng
dụng, khiến các yêu cầu hợp lệ từ người dùng không thể được xử lý. Các
phương thức tấn công DoS thường gặp bao gồm tấn công tràn bộ đệm, khai
thác lỗ hổng giao thức và tạo ra lưu lượng giả mạo nhằm gây tắc nghẽn
đường truyền.

Tấn công ngập lụt BHP Flooding được xem là một dạng cụ thể của DoS,
trong đó kẻ tấn công gửi một lượng lớn gói tin hoặc yêu cầu giả mạo đến
hệ thống làm quá tải băng thông và tài nguyên xử lý. Một số dạng tấn
công ngập lụt phổ biến có thể kể đến như SYN Flood, UDP Flood, ICMP
Flood và tấn công BHP Flooding trong môi trường mạng OBS. Đặc biệt,
trong kiến trúc OBS, tấn công BHP Flooding khai thác đặc điểm tách biệt
giữa gói điều khiển và chùm dữ liệu, dẫn đến việc tiêu tốn tài nguyên
mạng không cần thiết và làm suy giảm hiệu năng của hệ thống. Hậu quả của
các cuộc tấn công này có thể rất nghiêm trọng, bao gồm mất dữ liệu, gián
đoạn dịch vụ, giảm hiệu suất mạng và gây ra những tổn thất kinh tế đáng
kể.

### **2.1.2. Tấn công ngập lụt gói điều khiển (BHP Flooding)**

Trong mạng OBS, phần gói điều khiển (Burst Header Packet -- BHP) và phần
chùm dữ liệu (Data Burst -- DB) có cơ chế truyển tải tách biệt hoàn
toàn. Trong đó, gói điều khiển BHP được gửi đi trước một khoảng thời
gian offset đủ để thực hiện việc đặt trước tài nguyên và cấu hình chuyển
mạch tại các nút trung gian trên đường truyền từ nguồn đến đích. Cơ chế
này giúp tối ưu hóa tốc độ truyền dữ liệu và đáp ứng nhu cầu mở rộng
băng thông của các mạng thế hệ mới.

Tuy nhiên, chính sự tách rời giữa BHP và DB cùng với việc mạng OBS không
sử dụng bộ đệm quang tại các nút lõi đã vô tình tạo ra những thách thức
bảo mật nghiêm trọng. Tấn công ngập lụt BHP (BHP flooding) là một hình
thức tấn công từ chối dịch vụ (DoS) điển hình, khai thác trực tiếp vào
lỗ hổng trong cơ chế đặt trước tài nguyên.

-   *Cơ chế tấn công*: Kẻ tấn công sẽ gửi một lượng lớn các gói BHP giả
    mạo vào mạng nhằm chiếm dụng các kênh bước sóng và tài nguyên xử lý
    một cách bất hợp pháp. Điều nguy hiểm là các gói BHP này yêu cầu giữ
    chỗ tài nguyên nhưng thực tế không hề có dữ liệu thực (DB) đi kèm,
    khiến tài nguyên quang bị lãng phí và không thể phục vụ các kết nối
    khác.

-   *Hậu quả* : Các cuộc tấn công ngập lụt này tác động trực tiếp đến
    tính ổn định và hiệu suất toàn diện của hệ thống mạng quang. Việc
    tài nguyên bị chiếm dụng bởi lưu lượng giả mạo dẫn đến tình trạng
    gia tăng đột biến tỷ lệ mất chùm (Burst Loss Rate) đối với các luồng
    dữ liệu hợp lệ và làm suy giảm nghiêm trọng chất lượng dịch vụ
    (QoS).

![](media/image22.png){width="5.905511811023622in"
height="3.418448162729659in"}

***Hình 2.1. Cơ chế tấn công ngập lụt gói điều khiển BHP trong mạng
OBS.***

### **2.1.3 Ảnh hưởng của tấn công đến sự mất chùm và hiệu suất mạng**

*a) Sự gia tăng đột biến tỷ lệ mất chùm*

Tỷ lệ mất chùm là chỉ số cốt lõi phản ánh độ tin cậy của mạng OBS, giúp
đánh giá trực quan khả năng duy trì kết nối và mức độ thiệt hại về tài
nguyên khi hệ thống bị tấn công DoS.

-   *Cơ chế gây mất chùm*: Do mạng OBS không sử dụng bộ đệm quang tại
    các nút lõi, việc truyền tải chùm dữ liệu (DB) hoàn toàn phụ thuộc
    vào kết quả đặt trước tài nguyên của gói điều khiển (BHP). Khi quá
    trình này thất bại hoặc tài nguyên bị chiếm dụng bởi lưu lượng giả
    mạo, các chùm dữ liệu không có nơi lưu trữ tạm thời sẽ bị hủy bỏ
    ngay lập tức. Chính cơ chế này đã trực tiếp gây ra tình trạng mất
    chùm, trở thành điểm yếu chí mạng mà các cuộc tấn công DoS thường
    xuyên khai thác.

-   *Chiếm dụng tài nguyên ảo:* kẻ tấn công gửi hàng loạt gói điều khiển
    giả mạo để đặt trước các kênh bước sóng và tài nguyên chuyển mạch mà
    không có dữ liệu thực đi kèm. Hành vi chiếm dụng tài nguyên ảo này
    không chỉ gây lãng phí băng thông nghiêm trọng mà còn trực tiếp ngăn
    cản các chùm dữ liệu hợp lệ truy cập vào hệ thống.

-   *Hệ quả:* Các chùm dữ liệu hợp lệ đến sau sẽ không tìm được tài
    nguyên trống do đã bị các gói BHP giả \"giữ chỗ\" nhưng không có dữ
    liệu thực đi kèm và buộc phải bị hủy bỏ. Điều này dẫn đến việc tỷ lệ
    mất chùm tăng vọt, gây gián đoạn thông tin nghiêm trọng.

*b) Suy giảm thông lượng và hiệu suất mạng*

Hiệu suất của mạng quang thế hệ mới dựa trên khả năng truyền tải dung
lượng lớn với tốc độ cao. Tấn công DoS đánh trực tiếp vào ưu thế này:

-   *Lãng phí băng thông tiềm năng*: Mặc dù mạng OBS có băng thông rất
    lớn nhờ công nghệ WDM, nhưng các cuộc tấn công chiếm dụng tài nguyên
    bất hợp pháp khiến băng thông thực tế dành cho người dùng hợp lệ bị
    thu hẹp.

-   *Giảm thông lượng thực tế***:** Khi tỷ lệ mất chùm tăng cao, lượng
    dữ liệu truyền đích thành công (thông lượng) sẽ giảm xuống đáng kể.

-   *Quá tải nút mạng***:** Việc phải xử lý liên tục các gói BHP giả mạo
    làm suy giảm năng suất của bộ vi xử lý tại các nút trung gian, gây
    chậm trễ trong việc cấu hình chuyển mạch cho các luồng tin hợp lệ.

Tấn công BHP Flooding là mối đe dọa điển hình khai thác sự tách biệt
giữa điều khiển và dữ liệu để chiếm dụng tài nguyên bất hợp pháp, gây
lãng phí băng thông và tăng vọt tỷ lệ mất chùm. Hệ quả này làm suy giảm
chất lượng dịch vụ nghiêm trọng, đòi hỏi các giải pháp phát hiện và ứng
phó tự động nhằm đảm bảo tính ổn định cho hạ tầng mạng quang thế hệ mới.

### **2.1.4 Các phương thức tấn công ngập lụt**

#### **2.1.4.1 Tấn công tràn bộ đệm**

Tấn công tràn bộ đệm xảy ra khi một chương trình ghi dữ liệu vượt quá
kích thước bộ đệm, ghi đè lên vùng nhớ quan trọng. Điều này có thể làm
sập hệ thống, rò rỉ dữ liệu hoặc thực thi mã độc. Trong mạng chuyển mạch
chùm quang, bộ đệm tồn tại trong bộ xử lý gói điều khiển, bảng quản lý
tài nguyên và phần mềm điều khiển, khiến mạng chuyển mạch chùm quang dễ
bị khai thác.

**Phương thức tấn công:**

-   *Tràn bộ đệm ngăn xếp (Stack Overflow)*: Xảy ra khi một chuỗi dữ
    liệu quá dài ghi đè lên địa chỉ trả về của hàm, cho phép kẻ tấn công
    thực thi mã độc. Ví dụ: Một chương trình không giới hạn độ dài chuỗi
    nhập có thể bị tấn công bằng một payload chứa mã độc.

-   *Tràn bộ đệm vùng nhớ heap (Heap Overflow):* Lợi dụng lỗi trong cấp
    phát động, kẻ tấn công có thể ghi đè lên cấu trúc quản lý bộ nhớ,
    thay đổi luồng thực thi chương trình.

-   *Khai thác lỗi định dạng chuỗi (Format string attack):* Khi chương
    trình sử dụng printf(user_input); mà không kiểm tra đầu vào, kẻ tấn
    công có thể đọc hoặc ghi vào bộ nhớ tùy ý

-   *Tấn công tràn bộ đệm trong mạng chuyển mạch chùm quang:* Bộ xử lý
    gói điều khiển: Nếu hệ thống không kiểm tra kích thước gói điều
    khiển, kẻ tấn công có thể gửi dữ liệu quá lớn để ghi đè bộ nhớ. Bảng
    định tuyến và quản lý tài nguyên: Dữ liệu giả mạo có thể làm quá tải
    và gây lỗi hệ thống.

-   *Phần mềm điều khiển mạng chuyển mạch chùm quang*: Lỗ hổng bộ nhớ có
    thể bị khai thác để chiếm quyền điều khiển.

#### **2.1.4.2 Tấn công sử dụng lưu lượng giả mạo để làm tắc nghẽn đường truyền**

Tấn công lưu lượng giả mạo trong mạng OBS khai thác cơ chế đặt trước của
gói điều khiển nhằm chiếm dụng tài nguyên và gây tắc nghẽn hệ thống.
Hành vi này làm gián đoạn dịch vụ và trực tiếp ngăn chặn các luồng dữ
liệu hợp lệ, gây suy giảm nghiêm trọng hiệu suất truyền dẫn của hạ tầng
mạng quang.

**Phương thức tấn công:**

-   *Gửi lưu lượng BHP giả mạo*: Kẻ tấn công gửi lượng lớn các gói điều
    khiển hoặc dữ liệu giả nhằm gia tăng tải mạng một cách bất thường và
    gây tắc nghẽn.

-   *Khai thác cơ chế đặt trước tài nguyên:* Kẻ tấn công lợi dụng cơ chế
    đặt trước trong OBS để chiếm giữ bước sóng hoặc bộ đệm mà không
    truyền chùm dữ liệu hợp lệ, dẫn đến cạn kiệt tài nguyên.

-   *Truyền chùm dữ liệu rác*: Kẻ tấn công gửi các chùm dữ liệu không
    hợp lệ hoặc không có ý nghĩa nhằm tiêu tốn băng thông và làm suy
    giảm hiệu năng mạng.

-   *Kết hợp tấn công DoS/DDoS*: Kẻ tấn công phối hợp nhiều nguồn phát
    sinh lưu lượng lớn đồng thời nhằm khuếch đại mức độ tắc nghẽn và gây
    gián đoạn dịch vụ trên diện rộng.

## **2.2 Học máy và bảo mật trong mạng OBS** 

### **2.2.1 Vai trò của học máy trong bảo mật mạng OBS**

Trong mạng Optical Burst Switching (OBS), bảo mật mạng đóng vai trò quan
trọng do đặc tính truyền tải dữ liệu với tốc độ cao và lưu lượng mạng
lớn. Các cuộc tấn công từ chối dịch vụ như BHP flooding có thể làm suy
giảm hiệu năng mạng, gây mất gói dữ liệu và ảnh hưởng đến chất lượng
truyền tải. Vì vậy, việc ứng dụng các kỹ thuật Học máy (Machine Learning
-- ML) đã trở thành một giải pháp hiệu quả nhằm nâng cao khả năng bảo vệ
mạng OBS trước các mối đe dọa an ninh mạng hiện đại.

Học máy cho phép hệ thống tự động học hỏi từ dữ liệu lưu lượng mạng
trong quá khứ để phát hiện các hành vi bất thường và nhận dạng các mẫu
tấn công mà không cần phụ thuộc hoàn toàn vào các luật cấu hình thủ
công. Thông qua các thuật toán như SVM, KNN, Naïve Bayes hay Decision
Tree, hệ thống có thể phân loại lưu lượng thành lưu lượng hợp lệ và lưu
lượng tấn công với độ chính xác cao. Điều này giúp giảm đáng kể thời
gian phản ứng trước các cuộc tấn công mạng.

Ngoài khả năng phát hiện tấn công, các mô hình học máy còn hỗ trợ xử lý
dữ liệu theo thời gian thực với độ trễ thấp, phù hợp với môi trường
truyền tải tốc độ cao của mạng OBS. Sau khi được huấn luyện, mô hình có
thể nhanh chóng đưa ra quyết định phân loại gói tin, từ đó ngăn chặn sớm
các gói tin độc hại trước khi chúng gây ảnh hưởng đến tài nguyên mạng.
Đồng thời, ML còn giúp giảm tải cho hệ thống quản trị mạng thông qua
việc tự động hóa quá trình giám sát và phân tích lưu lượng.

Bên cạnh đó, học máy có khả năng thích nghi với các kiểu tấn công mới
thông qua việc cập nhật và huấn luyện lại mô hình trên các tập dữ liệu
mới. Điều này giúp hệ thống bảo mật trở nên linh hoạt hơn trước sự thay
đổi liên tục của các phương thức tấn công mạng hiện nay. Việc kết hợp
học máy trong bảo mật mạng OBS không chỉ giúp nâng cao độ chính xác
trong phát hiện tấn công mà còn góp phần cải thiện hiệu suất mạng, tăng
độ tin cậy và đảm bảo tính ổn định cho hệ thống truyền dẫn quang thế hệ
mới.

### **2.2.2 Ứng dụng của Học máy trong mạng OBS**

Học máy, với khả năng phân tích nâng cao, đóng vai trò quan trọng trong
các ứng dụng khác nhau trong bảo mật mạng OBS. Một ứng dụng phổ biến của
học máy là phát hiện các cuộc tấn công từ chối dịch vụ (DoS), đặc biệt
là tấn công BHP flooding. Thông qua việc phân tích dữ liệu lưu lượng
mạng, các thuật toán học máy có thể nhận dạng các đặc điểm bất thường
của gói tin và phân biệt giữa lưu lượng hợp lệ với lưu lượng tấn công.

Các mô hình như Naïve Bayes, KNN, SVM, Decision Tree hay PSO-SVM có khả
năng học từ dữ liệu mạng trong quá khứ để tự động phát hiện các hành vi
bất thường với độ chính xác cao. Điều này giúp giảm thiểu sự phụ thuộc
vào các phương pháp giám sát truyền thống dựa trên luật cố định.

Việc ứng dụng học máy không chỉ hỗ trợ phân loại lưu lượng theo thời
gian thực với độ trễ thấp phù hợp đặc thù mạng OBS, mà còn tối ưu hóa
hiệu suất thông qua dự đoán lưu lượng và cân bằng tải tài nguyên. Nhờ
khả năng thích nghi linh hoạt và huấn luyện lại trên các tập dữ liệu
mới, các mô hình này đảm bảo phát hiện kịp thời các biến thể tấn công
hiện đại, từ đó nâng cao tính an toàn, độ tin cậy và sự ổn định bền vững
cho hạ tầng mạng quang thế hệ mới.

### **2.2.3 Các nghiên cứu liên quan**

Bài toán phát hiện tấn công ngập lụt gói điều khiển BHP trong mạng
chuyển mạch chùm quang đã thu hút sự quan tâm của nhiều nhóm nghiên cứu
trong khoảng một thập kỷ trở lại đây, với phần lớn các công trình đi
theo hướng tiếp cận học máy. Có thể phân các nghiên cứu này thành ba
nhóm chính theo loại thuật toán được sử dụng.

Nhóm thứ nhất sử dụng cây quyết định và các luật phân loại. Rajab, Huang
và Al-Shargabi đề xuất phương pháp học luật từ cây quyết định, trong đó
các đặc trưng quan trọng nhất của lưu lượng BHP được lựa chọn để phân
loại nguồn thành các trạng thái hành xử khác nhau \[18\]. Ưu điểm của
hướng này là mô hình nhẹ, có khả năng giải thích và phù hợp với yêu cầu
xử lý thời gian thực tại nút OBS. Đây cũng là công trình đầu tiên giới
thiệu và công bố bộ dữ liệu chuẩn về tấn công ngập lụt BHP, sau này trở
thành bộ dữ liệu được sử dụng lặp lại trong hầu hết các nghiên cứu tiếp
theo.

Nhóm thứ hai sử dụng máy vector hỗ trợ kết hợp với các kỹ thuật tối ưu
tham số. Liu, Liao và Shi áp dụng máy vector hỗ trợ và dùng thuật toán
tối ưu bầy đàn để tinh chỉnh tham số, qua đó nâng cao tỷ lệ phát hiện so
với máy vector hỗ trợ truyền thống \[19\]. Efeoğlu và Tuna đánh giá hiệu
năng của thuật toán tối ưu cực tiểu tuần tự và thuật toán K\* trên cùng
bài toán, cho thấy nhiều thuật toán khác nhau đều đạt độ chính xác rất
cao trên bộ dữ liệu chuẩn \[22\].

Nhóm thứ ba khai thác học sâu và học bán giám sát. Hasan, Hasan và
Sattar sử dụng mô hình học sâu để phát hiện tấn công ngập lụt BHP và
cũng báo cáo độ chính xác gần như tuyệt đối \[20\]. Hossain và Haque áp
dụng thuật toán phân cụm K-means theo hướng bán giám sát nhằm phát hiện
và ngăn chặn tấn công khi nhãn dữ liệu hạn chế \[21\]. Các hướng này có
khả năng tự trích xuất đặc trưng và phát hiện mẫu tấn công phức tạp,
song đòi hỏi lượng dữ liệu và tài nguyên tính toán lớn hơn các mô hình
truyền thống. Gần đây nhất, hướng nghiên cứu này tiếp tục được mở rộng
tới các năm 2023-2025 với những thuật toán ngày càng phức tạp hơn: Nuha
và cộng sự đề xuất hàm khoảng cách bậc ba cho mô hình láng giềng gần
nhất và so sánh với bảy thuật toán học máy khác, báo cáo độ chính xác
99,3 phần trăm trên cùng bộ dữ liệu chuẩn \[38\]. Tuy nhiên, một điểm
chung xuyên suốt toàn bộ dòng nghiên cứu này, kể cả các công trình mới
nhất, là không một công trình nào đặt câu hỏi về tính toàn vẹn của bộ dữ
liệu: tất cả đều mặc nhiên tin vào độ chính xác gần tuyệt đối mà không
kiểm định hiện tượng rò rỉ nhãn. Đây chính là điểm khác biệt căn bản
trong cách tiếp cận của luận văn.

Bảng 2.1 tổng hợp và so sánh các nghiên cứu tiêu biểu theo thuật toán,
độ chính xác được báo cáo và đặc điểm nổi bật. Một quan sát đáng chú ý
là hầu hết các công trình đều báo cáo độ chính xác trong khoảng từ chín
mươi lăm đến một trăm phần trăm trên cùng một bộ dữ liệu chuẩn, bất kể
thuật toán được sử dụng là đơn giản hay phức tạp. Hiện tượng nhiều thuật
toán có độ phức tạp rất khác nhau cùng đạt độ chính xác gần tuyệt đối
trên một bộ dữ liệu là một dấu hiệu bất thường về mặt phương pháp luận,
gợi ý rằng bản thân bộ dữ liệu có thể chứa thông tin rò rỉ về nhãn. Nhận
định này sẽ được luận văn kiểm định định lượng trong Chương 3.

***Bảng 2.1. Tổng hợp các nghiên cứu tiêu biểu về phát hiện và đối phó
tấn công ngập lụt BHP.***

  --------------------------------------------------------------------------
  **Công trình** **Thuật toán** **Đặc điểm     **Độ chính xác **Hạn chế**
                                chính**        báo cáo**      
  -------------- -------------- -------------- -------------- --------------
  Rajab và CS.   Cây quyết      Đưa ra bộ dữ   Gần 100%       Đánh giá trên
  (2018) \[18\]  định + học     liệu chuẩn                    cùng bộ dữ
                 luật           UCI; rút gọn                  liệu, chưa
                                đặc trưng                     kiểm định rò
                                                              rỉ

  Liu và CS.     SVM + PSO      Tối ưu tham số Trên 99%       Phụ thuộc bộ
  (2021) \[19\]                 bằng tối ưu                   dữ liệu UCI;
                                bầy đàn                       không có cơ
                                                              chế ứng phó

  Hasan và CS.   Học sâu        Mạng nơ-ron    Trên 99%       Đòi hỏi tài
  (2018) \[20\]                 nhiều tầng                    nguyên tính
                                                              toán cao; chưa
                                                              kiểm định dữ
                                                              liệu

  Hossain &      K-means bán    Phù hợp khi    Khoảng 96%     Nhạy với chọn
  Haque (2019)   giám sát       nhãn hạn chế                  tâm cụm; tách
  \[21\]                                                      rời ứng phó

  Efeoğlu & Tuna SMO, K\*       Đánh giá nhiều Trên 95%       Cùng vấn đề rò
  (2021) \[22\]                 thuật toán cổ                 rỉ tiềm ẩn của
                                điển                          bộ dữ liệu UCI

  Sliti &        Phân tích lỗ   Xác thực gói   n/a            Tập trung mặt
  Boudriga       hổng + đối phó điều khiển                    phẳng điều
  (2014) \[8\]                                                khiển, không
                                                              học máy
  --------------------------------------------------------------------------

Bên cạnh khía cạnh thuật toán, một hạn chế chung của các nghiên cứu kể
trên là sự tách biệt giữa khâu phát hiện và khâu ứng phó. Phần lớn các
công trình dừng lại ở việc phân loại lưu lượng mà chưa đề xuất một cơ
chế hành động cụ thể để giảm thiểu tác hại sau khi đã phát hiện tấn
công. Ngoài ra, các nghiên cứu thường chỉ đánh giá trên một bộ dữ liệu
tĩnh duy nhất mà chưa kiểm chứng hiệu quả trong môi trường mô phỏng
động, nơi có thể đo lường các chỉ số như thông lượng và tỷ lệ mất chùm
theo thời gian.

## **2.3 Các kỹ thuật ứng phó tấn công DoS trong mạng OBS**

Phát hiện tấn công chỉ là bước đầu tiên trong quy trình bảo vệ mạng. Để
duy trì chất lượng dịch vụ khi mạng bị tấn công, hệ thống cần có cơ chế
ứng phó nhằm giảm thiểu hoặc loại bỏ tác động của lưu lượng độc hại. Các
kỹ thuật ứng phó tấn công DoS trong mạng OBS có thể được phân thành ba
nhóm chính.

Nhóm thứ nhất là giới hạn tốc độ và cách ly nguồn nghi ngờ. Khi một
nguồn bị phát hiện có hành vi bất thường, hệ thống có thể tạm thời giảm
tốc độ xử lý các gói điều khiển đến từ nguồn đó, hoặc cách ly hoàn toàn
nguồn này khỏi quá trình đặt trước tài nguyên. Cơ chế giới hạn tốc độ
thường được hiện thực bằng kỹ thuật gáo token, trong đó mỗi nguồn được
cấp một lượng token tương ứng với tốc độ cho phép, và các gói vượt quá
hạn mức sẽ bị loại bỏ hoặc đánh dấu \[29\], \[30\]. Ưu điểm của hướng
này là phản ứng nhanh và giảm tức thì lưu lượng tấn công, nhưng nhược
điểm là có thể ảnh hưởng đến luồng hợp lệ nếu tỷ lệ cảnh báo sai cao.

Nhóm thứ hai là điều chỉnh định tuyến và phân bổ lại tài nguyên. Khi
phát hiện tấn công trên một tuyến, hệ thống có thể chuyển hướng các chùm
dữ liệu hợp lệ sang đường đi khác hoặc ưu tiên cấp phát tài nguyên cho
các luồng đã được xác thực. Hướng tiếp cận này thường được khuyến nghị
tích hợp trực tiếp với khối phát hiện để tăng khả năng phản ứng kịp
thời, song đòi hỏi mạng phải có dư thừa tài nguyên và độ phức tạp quản
lý cao hơn.

Nhóm thứ ba là các cơ chế phòng vệ chuyên biệt cho mặt phẳng điều khiển.
Sliti và Boudriga phân tích lỗ hổng ngập lụt BHP và đề xuất biện pháp
đối phó dựa trên việc kiểm tra tính hợp lệ của gói điều khiển trước khi
cho phép đặt trước tài nguyên \[8\], \[9\]. Hướng này tập trung vào việc
xác thực nhẹ ở mức gói điều khiển nhằm ngăn chặn các yêu cầu đặt trước
giả mạo ngay từ đầu.

Hình 2.2 tổng hợp cách phân loại các kỹ thuật phát hiện và ứng phó tấn
công DoS trong mạng OBS theo hai trục chính. Một nhận xét quan trọng rút
ra từ việc khảo sát là các nghiên cứu hiện tại thường xử lý phát hiện và
ứng phó như hai bài toán riêng biệt, trong khi môi trường OBS với ràng
buộc độ trễ cực thấp lại đòi hỏi một quy trình tích hợp khép kín, nơi
kết quả phát hiện được chuyển ngay thành hành động ứng phó mà không qua
sự can thiệp thủ công.

![](media/image23.png){width="5.905511811023622in"
height="3.7234536307961505in"}

***Hình 2.2. Phân loại các kỹ thuật phát hiện và ứng phó tấn công DoS
trong mạng OBS.***

## **2.4 Vấn đề rò rỉ nhãn và học theo lối tắt trong đánh giá mô hình**

Một vấn đề phương pháp luận có ý nghĩa quyết định đối với độ tin cậy của
các kết quả phát hiện tấn công là hiện tượng rò rỉ nhãn. Rò rỉ nhãn xảy
ra khi tập đặc trưng dùng để huấn luyện mô hình chứa thông tin vốn chỉ
có được sau khi nhãn đã được xác định, khiến mô hình học được một lối
tắt thay vì học quy luật phân biệt thực sự. Kaufman và cộng sự đã hình
thức hóa khái niệm rò rỉ trong khai phá dữ liệu, chỉ ra rằng đây là một
trong những nguyên nhân phổ biến nhất dẫn đến kết quả đánh giá lạc quan
quá mức nhưng không tái lập được trong thực tế \[10\].

Trong bối cảnh học máy ứng dụng cho khoa học, Kapoor và Narayanan cảnh
báo rằng rò rỉ dữ liệu là nguồn gốc chính của khủng hoảng tái lập, khi
nhiều công bố báo cáo độ chính xác cao nhưng không thể tái hiện trên dữ
liệu độc lập \[11\], \[26\]. Hiện tượng này gắn liền với khái niệm học
theo lối tắt do Geirhos và cộng sự phân tích, trong đó mạng nơ-ron có xu
hướng khai thác các đặc trưng tương quan hời hợt thay vì các đặc trưng
có ý nghĩa nhân quả \[12\]. Lapuschkin và cộng sự gọi đây là hiệu ứng
Clever Hans, khi mô hình đưa ra dự đoán đúng nhưng dựa trên những căn cứ
hoàn toàn sai lệch \[13\].

Đối với bài toán phát hiện tấn công ngập lụt BHP, nguy cơ rò rỉ nhãn là
đặc biệt cao, bởi nhiều đặc trưng trong bộ dữ liệu chuẩn mang tính hậu
nghiệm, nghĩa là chúng mô tả trực tiếp hệ quả của trạng thái đã bị tấn
công chứ không phải nguyên nhân dẫn tới tấn công. Việc một mô hình đơn
giản như cây quyết định đạt độ chính xác tuyệt đối, thay vì là một thành
tựu, lại chính là tín hiệu cảnh báo cần được kiểm định. Đây là cơ sở lý
luận để luận văn thiết kế quy trình kiểm toán rò rỉ nhãn trong Chương 3
\[27\], nhằm bảo đảm các kết luận về năng lực phát hiện có giá trị khoa
học vững chắc.

## **2.5 Khoảng trống nghiên cứu và định hướng của luận văn**

Từ việc khảo sát các nghiên cứu liên quan, luận văn nhận diện ba khoảng
trống nghiên cứu chính làm cơ sở cho các đóng góp được trình bày trong
Chương 3.

Khoảng trống thứ nhất liên quan đến tính toàn vẹn của dữ liệu đánh giá.
Hầu hết các nghiên cứu phát hiện tấn công ngập lụt BHP đều dựa trên cùng
một bộ dữ liệu chuẩn và báo cáo độ chính xác gần như tuyệt đối, nhưng
chưa có công trình nào kiểm định một cách định lượng liệu bộ dữ liệu này
có bị rò rỉ nhãn hay không. Luận văn lấp khoảng trống này bằng cách áp
dụng quy trình kiểm toán ba lớp gồm phép thử từng đặc trưng đơn lẻ, đo
độ quan trọng hoán vị và đánh giá chéo có kiểm soát.

Khoảng trống thứ hai liên quan đến phương pháp xây dựng dữ liệu đánh giá
đáng tin cậy. Khi bộ dữ liệu chuẩn đã suy biến, cộng đồng cần một bộ dữ
liệu thay thế không bị rò rỉ. Luận văn đề xuất một quy trình sinh dữ
liệu phát hiện ở mức mạng từ dấu vết mô phỏng, kèm theo các phép kiểm
định để bảo đảm bộ dữ liệu mới không suy biến.

Khoảng trống thứ ba liên quan đến sự tách biệt giữa phát hiện và ứng
phó. Các nghiên cứu hiện tại phần lớn dừng ở khâu phát hiện mà chưa tích
hợp thành một quy trình khép kín có thể đo lường hiệu quả bằng các chỉ
số động của mạng. Luận văn lấp khoảng trống này bằng cách thiết kế và mô
phỏng định lượng một cơ chế khép kín phát hiện và ứng phó đặt tại nút
biên, đánh giá qua mức phục hồi thông lượng hợp pháp.

Ba khoảng trống nêu trên định hình toàn bộ nội dung thực nghiệm của
Chương 3, nơi luận văn lần lượt kiểm chứng từng luận điểm bằng dữ liệu
và mô phỏng cụ thể.

# **CHƯƠNG 3. MÔ PHỎNG VÀ PHÂN TÍCH KẾT QUẢ**

## **3.1 Mục tiêu và phương pháp luận của chương**

Chương này có nhiệm vụ kiểm chứng bằng thực nghiệm toàn bộ các luận điểm
mà luận văn đã đặt ra ở những chương trước. Quá trình kiểm chứng được tổ
chức thành hai pha nối tiếp nhau, mỗi pha gắn với một nhóm mục tiêu cụ
thể trong đề cương nghiên cứu.

Pha thứ nhất tập trung so sánh các mô hình học máy trên bộ dữ liệu
chuẩn, qua đó giải quyết mục tiêu thứ hai và thứ ba của đề tài. Ở pha
này, luận văn đánh giá năm mô hình học máy cổ điển trên bộ dữ liệu UCI
về tấn công ngập lụt gói điều khiển BHP, đồng thời kiểm định tính toàn
vẹn của chính bộ dữ liệu trước khi tin vào bất kỳ con số chính xác nào
mà nó tạo ra. Cách làm này xuất phát từ một nhận thức quan trọng rằng
một mô hình đạt độ chính xác cao chưa chắc đã phản ánh năng lực phát
hiện thật, nếu bản thân dữ liệu huấn luyện đã chứa sẵn lời giải.

Pha thứ hai chuyển sang mô phỏng động mạng OBS nhằm giải quyết mục tiêu
thứ tư và thứ năm. Ở pha này, luận văn dùng bộ công cụ NS2 kết hợp
mô-đun nOBS để tái tạo lại cuộc tấn công ngập lụt BHP một cách trung
thực, đo lường tác động thực tế của nó lên mạng, sinh ra một bộ dữ liệu
phát hiện không bị suy biến, và sau cùng thiết kế cơ chế ứng phó khép
kín đặt tại nút biên.

Triết lý xuyên suốt cả chương là một con số chỉ có giá trị khoa học khi
nó tái lập được và khi bộ dữ liệu sinh ra nó không bị suy biến một cách
tất định. Vì vậy, mọi kết quả trong chương đều được đưa qua các phép
kiểm định phản chứng, bao gồm việc kiểm tra từng đặc trưng đơn lẻ và
việc đánh giá chéo có kiểm soát rò rỉ giữa các nhóm dữ liệu.

## **3.2 Bộ dữ liệu UCI về tấn công ngập lụt BHP**

Bộ dữ liệu được sử dụng ở pha thứ nhất là tập \"OBS-Network-DataSet\"
công bố trên kho dữ liệu học máy UCI, gồm 1.075 mẫu với 21 đặc trưng số
và nhãn phân thành bốn lớp tương ứng với bốn trạng thái xử lý nguồn,
trong đó các lớp phân bố mất cân bằng. Đây chính là bộ dữ liệu được sử
dụng lặp lại trong hầu hết các nghiên cứu phát hiện tấn công ngập lụt
BHP, từ hướng cây quyết định, máy vector hỗ trợ kết hợp tối ưu bầy đàn,
học sâu, cho đến học bán giám sát. Xu hướng chung của các công trình này
là chạy đua theo độ chính xác, mỗi nghiên cứu lại bổ sung một mô hình
phức tạp hơn để nhích thêm vài phần trăm.

Vì dữ liệu mất cân bằng giữa các lớp, luận văn không chỉ dựa vào độ
chính xác thô mà báo cáo đồng thời nhiều chỉ số bổ trợ, gồm độ chính
xác, hệ số tương quan Matthews, độ chính xác cân bằng và điểm F1 trung
bình. Cách báo cáo đa chỉ số này giúp tránh ngộ nhận khi một mô hình chỉ
giỏi dự đoán lớp đa số.

Ngay từ khi khảo sát, luận văn đã nhận thấy một số đặc trưng trong bộ dữ
liệu mang tính hậu nghiệm, nghĩa là chúng mô tả trực tiếp hệ quả của
trạng thái đã bị tấn công chứ không phải nguyên nhân dẫn tới tấn công.
Các đặc trưng như trạng thái ngập lụt, trạng thái nút, hay những biến
trung bình của băng thông và tỷ lệ rớt gói qua nhiều lần chạy bị nghi
ngờ là nguồn gây rò rỉ nhãn. Giả thuyết này sẽ được kiểm định định lượng
ở mục tiếp theo.

## **3.3 So sánh các mô hình học máy**

### **3.3.1 Thiết lập thực nghiệm**

Ở pha thứ nhất, luận văn huấn luyện và so sánh năm mô hình học máy gồm
cây quyết định, máy vector hỗ trợ kết hợp tối ưu bầy đàn, mô hình láng
giềng gần nhất, máy vector hỗ trợ với hàm nhân RBF, và mô hình Naïve
Bayes. Việc đánh giá được thực hiện theo phương pháp chia tầng năm phần,
trong đó dữ liệu được chia thành năm phần cân đối về tỷ lệ lớp rồi luân
phiên dùng làm tập kiểm tra. Luận văn không dùng cách chia theo nhóm nút
vì biến nút trong bộ dữ liệu chỉ nhận hai giá trị, khiến cách chia này
bị suy biến. Bốn chỉ số được dùng để đánh giá gồm độ chính xác, hệ số
tương quan Matthews, độ chính xác cân bằng và điểm F1 trung bình.

### **3.3.2 Kết quả năm mô hình**

Bảng 3.1 trình bày kết quả chạy thật của năm mô hình theo phương pháp
chia tầng năm phần. Điều đáng chú ý là cây quyết định đạt độ chính xác
tuyệt đối trên toàn bộ các phần đánh giá. Trong nghiên cứu học máy, một
kết quả hoàn hảo như vậy không phải là dấu hiệu đáng mừng mà là tín hiệu
cảnh báo đầu tiên, buộc người nghiên cứu phải dừng lại để kiểm tra xem
mô hình có đang học một lối tắt nào đó hay không.

***Bảng 3.1. Kết quả năm mô hình học máy trên bộ dữ liệu UCI404 (chia
tầng năm phần).***

  -------------------------------------------------------------------------------------
  **Mô       **Độ chính  **Precision**   **Recall**   **Điểm F1** **Số đặc   **Độ trễ
  hình**     xác**                                                trưng**    suy luận**
  ---------- ----------- --------------- ------------ ----------- ---------- ----------
  Naïve      70,0±1,8    70,6±1,6        77,8±1,2     71,8±1,6    21         0,020 ms
  Bayes                                                                      

  Máy vector 84,2±2,1    86,9±2,0        86,5±3,3     86,3±2,3    21         0,219 ms
  hỗ trợ                                                                     

  Láng giềng 91,4±4,4    91,7±3,0        91,6±4,3     91,5±3,5    21         2,644 ms
  gần nhất                                                                   

  Cây quyết  100,0±0,0   100,0±0,0       100,0±0,0    100,0±0,0   21         0,006 ms
  định                                                                       

  PSO-SVM    100,0±0,0   100,0±0,0       100,0±0,0    100,0±0,0   21         0,134 ms
  -------------------------------------------------------------------------------------

### **3.3.3 Phân tích rò rỉ nhãn**

Đây là đóng góp phương pháp luận của luận văn, được thực hiện như một
nghiên cứu trường hợp về hiện tượng rò rỉ nhãn trong bộ dữ liệu được
dùng phổ biến. Để truy tìm nguyên nhân khiến cây quyết định đạt độ chính
xác tuyệt đối, luận văn tiến hành ba lớp kiểm định bổ sung.

Lớp kiểm định thứ nhất là phép thử từng đặc trưng đơn lẻ, kế thừa tư
tưởng phát hiện học theo lối tắt. Ở phép thử này, luận văn huấn luyện
cây quyết định chỉ với duy nhất một đặc trưng mỗi lần rồi đo độ chính
xác. Kết quả cho thấy có tới mười hai trong số hai mươi mốt đặc trưng tự
mình đã đủ sức tách bốn lớp gần như hoàn hảo, thể hiện trên Hình 3.1.
Một bộ dữ liệu lành mạnh sẽ không thể có hiện tượng này, vì không một
đặc trưng đơn lẻ nào lại chứa gần như toàn bộ thông tin về nhãn.

![](media/image24.png){width="5.708661417322834in"
height="3.378018372703412in"}

***Hình 3.1. Phép thử từng đặc trưng đơn lẻ trên bộ dữ liệu UCI404. Độ
chính xác của cây quyết định khi chỉ dùng một đặc trưng.***

Lớp kiểm định thứ hai dùng độ quan trọng hoán vị tính trên rừng ngẫu
nhiên hai trăm cây \[14\]. Phép đo này cho thấy chỉ riêng đặc trưng
trạng thái ngập lụt có độ quan trọng đáng kể, đạt khoảng 0,10, trong khi
mười tám đặc trưng còn lại có độ quan trọng gần như bằng không. Nói cách
khác, mô hình về bản chất chỉ đọc đúng một đặc trưng, và đặc trưng đó
gần như chính là nhãn được viết lại dưới dạng khác. Kết quả này được
minh họa trên Hình 3.2.

![](media/image25.png){width="5.708661417322834in"
height="3.4283945756780403in"}

***Hình 3.2. Độ quan trọng hoán vị tính trên rừng ngẫu nhiên đối với bộ
dữ liệu UCI404. Chỉ một đặc trưng thực sự đáng kể.***

Lớp kiểm định thứ ba là kết luận tổng hợp. Bộ dữ liệu UCI404 bị suy biến
một cách tất định, nghĩa là nhãn của nó có thể được suy ra trực tiếp từ
một vài đặc trưng hậu nghiệm. Do đó, mọi con số độ chính xác trong
khoảng từ 95 đến gần 100 phần trăm từng được báo cáo trên bộ dữ liệu này
thực chất không đo năng lực phát hiện tấn công, mà chỉ đo khả năng đọc
lại đặc trưng đã rò rỉ. Việc so sánh các thuật toán trên một bộ dữ liệu
như vậy là vô nghĩa về mặt khoa học. Đây là một khoảng trống thật sự
trong lĩnh vực, bởi cho đến nay chưa có nghiên cứu nào công bố phép kiểm
toán định lượng này, và phát hiện của luận văn phù hợp với cảnh báo về
khủng hoảng tái lập do rò rỉ dữ liệu gây ra.

## **3.4 Lựa chọn mô hình**

Vì bản thân benchmark đã suy biến, tiêu chí lựa chọn mô hình của luận
văn không thể dựa vào độ chính xác. Thay vào đó, luận văn lựa chọn dựa
trên các ràng buộc triển khai trong môi trường OBS thời gian thực, nơi
quyết định phải được đưa ra trong khoảng thời gian offset cực ngắn tại
nút biên.

Theo tiêu chí này, mô hình láng giềng gần nhất bị loại vì thuộc nhóm học
lười, độ trễ suy luận tăng theo số lượng mẫu nên không phù hợp với lõi
OBS vốn không có bộ đệm. Các mô hình hộp đen nặng cũng bị loại vì khó
giải thích và tốn tài nguyên. Cây quyết định được chọn làm mô hình vận
hành chính nhờ cấu trúc nhẹ, khả năng giải thích và độ trễ phát hiện
thấp; Naïve Bayes được giữ như một mô hình nền rất nhẹ để so sánh, nhưng
không dùng làm cổng kích hoạt phòng vệ do tỷ lệ cảnh báo sai cao trên dữ
liệu mức mạng.

## **3.5 Thiết kế cơ chế ứng phó khép kín**

### **3.5.1 Kiến trúc ba khối**

Lõi mạng OBS không có bộ đệm quang và buộc phải ra quyết định trong
khoảng thời gian offset chỉ vài micro giây, nên cơ chế ứng phó không thể
đặt ở lõi mà phải đặt tại nút biên, nơi gói tin vẫn còn được xử lý ở
miền điện tử. Trên cơ sở đó, luận văn thiết kế một vòng ứng phó khép kín
gồm bốn bước vận hành liên tục (Hình 3.3).

Bước thứ nhất là giám sát đặc trưng theo từng nguồn trong một cửa sổ
thời gian, trong đó hệ thống theo dõi các chỉ số như tốc độ phát gói
điều khiển, tỷ lệ gói điều khiển không hợp lệ, tỷ lệ rớt gói và mức sử
dụng băng thông. Bước thứ hai là phát hiện bằng mô hình cây quyết định
đã được kiểm chứng trên bộ dữ liệu mức mạng không suy biến; mô hình này
được chọn làm cổng kích hoạt vì có độ trễ phát hiện trung vị khoảng 0,10
giây và tỷ lệ cảnh báo sai trên cửa sổ lành thấp hơn nhiều so với Naïve
Bayes. Naïve Bayes vẫn được giữ trong phần so sánh như một mô hình nền
nhẹ, nhưng không dùng làm cổng vận hành do tỷ lệ cảnh báo sai cao. Bước
thứ ba là ra quyết định, trong đó kết quả phát hiện được ánh xạ sang các
hành động phân tầng theo mức độ nghiêm trọng. Nếu nguồn được xếp vào
nhóm an toàn, hệ thống cho phép lưu thông bình thường; nếu có dấu hiệu
nghi ngờ, hệ thống áp dụng giới hạn tốc độ; nếu nguồn có hành vi tấn
công rõ ràng, hệ thống cách ly tạm thời. Bước thứ tư là đóng vòng phản
hồi, trong đó các thống kê sau ứng phó tiếp tục được giám sát để điều
chỉnh trạng thái nguồn.

Xương sống kỹ thuật của cơ chế này gồm gáo token theo chuẩn đo lưu lượng
ba màu hai tốc độ \[24\], kết hợp danh sách xám, thời gian chờ tăng theo
cấp số nhân và ngưỡng kép có độ trễ để tránh dao động đóng mở liên tục.

![](media/image30.png){width="6.102362204724409in"
height="3.667306430446194in"}

*Hình 3.3. Kiến trúc cơ chế phát hiện--ứng phó khép kín đặt tại nút biên
vào mạng OBS.*

### **3.5.2 Mô hình mạng và ba kịch bản**

Mô hình mạng mô phỏng là một backbone quang hình chữ T gồm bảy nút quang
được đánh số từ 0 đến 6, trong đó lưu lượng đi vào qua hai nút biên và
đi ra tại một nút biên. Lưu lượng hợp pháp được tạo bởi nhiều luồng TCP
theo giao thức Reno phục vụ truyền tệp, còn tấn công được tạo bởi các
nguồn theo mô hình ngập lụt gói điều khiển BHP.

Để đánh giá có đối chứng, luận văn thiết lập ba kịch bản. Kịch bản nền
không có tấn công và không có phòng vệ, dùng làm mốc so sánh. Kịch bản
tấn công có lưu lượng hợp pháp và nguồn tấn công nhưng chưa bật phòng
vệ, dùng để đo tác động thuần của tấn công. Kịch bản ứng phó có đầy đủ
lưu lượng hợp pháp, nguồn tấn công và cơ chế phòng vệ, dùng để đo hiệu
quả của cơ chế khép kín. Cấu trúc ba kịch bản này được tóm tắt trong
Bảng 3.2.

***Bảng 3.2. Ba kịch bản mô phỏng đối chứng.***

  -----------------------------------------------------------------------
  **Kịch bản**      **Lưu lượng hợp   **Tấn công**      **Phòng vệ**
                    pháp**                              
  ----------------- ----------------- ----------------- -----------------
  Nền (S0)          Có                Không             Không

  Tấn công (S1)     Có                Có                Không

  Ứng phó (S2)      Có                Có                Có (gáo token và
                                                        cách ly)
  -----------------------------------------------------------------------

## **3.6 Mô phỏng và kết quả**

Công cụ mô phỏng là NS2 phiên bản 2.35 kết hợp mô-đun nOBS \[23\] chạy
trong môi trường Docker trên nền Ubuntu 18.04, cho phép xuất ra dấu vết
burst thật. Mỗi kịch bản được chạy với thời gian mô phỏng năm giây và
được lặp lại trên tám hạt giống ngẫu nhiên, trong đó cường độ tấn công
được dao động khoảng hai mươi phần trăm để bảo đảm kết quả không phụ
thuộc vào một cấu hình may rủi.

### **3.6.1 Tác động của tấn công ngập lụt BHP**

Kết quả so sánh giữa kịch bản nền và kịch bản tấn công cho thấy tấn công
ngập lụt BHP bóp nghẹt thông lượng hợp pháp khoảng năm mươi tư phần
trăm. Cơ chế gây hại ở đây là sự bỏ đói tài nguyên, trong đó các nguồn
tấn công không lùi bước liên tục chiếm chỗ đặt trước, đẩy các luồng TCP
hợp pháp vào trạng thái thiếu tài nguyên. Điều đáng lưu ý là tác động
này không đến từ việc tăng tỷ lệ mất chùm, bởi lõi mạng vẫn còn đủ bước
sóng, mà đến từ việc tài nguyên đặt trước bị chiếm dụng. Bảng 3.3 trình
bày các chỉ số định lượng của tác động này, còn Hình 3.4 minh họa trực
quan mức suy giảm thông lượng.

***Bảng 3.3. Tác động của tấn công lên các chỉ số mạng (tám hạt
giống).***

  --------------------------------------------------------------------------
  **Chỉ số**     **Kịch bản     **Kịch bản tấn **Thay đổi**   **Thống kê
                 nền**          công**                        Welch t**
  -------------- -------------- -------------- -------------- --------------
  Thông lượng    82.568         38.281         −53,6%         55,2
  hợp pháp (gói                                               
  TCP)                                                        

  Byte hợp pháp  85,8 MB        39,8 MB        −53,7%         55,2

  Burst gửi trên 40.462         64.839         +60,2%         −87,4
  backbone                                                    

  Tỷ lệ mất chùm khoảng 0,2%    khoảng 0,2%    không đổi      n/a
  --------------------------------------------------------------------------

![](media/image26.png){width="5.708661417322834in"
height="4.280376202974628in"}

***Hình 3.4. Tác động của tấn công ngập lụt BHP lên thông lượng hợp
pháp, so sánh giữa kịch bản nền và kịch bản tấn công trên tám hạt
giống.***

### **3.6.2 Đường cong tác động theo cường độ tấn công**

Để hiểu rõ quan hệ giữa cường độ tấn công và mức thiệt hại, luận văn
quét cường độ tấn công từ năm đến năm mươi megabit trên giây. Khi cường
độ tăng dần, thông lượng hợp pháp suy giảm gần như đơn điệu, giảm từ
khoảng năm mươi ba nghìn gói xuống còn khoảng mười hai nghìn năm trăm
gói, trong khi tải burst trên backbone tăng đều từ khoảng bốn mươi nghìn
lên một trăm sáu mươi nghìn. Luận văn ghi nhận một cách trung thực một
điểm bất thường tại mức bốn mươi megabit trên giây, nơi xu hướng tạm
thời đảo chiều một cách nhất quán trên ba hạt giống. Đây là hệ quả của
cơ chế lập lịch theo thời gian đặt trước chứ không phải nhiễu ngẫu
nhiên, vì vậy luận văn giữ nguyên dữ liệu mà không làm mượt. Toàn bộ
đường cong này được thể hiện trên Hình 3.5.

![](media/image27.png){width="5.708661417322834in"
height="3.5141076115485563in"}

***Hình 3.5. Đường cong tác động theo cường độ tấn công. Thông lượng hợp
pháp suy giảm khi cường độ tấn công tăng dần.***

### **3.6.3 Xây dựng bộ dữ liệu phát hiện không suy biến**

Sau khi đã chỉ ra rằng bộ dữ liệu UCI bị suy biến, luận văn đặt mục tiêu
sinh ra một bộ dữ liệu phát hiện trung thực từ chính dấu vết mô phỏng
NS2. Quá trình này được tiến hành qua ba lần thử, trong đó hai lần đầu
bị chính luận văn bác bỏ sau khi kiểm định, và chỉ lần thứ ba được chấp
nhận. Cách trình bày đầy đủ cả những lần thất bại nhằm bảo đảm tính
trung thực của phương pháp.

Lần thử thứ nhất đặt bài toán phát hiện theo từng nguồn với tấn công tốc
độ cao. Kết quả cho độ chính xác tuyệt đối, và ngay cả khi đánh giá chéo
theo nhóm vẫn giữ độ chính xác tuyệt đối, cho thấy mô hình chỉ đơn thuần
tách nguồn theo tốc độ. Vì vậy luận văn bác bỏ cách đặt bài toán này.

Lần thử thứ hai chuyển sang tấn công ẩn tốc độ thấp \[17\] nhưng vẫn cho
độ chính xác tuyệt đối. Chẩn đoán định lượng cho thấy riêng hệ số biến
thiên của khoảng cách giữa các gói đã đạt độ chính xác gần như tuyệt đối
khi đứng một mình. Nguyên nhân là các nguồn tấn công có hệ số biến thiên
rất ổn định quanh giá trị một, trong khi lưu lượng TCP hợp pháp có tính
bùng nổ với hệ số biến thiên cao hơn nhiều. Như vậy mô hình thực chất
chỉ học cách phân biệt giao thức UDP với giao thức TCP chứ không phải
phân biệt tấn công với lưu lượng bình thường, nên luận văn tiếp tục bác
bỏ.

Lần thử thứ ba đặt bài toán phát hiện ở mức mạng theo cửa sổ thời gian,
và đây là cách đặt bài toán được chấp nhận. Hướng này kế thừa truyền
thống phát hiện bất thường tập thể ở mức mạng \[15\], \[16\], \[28\],
trong đó nhãn cho biết một cửa sổ thời gian có đang bị tấn công hay
không, còn đặc trưng là các thống kê tổng hợp của toàn mạng mà không sử
dụng định danh nút. Trên một nghìn ba trăm cửa sổ, không một đặc trưng
đơn lẻ nào đạt tới ngưỡng suy biến, cho thấy bài toán đã thực sự đòi hỏi
năng lực phát hiện. Các mô hình phân hóa năng lực rõ rệt, với hệ số
tương quan Matthews trải dài từ khoảng 0,10 đến 0,98, được trình bày
trong Bảng 3.4. Khi đánh giá chéo theo hai mươi sáu lần chạy độc lập,
kết quả gần như không đổi, khẳng định bộ dữ liệu không bị rò rỉ và đáng
tin cậy.

***Bảng 3.4. Năng lực phát hiện trên benchmark mức mạng không suy
biến.***

  --------------------------------------------------------------------------
  **Mô hình**    **Độ chính     **Hệ số        **Độ chính xác **Điểm F1**
                 xác**          Matthews**     cân bằng**     
  -------------- -------------- -------------- -------------- --------------
  Máy vector hỗ  0,9931         0,9805         0,9850         0,9955
  trợ RBF                                                     

  Láng giềng gần 0,9569         0,8871         0,9627         0,9714
  nhất                                                        

  Cây quyết định 0,9131         0,7611         0,8887         0,9430

  Naïve Bayes    0,7415         0,1009         0,5357         0,8453
  --------------------------------------------------------------------------

### **3.6.4 Đường cong khả năng phát hiện theo độ ẩn của tấn công**

Lý thuyết phát hiện cổ điển gợi ý rằng hiệu năng phát hiện nên được đánh
giá như một hàm của cường độ tín hiệu thay vì chỉ báo cáo một con số đơn
lẻ. Áp dụng tư tưởng này, luận văn khảo sát hệ số tương quan Matthews
của hai mô hình tiêu biểu theo cường độ tấn công giảm dần, trình bày
trong Bảng 3.5 và minh họa trên Hình 3.6.

***Bảng 3.5. Hệ số tương quan Matthews theo cường độ tấn công.***

  -----------------------------------------------------------------------
  **Cường độ tấn công     **Máy vector hỗ trợ     **Cây quyết định**
  (Mb/s)**                RBF**                   
  ----------------------- ----------------------- -----------------------
  1 (ẩn nhất)             0,9368                  0,7397

  2                       0,9534                  0,8839

  3                       0,9850                  0,9455

  5                       0,9850                  0,9801

  8 đến 35 (rõ)           0,9867                  0,9733 đến 0,9867
  -----------------------------------------------------------------------

Kết quả cho thấy hiệu năng giảm đơn điệu khi tấn công càng ẩn, và khoảng
cách giữa máy vector hỗ trợ với cây quyết định lớn nhất ở vùng ẩn nhất,
nghĩa là tấn công càng tinh vi thì càng cần một mô hình mạnh. Điều đáng
khích lệ là ngay ở mức ẩn nhất, phát hiện ở mức mạng vẫn khả thi với hệ
số tương quan Matthews đạt khoảng 0,937, nhờ vào sức mạnh của các đặc
trưng tập thể. Đây chính là luận cứ thực nghiệm ủng hộ thiết kế giám sát
ở mức mạng đặt tại nút biên.

![](media/image28.png){width="5.708661417322834in"
height="4.044647856517935in"}

***Hình 3.6. Đường cong khả năng phát hiện theo độ ẩn của tấn công. Tấn
công càng ẩn càng đòi hỏi mô hình mạnh hơn.***

### **3.6.5 Hiệu quả của cơ chế ứng phó khép kín**

Cơ chế ứng phó thiết kế ở phần trên được hiện thực trong nOBS dưới dạng
một bộ điều tiết gáo token đặt tại nút biên. Khối phát hiện được gắn với
cổng cây quyết định ở mức cửa sổ; phép kiểm định trên bộ dữ liệu mức
mạng cho thấy cây quyết định phát hiện tấn công với độ trễ trung vị
khoảng 0,10 giây, nên trong mô phỏng NS2 cơ chế phòng vệ được kích hoạt
sau DET_DELAY = 0,10 giây kể từ khi tấn công bắt đầu. Theo tinh thần
thiết kế minh bạch, ngưỡng tốc độ cam kết được suy trực tiếp từ thống kê
baseline của kịch bản nền, trong đó nguồn hợp pháp có tốc độ cao nhất là
luồng duy trì kết nối đạt khoảng ba megabit trên giây, nên ngưỡng được
đặt ở mức bốn megabit trên giây một cách bảo thủ.

Một phép thử nội tại về cảnh báo sai đã được thực hiện để chứng minh cơ
chế phân biệt bằng hành vi chứ không bằng nhãn nguồn. Hai luồng duy trì
kết nối tốc độ ba megabit trên giây, vốn nằm dưới ngưỡng, được bộ điều
tiết tha đúng trong mọi lần chạy, trong khi tám nguồn tấn công tốc độ
khoảng mười hai megabit trên giây đều bị xử lý. Điều này khẳng định cơ
chế nhận diện dựa trên hành vi tốc độ thực tế chứ không phải dựa vào
việc biết trước nguồn nào là tấn công.

Bảng 3.6 trình bày thông lượng hợp pháp theo từng kịch bản với khoảng
tin cậy chín mươi lăm phần trăm. Khác với bản chạy trước đó, phép chạy
lại với cổng cây quyết định không còn xuất hiện hạt giống lỗi trong chế
độ cách ly; do đó cả bốn kịch bản trong bảng đều được tính trên tám hạt
giống. Hình 3.7 minh họa trực quan các mức phục hồi này.

***Bảng 3.6. Thông lượng hợp pháp theo kịch bản (khoảng tin cậy 95%).***

  --------------------------------------------------------------------------
  Kịch bản       n              Thông lượng    Khoảng tin cậy So với nền
                                (gói TCP)      95%            
  -------------- -------------- -------------- -------------- --------------
  Nền (S0)       8              82.568         n/a            100%

  Tấn công không 8              38.281         \[36.387;      −53,6%
  phòng vệ (S1)                                40.175\]       

  Giới hạn tốc   8              53.078         \[51.175;      64,3%
  độ (S2,                                      54.981\]       
  DT-gated, CIR                                               
  4 Mb)                                                       

  Cách ly (S2,   8              84.834         \[77.745;      102,7%
  DT-gated)                                    91.922\]       
  --------------------------------------------------------------------------

![](media/image29.png){width="5.708661417322834in"
height="3.8879975940507436in"}

***Hình 3.7. Hiệu quả của cơ chế ứng phó khép kín trên tám hạt giống với
khoảng tin cậy 95 phần trăm.***

Kết quả mới cho thấy chế độ giới hạn tốc độ phục hồi được khoảng ba mươi
ba phẩy bốn phần trăm khoảng thông lượng bị mất, đưa mạng từ mức khoảng
bốn mươi sáu phẩy bốn phần trăm baseline lên khoảng sáu mươi tư phẩy ba
phần trăm, đồng thời vẫn để cho nguồn tấn công một phần băng thông tối
thiểu, nên đây là cách đối xử mềm với rủi ro cảnh báo sai thấp. Chế độ
cách ly phục hồi gần như hoàn toàn và vượt nhẹ kịch bản nền, đạt khoảng
một trăm linh hai phẩy bảy phần trăm baseline, tương ứng một trăm linh
năm phẩy một phần trăm khoảng thông lượng bị mất được lấy lại. Cơ chế
của hiện tượng vượt nhẹ baseline là khi nguồn tấn công bị cách ly về mức
rất thấp, tài nguyên đặt trước được giải phóng và các luồng TCP hợp pháp
tận dụng khoảng trống này để phục hồi cửa sổ truyền.

Luận văn diễn giải kết quả này một cách thận trọng để tránh thổi phồng.
Việc kịch bản cách ly vượt nhẹ baseline là một quan sát cần được kiểm
chứng thêm chứ không phải một tuyên bố rằng phòng vệ làm mạng tốt hơn
bình thường, bởi hiệu ứng này phụ thuộc vào cấu hình tài nguyên đặt
trước cụ thể và đặc tính co giãn của TCP, nên cần khảo sát trên nhiều
tô-pô trước khi tổng quát hóa. Giữa hai chế độ có một sự đánh đổi rõ
ràng, trong đó cách ly cho thông lượng cao hơn nhưng là biện pháp cứng
có thể cắt oan nếu bộ phát hiện sai, còn giới hạn tốc độ an toàn hơn
nhưng phục hồi kém hơn.

Tổng hợp lại, kết quả này khép lại nửa phần ứng phó của đề tài, chứng
minh bằng định lượng rằng cơ chế khép kín đặt tại nút biên có thể phục
hồi thông lượng hợp pháp dưới tấn công ngập lụt BHP, với mức phục hồi từ
khoảng ba mươi ba phần trăm ở chế độ mềm cho tới khoảng một trăm linh
năm phần trăm khoảng thông lượng bị mất ở chế độ cứng, tùy theo tầng
hành động được áp dụng.

## **3.7 Bàn luận tổng hợp**

Từ toàn bộ kết quả của hai pha, luận văn rút ra ba nhận định tổng hợp.

Nhận định thứ nhất là sự hợp nhất của hai phát hiện về rò rỉ. Những con
số độ chính xác từ chín mươi chín đến một trăm phần trăm thường thấy
trong các nghiên cứu trước thực chất hoặc đo đặc trưng đã rò rỉ trong bộ
dữ liệu UCI, hoặc đo sự khác biệt giao thức ở mức nút trong dữ liệu NS2,
chứ không đo năng lực phát hiện thật. Chỉ có benchmark ở mức mạng, nơi
không một đặc trưng đơn lẻ nào đạt ngưỡng suy biến, mới đánh giá được
một cách công bằng.

Nhận định thứ hai là về bản chất đóng góp của luận văn. Đóng góp ở đây
không phải là một thuật toán học máy mới, mà gồm ba điểm. Thứ nhất là
phát hiện và định lượng hiện tượng rò rỉ trong một benchmark chuẩn được
dùng rộng rãi. Thứ hai là việc sinh ra một benchmark NS2 không suy biến.
Thứ ba là cơ chế phát hiện và ứng phó khép kín đặt tại nút biên đã được
mô phỏng và định lượng, với mức phục hồi thông lượng từ ba mươi mốt phần
trăm đến trên một trăm phần trăm tùy tầng hành động.

Nhận định thứ ba là phần trình bày trung thực các hạn chế. Việc kịch bản
cách ly vượt nhẹ baseline cần được kiểm chứng trên nhiều tô-pô trước khi
tổng quát hóa, và chưa thể khẳng định phòng vệ làm mạng tốt hơn bình
thường. Tấn công ngập lụt BHP được mô hình hóa bằng nguồn UDP tốc độ ổn
định như một xấp xỉ của hiệu ứng chiếm tài nguyên, chứ chưa tái tạo việc
giả mạo phần tiêu đề ở mức giao thức. Mô-đun nOBS và kịch bản bảy nút
giúp kiểm định có đối chứng, nhưng vẫn cần mở rộng sang nhiều tô-pô và
mẫu lưu lượng khác.

# **ĐÓNG GÓP CỦA LUẬN VĂN**

Luận văn đạt được các kết quả sau đây, đáp ứng đầy đủ năm mục tiêu cụ
thể đã đề ra trong đề cương nghiên cứu.

Đóng góp khoa học cốt lõi của luận văn không nằm ở việc đề xuất một
thuật toán phát hiện mới hay chạy đua độ chính xác như phần lớn các công
trình từ 2018 đến 2025, mà nằm ở ba điểm có tính phương pháp luận. Một
là, luận văn chứng minh định lượng rằng bộ dữ liệu chuẩn được cả cộng
đồng sử dụng suốt một thập kỷ đã bị suy biến do rò rỉ nhãn, qua đó giải
thích vì sao mọi thuật toán dù đơn giản hay phức tạp đều đạt độ chính
xác gần tuyệt đối. Hai là, luận văn xây dựng một bộ dữ liệu phát hiện ở
mức mạng không suy biến từ dấu vết mô phỏng trung thực, kèm quy trình
kiểm định để bảo đảm không một đặc trưng đơn lẻ nào tiết lộ nhãn. Ba là,
luận văn khép kín khoảng cách giữa phát hiện và ứng phó bằng một cơ chế
tích hợp đặt tại nút biên, được đánh giá bằng các chỉ số động của mạng.
Ba đóng góp này nhất quán với tinh thần cảnh báo về khủng hoảng tái lập
trong nghiên cứu học máy \[11\], và là phần giá trị khoa học bền vững
của luận văn bên cạnh việc hoàn thành đầy đủ năm mục tiêu kỹ thuật dưới
đây.

Thứ nhất, luận văn đã định lượng được tác động của tấn công ngập lụt BHP
lên mạng OBS thông qua mô phỏng NS2. Kết quả cho thấy tấn công gây suy
giảm thông lượng hợp pháp khoảng 53,6 phần trăm (kiểm định Welch t =
55,2 trên tám hạt giống), trong khi tỷ lệ mất chùm không tăng đáng kể.
Cơ chế gây hại được xác định là sự chiếm dụng tài nguyên đặt trước chứ
không phải nghẽn trực tiếp trên liên kết quang (mục tiêu 1).

Thứ hai, luận văn đã xây dựng và so sánh năm mô hình học máy trên bộ dữ
liệu UCI về tấn công ngập lụt BHP. Điểm khác biệt so với các nghiên cứu
trước là luận văn không chỉ báo cáo độ chính xác mà còn kiểm định tính
toàn vẹn của chính bộ dữ liệu. Bằng phương pháp phân tích từng đặc trưng
đơn lẻ và đo độ quan trọng hoán vị, luận văn phát hiện và chứng minh
định lượng rằng bộ dữ liệu UCI404 bị suy biến một cách tất định do rò rỉ
nhãn, trong đó mười hai trên hai mươi mốt đặc trưng tự mình đạt độ chính
xác gần tuyệt đối. Phát hiện này giải thích tại sao các mô hình trong
tài liệu đều đạt độ chính xác rất cao mà không thực sự đo năng lực phát
hiện tấn công (mục tiêu 2).

Thứ ba, dựa trên các ràng buộc triển khai thực tế của mạng OBS, cụ thể
là yêu cầu ra quyết định trong khoảng thời gian offset cực ngắn tại nút
biên, luận văn lựa chọn cây quyết định làm cổng phát hiện vận hành vì mô
hình này nhẹ, có khả năng giải thích, độ trễ phát hiện trung vị khoảng
0,10 giây và tỷ lệ cảnh báo sai thấp hơn Naïve Bayes trên dữ liệu mức
mạng. Naïve Bayes được giữ như một mô hình nền để so sánh, nhưng không
dùng làm cổng kích hoạt phòng vệ do tỷ lệ cảnh báo sai cao (mục tiêu 3).

Thứ tư, luận văn đề xuất và tích hợp cơ chế ứng phó khép kín gồm bốn
bước vận hành liên tục tại nút biên. Cơ chế này kết hợp giám sát theo
cửa sổ thời gian, phát hiện bằng mô hình nhẹ, ra quyết định phân tầng
(cho phép lưu thông, giới hạn tốc độ tạm thời, cách ly), và đóng vòng
phản hồi. Thiết kế sử dụng bộ điều tiết tốc độ theo nguyên tắc đo lưu
lượng ba màu hai tốc độ, với ngưỡng được suy trực tiếp từ thống kê lưu
lượng nền mà không dùng phán đoán định tính (mục tiêu 4).

Thứ năm, luận văn mô phỏng toàn bộ cơ chế đề xuất bằng NS2 phiên bản
2.35 kết hợp mô-đun nOBS trên ba kịch bản đối chứng và tám hạt giống
ngẫu nhiên. Kết quả chạy lại với cổng cây quyết định cho thấy chế độ
giới hạn tốc độ phục hồi 33,4 phần trăm thông lượng bị mất, còn chế độ
cách ly phục hồi 105,1 phần trăm khoảng thông lượng bị mất và đạt 102,7
phần trăm so với kịch bản nền. Không còn hạt giống lỗi trong phép chạy
mới. Hiện tượng vượt nhẹ baseline được diễn giải thận trọng như một quan
sát cần kiểm chứng thêm trên nhiều tô-pô, chứ không phải khẳng định
phòng vệ làm mạng tốt hơn trạng thái bình thường. Ngoài ra, luận văn xây
dựng được một bộ dữ liệu phát hiện mức mạng không suy biến từ dấu vết mô
phỏng, trong đó không một đặc trưng đơn lẻ nào đạt ngưỡng suy biến, và
đường cong khả năng phát hiện theo độ ẩn cho thấy phát hiện vẫn khả thi
ngay cả ở mức tấn công ẩn nhất (mục tiêu 5).

# **KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN**

## **Kết luận**

Luận văn đã hoàn thành đầy đủ năm mục tiêu cụ thể đặt ra trong đề cương
nghiên cứu. Qua quá trình thực nghiệm trên hai pha, luận văn rút ra các
kết luận sau.

Về bài toán phát hiện, luận văn chỉ ra rằng bộ dữ liệu chuẩn UCI về tấn
công ngập lụt BHP mà hầu hết các nghiên cứu trước sử dụng bị suy biến do
rò rỉ nhãn. Các con số độ chính xác cao (từ 95 đến 100 phần trăm) thường
được báo cáo thực chất không phản ánh năng lực phát hiện tấn công thật
sự. Phát hiện này có ý nghĩa phương pháp luận quan trọng, cảnh báo cộng
đồng nghiên cứu về việc cần kiểm định dữ liệu trước khi tin vào kết quả
mô hình.

Về bài toán ứng phó, luận văn chứng minh bằng định lượng rằng cơ chế
khép kín đặt tại nút biên có khả năng phục hồi thông lượng hợp pháp dưới
tấn công ngập lụt BHP. Thiết kế phân tầng cho phép cân bằng giữa mức
phục hồi và rủi ro cảnh báo sai, trong đó giới hạn tốc độ là biện pháp
mềm an toàn trước cảnh báo sai, còn cách ly là biện pháp cứng cho hiệu
quả cao hơn nhưng cần dùng thận trọng.

Về phương pháp đánh giá, luận văn đề xuất đánh giá phát hiện như một hàm
của cường độ tấn công thay vì chỉ một điểm đơn lẻ, và sinh ra bộ dữ liệu
benchmark mức mạng không suy biến từ dấu vết mô phỏng NS2.

## **Hướng phát triển**

Luận văn nhận thấy một số hạn chế cần được giải quyết trong các nghiên
cứu tiếp theo.

Thứ nhất, tấn công ngập lụt BHP trong luận văn được mô hình hóa bằng
nguồn tốc độ ổn định như một xấp xỉ của hiệu ứng chiếm tài nguyên, chưa
tái tạo việc giả mạo phần tiêu đề gói điều khiển ở mức giao thức. Hướng
phát triển tiếp theo là mở rộng mô hình tấn công để mô phỏng trung thực
hơn hành vi giả mạo BHP.

Thứ hai, hiện tượng kịch bản cách ly vượt nhẹ mức thông lượng nền cần
được kiểm chứng trên nhiều tô-pô mạng và nhiều mẫu lưu lượng khác nhau
trước khi tổng quát hóa.

Thứ ba, đường cong khả năng phát hiện theo độ ẩn hiện mới dừng ở mức tấn
công một megabit trên giây, chưa chạm tới điểm gãy nơi phát hiện thất
bại hoàn toàn. Việc mở rộng khảo sát xuống vùng tấn công cực ẩn sẽ giúp
xác định giới hạn thực sự của cơ chế.

Thứ tư, ngưỡng tốc độ cam kết và độ trễ phát hiện hiện được lấy từ thống
kê nền và kích thước cửa sổ benchmark. Nghiên cứu tiếp theo có thể tối
ưu các tham số này theo từng điều kiện mạng cụ thể để nâng cao hiệu quả
ứng phó.

# **TÀI LIỆU THAM KHẢO**

\[1\] B. Mukherjee, \"WDM optical communication networks: progress and
challenges,\" IEEE Journal on Selected Areas in Communications, vol. 18,
no. 10, pp. 1810--1824, 2000. DOI: 10.1109/49.887904.

\[2\] M. Yoo, C. Qiao, and S. Dixit, \"Optical burst switching for
service differentiation in the next-generation optical Internet,\" IEEE
Communications Magazine, vol. 39, no. 2, pp. 98--104, 2001. DOI:
10.1109/35.900637.

\[3\] Y. Xiong, M. Vandenhoute, and H. C. Cankaya, \"Control
architecture in optical burst-switched WDM networks,\" IEEE Journal on
Selected Areas in Communications, vol. 18, no. 10, pp. 1838--1851, 2000.
DOI: 10.1109/49.887906.

\[4\] C. Qiao and M. Yoo, \"Optical burst switching (OBS) --- a new
paradigm for an optical Internet,\" Journal of High Speed Networks, vol.
8, no. 1, pp. 69--84, 1999.

\[5\] S. Yao, B. Mukherjee, and S. Dixit, \"Advances in photonic packet
switching: an overview,\" IEEE Communications Magazine, vol. 38, no. 2,
pp. 84--94, 2000. DOI: 10.1109/35.819900.

\[6\] V. M. Vokkarane, Q. Zhang, J. P. Jue, and B. Chen, \"Generalized
burst assembly and scheduling techniques for QoS support in optical
burst-switched networks,\" in Proc. IEEE GLOBECOM 2002, vol. 3, pp.
2747--2751. DOI: 10.1109/glocom.2002.1189129.

\[7\] A. Wason and R. S. Kaler, \"Routing and wavelength assignment in
wavelength-routed all-optical WDM networks,\" Optik, vol. 121, no. 16,
pp. 1478--1486, 2010. DOI: 10.1016/j.ijleo.2009.02.012.

\[8\] M. Sliti and N. Boudriga, \"BHP flooding vulnerability and
countermeasure,\" Photonic Network Communications, vol. 29, no. 2, pp.
198--213, 2014. DOI: 10.1007/s11107-014-0484-9.

\[9\] N. Boudriga and M. Sliti, \"All optical switching control,\" in
Proc. 16th Int. Conf. on Transparent Optical Networks (ICTON), 2014, pp.
1--6. DOI: 10.1109/icton.2014.6876531.

\[10\] S. Kaufman, S. Rosset, C. Perlich, and O. Stitelman, \"Leakage in
data mining: formulation, detection, and avoidance,\" ACM Transactions
on Knowledge Discovery from Data, vol. 6, no. 4, pp. 1--21, 2012. DOI:
10.1145/2382577.2382579.

\[11\] S. Kapoor and A. Narayanan, \"Leakage and the reproducibility
crisis in machine-learning-based science,\" Patterns, vol. 4, no. 9, p.
100804, 2023. DOI: 10.1016/j.patter.2023.100804.

\[12\] R. Geirhos, J.-H. Jacobsen, C. Michaelis, R. Zemel, W. Brendel,
M. Bethge, and F. A. Wichmann, \"Shortcut learning in deep neural
networks,\" Nature Machine Intelligence, vol. 2, no. 11, pp. 665--673,
2020. DOI: 10.1038/s42256-020-00257-z.

\[13\] S. Lapuschkin, S. Wäldchen, A. Binder, G. Montavon, W. Samek, and
K.-R. Müller, \"Unmasking Clever Hans predictors and assessing what
machines really learn,\" Nature Communications, vol. 10, no. 1, p. 1096,
2019. DOI: 10.1038/s41467-019-08987-4.

\[14\] L. Breiman, \"Random forests,\" Machine Learning, vol. 45, no. 1,
pp. 5--32, 2001. DOI: 10.1023/A:1010933404324.

\[15\] V. Chandola, A. Banerjee, and V. Kumar, \"Anomaly detection: a
survey,\" ACM Computing Surveys, vol. 41, no. 3, pp. 1--58, 2009. DOI:
10.1145/1541880.1541882.

\[16\] A. Lakhina, M. Crovella, and C. Diot, \"Diagnosing network-wide
traffic anomalies,\" ACM SIGCOMM Computer Communication Review, vol. 34,
no. 4, pp. 219--230, 2004. DOI: 10.1145/1030194.1015492.

\[17\] A. Kuzmanovic and E. W. Knightly, \"Low-rate TCP-targeted denial
of service attacks,\" in Proc. ACM SIGCOMM 2003, pp. 75--86. DOI:
10.1145/863955.863966.

\[18\] A. Rajab, C.-T. Huang, and M. Al-Shargabi, \"Decision tree rule
learning approach to counter burst header packet flooding attack in
optical burst switching network,\" Optical Switching and Networking,
vol. 29, pp. 15--26, 2018. DOI: 10.1016/j.osn.2018.03.001.

\[19\] S. Liu, X. Liao, and H. Shi, \"A PSO-SVM for burst header packet
flooding attacks detection in optical burst switching networks,\"
Photonics, vol. 8, no. 12, p. 555, 2021. DOI: 10.3390/photonics8120555.

\[20\] M. Z. Hasan, K. M. Z. Hasan, and A. Sattar, \"Burst header packet
flood detection in optical burst switching network using deep learning
model,\" Procedia Computer Science, vol. 143, pp. 970--977, 2018. DOI:
10.1016/j.procs.2018.10.337.

\[21\] M. K. Hossain and M. M. Haque, \"A semi-supervised machine
learning approach using K-means algorithm to prevent burst header packet
flooding attack in optical burst switching network,\" Baghdad Science
Journal, vol. 16, no. 3 (Suppl.), p. 0804, 2019. DOI:
10.21123/bsj.2019.16.3(suppl.).0804.

\[22\] E. Efeoğlu and G. Tuna, \"Performance evaluation of sequential
minimal optimization and K\* algorithms for predicting burst header
packet flooding attacks on optical burst switching networks,\" Balkan
Journal of Electrical and Computer Engineering, vol. 9, no. 4, pp.
342--347, 2021. DOI: 10.17694/bajece.892150.

\[23\] H. Övergaard, nOBS --- an NS2-based simulation tool for optical
burst switching networks, Norwegian University of Science and Technology
(NTNU), 2004. \[Mã nguồn mô-đun nOBS cho NS2\].

\[24\] J. Heinanen and R. Guerin, \"A two rate three color marker,\"
IETF RFC 2698, 1999. DOI: 10.17487/RFC2698.

\[25\] M. K. Hossain, M. M. Haque, and M. A. A. Dewan, \"A comparative
analysis of semi-supervised learning in detecting burst header packet
flooding attack in optical burst switching network,\" Computers, vol.
10, no. 8, p. 95, 2021. DOI: 10.3390/computers10080095.

\[26\] E. Gibney, "Could machine learning fuel a reproducibility crisis
in science?," Nature, vol. 608, no. 7922, pp. 250--251, 2022. DOI:
10.1038/d41586-022-02035-w.

\[27\] Y. Zheng and V. Stodden, "The Idealized Machine Learning Pipeline
(IMLP) for advancing reproducibility in machine learning," in Proc. 2nd
ACM Conf. on Reproducibility and Replicability (ACM REP), 2024, pp.
110--120. DOI: 10.1145/3641525.3663630.

\[28\] Y. Liu, L. Zhang, and Y. Guan, "Sketch-based streaming PCA
algorithm for network-wide traffic anomaly detection," in Proc. IEEE
30th Int. Conf. on Distributed Computing Systems (ICDCS), 2010, pp.
807--816. DOI: 10.1109/icdcs.2010.45.

\[29\] A. K. Pandey and C. Pandu Rangan, "Mitigating denial of service
attack using proof of work and token bucket algorithm," in Proc. IEEE
Technology Students' Symposium (TechSym), 2011, pp. 43--47. DOI:
10.1109/techsym.2011.5783861.

\[30\] J. Y. Koh, J. T. C. Ming, and D. Niyato, "Rate limiting client
puzzle schemes for denial-of-service mitigation," in Proc. IEEE Wireless
Communications and Networking Conf. (WCNC), 2013, pp. 1848--1853. DOI:
10.1109/wcnc.2013.6554845.

\[31\] M. Klinkowski, J. Pedro, D. Careglio, and M. Pióro, "An overview
of routing methods in optical burst switching networks," Optical
Switching and Networking, vol. 7, no. 2, pp. 41--53, 2010. DOI:
10.1016/j.osn.2010.01.001.

\[32\] B. Praveen, J. Praveen, and C. Siva Ram Murthy, "A survey of
differentiated QoS schemes in optical burst switched networks," Optical
Switching and Networking, vol. 3, no. 2, pp. 134--142, 2006. DOI:
10.1016/j.osn.2006.05.003.

\[33\] S. Malik and U. Killat, "Impact of burst aggregation time on
performance in optical burst switching networks," Optical Switching and
Networking, vol. 2, no. 4, pp. 230--238, 2005. DOI:
10.1016/j.osn.2006.01.002.

\[34\] S.-Y. Oh and M. Kang, "A burst assembly algorithm in optical
burst switching networks," in Proc. Optical Fiber Communication Conf.
(OFC), 2002, pp. 771--773. DOI: 10.1109/ofc.2002.1036708.

\[35\] H. C. Cankaya and M. Jeong, "Optical burst switching: quality of
service, multicast, and operation and maintenance," in Emerging Optical
Network Technologies, 2005, pp. 155--176. DOI: 10.1007/0-387-22584-6_7.

\[36\] A.-H. Guan, B.-Y. Wang, and T. Wang, "Contention resolution and
burst assembly scheme based on burst segmentation in optical burst
switching networks," Optik, vol. 124, no. 14, pp. 1749--1754, 2013. DOI:
10.1016/j.ijleo.2012.05.052.

\[37\] M. Takieddine Seddik, O. Kadri, C. Bouarouguene, and H. Brahimi,
\"Detection of flooding attack on OBS network using Ant Colony
Optimization and machine learning,\" Computación y Sistemas, vol. 25,
no. 2, 2021. DOI: 10.13053/cys-25-2-3939.

\[38\] H. H. Nuha, S. A. Mugitama, A. Abo Absa, and Sutiyo, \"K-nearest
neighbors with third-order distance for flooding attack classification
in optical burst switching networks,\" IoT, vol. 6, no. 1, p. 1, 2024.
DOI: 10.3390/iot6010001.
