from __future__ import annotations


def test_end_to_end_swap_flow(client):
    # Create two users
    creator_resp = client.post(
        "/users/",
        json={
            "email": "ari@example.com",
            "display_name": "Ari",
            "favorite_plants": ["Monstera"],
            "radius_miles": 12,
        },
    )
    assert creator_resp.status_code == 201
    owner_id = creator_resp.json()["id"]

    seeker_resp = client.post(
        "/users/",
        json={
            "email": "sam@example.com",
            "display_name": "Sam",
            "favorite_plants": ["Philodendron"],
            "radius_miles": 20,
        },
    )
    assert seeker_resp.status_code == 201
    requester_id = seeker_resp.json()["id"]

    # Create a listing owned by Ari
    listing_resp = client.post(
        "/listings/",
        json={
            "owner_id": owner_id,
            "title": "Monstera cutting",
            "transaction_types": ["swap", "free"],
            "quantity": 1,
            "tags": ["cutting"],
            "photo_urls": ["https://example.com/photo.jpg"],
        },
    )
    assert listing_resp.status_code == 201
    listing_id = listing_resp.json()["id"]

    # Sam likes the listing and Ari confirms the match
    like_resp = client.post(
        f"/matches/{listing_id}/like",
        json={"user_id": requester_id},
    )
    assert like_resp.status_code == 200
    assert like_resp.json()["status"] == "liked"

    confirm_resp = client.post(
        f"/matches/{listing_id}/like",
        json={"user_id": owner_id, "target_user_id": requester_id},
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "matched"
    assert confirm_resp.json()["is_mutual"] is True

    # Create a chat thread and exchange a message
    thread_resp = client.post(
        "/threads/",
        json={
            "listing_id": listing_id,
            "starter_id": requester_id,
            "recipient_id": owner_id,
        },
    )
    assert thread_resp.status_code == 201
    thread_id = thread_resp.json()["id"]

    message_resp = client.post(
        f"/threads/{thread_id}/messages",
        json={
            "thread_id": thread_id,
            "sender_id": requester_id,
            "body": "Hey there! When can we swap?",
        },
    )
    assert message_resp.status_code == 201

    # Initiate a swap request
    swap_resp = client.post(
        "/swaps/",
        json={
            "listing_id": listing_id,
            "requester_id": requester_id,
        },
    )
    assert swap_resp.status_code == 201
    swap_payload = swap_resp.json()
    swap_id = swap_payload["id"]
    assert swap_payload["status"] == "pending"

    # Ari agrees then Sam completes the swap
    agree_resp = client.post(
        f"/swaps/{swap_id}/status",
        json={"status": "agreed", "actor_id": owner_id},
    )
    assert agree_resp.status_code == 200
    assert agree_resp.json()["status"] == "agreed"

    complete_resp = client.post(
        f"/swaps/{swap_id}/status",
        json={"status": "completed", "actor_id": requester_id},
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "completed"

    # Leave a rating for Ari
    rating_resp = client.post(
        "/ratings/",
        json={
            "swap_id": swap_id,
            "reviewer_id": requester_id,
            "reviewee_id": owner_id,
            "reliability_score": 5,
            "plant_health_score": 4,
            "comments": "Healthy plant and smooth meetup!",
        },
    )
    assert rating_resp.status_code == 201

    # Ratings summary should reflect the feedback
    summary_resp = client.get(f"/ratings/{owner_id}/summary")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_ratings"] == 1
    assert summary["average_reliability"] == 5.0
    assert summary["average_plant_health"] == 4.0
