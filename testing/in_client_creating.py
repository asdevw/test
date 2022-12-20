import pytest
@pytest.mark.django_db
class TestClientCreate:
    def test_correct_create(self, client):
        data = {"phone": 123123122, "tag": "some_tag", "timezone": "UTC"}
        post_response = client.post('/mainapp/client/create', data=data)
        get_response = client.get(f"/mainapp/client/{post_response.data['id']}")
        assert post_response.status_code == 201
        assert get_response.status_code == 200
        assert post_response.data["phone"] == 79994567890
        assert get_response.data["tag"] == "some_tag"
    def test_incorrect_phone_create(self, client):
        data1 = {"phone": 123123123, "tag": "some_tag", "timezone": "UTC"}
        data2 = {"phone": 123123124, "tag": "some_tag", "timezone": "UTC"}
        post_response1 = client.post('/mainapp/client/create', data=data1)
        post_response2 = client.post('/mainapp/client/create', data=data2)
        assert post_response1.status_code == 400
        assert post_response2.status_code == 400
    def test_incorrect_timezone_create(self, client):
        data = {"phone": 123123125, "tag": "some_tag", "timezone": "qwerty"}
        post_response = client.post('/mainapp/client/create', data=data)
        assert post_response.status_code == 400
