from django.urls import path
from .views import *

urlpatterns = [
    # 🔐 AUTH
    path('auth/login/', login_user),
    path('auth/register/', register_user),

    # 📚 COURSES
    path('courses/', get_courses),
    path('courses/<str:course_id>/', get_course_detail),

    # 🎓 ENROLL
    path('enroll/', enroll_user),
    path('enroll/<str:user_id>/', get_user_enrollments),
    path('enroll/check/<str:user_id>/<str:course_id>/', check_enrollment),

    # 👤 USER PROFILE
    path('users/<str:user_id>/', get_user_details),
    path('users/<str:user_id>/update/', update_user),
    path('users/<str:user_id>/profile-image/', get_profile_image),
    path('users/<str:user_id>/upload-image/', upload_profile_image),

    # 📊 PROGRESS
    path('progress/<str:user_id>/<str:course_id>/', get_progress),
    path('progress/update/<str:user_id>/<str:course_id>/', update_progress),

    # 💬 FEEDBACK
    path('feedbacks/<str:course_id>/', get_feedbacks),
    path('feedbacks/', post_feedback),

    # 🗣️ DISCUSSIONS
    path('discussions/<str:course_id>/', get_discussions),
    path('discussions/', post_discussion),

    # 🏆 ASSESSMENT & PERFORMANCE
    path('assessments/performance/<str:user_id>/', get_performance),
    path('assessments/<str:course_id>/', get_assessment),
    path('assessments/', submit_assessment),
]