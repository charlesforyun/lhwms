from django.forms import ModelForm
from incoming.models import IncomingApply
from lhwms.utils.forms import FormMixin


class IncomingApplyForm(FormMixin, ModelForm):
    class Meta:
        model = IncomingApply
        fields = [
            'apply_cons_mark',
            'mat_mark',
            'mat_type',
            'pars',
            'test_result',
            'wh_mark',
            'num',
        ]