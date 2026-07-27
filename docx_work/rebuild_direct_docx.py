from pathlib import Path
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import zipfile, os

base=Path(__file__).resolve().parents[1]
src=base/'deliverables/LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.docx'
# base is the repository root, resolved from this script location
out=base/'LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726.docx'
high=base/'LuanVan_ThS_NguyenQuangTin_CAPNHAT_KETQUA_NS2_20260726_HIGHLIGHT.docx'

def setp(p,text):
    if p.runs:
        p.runs[0].text=text
        for r in p.runs[1:]: r.text=''
    else: p.add_run(text)

doc=Document(src)
# Paragraph indices verified against the actual source DOCX.
repl={
334:'Pha thứ hai chuyển sang mô phỏng động mạng OBS nhằm đánh giá tác động của một nhánh điều khiển BHP trực tiếp tại nút biên và các chế độ ứng phó tương ứng. Ma trận mới sử dụng native NS-2.35 kết hợp nOBS, gồm bốn ô S0, S1, S2-rate-limit và S2-isolation trên tám seed cố định. Nhánh này tạo control-only BHP có payload dữ liệu vắng mặt và kiểm tra admission trước reservation; nó không phải là phép nhúng trực tiếp mô hình học máy vào vòng chạy NS-2 và không được đồng nhất với nhánh UDP/CBR tạo valid data burst trước đây.',
365:'3.5.2 Mô hình mạng và bốn kịch bản đối chứng',
367:'Để đánh giá có đối chứng, ma trận gồm bốn ô kịch bản: S0 là trạng thái nền không tấn công; S1 có direct BHP flooding với guard baseline không giới hạn thực tế (budget 1e9); S2-rate-limit bật giới hạn theo ngân sách BHP; và S2-isolation bật cách ly tại nút biên. Hai biến thể S2 dùng cùng tải, seed và cấu hình mạng như S1 để bảo đảm so sánh theo cặp. Cấu trúc bốn ô được tóm tắt trong Bảng 3.2.',
370:'Công cụ mô phỏng là NS-2 phiên bản 2.35 kết hợp mô-đun nOBS trên môi trường Linux. Ma trận chính gồm 32 lượt chạy: bốn kịch bản nhân với tám seed cố định 101, 202, 303, 404, 505, 606, 707 và 808; mỗi lượt kéo dài 5 giây. Tô-pô tái dựng gồm bảy nút, liên kết quang 1000 Mb/s, hai luồng TCP hợp pháp với access 155 Mb/s và tám nguồn direct BHP. Mỗi nguồn phát control-only BHP với claimed size 1000 byte và một packet; tốc độ danh nghĩa là 12 Mb/s/nguồn, còn tốc độ hiệu dụng theo tám seed nằm trong khoảng 9,8926–14,2687 Mb/s/nguồn, trung bình 12,3153 Mb/s/nguồn. Guard dùng event budget và reservation-cost budget, không phải CIR payload 4 Mb/s. Các khoảng 95% trong phần này chỉ là khoảng mô tả trên tám seed cố định, không phải ước lượng bất định tổng quát.',
372:'Trong ma trận direct-BHP, S1 làm số gói TCP hợp pháp nhận được giảm từ trung bình 48.678 ở S0 xuống 24.307,5 ở S1, tương ứng giảm 50,07%; số byte TCP hợp pháp giảm từ 50.623.120 xuống 25.277.800, tương ứng giảm 50,07%. Số cặp burst quang giảm từ 4.917 xuống 2.892,875 và số reservation thành công giảm từ 19.606 xuống 11.543,625. Explicit data drops bằng 0 ở S0 và S1. Kết quả phù hợp với cơ chế direct control-only BHP cạnh tranh trên đường reservation; không được diễn giải là tải UDP tạo thêm valid data burst.',
377:'Nhánh sweep detection/impact cũ không được dùng để suy luận cho ma trận direct-BHP mới. Ma trận được báo cáo ở đây là một thiết kế paired fixed-seed gồm bốn ô, nhằm cô lập tác động của direct control admission và hiệu quả của hai guard profile. Vì vậy, không giữ các đường cong 5–50 Mb/s, điểm đảo chiều hay các số liệu sweep không có cùng provenance với ma trận 32 ô.',
381:'Ma trận direct-BHP không được dùng để tuyên bố đã xây dựng benchmark ML không suy biến. Các kết quả ML UCI và native window benchmark được giữ ở nhánh audit riêng; trong đó PSO-SVM, latency triển khai và detector online chưa có artifact đầy đủ. Direct matrix chỉ kiểm chứng causal path của control creation–observation–decision–action–outcome và network response.',
382:'Các phép thử direct-BHP kiểm tra rằng control được tạo, quan sát, quyết định và tác động theo đúng thứ tự thời gian; action DROP hoặc QUARANTINE xảy ra trước lần gọi reservation tương ứng. Đây là gate nhân quả của guard, không phải phép đánh giá độ chính xác của một bộ phân loại.',
383:'Nhánh direct-BHP dùng bộ điều khiển trạng thái/token-budget xác định với dữ liệu quan sát đồng thời. Guard không được gọi là detector ML vận hành; các claim về accuracy, MCC, latency hoặc lựa chọn cây quyết định chỉ được dùng nếu có artifact và protocol độc lập tương ứng.',
384:'Do đó, direct matrix được xem là thực nghiệm kiểm chứng admission và mitigation ở mức mạng, không phải benchmark huấn luyện detector. Các kết luận chỉ giới hạn trong tô-pô bảy nút, traffic profile đã khai báo, thời lượng 5 giây và tám seed cố định.',
387:'Ma trận direct-BHP không cung cấp đường cong khả năng phát hiện theo độ ẩn. Các số liệu MCC theo mức 1–35 Mb/s của bản cũ không có raw trace và lineage khớp với thí nghiệm mới, nên không được trình bày như kết quả tái lập.',
389:'Vì chưa có benchmark detector online không suy biến và chưa có phép đo latency end-to-end, luận văn không suy diễn từ ma trận này rằng một mô hình mạnh hơn là cần thiết ở vùng tấn công ẩn. Đây là giới hạn bằng chứng và là hướng thực nghiệm tiếp theo.',
392:'3.6.5 Hiệu quả của hai chế độ kiểm soát direct-BHP tại nút biên',
393:'Hai chế độ được hiện thực trong native NS-2.35+nOBS tại nút biên. Guard quan sát trực tiếp các control BHP, áp dụng event budget và reservation-cost budget trước lần reservation đầu tiên. S2-rate-limit cho phép một phần nhỏ control theo profile rồi chuyển các control vượt profile vào quarantine; S2-isolation dùng profile cách ly chặt hơn. Đây là response của một state/token-budget guard với dữ liệu quan sát đồng thời, không phải việc nhúng trực tiếp cây quyết định hay mô hình PSO-SVM vào vòng chạy NS-2.',
394:'Trong direct matrix, S0 chỉ có hai luồng TCP hợp pháp; S1 bổ sung tám nguồn direct BHP control-only và dùng guard baseline với budget 1e9 nên không giới hạn thực tế; hai S2 giữ nguyên traffic và seed của S1 nhưng bật profile kiểm soát tương ứng. Direct BHP dùng marker lifecycle nội bộ để đi vào synthetic control path; marker này không phải nhãn quan sát của detector. Do đó, kết quả đo hiệu quả mitigation không chứng minh false-positive rate đối với legitimate nOBS controls, vì các control hợp pháp không đi vào explicit direct-BHP guard path.',
395:'Bảng 3.6 trình bày số gói TCP hợp pháp theo bốn ô kịch bản. Cả 32 lượt chạy đều kết thúc thành công; mỗi ô có tám seed. Raw out.tr được parse độc lập; audit chain trong bhp_audit.log được validator kiểm tra; kết quả được đối chiếu với validation.json và validation.rerun.json. Các khoảng trong bảng là khoảng mô tả trên tập seed cố định.',
399:'S2-rate-limit nâng số gói TCP hợp pháp từ 24.307,5 ở S1 lên 48.678, đạt 100% mức S0 và khôi phục toàn bộ phần TCP bị mất trong cấu hình khảo sát. S2-isolation cũng đạt 48.678 gói, tương đương 100% mức S0 và khôi phục 100% phần bị mất. Hai chế độ có cùng network outcome trong cả tám seed; không có cơ sở kết luận chế độ nào ưu việt hơn về throughput.',
400:'Khác biệt giữa hai chế độ nằm ở action trace chứ không nằm ở số byte TCP cuối cùng. Rate-limit ghi nhận 48 control được admitted, 144 DROP_OVER_PROFILE, 433.328 QUARANTINE và 32 RELEASE trên toàn ma trận; isolation ghi nhận 16 admitted, 144 DROP_OVER_PROFILE và 433.360 QUARANTINE. Hai S2 đều làm giảm mạnh số direct BHP admitted so với S1, trong khi hai flow TCP hợp pháp không thấp hơn S1 và trở lại mức S0.',
401:'Tổng hợp lại, ma trận 32 lượt chạy cho thấy trong cấu hình direct-BHP đã khai báo, cả rate-limit và isolation đều ngăn phần lớn control-only BHP trước reservation và phục hồi thông lượng TCP hợp pháp về đúng mức S0. Kết luận chỉ áp dụng cho tô-pô bảy nút, traffic profile, thời lượng 5 giây và tám seed cố định; zero collateral ở đây chỉ là kết quả của hai flow được quan sát và phạm vi guard đã khai báo, không phải false-positive rate tổng quát.',
404:'Nhận định thứ nhất là sự phân biệt giữa các nhánh bằng chứng. UCI404 là audit offline của một benchmark có duplicate/dependence và target-policy/proxy leakage risk; native direct-BHP matrix là thực nghiệm admission/mitigation ở mức mạng. Không được dùng kết quả của một nhánh để chứng minh claim của nhánh kia.',
405:'Nhận định thứ hai là bản chất đóng góp của luận văn. Đóng góp thực nghiệm hiện được hỗ trợ gồm: kiểm toán rò rỉ và tính tái lập của UCI404 theo protocol leakage-aware; xây dựng native direct-BHP control path có audit nhân quả; và đánh giá hai chế độ ứng phó tại nút biên bằng ma trận 32 ô. Ma trận mới cho thấy S1 giảm 50,07% byte TCP hợp pháp, còn cả hai S2 phục hồi 100% mức S0 trong cấu hình khảo sát.',
406:'Nhận định thứ ba là phạm vi và giới hạn suy luận. Direct BHP producer dùng marker lifecycle để chọn synthetic control path; vì vậy kết quả không chứng minh detector inference từ wire-visible evidence, không phải exact reproduction của PSO-SVM hay closed-loop ML deployment. Audit provenance, source-generation consistency, legitimate-control coexistence và generalization trên nhiều tô-pô vẫn cần được mở rộng.',
409:'Luận văn đạt được các kết quả thực nghiệm được kiểm chứng trong phạm vi artifact hiện có; các mục tiêu chưa có đủ bằng chứng được nêu rõ là giới hạn, không được nâng thành kết luận đã hoàn tất.',
411:'Thứ nhất, native direct-BHP matrix trên NS-2.35+nOBS gồm 32 lượt chạy hợp lệ. Trên tám seed cố định, số gói TCP hợp pháp giảm từ 48.678 xuống 24.307,5 giữa S0 và S1, tương ứng giảm 50,07%; số byte giảm từ 50.623.120 xuống 25.277.800. Đây là bằng chứng về tác động của synthetic direct control-only BHP trong cấu hình tái dựng, không phải exact reproduction của mọi forged-BHP behavior.',
413:'Thứ ba, chưa có bằng chứng đủ để lựa chọn model vận hành theo Pareto accuracy–latency–resource. UCI404 có pipeline audit cho bốn baseline; PSO-SVM, latency end-to-end, model-size và detector deployment artifact chưa được tái lập. Vì vậy, cây quyết định không được tuyên bố là detector vận hành đã kiểm chứng từ ma trận direct-BHP.',
414:'Thứ tư, native direct-BHP guard kiểm chứng được admission trước reservation, causal ordering và hai actuator profile. Tuy nhiên, đây là deterministic contemporaneous token-budget state machine; chưa phải closed-loop ML detector–decision–response với attribution tin cậy, false-positive accounting, graylist, backoff/hysteresis và feedback recovery đầy đủ.',
415:'Thứ năm, ma trận 32 lượt bằng NS-2.35+nOBS trên bốn ô kịch bản và tám seed cố định cho thấy S2-rate-limit và S2-isolation đều đạt 48.678 gói TCP hợp pháp, bằng 100% S0 và cao hơn S1. Kết quả chứng minh hiệu quả network response của hai profile trong cấu hình nghiên cứu, không đồng nghĩa bộ phát hiện ML đã được nhúng trực tiếp vào NS-2 hoặc hệ thống đã sẵn sàng triển khai.',
418:'Qua hai pha thực nghiệm và các gate kiểm toán, luận văn xác lập được những kết luận trong phạm vi artifact đã tái kiểm; những claim thiếu artifact gốc không được xem là đã tái lập.',
420:'Về bài toán ứng phó, direct-BHP matrix cho thấy rate-limit và isolation đều phục hồi byte TCP hợp pháp từ 25.277.800 ở S1 lên 50.623.120 ở S2, đạt 100% mức S0 trong cấu hình khảo sát. Đây là oracle/guard effectiveness với synthetic direct-control path; chưa phải bằng chứng của detector-driven closed loop hoặc false-positive safety tổng quát.',
421:'Về phương pháp đánh giá, luận văn tách riêng UCI404 offline audit, native network experiment và direct-BHP control-path evidence. Việc tách lineage này ngăn không cho số liệu synthetic MVP hoặc benchmark cũ được dùng như bằng chứng NS-2.35+nOBS.',
424:'Thứ nhất, direct-BHP producer hiện là synthetic control-only path và còn dùng marker lifecycle nội bộ để chọn nhánh xử lý; cần chứng minh thêm rằng decision có thể dựa trên wire-visible contemporaneous evidence, không bị ảnh hưởng bởi producer-side oracle. Cần bổ sung end-to-end reservation outcome, source-generation consistency và lifecycle safety.',
425:'Thứ hai, cần kiểm thử coexistence giữa legitimate nOBS controls và direct controls trên cùng trusted ingress/identity, đồng thời đo collateral theo flow, delay, jitter và các lớp traffic khác. Zero collateral hiện tại chỉ giới hạn ở hai flow TCP hợp pháp đã cấu hình.',
426:'Thứ ba, cần mở rộng ma trận sang nhiều seed, rate, claimed reservation cost và tô-pô; đồng thời điều tra reproducibility của build, compiler/toolchain và external provenance cho run metadata. Tám seed hiện tại chỉ hỗ trợ mô tả trong workload đã khai báo.',
427:'Thứ tư, cần tích hợp detector online nếu mục tiêu là closed-loop detection–decision–response: định nghĩa feature window causally available, trusted attribution, measured p50/p95/p99 latency, state transitions, rollback và failure tests. Không gọi guard hiện tại là PSO-SVM, RFC2698 đầy đủ hoặc detector ML vận hành.'
}
for i,text in repl.items():
    setp(doc.paragraphs[i],text)
