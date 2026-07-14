import { KnowledgeJobDetail } from "@/features/knowledge/knowledge-job-detail";

export default async function KnowledgeJobPage({
  params,
}: {
  params: Promise<{ jobId: string }>;
}) {
  const { jobId } = await params;
  return <KnowledgeJobDetail jobId={jobId} />;
}
