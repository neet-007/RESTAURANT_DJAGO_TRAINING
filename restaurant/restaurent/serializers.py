from rest_framework import serializers
from user_auth.serializers import UserSerializer
from django.db.models import Sum
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True, required=False)
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields = '__all__'

    def create(self, validated_data):
        category = validated_data.pop('category')
        if Category.objects.filter(name__iexact=category.get('name')).exists():
            validated_data['category'] = Category.objects.get(name__iexact=category.get('name'))
        else:
            serialized_data = CategorySerializer(data=category)
            if serialized_data.is_valid():
                category = serialized_data.save()
                validated_data['category'] = category
            else:
                raise serializers.ValidationError()

        return self.Meta.model.objects.create(**validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.StringRelatedField()
    class Meta:
        model = CartItem
        exclude = ['cart']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, required=False)
    total = serializers.IntegerField(read_only=True, required=False)
    menu_items_in = serializers.DictField(write_only=True)
    menu_items_out = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = Cart
        fields = "__all__"

    def get_menu_items_out(self, obj):
        return CartItemSerializer(obj.cartitem_set.all(), many=True).data

    def validate(self, attrs):
        menu_items = attrs.get('menu_items_in')
        if menu_items:
            if all(isinstance(value, int) for value in menu_items.values()):
                print(MenuItem.objects.filter(pk__in=list(map(int, menu_items.keys()))).count())
                print(len(menu_items))
                if MenuItem.objects.filter(pk__in=list(map(int, menu_items.keys()))).count() == len(menu_items):
                    return attrs
                raise serializers.ValidationError('some items pks are not valid')
            raise serializers.ValidationError('some items are not integers')
        raise serializers.ValidationError('no items where provided')


    def create(self, validated_data):
        user = user=self.context.get('user')
        if not self.Meta.model.objects.filter(user=user).exists():
            cart = self.Meta.model.objects.create(user=user, total=0)
            menu_items = MenuItem.objects.filter(pk__in=validated_data.get('menu_items_in').keys())
            cart_items = []
            for item in menu_items:
                quantity = int(validated_data.get('menu_items_in').get(str(item.pk)))
                cart_items.append(CartItem(cart=cart, menu_item=item, quantity=quantity, price=item.price))
                cart.total += (item.price * quantity)
            CartItem.objects.bulk_create(cart_items)
            cart.save()
            return cart
        raise serializers.ValidationError('user has cart')

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

