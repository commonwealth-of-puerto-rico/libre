from __future__ import absolute_import

import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

import furl

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions

from data_drivers.query import Query
from data_drivers.utils import parse_request


class ClientForm(forms.Form):
    #data_source = forms.
    query_string = forms.CharField(widget=forms.Textarea, required=False)
    as_nested_list = forms.BooleanField()
    as_dict_list = forms.BooleanField()
    json_path = forms.CharField(widget=forms.Textarea, required=False)
    result = forms.CharField(widget=forms.Textarea, required=False)
    groups = forms.CharField(widget=forms.Textarea, required=False)
    aggregates = forms.CharField(widget=forms.Textarea, required=False)

    join_type = forms.ChoiceField(
        choices = (
            (1, _('OR')),
            (2, _('AND'))
        ),
        widget = forms.RadioSelect,
        initial = '1',
    )

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('query_string', css_class='input-xxlarge'),
        Field('join_type', css_class='input-xxlarge'),
        Field('groups', rows='3', css_class='input-xxlarge'),
        Field('aggregates', rows='3', css_class='input-xxlarge'),
        Field('json_path', rows='1', css_class='input-xxlarge'),
        'as_nested_list',
        'as_dict_list',
        Field('result', css_class='input-xxlarge'),


        FormActions(
            Submit('save_changes', _('Commit'), css_class="btn-primary"),
            Submit('clear', _('Clear')),
        )
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(ClientForm, self).__init__(*args, **kwargs)
        if request:
            self.parse_request(request)

    def parse_request(self, request):
        query = Query(None)
        query.parse_query(parse_request(request))

        initial={
            'query_string': u'&'.join(['%(field)s__%(filter_name)s=%(original_value)s' % filter for filter in query.filters]),
            'as_nested_list': query.as_nested_list,
            'as_dict_list': query.as_dict_list,
            'json_path': query.json_path,
            'join_type': query.join_type,
            'groups': u'&'.join(query.groups),
            'aggregates': u'&'.join(query.aggregates),
        }

        for field, value in initial.items():
            try:
                self.fields[field].initial = value
            except KeyError:
                pass

        self.fields['result'].initial = _('No results')

    def compose_query_string(self):
        result = furl.furl()
        return result
