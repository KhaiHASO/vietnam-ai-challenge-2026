import Image from "next/image";
import Link from "next/link";
import styles from "./CropDoctorLanding.module.scss";

const navItems = [
  ["Problems", "#problem"],
  ["Solution", "#solution"],
  ["Agents", "#agents"],
  ["Demo Flow", "#demo"],
];

const featureTiles = [
  {
    title: "Vision Diagnosis",
    text: "Upload a crop image and let AI detect visible disease signs.",
    icon: "ri-camera-lens-line",
  },
  {
    title: "Safe IPM Care",
    text: "Recommendations are checked against Integrated Pest Management principles.",
    icon: "ri-shield-check-line",
  },
  {
    title: "Crop Health Diary",
    text: "Every diagnosis, action plan, log, and 48h reminder is saved.",
    icon: "ri-book-open-line",
  },
];

const problemCards = [
  {
    title: "Diseases are detected too late",
    text: "Early leaf spots and stress signs are easy to miss until infection spreads across the field.",
    icon: "ri-alarm-warning-line",
  },
  {
    title: "Treatment choices can be risky",
    text: "Incorrect pesticide timing or dosage can harm crops, people, soil health, and nearby ecosystems.",
    icon: "ri-shield-flash-line",
  },
  {
    title: "Crop records are scattered",
    text: "Photos, symptoms, weather, treatment notes, and follow-up results rarely live in one diary.",
    icon: "ri-file-list-3-line",
  },
  {
    title: "Farmers need field-ready help",
    text: "Diagnosis support should be fast, mobile-friendly, and useful while the farmer is still in the field.",
    icon: "ri-smartphone-line",
  },
];

const solutionSteps = [
  {
    title: "Upload Image",
    text: "Capture the affected leaves, stems, fruit, or whole plant directly from the field.",
    icon: "ri-image-add-line",
  },
  {
    title: "AI Vision",
    text: "PyTorch inference identifies visible disease patterns and an initial confidence signal.",
    icon: "ri-eye-line",
  },
  {
    title: "Symptom Questions",
    text: "The agent collects spread, severity, affected parts, and recent field conditions.",
    icon: "ri-question-answer-line",
  },
  {
    title: "Weather Context",
    text: "Crop type, location, humidity, rain, and farm notes help reduce one-shot diagnosis errors.",
    icon: "ri-cloud-line",
  },
  {
    title: "IPM Recommendation",
    text: "Reasoning and Safety Agents turn evidence into practical, lower-risk crop care steps.",
    icon: "ri-seedling-line",
  },
  {
    title: "48h Follow-up",
    text: "The case, agent logs, treatment plan, and reminder become part of the crop health diary.",
    icon: "ri-notification-3-line",
  },
];

const agents = [
  {
    name: "Vision Agent",
    text: "Analyzes uploaded crop images and detects visible disease signs.",
    icon: "ri-eye-line",
  },
  {
    name: "Symptom Agent",
    text: "Asks farmers about spread, affected leaves, stems, fruit, and field conditions.",
    icon: "ri-question-answer-line",
  },
  {
    name: "Context Agent",
    text: "Uses farm context, crop type, location, and weather to support diagnosis.",
    icon: "ri-cloud-line",
  },
  {
    name: "Reasoning Agent",
    text: "Combines image results, symptoms, and context to generate a likely diagnosis.",
    icon: "ri-brain-line",
  },
  {
    name: "Safety Agent",
    text: "Checks recommendations against safe IPM principles and avoids risky chemical advice.",
    icon: "ri-shield-check-line",
  },
  {
    name: "Diary Agent",
    text: "Saves the diagnosis, treatment plan, agent logs, and follow-up reminders.",
    icon: "ri-calendar-check-line",
  },
];

const highlights = [
  ["AI-native workflow", "Multi-step diagnosis flow powered by specialized agents.", "ri-flow-chart"],
  ["PyTorch inference", "Image classification and disease recognition using a trained model.", "ri-cpu-line"],
  ["DeepSeek reasoning", "Reasoning support for diagnosis explanation and treatment suggestions.", "ri-brain-line"],
  ["IPM safety guardrails", "Safer recommendations based on Integrated Pest Management principles.", "ri-shield-keyhole-line"],
  ["Agent logs and audit trace", "Transparent workflow logs for demo, review, and debugging.", "ri-file-list-3-line"],
  ["Crop care reminders", "Follow-up reminders after 48 hours to check crop recovery.", "ri-notification-3-line"],
];

