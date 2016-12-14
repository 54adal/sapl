from rest_framework.filters import DjangoFilterBackend
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from sapl.api.serializers import MobileSessaoPlenariaSerializer
from sapl.sessao.models import SessaoPlenaria


class MobileSessaoPlenariaViewSet(ListModelMixin,
                                  RetrieveModelMixin,
                                  GenericViewSet):

    permission_classes = (AllowAny,)
    serializer_class = MobileSessaoPlenariaSerializer
    queryset = SessaoPlenaria.objects.all()
    pagination_class = None
