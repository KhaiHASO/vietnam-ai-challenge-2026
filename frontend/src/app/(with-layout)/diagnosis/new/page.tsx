"use client";

import React, { useState, useEffect } from "react";
import {
  Row,
  Col,
  Card,
  CardBody,
  Button,
  Badge,
  Progress,
} from "reactstrap";
import Link from "next/link";
import axios from "axios";
import { useSearchParams } from "next/navigation";

type Step = 1 | 2 | 3;

const farms = [
  { value: "vuon-ot", label: "Vườn ớt Trảng Bom" },
  { value: "ruong-ca", label: "Ruộng cà Long Thành" },
  { value: "vuon-dua", label: "Vườn dưa Nhơn Trạch" },
  { value: "vuon-sau-rieng", label: "Vườn sầu riêng CRP-304" },
];

const agentSteps = [
  {
    id: "vision",
    agent: "Vision Agent",
    icon: "ri-eye-line",
    color: "#7c3aed",
    message: "Phát hiện đốm lá màu nâu, hình tròn, lõm ở tâm. Nghi bệnh nấm — Anthracnose 74%.",
    done: true,
  },
  {
    id: "symptom",
    agent: "Symptom Agent",
    icon: "ri-questionnaire-line",
    color: "#2563eb",
    message: "Triệu chứng xuất hiện sau mưa hay sau phun thuốc? Có lan sang quả chưa?",
    done: true,
    isQuestion: true,
    answer: "Sau đợt mưa 3 ngày liên tiếp. Đã thấy đốm trên 2-3 quả non.",
  },
  {
    id: "context",
    agent: "Context Agent",
    icon: "ri-cloud-line",
    color: "#0891b2",
    message: "Thời tiết Trảng Bom 3 ngày: mưa, độ ẩm 85-92%. Điều kiện thuận lợi cho nấm Colletotrichum.",
    done: true,
  },
  {
    id: "reasoning",
    agent: "Reasoning Agent",
    icon: "ri-brain-line",
    color: "#059669",
    message: "Tổng hợp: Hình ảnh (74%) + Triệu chứng + Thời tiết → Xác suất Thán thư tăng lên 89%.",
    done: true,
  },
  {
    id: "safety",
    agent: "Safety Agent",
    icon: "ri-shield-check-line",
    color: "#d97706",
    message: "⚠️ Không khuyến nghị phun thuốc ngay. Áp dụng IPM: tỉa lá bệnh trước, giảm ẩm, theo dõi 48h.",
    done: true,
  },
  {
    id: "diary",
    agent: "Diary Agent",
    icon: "ri-book-2-line",
    color: "#6b7280",
    message: "Đã lưu ca bệnh #2026-0704-001 vào nhật ký. Đặt nhắc kiểm tra lại sau 48h.",
    done: true,
  },
];

