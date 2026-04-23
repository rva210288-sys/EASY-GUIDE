from django.db import models, transaction


class Chat(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_group = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    def add_client(self, client_id):
        assert self.is_group
        ChatToClient.objects.create(chat=self, client_id=client_id)

    def remove_client(self, client_id):
        assert self.is_group
        ChatToClient.objects.filter(chat=self, client=client_id).delete()

    @classmethod
    def get_tetatet(cls, client1, client2):
        queryset = ChatToClient.objects.filter(chat__is_group=False)

        chats1 = queryset.filter(client=client1).values_list('chat_id', flat=True)
        chats2 = queryset.filter(client=client2).values_list('chat_id', flat=True)

        intersection = set(chats1) & set(chats2)

        if intersection:
            chat_id = next(intersection)
            return cls.objects.get(id=chat_id)
        else:
            return None

    @classmethod
    @transaction.atomic
    def create_tetatet(cls, client_id1, client_id2):
        chat = cls.objects.create(is_group=False)
        ChatToClient.objects.create(chat=chat, client_id=client_id1)
        ChatToClient.objects.create(chat=chat, client_id=client_id2)
        return chat


class ChatToClient(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    last_seen = models.DateTimeField(null=True, default=None, blank=True)

    class Meta:
        unique_together = ('chat', 'client')

    def __str__(self):
        return str(self.id)


class ChatMessage(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return str(self.id)
