from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny

from . import utils


class Choices:
    def __init__(self, *keys):
        self._keys = list(keys)

    def __repr__(self):
        s = ""
        for index, key in self.as_choices_list():
            s += f"{index} : {key}\n"
        return s

    def __getattr__(self, key):
        try:
            return self._keys.index(key)
        except ValueError:
            return super().__getattr__(key)

    def __getitem__(self, index):
        if index <= 0:
            raise IndexError(index)
        return self._keys[index - 1]

    def as_choices_list(self):
        return list(enumerate(self._keys, 1))


class ChoicesViewSet(ViewSet):
    # Must be specified in defining ViewSet
    choices_obj = None

    permission_classes = (AllowAny,)

    def list(self, request):
        data = utils.tuple2dict(
            self.choices_obj.as_choices_list(),
            keys=('value', 'label'),
            many=True
        )
        return Response(data)

    def retrieve(self, request, pk=None):
        pk = int(pk)
        try:
            label = self.choices_obj[pk]
        except IndexError:
            raise NotFound(detail="Item not found", code=404)
        else:
            return Response({
                'value': pk,
                'label': label,
            })
