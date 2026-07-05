import Image from "next/image";
import Link from "next/link";
import styles from "./CropDoctorLanding.module.scss";

const problemCards = [
  {
    title: "Phát hiện bệnh cây muộn",
    text: "Triệu chứng nhỏ trên lá thường bị bỏ qua cho đến khi bệnh lan rộng trong vườn.",
    icon: "ri-alarm-warning-line",
  },
  {
    title: "Dễ dùng thuốc sai cách",
    text: "Quyết định xử lý phụ thuộc kinh nghiệm rời rạc, dễ phun quá liều hoặc sai thời điểm.",
    icon: "ri-flask-line",
  },
  {
    title: "Thiếu nhật ký mùa vụ",
    text: "Ảnh bệnh, triệu chứng, khuyến nghị và lần xử lý sau không được lưu theo một hồ sơ chuẩn.",
    icon: "ri-book-open-line",
  },
  {
    title: "Chậm hỗ trợ tại ruộng",
    text: "Nông hộ cần một công cụ chẩn đoán nhanh ngay khi phát hiện dấu hiệu bất thường.",
    icon: "ri-smartphone-line",
  },
];

const solutionSteps = [
  {
    title: "Upload ảnh cây bệnh",
    text: "Nông hộ chụp ảnh lá, quả hoặc thân cây ngay tại ruộng.",
  },
  {
    title: "AI phân tích ảnh",
    text: "PyTorch inference nhận diện dấu hiệu bệnh và độ tin cậy ban đầu.",
  },
  {
    title: "Agent hỏi thêm triệu chứng",
    text: "Symptom Agent bổ sung thời điểm xuất hiện, tốc độ lan, điều kiện chăm sóc.",
  },
  {
    title: "Lấy bối cảnh thời tiết",
    text: "Context Agent xem mưa, độ ẩm và lịch chăm sóc để giảm chẩn đoán sai.",
  },
  {
    title: "Khuyến nghị IPM an toàn",
    text: "Reasoning và Safety Agent ưu tiên biện pháp quản lý dịch hại tổng hợp.",
  },
  {
    title: "Lưu nhật ký, nhắc 48h",
    text: "Diary Agent tạo hồ sơ bệnh án và lịch follow-up sau 48 giờ.",
  },
];

const agents = [
  {
    name: "Vision Agent",
    text: "Đọc ảnh cây bệnh và trích xuất dấu hiệu thị giác.",
    icon: "ri-eye-line",
  },
  {
    name: "Symptom Agent",
    text: "Hỏi thêm triệu chứng để tránh kết luận vội.",
    icon: "ri-question-answer-line",
  },
  {
    name: "Context Agent",
    text: "Ghép bối cảnh thời tiết, nông trại và lịch chăm sóc.",
    icon: "ri-cloud-line",
  },
  {
    name: "Reasoning Agent",
    text: "Tổng hợp bằng chứng bằng DeepSeek reasoning.",
    icon: "ri-brain-line",
  },
  {
    name: "Safety Agent",
    text: "Chặn khuyến nghị rủi ro, ưu tiên IPM an toàn.",
    icon: "ri-shield-check-line",
  },
  {
    name: "Diary Agent",
    text: "Lưu bệnh án, agent logs và lịch nhắc chăm sóc.",
    icon: "ri-calendar-check-line",
  },
];

const highlights = [
  ["AI-native workflow", "Luồng chẩn đoán được thiết kế quanh agent, log và truy vết."],
  ["PyTorch inference", "Mô hình thị giác chạy inference cho ảnh bệnh cây."],
  ["DeepSeek reasoning", "Lớp suy luận tổng hợp ảnh, triệu chứng và bối cảnh."],
  ["Safety guardrail IPM", "Khuyến nghị ưu tiên an toàn sinh học trước hóa chất."],
  ["Agent logs/audit trace", "Mỗi bước agent đều có dấu vết để giải thích với giám khảo."],
  ["Reminder chăm sóc", "Tự tạo lịch kiểm tra lại sau 48 giờ cho từng ca bệnh."],
];

const demoFlow = [
  "Chọn nông trại",
  "Upload ảnh",
  "Nhập triệu chứng",
  "AI chẩn đoán",
  "Lưu bệnh án",
  "Xem agent logs",
];

