from django.urls import path
from .views import SendMessageView, MessageHistoryView, UpdateReadStatusView

urlpatterns = [
    path('send/', SendMessageView.as_view(), name='send-message'),
    path('history/<int:user_id>/', MessageHistoryView.as_view(), name='message-history'),
    path('read/<int:pk>/', UpdateReadStatusView.as_view(), name='update-read-status'),
]