# Update captions and tables by verified table indices.
for i,p in enumerate(doc.paragraphs):
    if 'Bảng 3.2. Ba kịch bản' in p.text: setp(p,p.text.replace('Ba kịch bản','Bốn kịch bản'))
    if 'Hình 3.4.' in p.text: setp(p,'Hình 3.4. Tác động của direct control-only BHP lên thông lượng TCP hợp pháp giữa S0 và S1 trên tám seed cố định.')
    if 'Hình 3.7.' in p.text: setp(p,'Hình 3.7. Hiệu quả của hai chế độ kiểm soát direct-BHP trên tám seed cố định.')
    if 'Bảng 3.6.' in p.text: setp(p,'Bảng 3.6. Thông lượng TCP hợp pháp theo bốn kịch bản direct-BHP (khoảng mô tả trên tám seed).')
# Tables 3, 4, 7 are verified from source inventory.
rows3=[['Kịch bản','Lưu lượng hợp pháp','Direct BHP','Phòng vệ'],['S0 – nền','Có','Không','Không'],['S1 – tấn công','Có','Có, baseline không giới hạn','Không'],['S2-rate-limit','Có','Có','Event/reservation budget'],['S2-isolation','Có','Có','Quarantine/cách ly']]
while len(doc.tables[3].rows)<len(rows3):
    doc.tables[3].add_row()
