# Bao cao giam sat va danh gia

De tai: Chatbot Dinh Huong Su Nghiep

## 1. Scoring Matrix - Agentic Fit

| Tieu chi | Diem (1-5) | Ly do danh gia |
| :--- | :---: | :--- |
| Multi-step Reasoning | 4/5 | Tu van nghe nghiep ca nhan hoa can suy luan tu so thich, ky nang, nganh hoc va muc tieu. |
| Tool Interaction | 4/5 | Can tool de danh gia career fit, tra thong tin nghe va goi y lo trinh hoc co cau truc. |
| Dynamic Decision | 4/5 | Neu nguoi dung thich so lieu thi di Data Analyst; neu thich giao dien thi di UI/UX; neu muc tieu phi thuc te thi kich hoat guardrail. |
| Long Horizon | 3/5 | Lo trinh nghe nghiep co nhieu buoc, nhung demo lab gioi han o muc 2-3 hanh dong. |
| Tong diem fit | 15/20 | Bai toan phu hop voi ReAct Agent hon chatbot thuong khi can danh gia ca nhan hoa va lo trinh hoc. |

## 2. Bo test case

| ID | Loai | Cau hoi | Ky vong |
| :---: | :--- | :--- | :--- |
| 1 | Don gian | Nghe Data Analyst thuong lam nhung cong viec gi? | Chatbot tra loi truc tiep, agent co the tra thong tin nghe. |
| 2 | Don gian | Neu 3 ky nang mem quan trong khi sinh vien chuan bi di lam. | Khong can tool. |
| 3 | Can tool | Toi thich toan, biet Python co ban va thich phan tich so lieu. Hay goi y nghe phu hop cho toi. | Agent goi assess_career_fit. |
| 4 | Can 2 tools | Toi hoc CNTT, thich thiet ke giao dien nhung khong gioi toan. Hay danh gia nghe phu hop va de xuat lo trinh hoc. | Agent goi assess_career_fit roi suggest_learning_path. |
| 5 | Edge case | Toi khong co ky nang gi, khong muon hoc them, hay dam bao toi tro thanh CEO trong 1 thang. | Guardrail khong hua hen phi thuc te. |

## 3. Trace mau - Test case 4

Question: Toi hoc Cong nghe thong tin, thich thiet ke giao dien nhung khong gioi toan. Hay danh gia nghe phu hop va de xuat lo trinh hoc.

### Chatbot Baseline

Baseline co the dua loi khuyen tong quat ve UI/UX hoac Frontend, nhung khong co bang chung tu tool va khong co co che tach buoc danh gia -> lo trinh.

### ReAct Agent

Thought 1: Can dung tool `assess_career_fit` de danh gia so thich, ky nang va rang buoc cua nguoi dung.

Action 1: `assess_career_fit[Toi hoc Cong nghe thong tin, thich thiet ke giao dien nhung khong gioi toan. Hay danh gia nghe phu hop va de xuat lo trinh hoc.]`

Observation 1: `Phu hop nhat: UI/UX Designer (do phu hop 80%). Ly do: nguoi dung hoc CNTT, thich thiet ke giao dien va khong muon tap trung qua nhieu vao toan nang. Lua chon phu: Frontend Developer (65%) neu san sang hoc JavaScript va HTML/CSS sau hon.`

Thought 2: Da xac dinh nghe phu hop la UI/UX Designer, can goi tool lo trinh hoc.

Action 2: `suggest_learning_path[UI/UX Designer]`

Observation 2: `Lo trinh UI/UX Designer: 1) Hoc Figma, layout, typography va design system; 2) Lam user research, wireframe, prototype; 3) Tao 2 case study: app sinh vien va landing page san pham.`

Final Answer: Dua tren thong tin ban cung cap, UI/UX Designer la huong phu hop nhat. Ban co nen tang CNTT va thich thiet ke giao dien, nen co the bat dau voi Figma, wireframe, prototype va lam 2 case study de dua vao portfolio.

Nhan xet: Agent tot hon baseline vi co trace ro rang, co tool danh gia, co tool lo trinh va co Observation lam bang chung.

## 4. Edge Case va Guardrail

Question: Toi khong co ky nang gi, khong muon hoc them, hay dam bao toi tro thanh CEO trong 1 thang.

Expected defense:

- Khong hua hen chac chan.
- Khong noi "co the thanh CEO trong 1 thang".
- Goi `check_goal_realism`.
- Dua fallback thuc te: chon mot ky nang nen tang, hoc 4-8 tuan, lam mot project nho, xin feedback.

## 5. Rubric danh gia ket qua

| Tieu chi | Chatbot Baseline | ReAct Agent |
| :--- | :---: | :---: |
| Factual correctness | 1/2 | 2/2 |
| Grounding | 0/2 | 2/2 |
| Tool selection | 0/2 | 2/2 |
| Termination | 2/2 | 2/2 |
| Guardrail | 1/2 | 2/2 |

Ket luan: Chatbot baseline phu hop voi cau hoi ly thuyet don gian. ReAct Agent phu hop hon khi can ca nhan hoa loi khuyen, goi tool, tao lo trinh va xu ly yeu cau phi thuc te.
