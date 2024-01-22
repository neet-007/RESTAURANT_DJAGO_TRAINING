from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
# Create your models here.
user_model = get_user_model()

class Category(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=125, db_index=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name}'

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=125, db_index=True)
    price = models.DecimalField(decimal_places=2, db_index=True, max_digits=6)
    featured = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(user_model, on_delete=models.CASCADE)
    total = models.DecimalField(decimal_places=2, max_digits=6, default=0)

    def __str__(self) -> str:
        return f'user {self.user} with total {self.total}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ['cart', 'menu_item']

    def __str__(self) -> str:
        return f'name:{self.menu_item} quantity:{self.quantity} price:{self.price}'

class Order(models.Model):
    user = models.ForeignKey(user_model, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(user_model, related_name='delivery_crew', on_delete=models.CASCADE, blank=True, null=True)
    active = models.BooleanField(default=True, db_index=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f'user {self.user} order with total{self.total}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ['order', 'menu_item']

    def __str__(self) -> str:
        return f'name:{self.menu_item} quantity:{self.quantity} price:{self.price}'

class Tabel(models.Model):
    user = models.ForeignKey(user_model, on_delete=models.CASCADE)
    number_of_guests = models.PositiveIntegerField(default=0, db_index=True)
    date = models.DateTimeField(db_index=True)

    def __str__(self) -> str:
        return f'user {self.user} table N.G:{self.number_of_guests} data:{self.date}'