export default function CropDoctorLanding() {
  return (
    <main className={styles.page}>
      <nav className={styles.nav} aria-label="CropDoctor AI navigation">
        <div className={`container d-flex align-items-center justify-content-between ${styles.navInner}`}>
          <Link href="/" className="d-inline-flex align-items-center gap-2 text-decoration-none">
            <span className={styles.brandMark}>
              <i className="ri-plant-line"></i>
            </span>
            <span className={styles.brandText}>CropDoctor AI</span>
          </Link>

          <div className={`d-flex align-items-center gap-4 ${styles.navLinks}`}>
            <Link href="#problem" className={styles.navLink}>
              Vấn đề
            </Link>
            <Link href="#solution" className={styles.navLink}>
              Giải pháp
            </Link>
            <Link href="#agents" className={styles.navLink}>
              6 Agent
            </Link>
            <Link href="#demo" className={styles.navLink}>
              Demo flow
            </Link>
          </div>

          <Link href="/diagnosis/new" className={styles.primaryButton}>
            Dùng thử
            <i className="ri-arrow-right-line"></i>
          </Link>
        </div>
      </nav>

      <section className={styles.hero} id="hero">
        <div className={styles.heroImage}>
          <Image
            src="/images/cropdoctor/dashboard-overview.png"
            alt="Giao diện tổng quan CropDoctor AI"
            fill
            priority
            sizes="100vw"
          />
        </div>
        <div className={styles.heroOverlay}></div>
        <div className={styles.heroPattern}></div>

        <div className="container position-relative">
          <div className={styles.eyebrow}>
            <i className="ri-sparkling-2-line"></i>
            AI-native crop diagnosis for Vietnam AI Challenge 2026
          </div>
          <h1 className={styles.heroTitle}>CropDoctor AI</h1>
          <p className={styles.heroLead}>
            Trợ lý AI chẩn đoán và chăm sóc cây trồng cho nông hộ: từ ảnh bệnh cây,
            triệu chứng, thời tiết đến khuyến nghị IPM an toàn và nhật ký theo dõi.
          </p>

          <div className={styles.heroActions}>
            <Link href="/diagnosis/new" className={styles.primaryButton}>
              Dùng thử chẩn đoán
              <i className="ri-microscope-line"></i>
            </Link>
            <Link href="/diagnosis/history" className={styles.secondaryButton}>
              Xem lịch sử chẩn đoán
              <i className="ri-history-line"></i>
            </Link>
          </div>

          <div className={styles.heroStats} aria-label="Điểm mạnh chính của CropDoctor AI">
            <div className={styles.heroStat}>
              <strong>6 Agent</strong>
              <span>Vision, Symptom, Context, Reasoning, Safety, Diary</span>
            </div>
            <div className={styles.heroStat}>
              <strong>48h</strong>
              <span>Follow-up tự động cho ca cần theo dõi</span>
            </div>
            <div className={styles.heroStat}>
              <strong>IPM</strong>
              <span>Guardrail an toàn trước khuyến nghị xử lý</span>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.section} id="problem">
        <div className="container">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>Vấn đề</span>
            <h2 className={styles.sectionTitle}>Bệnh cây không chờ nông hộ kịp hỏi chuyên gia.</h2>
            <p className={styles.sectionText}>
              CropDoctor AI tập trung vào những điểm nghẽn rất thật ở ruộng: phát hiện muộn,
              xử lý thiếu căn cứ và không có hồ sơ theo dõi sau chẩn đoán.
            </p>
          </div>

          <div className="row g-3 g-lg-4">
            {problemCards.map((item) => (
              <div className="col-md-6 col-xl-3" key={item.title}>
                <article className={styles.problemCard}>
                  <span className={styles.iconBadge}>
                    <i className={item.icon}></i>
                  </span>
                  <h3>{item.title}</h3>
                  <p>{item.text}</p>
                </article>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className={`${styles.section} ${styles.sectionSoft}`} id="solution">
        <div className="container">
          <div className="row g-4 g-xl-5 align-items-center">
            <div className="col-lg-6">
              <div className={styles.sectionKicker}>Giải pháp</div>
              <h2 className={styles.sectionTitle}>Một ca bệnh đi qua ảnh, agent và nhật ký chăm sóc.</h2>
              <p className={styles.sectionText}>
                Thay vì chỉ trả về một nhãn bệnh, hệ thống gom đủ bằng chứng để đưa ra chẩn đoán
                có thể giải thích, an toàn hơn và theo dõi được sau demo.
              </p>

              <div className={`mt-4 ${styles.timeline}`}>
                {solutionSteps.map((step, index) => (
                  <div className={styles.timelineItem} key={step.title}>
                    <span className={styles.timelineNumber}>{index + 1}</span>
                    <div>
                      <h3>{step.title}</h3>
                      <p>{step.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="col-lg-6">
              <div className={styles.solutionImage}>
                <Image
                  src="/images/cropdoctor/new-diagnosis.png"
                  alt="Màn hình chẩn đoán mới của CropDoctor AI"
                  width={1440}
                  height={900}
                  sizes="(max-width: 991px) 100vw, 50vw"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.section} id="agents">
        <div className="container">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>Quy trình 6 Agent</span>
            <h2 className={styles.sectionTitle}>Pipeline AI có trace rõ ràng cho từng quyết định.</h2>
            <p className={styles.sectionText}>
              Mỗi agent phụ trách một phần bằng chứng, giúp phần demo không chỉ đẹp mà còn có câu chuyện kỹ thuật thuyết phục.
            </p>
          </div>

          <div className={styles.agentGrid}>
            {agents.map((agent, index) => (
              <article className={styles.agentCard} key={agent.name}>
                <span className={styles.agentStep}>Agent {index + 1}</span>
                <div className={`${styles.iconBadge} mt-3`}>
                  <i className={agent.icon}></i>
                </div>
                <h3>{agent.name}</h3>
                <p>{agent.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className={`${styles.section} ${styles.sectionSoft}`}>
        <div className="container">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>Điểm nổi bật</span>
            <h2 className={styles.sectionTitle}>Đủ rõ cho người ngoài, đủ sâu cho ban giám khảo.</h2>
          </div>

          <div className="row g-3 g-lg-4">
            {highlights.map(([title, text], index) => (
              <div className="col-md-6 col-xl-4" key={title}>
                <article className={styles.featureCard}>
                  <span className={styles.iconBadge}>
                    <i
                      className={
                        [
                          "ri-flow-chart",
                          "ri-cpu-line",
                          "ri-brain-line",
                          "ri-shield-keyhole-line",
                          "ri-file-list-3-line",
                          "ri-notification-3-line",
                        ][index]
                      }
                    ></i>
                  </span>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </article>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.section} id="demo">
        <div className="container">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>Demo flow</span>
            <h2 className={styles.sectionTitle}>Một đường chạy ngắn, dễ trình bày trong phòng thi.</h2>
            <p className={styles.sectionText}>
              Người xem thấy ngay app hoạt động từ chọn nông trại đến agent logs, không cần backend phức tạp để hiểu giá trị.
            </p>
          </div>

          <div className={styles.demoGrid}>
            <div className={styles.demoList}>
              {demoFlow.map((item, index) => (
                <article className={styles.demoCard} key={item}>
                  <span className={styles.demoIndex}>{index + 1}</span>
                  <div>
                    <h3>{item}</h3>
                    <p>
                      {index === 5
                        ? "Mở trace để xem Vision, Symptom, Context, Reasoning, Safety và Diary Agent đã làm gì."
                        : "Một bước rõ ràng trong luồng chẩn đoán để ban giám khảo dễ theo dõi."}
                    </p>
                  </div>
                </article>
              ))}
            </div>

            <div className={styles.demoScreens}>
              <div className={styles.screenFrame}>
                <Image
                  src="/images/cropdoctor/agent-logs.png"
                  alt="Màn hình nhật ký Agent của CropDoctor AI"
                  width={1440}
                  height={900}
                  sizes="(max-width: 991px) 100vw, 55vw"
                />
              </div>
              <div className={styles.screenFrame}>
                <Image
                  src="/images/cropdoctor/ipm-recommendations.png"
                  alt="Màn hình khuyến nghị IPM của CropDoctor AI"
                  width={1440}
                  height={900}
                  sizes="(max-width: 991px) 100vw, 55vw"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.ctaBand}>
        <div className="container">
          <div className={styles.ctaContent}>
            <div>
              <h2>Bắt đầu chẩn đoán cây trồng ngay.</h2>
              <p>
                CropDoctor AI giúp nông hộ có một quy trình chẩn đoán nhanh, có giải thích,
                có guardrail an toàn và có nhật ký để theo dõi sau 48 giờ.
              </p>
            </div>
            <Link href="/diagnosis/new" className={styles.primaryButton}>
              Bắt đầu chẩn đoán ngay
              <i className="ri-arrow-right-line"></i>
            </Link>
          </div>
        </div>
      </section>

      <footer className={styles.footer}>
        <div className="container d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
          <span>CropDoctor AI - Vietnam AI Challenge 2026</span>
          <Link href="/diagnosis/history" className="text-white text-decoration-none">
            Xem lịch sử chẩn đoán
          </Link>
        </div>
      </footer>
    </main>
  );
}
