from rest_framework import generics, views
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from job_listing.models import Job, ApplyJob
from .serializers import JobSerializer, ApplyJobSerializer, UserAppliedJobSerializer, GetUserApplicationsSerializer


# OPTION 1
# TODO: change this -> only logged in users should add jobs
class JobListView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    # permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class LatestJobsView(generics.ListAPIView):
    queryset = Job.objects.all().order_by('-published')[:4]
    serializer_class = JobSerializer


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


def is_valid_queryparam(param):
    return param != '' and param is not None


def filter(request):
    qs = Job.objects.all()
    title_contains_query = request.GET.get('title')
    title_contains_type = request.GET.get('type')

    if is_valid_queryparam(title_contains_query):
        qs = qs.filter(title__icontains=title_contains_query)

    elif is_valid_queryparam(title_contains_type):
        qs = qs.filter(employment_status__icontains=title_contains_type)
    return qs


class JobFilterView(generics.ListAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        qs = filter(self.request)
        return qs


class ApplyJobView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, ]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ApplyJobSerializer

    def perform_create(self, serializer):
        return serializer.save(applicant=self.request.user)


class UserAppliedJobView(views.APIView):
    serializer_class = UserAppliedJobSerializer

    def post(self, request, format=None):
        serializer = UserAppliedJobSerializer(data=request.data)
        if serializer.is_valid():
            job_id = serializer.data.get("job")
            applicant_id = serializer.data.get("applicant")
            userJob = ApplyJob.objects.filter(
                job=job_id, applicant=applicant_id)
            user_email = [user.email for user in userJob]
            return Response(user_email, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserApplicationsView(generics.ListAPIView):
    queryset = ApplyJob.objects.all().order_by('-published')[:4]
    serializer_class = JobSerializer
    GetUserApplicationsSerializer