for ri,row in enumerate(rows3):
    for ci,val in enumerate(row): doc.tables[3].cell(ri,ci).text=val
rows4=[
    ['Chỉ số','S0 – nền','S1 – tấn công','Thay đổi S1/S0','Phạm vi'],
    ['Gói TCP hợp pháp','48.678','24.307,5','−50,07%','8 seed cố định'],
    ['Byte TCP hợp pháp','50.623.120','25.277.800','−50,07%','8 seed cố định'],
    ['Cặp burst quang','4.917','2.892,875','−41,17%','8 seed cố định'],
    ['Reservation thành công','19.606','11.543,625','−41,12%','8 seed cố định'],
    ['Explicit data drops','0','0','—','8 seed cố định'],
]
while len(doc.tables[4].rows)<len(rows4): doc.tables[4].add_row()
for ri,row in enumerate(rows4):
    for ci,val in enumerate(row): doc.tables[4].cell(ri,ci).text=val
rows7=[['Kịch bản','n','Gói TCP hợp pháp (TB)','Khoảng mô tả','So với S0'],['S0 – nền','8','48.678','[48.678; 48.678]','100%'],['S1 – tấn công','8','24.307,5','[20.068,244; 28.546,756]','49,93%'],['S2-rate-limit','8','48.678','[48.678; 48.678]','100%'],['S2-isolation','8','48.678','[48.678; 48.678]','100%']]
for ri,row in enumerate(rows7):
    for ci,val in enumerate(row): doc.tables[7].cell(ri,ci).text=val
