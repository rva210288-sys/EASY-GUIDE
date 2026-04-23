from django.views.generic import TemplateView


class VueComponentView(TemplateView):
    template_name = 'vue-component.html'
    vue_component = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attr_str = self._build_attr_str(kwargs)
        context['tag'] = "<{} {}/>".format(self.vue_component, attr_str)
        return context

    @classmethod
    def _build_attr_str(cls, kwargs):
        attr_str = ""
        for key, value in kwargs.items():
            if isinstance(value, int):
                attr_str += ':{}="{}" '.format(key, value)
            elif isinstance(value, str):
                attr_str += '{}="{}" '.format(key, value)
        return attr_str
