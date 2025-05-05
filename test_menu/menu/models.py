
from django.db import models

class MenuItem(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    url = models.CharField(max_length=200, verbose_name="URL", blank=True, null=True)
    named_url = models.CharField(max_length=100, verbose_name="Named URL", blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительский пункт"
    )
    menu_name = models.CharField(max_length=50, verbose_name="Имя меню")

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"

    def get_url(self):
        if self.named_url:
            from django.urls import reverse
            return reverse(self.named_url)
        return self.url or '#'

    def __str__(self):
        return self.name