# Replace embedded legacy figures with direct-matrix figures if relationship members exist.
fig1=base/'docx_work/figure_3_4_direct.png'; fig2=base/'docx_work/figure_3_7_direct.png'
# generate simple figures from validated means; avoid dependency on old scripts.
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,ax=plt.subplots(figsize=(7.1,5.1),dpi=180); bars=ax.bar(['S0 – nền','S1 – direct BHP'],[48678,24307.5],color=['#2F6B9A','#C44E52'],width=.58); ax.set_ylabel('Gói TCP hợp pháp nhận được'); ax.set_title('Tác động của direct control-only BHP'); ax.grid(axis='y',alpha=.25); ax.bar_label(bars,labels=['48.678','24.307,5'],padding=5,fontweight='bold'); ax.text(.5,-.15,'Khoảng mô tả trên 8 seed cố định',transform=ax.transAxes,ha='center',fontsize=9); fig.tight_layout(); fig.savefig(fig1,bbox_inches='tight'); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.1,5.1),dpi=180); bars=ax.bar(['S0','S1','S2-rate-limit','S2-isolation'],[48678,24307.5,48678,48678],color=['#2F6B9A','#C44E52','#55A868','#8172B3'],width=.65); ax.set_ylabel('Gói TCP hợp pháp nhận được'); ax.set_title('Hai chế độ kiểm soát direct-BHP'); ax.grid(axis='y',alpha=.25); ax.bar_label(bars,labels=['48.678','24.307,5','48.678','48.678'],padding=5,fontsize=9,fontweight='bold'); ax.text(.5,-.15,'8 seed cố định; S2 đạt 100% mức S0',transform=ax.transAxes,ha='center',fontsize=8.5); fig.tight_layout(); fig.savefig(fig2,bbox_inches='tight'); plt.close(fig)

