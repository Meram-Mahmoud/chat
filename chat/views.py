from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Message, UnreadMessageCount
from .serializers import MessageSerializer


class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        sender = self.request.user
        
        # Ensure receiver exists and is a valid user
        receiver_id = self.request.data.get('receiver')
        try:
            receiver = User.objects.get(pk=receiver_id)
        except User.DoesNotExist:
            raise ValidationError('Receiver does not exist.')

        # Save the message with the sender and receiver
        serializer.save(sender=sender, receiver=receiver)

        # Update or create unread message count for the receiver
        unread, created = UnreadMessageCount.objects.get_or_create(user=receiver)
        unread.count += 1
        unread.save()


class MessageHistoryView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_user_id = self.kwargs['user_id']
        
        # Ensure other_user exists
        try:
            other_user = User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            raise ValidationError('Other user does not exist.')

        # Fetch messages between the authenticated user and the other user
        return Message.objects.filter(
            (Q(sender=user) & Q(receiver=other_user)) | 
            (Q(sender=other_user) & Q(receiver=user))
        ).order_by('timestamp')


class UpdateReadStatusView(generics.UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the logged-in user is the receiver of the message
        if request.user != instance.receiver:
            return Response({'detail': 'Permission denied.'}, status=403)

        # Mark message as read
        instance.is_read = True
        instance.save()

        # Update the unread count for the user
        unread, created = UnreadMessageCount.objects.get_or_create(user=request.user)
        unread.count = max(0, unread.count - 1)
        unread.save()

        # Return the updated message
        return Response(self.get_serializer(instance).data)
