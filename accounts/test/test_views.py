# from django.urls import reverse
# from rest_framework.status import (
#     HTTP_200_OK,
#     HTTP_401_UNAUTHORIZED,
#     HTTP_400_BAD_REQUEST,
#     HTTP_403_FORBIDDEN,
#     HTTP_205_RESET_CONTENT
# )
# from rest_framework.test import APITestCase
#
# from tests.accounts.api.mixin import ViewsTestCaseMixin
#
# test_email1 = 'login@mail.com'
# test_email2 = 'login@gmail.com'
# test_email3 = 'test@gmail.com'
# test_password = 'Password123'
# json_content = 'application/json'
#
#
# class TestTokenVerifyAPIView(APITestCase, ViewsTestCaseMixin):
#     def setUp(self):
#         self.user, self.access_token, _ = self.create_employee(test_email1, test_password)
#
#     def test_verify_token_url_is_public(self):
#         res = self.client.post(reverse('token-verify'), {'token': self.access_token})
#         self.assertEqual(res.status_code, HTTP_200_OK)
#
#
# class TestLogoutAPIView(APITestCase, ViewsTestCaseMixin):
#     def setUp(self):
#         self.user, self.access_token, self.refresh_token = self.create_employee(
#             test_email1, test_password
#         )
#
#     def test_logout_view_requires_auth(self):
#         res = self.client.post(reverse('logout'))
#         self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED, {'refresh': self.refresh_token})
#
#     def test_logout_view_fails(self):
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
#         res = self.client.post(reverse('logout'), {'refresh': ''})
#         self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)
#         res = self.client.post(reverse('logout'), {'refresh': ''})
#         self.assertEqual(res.status_code, HTTP_400_BAD_REQUEST)
#
#     def test_logout_view_succeeds(self):
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
#         res = self.client.post(reverse('logout'), {'refresh': self.refresh_token})
#         self.assertEqual(res.status_code, HTTP_205_RESET_CONTENT)
#
#
# class TestUserRetrieveUpdateAPIView(APITestCase, ViewsTestCaseMixin):
#     def setUp(self):
#         self.user, self.access_token, _ = self.create_employee(test_email1, test_password)
#         self.admin_user,self.admin_access_token,_ = self.create_admin(test_email2, test_password)
#
#     def test_retrieve_update_requires_auth(self):
#         res = self.client.get(reverse('get-update-user', kwargs={'pk': 1}))
#         self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)
#
#         res = self.client.patch(reverse('get-update-user', kwargs={'pk': 1}))
#         self.assertEqual(res.status_code, HTTP_401_UNAUTHORIZED)
#
#     def test_retrieve_succeeds_for_user_owner(self):
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
#         res = self.client.get(reverse('get-update-user', kwargs={'pk': self.user.pk}))
#         self.assertEqual(res.status_code, HTTP_200_OK)
#
#     def test_update_fails_for_not_owners(self):
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
#         res = self.client.get(reverse('get-update-user', kwargs={'pk': self.admin_user.pk}))
#         self.assertEqual(res.status_code, HTTP_403_FORBIDDEN)
