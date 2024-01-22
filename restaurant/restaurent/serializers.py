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
    featured = serializers.BooleanField(required=False)
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
                raise serializers.ValidationError('category no valid')

        return self.Meta.model.objects.create(**validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.StringRelatedField()
    class Meta:
        model = CartItem
        exclude = ['cart']

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.StringRelatedField()
    class Meta:
        model = OrderItem
        exclude = ['order']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, required=False)
    total = serializers.IntegerField(read_only=True, required=False)
    menu_items_in = serializers.DictField(write_only=True)
    menu_items_out = serializers.SerializerMethodField(read_only=True, required=False)
    remove_items = serializers.ListField(required=False)
    class Meta:
        model = Cart
        fields = "__all__"

    def get_menu_items_out(self, obj):
        return CartItemSerializer(obj.cartitem_set.all(), many=True).data

    def validate(self, attrs):
        menu_items = attrs.get('menu_items_in')
        remove_items = attrs.get('remove_items')
        if menu_items:
            if self.context.get('method') == 'PUT':
                if CartItem.objects.filter(cart=self.instance, menu_item__pk__in=menu_items.keys()).count() == len(menu_items):
                    return attrs
                raise serializers.ValidationError('some items are not in cart')
            if all(isinstance(value, int) for value in menu_items.values()):
                if MenuItem.objects.filter(pk__in=list(map(int, menu_items.keys()))).count() == len(menu_items):
                    return attrs
                raise serializers.ValidationError('some items pks are not valid')
            raise serializers.ValidationError('some items are not integers')
        if remove_items:
            if all(isinstance(value,int) for value in remove_items):
                if all(item.cart == self.instance for item in CartItem.objects.filter(cart=self.instance, pk__in=remove_items)):
                    return attrs
                raise serializers.ValidationError('some items are not in cart')
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

    def update(self, instance, validated_data):
        if self.context.get('method') == 'PUT':
            update_items = CartItem.objects.filter(cart=instance, menu_item__pk__in=validated_data.get('menu_items_in'))
            for item in update_items:
                instance.total -= item.price * item.quantity
                item.quantity = validated_data.get('menu_items_in').get(str(item.menu_item.pk))
                item.save()
                instance.total += item.price * item.quantity

            instance.save()
            return instance

        if validated_data.get('menu_items_in'):
            items = validated_data.get('menu_items_in')
            existing_items = CartItem.objects.filter(cart=instance, menu_item__pk__in=items.keys())
            if existing_items:
                for item in existing_items:
                    item.quantity += items.get(str(item.menu_item.pk))
                    item.save()
                    instance.total += item.price * items.get(str(item.menu_item.pk))
                    items.pop(str(item.menu_item.pk))

            if items:
                menu_items = MenuItem.objects.filter(pk__in=items.keys())
                cart_items = []
                for item in menu_items:
                    cart_items.append(CartItem(cart=instance, menu_item=item, price=item.price, quantity=items.get(str(item.pk))))
                    instance.total += (item.price * items.get(str(item.pk)))
                CartItem.objects.bulk_create(cart_items)

        if validated_data.get('remove_items'):
            items_delete = CartItem.objects.filter(cart=instance, pk__in=validated_data.get('remove_items'))
            for item in items_delete:
                instance.total -= item.price * item.quantity
            items_delete.delete()

        instance.save()
        return instance

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, required=False)
    total = serializers.IntegerField(read_only=True, required=False)
    delivery_crew = UserSerializer(required=False)
    active = serializers.BooleanField(required=False)
    order_items_in = serializers.DictField(write_only=True, required=False)
    order_items_out = serializers.SerializerMethodField()
    remove_items = serializers.ListField(write_only=True, required=False)
    class Meta:
        model = Order
        fields = '__all__'


    def get_order_items_out(self, obj):
        return OrderItemSerializer(obj.orderitem_set.all(), many=True).data


    def validate(self, attrs):
        if attrs.get('order_items_in'):
            a = attrs.get('order_items_in')
            if all(isinstance(value,int) for value in a.values()):
                if MenuItem.objects.filter(pk__in=list(map(int, a.keys()))).count() == len(a):
                    return attrs
                raise serializers.ValidationError('some items are not the the menu')
            raise serializers.ValidationError('some items pks are not int')

        if attrs.get('remove_items'):
            if all(isinstance(value, int) for value in attrs.get('remove_items')):
                if OrderItem.objects.filter(order=self.instance, pk__in=attrs.get('remove_items')):
                    return attrs
                raise serializers.ValidationError('some items or not in order')
            raise serializers.ValidationError('some items are not int')

        if Cart.objects.filter(user=self.context.get('user')).exists():
            return attrs
        raise serializers.ValidationError('user must have cart or provide items')


    def create(self, validated_data):
        if not Order.objects.filter(user=self.context.get('user'), active=True).exists():
            order = self.Meta.model.objects.create(user=self.context.get('user'))
            order_items = []
            if validated_data.get('order_items_in'):

                for item in MenuItem.objects.filter(pk__in=list(map(int, validated_data.get('order_items_in').keys()))):
                    quantity = validated_data.get('order_items_in').get(str(item.pk))
                    order_items.append(OrderItem(order=order, menu_item=item, quantity=quantity, price=item.price))
                    order.total += item.price * quantity
            else:

                for item in CartItem.objects.filter(cart__user=self.context.get('user')):
                    order_items.append(OrderItem(order=order, menu_item=item.menu_item, quantity=item.quantity, price=item.price))
                    order.total += item.price * item.quantity
                Cart.objects.filter(user=self.context.get('user')).delete()

            order.save()
            OrderItem.objects.bulk_create(order_items)
            return order
        raise serializers.ValidationError('user can have only 1 active order')

    def update(self, instance, validated_data):
        if self.context.get('method') == 'PUT':
            update_items = OrderItem.objects.filter(order=instance, menu_item__pk__in=validated_data.get('order_items_in'))
            for item in update_items:
                instance.total -= item.price * item.quantity
                item.quantity = validated_data.get('order_items_in').get(str(item.menu_item.pk))
                item.save()
                instance.total += item.price * item.quantity

            instance.save()
            return instance

        if validated_data.get('order_items_in'):
            items = validated_data.get('order_items_in')
            existing_items = OrderItem.objects.filter(oder=instance, menu_item__pk__in=items.keys())
            if existing_items:
                for item in existing_items:
                    item.quantity += items.get(str(item.menu_item.pk))
                    item.save()
                    instance.total += item.price * items.get(str(item.menu_item.pk))
                    items.pop(str(item.menu_item.pk))

            if items:
                menu_items = MenuItem.objects.filter(pk__in=items.keys())
                order_items = []
                for item in menu_items:
                    order_items.append(OrderItem(order=instance, menu_item=item, price=item.price, quantity=items.get(str(item.pk))))
                    instance.total += (item.price * items.get(str(item.pk)))
                OrderItem.objects.bulk_create(order_items)

        if validated_data.get('remove_items'):
            items_delete = OrderItem.objects.filter(order=instance, pk__in=validated_data.get('remove_items'))
            for item in items_delete:
                instance.total -= item.price * item.quantity
            items_delete.delete()

        instance.save()
        return instance

class TableSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    user_in = serializers.CharField(required=False, write_only=True)
    class Meta:
        model = Tabel
        fields = '__all__'

    def validate(self, attrs):
        if attrs.get('user_in'):

            user = get_user_model().objects.filter(email=attrs.pop('user_in'))
            if not user:
                raise serializers.ValidationError('user not found')
            attrs['user'] = user[0]

        else:
            attrs['user'] = self.context.get('user')
        return super().validate(attrs)