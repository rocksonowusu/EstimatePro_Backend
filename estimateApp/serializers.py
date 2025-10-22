from rest_framework import serializers
from .models import UserProfile, BusinessProfile, Estimate, EstimateItem, MaterialDescription

class OnboardingSerializers(serializers.Serializer):
    email = serializers.EmailField()
    image = serializers.ImageField(required=False)  # Company letterhead image
    name = serializers.CharField(max_length=255)      # Business name, also used as online name
    phone = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=255)
    website = serializers.CharField(max_length=255, required=False, allow_blank=True)
    taxId = serializers.CharField(max_length=100, required=False, allow_blank=True)
    established = serializers.CharField(max_length=20, required=False, allow_blank=True)
    industry = serializers.CharField(max_length=100, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        email = validated_data.get('email')
        name = validated_data.get('name')
        
        # Create or update the user with the provided email and name.
        user, _ = UserProfile.objects.update_or_create(
            email=email,
            defaults={'online_name': name}
        )

        # Create or update the BusinessProfile using the submitted business details.
        bp, _ = BusinessProfile.objects.update_or_create(
            user=user,
            defaults={
                'business_name': name,
                'phone': validated_data.get('phone'),
                'address': validated_data.get('address'),
                'website': validated_data.get('website', ''),
                'tax_id': validated_data.get('taxId', ''),
                'established': validated_data.get('established', ''),
                'industry': validated_data.get('industry', ''),
                'description': validated_data.get('description', ''),
                'background_image': validated_data.get('image', None)
            }
        )
        # Use the company letterhead image as the profile picture.
        profile_pic = bp.background_image.url if bp.background_image else None
        
        return {
            'online_name': name,
            'profile_pic': profile_pic
        }

class MaterialDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialDescription
        fields = ['id', 'name']


class EstimateItemSerializer(serializers.ModelSerializer):
    chosen_material = MaterialDescriptionSerializer(read_only=True)
    chosen_material_id = serializers.PrimaryKeyRelatedField(
        queryset=MaterialDescription.objects.all(),
        source='chosen_material',
        write_only=True,
        required=False,
        allow_null= True
    )

    class Meta:
        model = EstimateItem
        fields = ['id', 'chosen_material', 'chosen_material_id', 'description', 'quantity','unit', 'unit_price', 'amount']

class EstimateSerializer(serializers.ModelSerializer):
    items = EstimateItemSerializer(many=True)
    user_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Estimate
        fields = [
            'id', 'user_email', 'client_name', 'estimate_title', 'notes',
            'workmanship', 'total_materials', 'grand_total', 'created_at', 'items'
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user_email = validated_data.pop('user_email')  # Correct field name
        try:
            user = UserProfile.objects.get(email=user_email)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({"user_email": "User not found with this email."})
        estimate = Estimate.objects.create(created_by=user, **validated_data)
        for item_data in items_data:
            EstimateItem.objects.create(estimate=estimate, **item_data)
        return estimate
    
    def update(self, instance, validated_data):
        """Update an existing estimate and it's items"""

        items_data = validated_data.pop('items', None)

        instance.client_name = validated_data.get('client_name', instance.client_name)
        instance.estimate_title = validated_data.get('estimate_title', instance.estimate_title)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.workmanship = validated_data.get('workmanship', instance.workmanship)
        instance.total_materials = validated_data.get('total_materials', instance.total_materials)
        instance.grand_total = validated_data.get('grand_total', instance.grand_total)
        instance.save()

        #Update items if provided
        if items_data is not None:
            # Get Existing items
            existing_items ={item.id: item for item in instance.items.all()}
            existing_items_ids = set(existing_items.keys())
            updated_items_ids = set()

            for item_data in items_data:
                item_id = item_data.get('id', None)

                if item_id and item_id in existing_items:
                    item = existing_items[item_id]
                    for attr, value in item_data.items():
                        if attr != 'id':
                            setattr(item, attr, value)
                    item.save()
                    updated_items_ids.add(item_id)
                else:
                    # Create new item
                    EstimateItem.objects.create(estimate=instance, **item_data)
                # Delete items not in the update
                items_to_delete = existing_items_ids - updated_items_ids
                if items_to_delete:
                    instance.items.filter(id__in=items_to_delete).delete()
            return instance
                




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['email', 'online_name']
        extra_kwargs = {
            'email': {'read_only': True}  # Prevent email from being edited
        }

class BusinessProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = BusinessProfile
        fields = [
            'user_email', 'business_name', 'phone', 'address', 'website', 
            'tax_id', 'established', 'industry', 'description', 'background_image'
        ]
        extra_kwargs = {
            'background_image': {'required': False, 'allow_null': True}
        }