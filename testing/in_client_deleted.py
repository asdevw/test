import pytest
from mailing.models import Client

@pytest.mark.django_db
class TestClientPut:
    def test_correct_put(self, client):
        data = {"phone": 123123123, "mobile_operator": 999, "tag": "some_tag", "timezone": "UTC"}
        mailing_client = Client.objects.create(**data)
        change_data = {"phone": 123123123, "tag": "some_tag_change", "timezone": "Europe/Moscow"}
        put_response = client.put(f"/mainapp/client/{mailing_client.id}", data=change_data,content_type="application/json")
        assert put_response.status_code == 200
        assert put_response.data["phone"] == 123123123
        assert put_response.data["tag"] == "some_tag_change"
        assert put_response.data["timezone"] == "Europe/Moscow"

    def test_incorrect_put_timezone(self, client):
        data = {"phone": 123123123, "mobile_operator": 999, "tag": "some_tag", "timezone": "UTC"}
        mailing_client = Client.objects.create(**data)
        change_data = {"phone": 123123123, "tag": "some_tag_change", "timezone": "somE_Zone"}
        put_response = client.put(f"/mainapp/client/{mailing_client.id}", data=change_data,content_type="application/json")
        assert put_response.status_code == 400
    def test_incorrect_put_phone(self, client):
        data = {"phone": 123123123, "mobile_operator": 999, "tag": "some_tag", "timezone": "UTC"}
        mailing_client = Client.objects.create(**data)
        change_data = {"phone": 1231231234, "tag": "some_tag_change", "timezone": "Europe/Moscow"}
        put_response = client.put(f"/mainapp/client/{mailing_client.id}", data=change_data,content_type="application/json")
        assert put_response.status_code == 400

@pytest.mark.djaainapp
class TestClientDelete:
    def test_delete_client(self, client):
        data = {"phone": 123123123, "mobile_operator": 999, "tag": "some_tag", "timezone": "UTC"}
        mailing_client = Client.objects.create(**data)
        delete_response = client.delete(f"/mailing/client/{mailing_client.id}")
        get_response = client.get(f"/mainapp/client/{mailing_client.id}")

        assert delete_response.status_code == 204
        assert get_response.status_code == 404
