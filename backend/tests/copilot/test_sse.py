def test_sse_resume_starts_after_last_event(client, auth_header) -> None:
    response = client.post(
        "/api/v1/copilot/sessions/s1/messages",
        headers={**auth_header, "Idempotency-Key": "k1", "Last-Event-ID": "evt-2"},
        json={"query": "Triệu chứng đạo ôn?", "expected_conversation_revision": 0},
    )
    assert "id: evt-1\n" not in response.text
