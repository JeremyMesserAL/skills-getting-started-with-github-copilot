def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 302)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert set(data["Chess Club"].keys()) == {
        "description",
        "schedule",
        "max_participants",
        "participants",
    }


def test_signup_success_adds_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_email_returns_conflict(client):
    # Arrange
    activity_name = "Programming Class"

    # Act
    first = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "  student@mergington.edu  "},
    )
    second = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "STUDENT@MERGINGTON.EDU"},
    )

    # Assert
    assert first.status_code == 200
    assert second.status_code == 409


def test_signup_unknown_activity_returns_not_found(client):
    # Arrange

    # Act
    response = client.post(
        "/activities/NotARealClub/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404


def test_unregister_success_removes_participant(client):
    # Arrange
    activity_name = "Drama Club"
    email = "remove-me@mergington.edu"

    # Act
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_email_normalization_allows_case_space_variants(client):
    # Arrange
    activity_name = "Science Club"
    original = "MixedCase@mergington.edu"

    # Act
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": original},
    )
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "  mixedcase@MERGINGTON.edu  "},
    )
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert original not in activities[activity_name]["participants"]


def test_unregister_non_registered_participant_returns_not_found(client):
    # Arrange

    # Act
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "not-registered@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404


def test_unregister_unknown_activity_returns_not_found(client):
    # Arrange

    # Act
    response = client.delete(
        "/activities/NotARealClub/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