const demoFlow = [
  "Select a farm",
  "Upload crop image",
  "Enter symptoms",
  "AI generates diagnosis",
  "Save crop case",
  "View agent logs",
];

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <span className={styles.sectionLabel}>
      <i className="ri-leaf-line"></i>
      {children}
    </span>
  );
}

export default function CropDoctorLanding() {
  return (
    <main className={styles.page}>
      <nav className={styles.nav} aria-label="CropDoctor AI navigation">
        <div className={`container ${styles.navInner}`}>
          <Link href="/" className={styles.brand}>
            <span className={styles.brandMark}>
              <i className="ri-plant-line"></i>
            </span>
            <span>CropDoctor AI</span>
          </Link>

          <div className={styles.navLinks}>
            {navItems.map(([label, href]) => (
              <Link href={href} className={styles.navLink} key={href}>
                {label}
              </Link>
            ))}
          </div>

          <Link href="/diagnosis/new" className={styles.navButton}>
            Try Diagnosis
            <i className="ri-arrow-right-up-line"></i>
          </Link>
        </div>
      </nav>

      <section className={styles.hero} id="hero">
        <div className={styles.heroImage}>
          <Image
            src="/images/cropdoctor/dashboard-overview.png"
            alt="CropDoctor AI dashboard overview"
            fill
            priority
            sizes="100vw"
          />
        </div>
        <div className={styles.heroOverlay}></div>
        <div className={styles.heroLines} aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>

        <div className="container position-relative">
          <div className={styles.heroContent}>
            <div className={styles.heroKicker}>
              <i className="ri-leaf-line"></i>
              AI-powered crop diagnosis and plant care assistant for farmers
            </div>
            <h1>AI Crop Diagnosis for Healthier Farms</h1>
            <p>
              CropDoctor AI helps farmers upload crop images, describe symptoms, receive AI-assisted diagnosis,
              get safer IPM recommendations, save records, and schedule follow-up care.
            </p>
            <div className={styles.heroActions}>
              <Link href="/diagnosis/new" className={styles.primaryButton}>
                Try Diagnosis
                <i className="ri-microscope-line"></i>
              </Link>
              <Link href="/diagnosis/history" className={styles.secondaryButton}>
                View Diagnosis History
                <i className="ri-history-line"></i>
              </Link>
            </div>
          </div>

          <div className={styles.heroConsole} aria-label="CropDoctor AI diagnosis preview">
            <div className={styles.consoleImage}>
              <Image
                src="/images/cropdoctor/new-diagnosis.png"
                alt="CropDoctor AI new diagnosis screen"
                width={920}
                height={580}
                sizes="(max-width: 991px) 100vw, 54vw"
              />
            </div>
            <div className={styles.consolePanel}>
              <span>Likely diagnosis</span>
              <strong>Tomato leaf blight</strong>
              <small>Safety Agent approved IPM-first actions.</small>
            </div>
            <div className={styles.followBadge}>
              <i className="ri-notification-3-line"></i>
              48h follow-up
            </div>
          </div>
        </div>
      </section>

      <section className={styles.featureStrip} aria-label="CropDoctor AI key capabilities">
        <div className="container">
          <div className="row g-3">
            {featureTiles.map((item) => (
              <div className="col-md-4" key={item.title}>
                <article className={styles.featureTile}>
                  <span>
                    <i className={item.icon}></i>
                  </span>
                  <h2>{item.title}</h2>
                  <p>{item.text}</p>
                </article>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.aboutSection} id="problem">
        <div className="container">
          <div className="row g-4 g-xl-5 align-items-center">
            <div className="col-lg-5">
              <div className={styles.organicImageCard}>
                <Image
                  src="/images/cropdoctor/diagnosis-history.png"
                  alt="CropDoctor AI diagnosis history"
                  width={900}
                  height={620}
                  sizes="(max-width: 991px) 100vw, 40vw"
                />
                <div className={styles.roundStamp}>
                  <strong>Traceable</strong>
                  <span>AI Workflow</span>
                </div>
              </div>
            </div>

            <div className="col-lg-7">
              <SectionLabel>Why farmers need it</SectionLabel>
              <h2 className={styles.sectionTitle}>Why Farmers Need Faster Crop Diagnosis</h2>
              <p className={styles.sectionText}>
                Crop diseases move faster than paperwork. Farmers need a clear, field-ready way to identify problems,
                choose safer actions, and keep useful records for the next visit.
              </p>

              <div className={styles.problemGrid}>
                {problemCards.map((item) => (
                  <article className={styles.problemCard} key={item.title}>
                    <span className={styles.iconCircle}>
                      <i className={item.icon}></i>
                    </span>
                    <div>
                      <h3>{item.title}</h3>
                      <p>{item.text}</p>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={`${styles.section} ${styles.sectionSoft}`} id="solution">
        <div className="container">
          <div className={styles.sectionHeader}>
            <SectionLabel>How CropDoctor AI helps</SectionLabel>
            <h2 className={styles.sectionTitle}>From Field Photo to Safer Crop Care</h2>
            <p className={styles.sectionText}>
              Inspired by an organic farm service flow, each step is simple for farmers and traceable for judges.
            </p>
          </div>

          <div className={styles.processGrid}>
            {solutionSteps.map((step, index) => (
              <article className={styles.processCard} key={step.title}>
                <span className={styles.processNumber}>{String(index + 1).padStart(2, "0")}</span>
                <div className={styles.processIcon}>
                  <i className={step.icon}></i>
                </div>
                <h3>{step.title}</h3>
                <p>{step.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.section} id="agents">
        <div className="container">
          <div className={styles.sectionHeader}>
            <SectionLabel>Agent workflow</SectionLabel>
            <h2 className={styles.sectionTitle}>Six Specialized Agents Working Together</h2>
            <p className={styles.sectionText}>
              A clean AI pipeline gives the product a strong technical story without overwhelming farmers.
            </p>
          </div>

          <div className={styles.agentGrid}>
            {agents.map((agent, index) => (
              <article className={styles.agentCard} key={agent.name}>
                <span className={styles.agentIndex}>{index + 1}</span>
                <span className={styles.iconCircle}>
                  <i className={agent.icon}></i>
                </span>
                <h3>{agent.name}</h3>
                <p>{agent.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.ecoBand}>
        <div className="container">
          <div className={styles.ecoContent}>
            <SectionLabel>Built for AI-native crop care</SectionLabel>
            <h2>Modern agriculture, safer recommendations, and a traceable AI diary.</h2>
            <Link href="/diagnosis/new" className={styles.lightButton}>
              Start Diagnosis Now
              <i className="ri-arrow-right-line"></i>
            </Link>
          </div>
        </div>
      </section>

      <section className={`${styles.section} ${styles.sectionSoft}`} id="features">
        <div className="container">
          <div className={styles.sectionHeader}>
            <SectionLabel>Product highlights</SectionLabel>
            <h2 className={styles.sectionTitle}>Built for Competition-Ready Crop Care</h2>
            <p className={styles.sectionText}>
              The page stays farmer-friendly while still surfacing the AI engineering details judges care about.
            </p>
          </div>

          <div className="row g-3 g-lg-4">
            {highlights.map(([title, text, icon]) => (
              <div className="col-md-6 col-xl-4" key={title}>
                <article className={styles.highlightCard}>
                  <span className={styles.iconCircle}>
                    <i className={icon}></i>
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
            <SectionLabel>Judge-friendly walkthrough</SectionLabel>
            <h2 className={styles.sectionTitle}>Demo Flow</h2>
            <p className={styles.sectionText}>
              A short, predictable journey helps judges understand the product in minutes.
            </p>
          </div>

          <div className={styles.demoFlow}>
            {demoFlow.map((step, index) => (
              <article className={styles.demoStep} key={step}>
                <span>{index + 1}</span>
                <h3>{step}</h3>
              </article>
            ))}
          </div>

          <div className={styles.demoScreens}>
            <div className={styles.screenFrame}>
              <Image
                src="/images/cropdoctor/agent-logs.png"
                alt="CropDoctor AI agent log preview"
                width={1440}
                height={900}
                sizes="(max-width: 991px) 100vw, 48vw"
              />
            </div>
            <div className={styles.screenFrame}>
              <Image
                src="/images/cropdoctor/ipm-recommendations.png"
                alt="CropDoctor AI IPM recommendation preview"
                width={1440}
                height={900}
                sizes="(max-width: 991px) 100vw, 48vw"
              />
            </div>
          </div>
        </div>
      </section>

      <section className={styles.ctaBand}>
        <div className="container">
          <div className={styles.ctaContent}>
            <SectionLabel>Ready for the first case</SectionLabel>
            <h2>Start Your First Crop Diagnosis</h2>
            <p>Help farmers detect crop problems earlier, choose safer actions, and track plant recovery with AI.</p>
            <Link href="/diagnosis/new" className={styles.primaryButton}>
              Start Diagnosis Now
              <i className="ri-arrow-right-line"></i>
            </Link>
          </div>
        </div>
      </section>

      <footer className={styles.footer}>
        <div className="container d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
          <span>CropDoctor AI - Vietnam AI Challenge 2026</span>
          <Link href="/diagnosis/history">View Diagnosis History</Link>
        </div>
      </footer>
    </main>
  );
}
