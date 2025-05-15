from django.db import models

class Contato(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    mensagem = models.TextField()

    def __str__(self):
        return self.nome
