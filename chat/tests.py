from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Message, UnreadMessageCount


class ChatAPITestCase(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')

        # Ensure UnreadMessageCount exists for both users
        UnreadMessageCount.objects.get_or_create(user=self.user1, defaults={'count': 0})
        UnreadMessageCount.objects.get_or_create(user=self.user2, defaults={'count': 0})

        # Login user1 for test purposes
        self.client.login(username='user1', password='pass123')

    def test_send_message(self):
        # URL for sending a message
        url = reverse('send-message') 
        # Payload data for sending a message
        data = {
            'receiver': self.user2.id,  # Assuming the receiver expects a user ID
            'content': 'Hello, this is a test message.'
        }

        # Send a POST request to the send-message endpoint
        response = self.client.post(url, data, format='json')

        # Print response data for debugging purposes
        print(response.data)

        # Assert that the response status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that a new message is created
        self.assertEqual(Message.objects.count(), 1)

        # Assert that the unread message count for user2 is updated
        unread_count = UnreadMessageCount.objects.get(user=self.user2)
        self.assertEqual(unread_count.count, 1)

    def test_message_history(self):
        # Create a message from user1 to user2
        Message.objects.create(sender=self.user1, receiver=self.user2, content='Hello again!')

        # URL for retrieving message history
        url = reverse('message-history', kwargs={'user_id': self.user2.id})  
        # Send a GET request to the message-history endpoint
        response = self.client.get(url)

        # Print response data for debugging purposes
        print(response.data)

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the returned message history is correct
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Hello again!')

    def test_update_read_status(self):
        # Create a message from user1 to user2
        message = Message.objects.create(sender=self.user1, receiver=self.user2, content='Check read status')

        # URL for updating read status
        url = reverse('update-read-status', kwargs={'pk': message.id})  

        # Ensure the user making the request is allowed to update the status
        self.client.login(username='user2', password='pass123')

        # Send a PATCH request to update the message read status
        response = self.client.patch(url, {'is_read': True}, format='json')

        # Print response data for debugging purposes
        print(response.data)

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Reload the message from the database
        message.refresh_from_db()

        # Assert that the message read status is updated
        self.assertTrue(message.is_read)

        # Check if unread message count is updated for user2
        unread_count = UnreadMessageCount.objects.get(user=self.user2)
        self.assertEqual(unread_count.count, 0)  # Should be 0 since the message is now read
