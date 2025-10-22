from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Estimate,MaterialDescription, BusinessProfile,EstimateItem
from .serializers import OnboardingSerializers, EstimateSerializer,MaterialDescriptionSerializer, BusinessProfileSerializer,UserProfileSerializer,EstimateItemSerializer
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)


class OnboardingView(APIView):
    def post(self, request, format=None):
        """
        Accepts an email, business details, and an optional company letterhead image.
        Creates or updates the UserProfile and BusinessProfile.
        Returns the display name and the profile picture URL (from the uploaded letterhead).
        """
        serializer = OnboardingSerializers(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        Retrieves the user’s display name and the company letterhead (profile picture)
        using the provided email or business_name query parameter.
        """
        email = request.query_params.get('email')
        business_name = request.query_params.get('business_name')

        if not email and not business_name:
            return Response(
                {'error': 'Email or Business Name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if email:
                user = UserProfile.objects.get(email=email)
                bp = getattr(user, 'business_profile', None)
            else:
                bp = BusinessProfile.objects.get(business_name__iexact=business_name)
                user = bp.user

            profile_pic = bp.background_image.url if bp and bp.background_image else None
            return Response(
                {'online_name': user.online_name, 'profile_pic': profile_pic},
                status=status.HTTP_200_OK
            )
        except (UserProfile.DoesNotExist, BusinessProfile.DoesNotExist):
            return Response(
                {'error': 'User or Business not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CreateEstimateView(APIView):
    def post(self, request, format=None):
        serializer = EstimateSerializer(data=request.data)
        if serializer.is_valid():
            estimate = serializer.save()
            return Response(EstimateSerializer(estimate).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EstimatePreview(APIView):
    """
    Generate and return PDF preview of an estimate with proper page breaks
    """
    
    def get(self, request, pk, format=None):
        try:
            estimate = Estimate.objects.get(pk=pk)
        except Estimate.DoesNotExist:
            return Response(
                {'error': 'Estimate not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get business profile and letterhead
        business_profile = getattr(estimate.created_by, 'business_profile', None)
        letterhead_path = None
        
        if business_profile and business_profile.background_image:
            letterhead_path = business_profile.background_image.path
        
        # Prepare context for template
        context = {
            'estimate': estimate,
            'letterhead_path': letterhead_path,
            'business_profile': business_profile,
        }
        
        # Render HTML template
        html_string = render_to_string('estimate_preview.html', context)
        
        # Configure fonts for better rendering
        font_config = FontConfiguration()
        
        # Additional CSS for proper page breaking
        extra_css = CSS(string='''
            @page {
                size: A4;
                margin: 25mm 20mm;
                
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-family: 'Roboto', Arial, sans-serif;
                    font-size: 10px;
                    color: #666;
                }
            }
            
            /* Ensure watermark only on first page */
            .watermark-container {
                position: absolute;
                page-break-after: avoid;
            }
            
            /* Proper table page breaking */
            table {
                page-break-inside: auto;
            }
            
            thead {
                display: table-header-group;
                page-break-inside: avoid;
                page-break-after: avoid;
            }
            
            tbody {
                display: table-row-group;
            }
            
            tbody tr {
                page-break-inside: avoid !important;
                page-break-after: auto;
            }
            
            /* Keep totals together */
            .totals-wrapper {
                page-break-inside: avoid !important;
            }
            
            /* Keep notes together */
            .notes {
                page-break-inside: avoid !important;
            }
            
            /* Keep footer together */
            .footer {
                page-break-inside: avoid !important;
            }
            
            /* Prevent orphans and widows */
            p, div {
                orphans: 3;
                widows: 3;
            }
            
            /* First page specific styling */
            .first-page-content {
                page-break-after: avoid;
            }
            
            .header {
                page-break-after: avoid;
            }
            
            .info-grid {
                page-break-inside: avoid;
            }
        ''', font_config=font_config)
        
        # Generate PDF with enhanced settings
        html = HTML(
            string=html_string, 
            base_url=request.build_absolute_uri('/')
        )
        
        pdf_file = html.write_pdf(
            stylesheets=[extra_css],
            font_config=font_config,
            # Optimize PDF size
            optimize_size=('fonts', 'images'),
            # Better image handling
            presentational_hints=True
        )
        
        # Create response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        
        # Create clean filename
        client_name_title = estimate.client_name.title() if estimate.client_name else str(estimate.id)
        # Remove special characters that might cause issues
        clean_client_name = ''.join(c for c in client_name_title if c.isalnum() or c in (' ', '-', '_'))
        
        response['Content-Disposition'] = f'inline; filename="Estimate_for_{clean_client_name}.pdf"'
        
        # Log for debugging
        logger.info(f"Generated PDF for Estimate ID: {estimate.id}, Client: {estimate.client_name}")
        
        return response

class GetAllEstimates(APIView):
    def get(self, request, format=None):
        estimates = Estimate.objects.all()
        serializer = EstimateSerializer(estimates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MaterialDescriptionListView(APIView):
    def get(self, request, format=None):
        materials = MaterialDescription.objects.all()
        serializer = MaterialDescriptionSerializer(materials, many = True)
        return Response(serializer.data)

class UserProfileView(APIView):
    def get(self, request, format=None):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = UserProfile.objects.get(email=email)
            serializer = UserProfileSerializer(user)  # Add this line
            return Response(serializer.data)  # Add this return
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, format=None):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error':'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = UserProfile.objects.get(email=email)
            serializer = UserProfileSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class BusinessProfileView(APIView):
    def get(self, request, format=None):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = UserProfile.objects.get(email=email)
            business_profile = user.business_profile
            serializer = BusinessProfileSerializer(business_profile)
            return Response(serializer.data)  # This was missing
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except BusinessProfile.DoesNotExist:
            return Response(
                {'error': 'Business profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, format=None):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = UserProfile.objects.get(email=email)
            business_profile = user.business_profile
            serializer = BusinessProfileSerializer(business_profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except BusinessProfile.DoesNotExist:
            return Response(
                {'error': 'Business profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class DeleteAccountView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = UserProfile.objects.get(email=email)
            user.delete()
            return Response(
                {"message":"Account deleted successfully"},
                status=status.HTTP_200_OK
            )
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND)

class EditEstimateView(APIView):
    def put(self, request, pk, format=None):
        """
        Edit an existing estimate by id
        """
        # Make a copy of data and remove user_email if present
        data = request.data.copy()
        if 'user_email' in data:
            data.pop('user_email')
        
        # Get Estimate by id
        try:
            estimate = Estimate.objects.get(pk=pk)
        except Estimate.DoesNotExist:
            return Response(
                {'error': "Estimate not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # FIX 1: Use 'data' instead of 'request.data'
        serializer = EstimateSerializer(estimate, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()

            # Handle items update separately if provided
            if 'items' in data:
                items_data = data['items']
                self.update_estimate_items(estimate, items_data)

            # Return the updated estimate
            updated_estimate = Estimate.objects.get(pk=pk)
            return Response(
                EstimateSerializer(updated_estimate).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_estimate_items(self, estimate, items_data):
        """
        Helper function to update estimate items
        """
        # Get existing items as a dictionary
        existing_items_dict = {item.id: item for item in estimate.items.all()}
        
        # FIX 2: Correct way to get existing item IDs
        existing_item_ids = set(existing_items_dict.keys())
        
        # Track which items were updated/created
        updated_item_ids = set()

        for item_data in items_data:
            item_id = item_data.get('id', None)
            
            # FIX 3: Better handling of item_id checking
            if item_id and item_id in existing_items_dict:
                # Update existing item
                item = existing_items_dict[item_id]
            
                # Handle chosen_material_id if present
                if 'chosen_material_id' in item_data:
                    material_id = item_data.pop('chosen_material_id')
                    if material_id:
                        try:
                            material = MaterialDescription.objects.get(id=material_id)
                            item.chosen_material = material
                        except MaterialDescription.DoesNotExist:
                            pass
                
                # Update all fields except 'id'
                for field, value in item_data.items():
                    if field != 'id':
                        setattr(item, field, value)
                
                item.save()
                updated_item_ids.add(item_id)
            else:
                # Create a new item
                item_create_data = item_data.copy()
                
                # Handle chosen_material_id
                if 'chosen_material_id' in item_create_data:
                    material_id = item_create_data.pop('chosen_material_id')
                    if material_id:
                        try:
                            material = MaterialDescription.objects.get(id=material_id)
                            item_create_data['chosen_material'] = material
                        except MaterialDescription.DoesNotExist:
                            pass

                # Remove 'id' if it exists but is None, 0, or empty
                if 'id' in item_create_data:
                    item_create_data.pop('id')

                # Create new item
                new_item = EstimateItem.objects.create(
                    estimate=estimate, 
                    **item_create_data
                )
                # Don't add to updated_item_ids since it's new
        
        # Delete items that were not included in the update
        items_to_delete = existing_item_ids - updated_item_ids
        if items_to_delete:
            estimate.items.filter(id__in=items_to_delete).delete()