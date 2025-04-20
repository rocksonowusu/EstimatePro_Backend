from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, Estimate,MaterialDescription, BusinessProfile
from .serializers import OnboardingSerializers, EstimateSerializer,MaterialDescriptionSerializer, BusinessProfileSerializer,UserProfileSerializer
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
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
    def get(self, request, pk, format=None):
        try:
            estimate = Estimate.objects.get(pk=pk)
        except Estimate.DoesNotExist:
            return Response({'error': 'Estimate not found'}, status=status.HTTP_404_NOT_FOUND)
        
        business_profile = getattr(estimate.created_by, 'business_profile', None)
        letterhead_url = business_profile.background_image.url if business_profile and business_profile.background_image else None

        context = {
            'estimate': estimate,
            'letterhead_url': letterhead_url
        }
        html_string = render_to_string('estimate_preview.html', context)
        
        # Generate the PDF file.
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        
        response = HttpResponse(pdf_file, content_type='application/pdf')
        
        # Log the client_name for debugging.
        logger.debug(f"Estimate ID: {estimate.id}, Client Name: {estimate.client_name}")
        client_name_title = estimate.client_name.title() if estimate.client_name else str(estimate.id)
        
        # Set the file name with the capitalized client name.
        response['Content-Disposition'] = f'inline; filename="Estimate for {client_name_title}.pdf"'
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
                status=status.HTTP_404_NOT_FOUND
            )