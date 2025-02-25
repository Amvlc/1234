from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import Truncator
from django.conf import settings

from . import const

User = get_user_model()


class CommonInfo(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено"
    )

    class Meta:
        abstract = True


class Location(CommonInfo):
    name = models.CharField(
        max_length=const.MAX_LENGTH, verbose_name="Название места"
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return Truncator(self.name).chars(const.MAX_MODELS_LENGTH)


class Category(CommonInfo):
    title = models.CharField(
        max_length=const.MAX_LENGTH, verbose_name="Заголовок"
    )
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        max_length=const.CAT_LENGTH,
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; разрешены символы "
            "латиницы, цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return Truncator(self.title).chars(const.MAX_MODELS_LENGTH)

    def get_absolute_url(self):
        return reverse(
            "blog:category_posts", kwargs={"category_slug": self.slug}
        )


class Post(CommonInfo):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("scheduled", "Scheduled"),
    )
    title = models.CharField(
        max_length=const.MAX_LENGTH, verbose_name="Заголовок"
    )
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — можно "
            "делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="posts",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение",
        related_name="posts",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
        related_name="posts",
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="draft"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-pub_date",)
        default_related_name = "posts"

    def __str__(self):
        return Truncator(self.title).chars(const.MAX_LENGTH)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"post_id": self.pk})


class Comment(CommonInfo):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор комментария",
        related_name="comments",
    )
    text = models.TextField(verbose_name="Текст комментария")

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return (
            f"Комментарий от {self.author.username} к публикации {self.post}",
            f"текст: {self.text}",
        )
