from django.urls import path
from .views import DeleteAccountView,UserProfileView,BusinessProfileView,OnboardingView, CreateEstimateView, EstimatePreview,MaterialDescriptionListView,GetAllEstimates,EditEstimateView

urlpatterns = [
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('estimates/', CreateEstimateView.as_view(), name='create-estimate'),
    path('all-estimates/', GetAllEstimates.as_view(), name='all-estimates'),
    path('estimates/<int:pk>/preview/', EstimatePreview.as_view(), name='estimate-preview'),
    path('material-descriptions/', MaterialDescriptionListView.as_view(), name='material-descriptions'),
    path('user-profile/', UserProfileView.as_view(), name='user-profile'),
    path('business-profile/', BusinessProfileView.as_view(), name='business-profile'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('estimates/<int:pk>/edit/', EditEstimateView.as_view(), name='edit-estimate'),
]