def replace_media(path,mapping):
    tmp=path.with_suffix('.tmp.docx')
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist(): zout.writestr(item, mapping.get(item.filename, zin.read(item.filename)))
    os.replace(tmp,path)
doc.save(out)
with zipfile.ZipFile(out) as z:
    media = [n for n in z.namelist() if n.startswith("word/media/")]
if "word/media/image26.png" in media and "word/media/image29.png" in media:
    replace_media(out, {"word/media/image26.png": fig1.read_bytes(), "word/media/image29.png": fig2.read_bytes()})
# Create the review copy. Differences against the packaged baseline are highlighted;
# the explicitly rebuilt thesis sections/tables are also marked unconditionally so
# the review artifact remains useful when the packaged baseline is already the
# corrected final document.
new=Document(out); old=Document(src)
oldp=[p.text for p in old.paragraphs]; oldt=[[[c.text for c in r.cells] for r in t.rows] for t in old.tables]
explicit_paragraphs = set(repl)
for i,p in enumerate(new.paragraphs):
    if p.text and (i in explicit_paragraphs or i>=len(oldp) or p.text!=oldp[i]):
        for r in p.runs: r.font.highlight_color=WD_COLOR_INDEX.YELLOW
for ti,t in enumerate(new.tables):
    for ri,row in enumerate(t.rows):
        for ci,c in enumerate(row.cells):
            ov=oldt[ti][ri][ci] if ti<len(oldt) and ri<len(oldt[ti]) and ci<len(oldt[ti][ri]) else None
            if c.text and (ti in {3, 4, 7} or c.text!=ov):
                for p in c.paragraphs:
                    for r in p.runs: r.font.highlight_color=WD_COLOR_INDEX.YELLOW
                tcPr=c._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),'FFF2CC'); tcPr.append(shd)
new.save(high)
print(out); print(high)