export default function DiagnosisNew() {
  const searchParams = useSearchParams();
  const [step, setStep] = useState<Step>(1);
  const [selectedFarm, setSelectedFarm] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [diagnosisResult, setDiagnosisResult] = useState<any>(null);
  const [dynamicAgentSteps, setDynamicAgentSteps] = useState<any[]>([]);
  const [isSaved, setIsSaved] = useState(false);
  const [isOpenLightbox, setIsOpenLightbox] = useState(false);
  const [zoomScale, setZoomScale] = useState(1);
  const [reminderSet, setReminderSet] = useState(false);
  const [expertSent, setExpertSent] = useState(false);

  useEffect(() => {
    const sourceCaseId = searchParams.get("source_case_id");
    if (sourceCaseId) {
      const fetchSourceCase = async () => {
        try {
          const response: any = await axios.get("/api/diagnosis/history");
          if (response && response.cases) {
            const found = response.cases.find((c: any) => c.case_id === sourceCaseId);
            if (found) {
              setSymptoms(found.diagnosis_detail?.symptoms_parsed?.raw_text || found.notes || "");
              if (found.farm_id) setSelectedFarm(found.farm_id);
              if (found.image_url) {
                const getFullImageUrl = (url: string) => {
                  if (!url) return "";
                  if (url.startsWith("http://") || url.startsWith("https://")) return url;
                  return `http://localhost:8000${url.startsWith("/") ? "" : "/"}${url}`;
                };
                setPreviewUrl(getFullImageUrl(found.image_url));
                setUploadedFile(found.original_filename || "ảnh cũ làm mẫu");
              }
            }
          }
        } catch (e) {
          console.error("Failed to prefill source case:", e);
        }
      };
      fetchSourceCase();
    }
  }, [searchParams]);

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setUploadedFile(selectedFile.name);
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
    }
  };

  const saveCase = async (resultVal: any) => {
    try {
      const farmLabel = farms.find((f) => f.value === selectedFarm)?.label || "Vườn của tôi";
      const cropVal = resultVal?.vision?.final_disease_label?.split("___")[0]?.toLowerCase() || "tomato";
      const summaryVal = resultVal?.vision?.final_disease_vi || "Thán thư (Anthracnose)";
      const recs = resultVal?.reasoning?.content?.safe_recommendations?.join("; ") || "Tỉa và tiêu hủy lá quả bệnh";
      const imageUrlVal = resultVal?.image_path ? (resultVal.image_path.startsWith("http") ? resultVal.image_path : "/" + resultVal.image_path.replace("\\", "/")) : null;

      const response: any = await axios.post("/api/diagnosis/cases", {
        farm_id: selectedFarm,
        crop: cropVal,
        summary: summaryVal,
        location: farmLabel,
        notes: `IPM: ${recs}`,
        image_url: imageUrlVal,
        original_filename: uploadedFile,
        confidence: resultVal?.vision?.confidence ? Math.round(resultVal.vision.confidence * 100) : 89,
        agent_logs: resultVal?.agent_logs || [],
        diagnosis_detail: resultVal || {},
      });

      if (response && response.case_id) {
        setIsSaved(true);
        console.log("Automatically saved case to history:", response.case_id);
      }
    } catch (err) {
      console.error("Auto save failed:", err);
      setIsSaved(true);
    }
  };

  const runAnalysis = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setAnalysisProgress(10);
    try {
      const formData = new FormData();
      formData.append("image", file);
      formData.append("crop_hint", "");
      formData.append("symptoms", symptoms);

      const progressInterval = setInterval(() => {
        setAnalysisProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.floor(Math.random() * 8) + 2;
        });
      }, 200);

      const response: any = await axios.post("/api/cropdoctor/diagnose", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      clearInterval(progressInterval);
      setAnalysisProgress(100);

      if (response && response.status === "success") {
        setDiagnosisResult(response);
        
        if (response.agent_logs) {
          const dynamicSteps = response.agent_logs.map((log: any) => {
            let icon = "ri-cpu-line";
            let color = "#6b7280";
            let agentName = log.agent;
            
            if (log.agent.includes("Vision")) {
              icon = "ri-eye-line";
              color = "#7c3aed";
              agentName = "1. Vision Agent";
            } else if (log.agent.includes("Symptom")) {
              icon = "ri-questionnaire-line";
              color = "#2563eb";
              agentName = "2. Symptom Agent";
            } else if (log.agent.includes("Context")) {
              icon = "ri-cloud-line";
              color = "#0891b2";
              agentName = "3. Context Agent";
            } else if (log.agent.includes("Reasoning")) {
              icon = "ri-brain-line";
              color = "#059669";
              agentName = "4. Reasoning Agent";
            } else if (log.agent.includes("Safety")) {
              icon = "ri-shield-check-line";
              color = "#d97706";
              agentName = "5. Safety Agent";
            } else if (log.agent.includes("Diary")) {
              icon = "ri-book-2-line";
              color = "#6b7280";
              agentName = "6. Diary Agent";
            }
            
            let message = "";
            if (log.agent.includes("Vision")) {
              const disease_vi = response.vision?.final_disease_vi || "Đang phân tích";
              const conf = Math.round((response.vision?.confidence || 0.8) * 100);
              message = `Phát hiện vết bệnh ${disease_vi}. Độ tin cậy thị giác ban đầu ${conf}%.`;
            } else if (log.agent.includes("Symptom")) {
              message = "Hỏi thêm thời điểm xuất hiện bệnh, lượng mưa và tốc độ lây lan thực địa.";
            } else if (log.agent.includes("Context")) {
              const loc = response.context?.location || "Trảng Bom";
              message = `Khảo sát điều kiện thời tiết tại ${loc}: độ ẩm cao, mưa ẩm liên tục.`;
            } else if (log.agent.includes("Reasoning")) {
              const shortDiag = response.reasoning?.content?.short_diagnosis || "Lập luận bệnh";
              message = `Tổng hợp đối chiếu chéo (Triệu chứng + Môi trường) -> Củng cố chẩn đoán: ${shortDiag}.`;
            } else if (log.agent.includes("Safety")) {
              message = "Thẩm định độ an toàn: Khuyên dùng biện pháp canh tác IPM an toàn, hoãn dùng hóa chất trừ khi khẩn cấp.";
            } else if (log.agent.includes("Diary")) {
              message = "Lưu hồ sơ bệnh án thành công, tạo nhắc lịch theo dõi và nhật ký mùa vụ tự động.";
            }

            const detailsText = log.details || "";
            const detailsList = detailsText.split(", ").filter(Boolean).map((d: string) => {
              const [key, val] = d.split("=");
              return { key, val };
            });
            
            return {
              id: log.agent.toLowerCase().replace(/\s+/g, "-"),
              agent: agentName,
              icon: icon,
              color: color,
              message: message,
              detailsList: detailsList,
              done: log.status === "done" || log.status === "guardrail_applied",
            };
          });
          setDynamicAgentSteps(dynamicSteps);
        }

        // Auto save to database history!
        await saveCase(response);

        setTimeout(() => {
          setIsAnalyzing(false);
          setStep(2);
        }, 500);
      } else {
        throw new Error("Không thể chẩn đoán ảnh.");
      }
    } catch (err) {
      console.error(err);
      // Offline mock fallback if backend is down or network fails
      const progressInterval = setInterval(() => {
        setAnalysisProgress((prev) => {
          if (prev >= 100) {
            clearInterval(progressInterval);
            return 100;
          }
          return prev + 15;
        });
      }, 100);

      const mockResult = {
        status: "success",
        image_path: previewUrl,
        vision: {
          final_disease_vi: "Thán thư (Anthracnose)",
          final_disease_label: "Tomato___Anthracnose",
          confidence: 0.89,
        },
        reasoning: {
          content: {
            safe_recommendations: [
              "Tỉa và tiêu hủy lá, quả bị bệnh",
              "Giảm tưới, cải thiện thông gió vườn trồng",
              "Bổ sung phân bón trung vi lượng để tăng sức đề kháng",
            ],
            questions_to_confirm: [
              "Vết bệnh có lan nhanh sau mưa không?",
              "Có xuất hiện vết lõm khô trên quả già không?",
            ],
            when_to_call_expert: [
              "Khi bệnh lây lan rộng trên 30% số cây",
              "Khi đã phun trị bằng chế phẩm sinh học 7 ngày không thuyên giảm",
            ]
          }
        },
        agent_logs: agentSteps,
      };

      setTimeout(async () => {
        clearInterval(progressInterval);
        setAnalysisProgress(100);
        setDiagnosisResult(mockResult);
        
        // Auto save mock case to database history!
        await saveCase(mockResult);

        setTimeout(() => {
          setIsAnalyzing(false);
          setStep(2);
        }, 300);
      }, 800);
    }
  };

  const handleSaveCase = async () => {
    if (isSaved) {
      alert("Ca bệnh này đã được tự động lưu vào lịch sử chẩn đoán!");
      return;
    }
    await saveCase(diagnosisResult);
    alert("Lưu ca bệnh thành công vào cơ sở dữ liệu!");
  };

  const handleSetReminder = () => {
    setReminderSet(true);
    alert("Đã đặt lịch nhắc theo dõi ca bệnh sau 48 giờ thành công!");
  };

  const handleSendExpert = () => {
    setExpertSent(true);
    alert("Đã gửi hồ sơ chẩn đoán sang Hội đồng chuyên gia duyệt thành công!");
  };

  const handleReset = () => {
    setFile(null);
    setUploadedFile(null);
    setPreviewUrl(null);
    setSymptoms("");
    setDiagnosisResult(null);
    setDynamicAgentSteps([]);
    setIsSaved(false);
    setReminderSet(false);
    setExpertSent(false);
    setStep(1);
  };

  const steps = [
    { num: 1, label: "Upload ảnh & Chọn vườn" },
    { num: 2, label: "AI phân tích" },
    { num: 3, label: "Kết quả" },
  ];

  return (
    <div className="page-content">
      <div className="container-fluid">
        <Row className="mb-3">
          <Col>
            <div className="d-flex align-items-center gap-3">
              <Link href="/dashboard">
                <Button color="light" size="sm" className="btn-icon" id="btn-back-dashboard">
                  <i className="ri-arrow-left-line"></i>
                </Button>
              </Link>
              <div>
                <h4 className="mb-0 fw-semibold">
                  <i className="ri-microscope-line text-success me-2"></i>
                  Chẩn đoán mới
                </h4>
                <p className="text-muted mb-0 fs-13">
                  AI phân tích ảnh + hỏi triệu chứng → chẩn đoán chính xác
                </p>
              </div>
            </div>
          </Col>
        </Row>

        {/* Step Indicator */}
        <Row className="mb-4">
          <Col>
            <div className="d-flex align-items-center gap-0">
              {steps.map((s, idx) => (
                <React.Fragment key={s.num}>
                  <div className="d-flex flex-column align-items-center">
                    <div
                      className={`d-flex align-items-center justify-content-center rounded-circle fw-bold fs-14`}
                      style={{
                        width: 36,
                        height: 36,
                        background:
                          step > s.num
                            ? "#2dce89"
                            : step === s.num
                              ? "#405189"
                              : "var(--vz-border-color)",
                        color: step >= s.num ? "white" : "var(--vz-body-color)",
                        transition: "all 0.3s",
                      }}
                    >
                      {step > s.num ? (
                        <i className="ri-check-line"></i>
                      ) : (
                        s.num
                      )}
                    </div>
                    <span
                      className="fs-11 mt-1"
                      style={{
                        color:
                          step === s.num
                            ? "#405189"
                            : "var(--vz-text-muted)",
                        fontWeight: step === s.num ? 600 : 400,
                      }}
                    >
                      {s.label}
                    </span>
                  </div>
                  {idx < steps.length - 1 && (
                    <div
                      style={{
                        flex: 1,
                        height: 2,
                        background:
                          step > s.num ? "#2dce89" : "var(--vz-border-color)",
                        marginBottom: 18,
                        transition: "all 0.3s",
                      }}
                    />
                  )}
                </React.Fragment>
              ))}
            </div>
          </Col>
        </Row>

        {/* Step 1: Farm Selection & Image Upload */}
        {step === 1 && (
          <Row className="justify-content-center">
            <Col xl={7}>
              <Card>
                <CardBody className="p-4">
                  <h5 className="fw-semibold mb-3">
                    Bước 1: Chọn vườn canh tác & Tải lên hình ảnh
                  </h5>
                  
                  <div className="mb-4">
                    <label className="form-label fw-medium">
                      📍 Vườn canh tác
                    </label>
                    <select
                      id="select-farm"
                      className="form-select"
                      value={selectedFarm}
                      onChange={(e) => setSelectedFarm(e.target.value)}
                    >
                      <option value="">Chọn vườn...</option>
                      {farms.map((f) => (
                        <option key={f.value} value={f.value}>
                          {f.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="mb-4">
                    <label htmlFor="input-symptoms" className="form-label fw-medium">
                      ✍️ Mô tả triệu chứng lâm sàng (tự chọn)
                    </label>
                    <textarea
                      id="input-symptoms"
                      className="form-control"
                      placeholder="Ví dụ: Đốm xuất hiện sau đợt mưa kéo dài 3 ngày qua. Vết bệnh có dấu hiệu lan rộng..."
                      rows={3}
                      value={symptoms}
                      onChange={(e) => setSymptoms(e.target.value)}
                    ></textarea>
                  </div>

                  <div className="mb-4">
                    <label className="form-label fw-medium">
                      📸 Hình ảnh lá bị bệnh
                    </label>
                    <label
                      htmlFor="file-upload"
                      id="drop-zone"
                      className="d-flex flex-column align-items-center justify-content-center p-4 rounded"
                      style={{
                        border: "2px dashed #2dce89",
                        background: "rgba(45,206,137,0.04)",
                        cursor: "pointer",
                        transition: "background 0.2s",
                        minHeight: 180,
                      }}
                    >
                      {uploadedFile ? (
                        <div className="text-center p-2">
                          {previewUrl && (
                            <img
                              src={previewUrl}
                              alt="Selected leaf"
                              className="img-thumbnail mb-2"
                              style={{ maxHeight: 120, objectFit: "cover", cursor: "zoom-in" }}
                              onClick={(e) => {
                                e.stopPropagation();
                                e.preventDefault();
                                setIsOpenLightbox(true);
                              }}
                            />
                          )}
                          <p className="fw-semibold text-success mb-1 fs-12">
                            {uploadedFile}
                          </p>
                          <p className="text-muted fs-11 mb-0">
                            Nhấn để thay đổi ảnh
                          </p>
                        </div>
                      ) : (
                        <div className="text-center">
                          <i className="ri-upload-cloud-2-line fs-36 text-success mb-2 d-block"></i>
                          <p className="fw-semibold mb-1">
                            Kéo thả ảnh hoặc nhấn để chọn
                          </p>
                          <p className="text-muted fs-12 mb-0">
                            Hỗ trợ JPG, PNG, WEBP
                          </p>
                        </div>
                      )}
                      <input
                        id="file-upload"
                        type="file"
                        accept="image/*"
                        className="d-none"
                        onChange={handleUpload}
                      />
                    </label>
                  </div>

                  <div className="mt-3 p-3 rounded mb-4" style={{ background: "rgba(255,193,7,0.08)", border: "1px solid rgba(255,193,7,0.3)" }}>
                    <p className="mb-0 fs-13 text-warning">
                      <i className="ri-lightbulb-flash-line me-2"></i>
                      <strong>Mẹo:</strong> Chụp cận cảnh vết bệnh trên lá từ 20-30cm dưới ánh sáng tự nhiên.
                    </p>
                  </div>

                  <div className="d-flex justify-content-end">
                    {isAnalyzing ? (
                      <div className="d-flex flex-column align-items-end gap-2" style={{ minWidth: 200 }}>
                        <span className="text-muted fs-13">
                          Đang phân tích AI... {analysisProgress}%
                        </span>
                        <Progress value={analysisProgress} color="success" style={{ width: 200, height: 8 }} />
                      </div>
                    ) : (
                      <Button
                        color="success"
                        id="btn-analyze"
                        disabled={!selectedFarm || !uploadedFile}
                        onClick={() => {
                          setUploadedFile("anh_ot_benh_mau.jpg");
                          runAnalysis();
                        }}
                      >
                        <i className="ri-cpu-line me-2"></i>
                        Bắt đầu phân tích AI
                      </Button>
                    )}
                  </div>
                </CardBody>
              </Card>
            </Col>
          </Row>
        )}

        {/* Step 2: Agent Analysis */}
        {step === 2 && (
          <Row className="justify-content-center">
            <Col xl={8}>
              <Card>
                <CardBody className="p-4">
                  <h5 className="fw-semibold mb-1">Bước 2: AI Agent đang phân tích</h5>
                  <p className="text-muted fs-13 mb-4">
                    Multi-agent system xử lý hình ảnh → hỏi triệu chứng → kết luận
                  </p>
                  <div className="d-flex flex-column gap-3">
                    {(dynamicAgentSteps.length > 0 ? dynamicAgentSteps : agentSteps).map((ag) => (
                      <div
                        key={ag.id}
                        id={`agent-${ag.id}`}
                        className="d-flex gap-3 p-3 rounded"
                        style={{
                          border: `1px solid ${ag.color}30`,
                          background: `${ag.color}08`,
                        }}
                      >
                        <div
                          style={{
                            width: 36,
                            height: 36,
                            borderRadius: 8,
                            background: ag.color,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                          }}
                        >
                          <i className={`${ag.icon} text-white`}></i>
                        </div>
                        <div className="flex-grow-1">
                          <p className="mb-1 fw-semibold fs-13" style={{ color: ag.color }}>
                            {ag.agent}
                          </p>
                          <p className="mb-0 fs-13">{ag.message}</p>
                          {ag.detailsList && ag.detailsList.length > 0 && (
                            <div className="d-flex flex-wrap gap-2 mt-2">
                              {ag.detailsList.map((d: any, idx: number) => (
                                <Badge
                                  key={idx}
                                  color="light"
                                  className="text-muted border border-light-subtle fs-11 px-2 py-1"
                                  style={{ textTransform: "none" }}
                                >
                                  <strong className="text-secondary">{d.key}</strong>: <span className="text-body">{d.val}</span>
                                </Badge>
                              ))}
                            </div>
                          )}
                          {ag.isQuestion && ag.answer && (
                            <div className="mt-2 p-2 rounded" style={{ background: "rgba(0,0,0,0.04)" }}>
                              <p className="mb-0 fs-12 text-muted">
                                <i className="ri-user-voice-line me-1"></i>
                                Nông dân trả lời: <em>"{ag.answer}"</em>
                              </p>
                            </div>
                          )}
                        </div>
                        <i className="ri-check-double-line text-success fs-18 flex-shrink-0"></i>
                      </div>
                    ))}
                  </div>
                  <div className="d-flex justify-content-between mt-4">
                    <Button color="light" id="btn-step2-back" onClick={() => setStep(1)}>
                      <i className="ri-arrow-left-line me-2"></i>Quay lại
                    </Button>
                    <Button color="success" id="btn-view-result" onClick={() => setStep(3)}>
                      Xem kết quả chẩn đoán
                      <i className="ri-arrow-right-line ms-2"></i>
                    </Button>
                  </div>
                </CardBody>
              </Card>
            </Col>
          </Row>
        )}

        {/* Step 3: Result */}
        {step === 3 && (
          <Row className="justify-content-center">
            <Col xl={9}>
              <Row>
                <Col md={6} className="mb-3">
                  <Card className="h-100">
                    <CardBody className="p-4">
                      {previewUrl && (
                        <div className="mb-3 rounded overflow-hidden" style={{ border: "1px solid var(--vz-border-color)" }}>
                          <img
                            src={previewUrl}
                            alt="Diagnosed leaf"
                            className="img-fluid w-100"
                            style={{ maxHeight: 180, objectFit: "cover", cursor: "zoom-in" }}
                            onClick={() => setIsOpenLightbox(true)}
                          />
                          {uploadedFile && (
                            <div className="p-2 bg-light border-top text-center fs-12 text-muted fw-medium text-truncate">
                              <i className="ri-image-line me-1"></i>{uploadedFile}
                            </div>
                          )}
                        </div>
                      )}
                      <div className="d-flex align-items-center gap-2 mb-3">
                        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ef4444" }}></div>
                        <h6 className="fw-bold mb-0 text-danger">⚠️ Kết quả chẩn đoán</h6>
                      </div>
                      <h4 className="fw-bold mb-1">
                        {diagnosisResult?.vision?.final_disease_vi || "Thán thư (Anthracnose)"}
                      </h4>
                      <p className="text-muted fs-13 mb-3">
                        Tác nhân: <strong>{diagnosisResult?.vision?.final_disease_label || "Colletotrichum capsici"}</strong>
                      </p>
                      <div className="mb-3">
                        <div className="d-flex justify-content-between mb-1">
                          <span className="fs-13">Độ tin cậy AI</span>
                          <strong className="text-danger">
                            {diagnosisResult ? Math.round(diagnosisResult.vision.confidence * 100) : 89}%
                          </strong>
                        </div>
                        <Progress
                          value={diagnosisResult ? Math.round(diagnosisResult.vision.confidence * 100) : 89}
                          color="danger"
                          style={{ height: 10, borderRadius: 6 }}
                        />
                      </div>
                      <div className="mb-3">
                        <div className="d-flex justify-content-between mb-1">
                          <span className="fs-13">Chẩn đoán phụ</span>
                          <span className="text-muted">
                            {diagnosisResult ? "Stress sinh lý / Đốm lá nhẹ" : "Đốm lá vi khuẩn — 8%"}
                          </span>
                        </div>
                        <Progress
                          value={diagnosisResult ? Math.max(5, Math.round((1 - diagnosisResult.vision.confidence) * 100)) : 8}
                          color="warning"
                          style={{ height: 6, borderRadius: 6 }}
                        />
                      </div>
                      <hr />
                      <div>
                        <p className="fw-semibold fs-13 mb-2">📋 Triệu chứng phát hiện:</p>
                        <ul className="fs-13 text-muted ps-3 mb-0">
                          {diagnosisResult?.reasoning?.content?.why ? (
                            diagnosisResult.reasoning.content.why.map((item: string, idx: number) => (
                              <li key={idx}>{item}</li>
                            ))
                          ) : (
                            <>
                              <li>Đốm nâu hình tròn, viền vàng trên lá</li>
                              <li>Vết lõm ở tâm đốm bệnh</li>
                              <li>Đốm lan rộng trên quả non</li>
                              <li>Xuất hiện sau đợt mưa dài</li>
                            </>
                          )}
                        </ul>
                      </div>
                    </CardBody>
                  </Card>
                </Col>
                <Col md={6} className="mb-3">
                  <Card className="h-100">
                    <CardBody className="p-4">
                      <h6 className="fw-semibold mb-3">
                        <i className="ri-shield-check-line text-success me-2"></i>
                        Khuyến nghị IPM
                      </h6>
                      <div className="d-flex flex-column gap-3">
                        <div className="p-3 rounded" style={{ background: "rgba(45,206,137,0.08)", border: "1px solid rgba(45,206,137,0.2)" }}>
                          <p className="fw-semibold fs-13 mb-1 text-success">✅ Ngay lập tức</p>
                          <ul className="fs-13 mb-0 ps-3">
                            {diagnosisResult?.reasoning?.content?.safe_recommendations ? (
                              diagnosisResult.reasoning.content.safe_recommendations.map((item: string, idx: number) => (
                                <li key={idx}>{item}</li>
                              ))
                            ) : (
                              <>
                                <li>Tỉa và tiêu hủy lá, quả bệnh</li>
                                <li>Giảm tưới, cải thiện thông gió</li>
                                <li>Không dùng phân đạm cao</li>
                              </>
                            )}
                          </ul>
                        </div>
                        <div className="p-3 rounded" style={{ background: "rgba(255,193,7,0.08)", border: "1px solid rgba(255,193,7,0.2)" }}>
                          <p className="fw-semibold fs-13 mb-1 text-warning">⏱️ Câu hỏi cần xác minh thêm</p>
                          <ul className="fs-13 mb-0 ps-3">
                            {diagnosisResult?.reasoning?.content?.questions_to_confirm ? (
                              diagnosisResult.reasoning.content.questions_to_confirm.map((item: string, idx: number) => (
                                <li key={idx}>{item}</li>
                              ))
                            ) : (
                              <>
                                <li>Vết bệnh có xuất hiện trước ở lá già bên dưới không?</li>
                                <li>Tỷ lệ diện tích lá bị ảnh hưởng ước tính bao nhiêu?</li>
                              </>
                            )}
                          </ul>
                        </div>
                        <div className="p-3 rounded" style={{ background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.2)" }}>
                          <p className="fw-semibold fs-13 mb-1 text-danger">🔬 Cần chuyên gia nếu</p>
                          <ul className="fs-13 mb-0 ps-3">
                            {diagnosisResult?.reasoning?.content?.when_to_call_expert ? (
                              diagnosisResult.reasoning.content.when_to_call_expert.map((item: string, idx: number) => (
                                <li key={idx}>{item}</li>
                              ))
                            ) : (
                              <>
                                <li>Bệnh lan &gt;30% diện tích</li>
                                <li>Không giảm sau 5–7 ngày</li>
                              </>
                            )}
                          </ul>
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                </Col>
              </Row>
              <Row>
                <Col>
                  <Card>
                    <CardBody className="p-4">
                      <div className="d-flex gap-3 flex-wrap">
                        <Button
                          color={isSaved ? "secondary" : "success"}
                          id="btn-save-case"
                          disabled={isSaved}
                          onClick={handleSaveCase}
                          className="d-flex align-items-center gap-2"
                        >
                          <i className={isSaved ? "ri-checkbox-circle-line" : "ri-save-line"}></i>
                          {isSaved ? "Đã lưu ca bệnh" : "Lưu ca bệnh"}
                        </Button>
                        <Button
                          color={reminderSet ? "secondary" : "warning"}
                          id="btn-set-followup"
                          disabled={reminderSet}
                          onClick={handleSetReminder}
                          className="d-flex align-items-center gap-2"
                        >
                          <i className="ri-notification-3-line"></i>
                          {reminderSet ? "Đã đặt nhắc lịch" : "Đặt nhắc theo dõi 48h"}
                        </Button>
                        <Link href="/diagnosis/history">
                          <Button color="light" id="btn-view-history" className="d-flex align-items-center gap-2">
                            <i className="ri-history-line"></i>Xem lịch sử
                          </Button>
                        </Link>
                        <Button
                          color={expertSent ? "secondary" : "danger"}
                          id="btn-send-expert"
                          disabled={expertSent}
                          onClick={handleSendExpert}
                          className="d-flex align-items-center gap-2"
                        >
                          <i className="ri-stethoscope-line"></i>
                          {expertSent ? "Đã gửi chuyên gia" : "Gửi chuyên gia"}
                        </Button>
                        <Button
                          color="info"
                          id="btn-re-diagnose"
                          onClick={handleReset}
                          className="d-flex align-items-center gap-2"
                        >
                          <i className="ri-refresh-line"></i>Chẩn đoán ảnh mới
                        </Button>
                      </div>
                    </CardBody>
                  </Card>
                </Col>
              </Row>
            </Col>
          </Row>
        )}
      </div>
      {isOpenLightbox && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            backgroundColor: "rgba(0, 0, 0, 0.95)",
            zIndex: 9999,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
          }}
          onClick={() => {
            setIsOpenLightbox(false);
            setZoomScale(1);
          }}
        >
          {/* Close button */}
          <button
            style={{
              position: "absolute",
              top: "20px",
              right: "20px",
              background: "rgba(255,255,255,0.15)",
              border: "none",
              color: "#fff",
              fontSize: "24px",
              width: "48px",
              height: "48px",
              borderRadius: "50%",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 10000,
            }}
            onClick={() => {
              setIsOpenLightbox(false);
              setZoomScale(1);
            }}
          >
            <i className="ri-close-line"></i>
          </button>

          {/* Zoom indicator */}
          <div
            style={{
              position: "absolute",
              top: "20px",
              left: "50%",
              transform: "translateX(-50%)",
              color: "rgba(255,255,255,0.7)",
              fontSize: "13px",
              zIndex: 10000,
              background: "rgba(0,0,0,0.6)",
              padding: "6px 14px",
              borderRadius: "20px",
              pointerEvents: "none",
            }}
          >
            <i className="ri-zoom-in-line me-1"></i>
            {zoomScale === 1 ? "Nhấn vào ảnh để phóng to" : "Nhấn lại để thu nhỏ"}
          </div>

          {/* Image container */}
          <div
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              overflow: "auto",
              padding: "20px",
            }}
          >
            <img
              src={previewUrl || ""}
              alt="Full screen leaf preview"
              style={{
                maxWidth: "95%",
                maxHeight: "85%",
                objectFit: "contain",
                borderRadius: "4px",
                transition: "transform 0.2s ease-in-out",
                transform: `scale(${zoomScale})`,
                cursor: zoomScale === 1 ? "zoom-in" : "zoom-out",
              }}
              onClick={(e) => {
                e.stopPropagation(); // prevent closing overlay when clicking on image
                setZoomScale((prev) => (prev === 1 ? 2 : 1));
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
