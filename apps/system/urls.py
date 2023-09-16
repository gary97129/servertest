from django.urls import path, include
from .views import TaskList, UserViewSet, OrganizationViewSet, PermissionViewSet, RoleViewSet, PositionViewSet, TestView, DictTypeViewSet, DictViewSet, PTaskViewSet, PatientViewSet, OrderViewSet, ClinicViewSet, DoctorViewSet, LaboratoriesViewSet,manufacturersViewSet
from rest_framework import routers
# from system.views import show_one


router = routers.DefaultRouter()
router.register('user', UserViewSet, basename="user")
router.register('organization', OrganizationViewSet, basename="organization")
router.register('permission', PermissionViewSet, basename="permission")
router.register('role', RoleViewSet, basename="role")
router.register('position', PositionViewSet, basename="position")
router.register('dicttype', DictTypeViewSet, basename="dicttype")
router.register('dict', DictViewSet, basename="dict")
router.register('ptask', PTaskViewSet, basename="ptask")
router.register('patient', PatientViewSet, basename="patient")
router.register('order', OrderViewSet, basename="order")
router.register('clinic', ClinicViewSet, basename="clinic")
router.register('doctor', DoctorViewSet, basename="doctor")
router.register('laboratories', LaboratoriesViewSet, basename="laboratories")
router.register('manufacturers', manufacturersViewSet, basename="manufacturers")
urlpatterns = [
    path('', include(router.urls)),
    path('task/', TaskList.as_view()),
    path('test/', TestView.as_view())
]
