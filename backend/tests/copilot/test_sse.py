def test_sse_resume_starts_after_last_event(client, auth_header) -> None:
    response = client.post(
        "/api/v1/copilot/sessions/s1/messages",
        headers={**auth_header, "Idempotency-Key": "k1", "Last-Event-ID": "evt-2"},
        json={"query": "Triệu chứng đạo ôn?", "expected_conversation_revision": 0},
    )
    assert "id: evt-1\n" not in response.text


def test_sse_resume_skips_the_exact_last_event_not_a_hardcoded_id(client, auth_header) -> None:
    response = client.post(
        "/api/v1/copilot/sessions/s2/messages",
        headers={
            **auth_header,
            "Idempotency-Key": "resume-key",
            "Last-Event-ID": "evt-1-start",
        },
        json={"query": "Triệu chứng đạo ôn?", "expected_conversation_revision": 0},
    )
    assert "id: evt-1-start\n" not in response.text


def test_sse_replays_persisted_events_after_the_last_received_event(client, auth_header) -> None:
    first = client.post(
        "/api/v1/copilot/sessions/s3/messages",
        headers={**auth_header, "Idempotency-Key": "replay-key"},
        json={"query": "Cay lua can gi?", "expected_conversation_revision": 0},
    )
    resumed = client.post(
        "/api/v1/copilot/sessions/s3/messages",
        headers={
            **auth_header,
            "Idempotency-Key": "replay-key",
            "Last-Event-ID": "evt-1-start",
        },
        json={"query": "Cay lua can gi?", "expected_conversation_revision": 0},
    )

    assert "id: evt-1-start\n" in first.text
    assert "id: evt-1-end\n" in resumed.text
    assert "id: evt-1-start\n" not in resumed.text
