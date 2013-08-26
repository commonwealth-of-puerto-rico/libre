from __future__ import absolute_import

import HTMLParser
import logging

from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Field, MultiField
from crispy_forms.bootstrap import FormActions, InlineRadios

from data_drivers.query import Query
from data_drivers.literals import JOIN_TYPE_AND, JOIN_TYPE_CHOICES, JOIN_TYPES
from data_drivers.models import Source
from data_drivers.utils import parse_request

logger = logging.getLogger(__name__)
htmlparser = HTMLParser.HTMLParser()
renderer_choices = (
    ('json', _('JSON')),
    ('xml', _('XML')),
    ('map_leaflet', _('Leaflet')),
    ('api', _('Browseable API')),
)


class ClientForm(forms.Form):
    server = forms.CharField(label=_('Server'))
    source = forms.ModelChoiceField(label=_('Source'), queryset=Source.objects.none(), to_field_name='slug')
    filters = forms.CharField(label=_('Filter'), widget=forms.Textarea, required=False)
    as_nested_list = forms.BooleanField(label=_('As nested list'), required=False)
    as_dict_list = forms.BooleanField(label=_('As dictionay list'), required=False)
    json_path = forms.CharField(label=_('JSON path'), required=False)
    groups = forms.CharField(label=_('Groups'), required=False)
    aggregates = forms.CharField(label=_('Aggregates'), required=False)
    renderer = forms.ChoiceField(label=_('Format'), choices=renderer_choices)
    query_string = forms.CharField(label=_('Query string'), widget=forms.Textarea, required=False)

    join_type = forms.ChoiceField(
        choices=JOIN_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial=JOIN_TYPE_AND,
        required=False
    )

    helper = FormHelper()
    helper.layout = Layout(
        Div(
            Div('server', css_class='span5'),
            Div('source', css_class='span5'),
            Div(InlineRadios('join_type'), css_class='span2'),

            Div(Field('filters', rows=2, css_class='span12'), css_class='span12'),
            Div(Field('groups', rows='1', css_class='span4'), css_class='span4'),
            Div(Field('aggregates', rows='1', css_class='span4'), css_class='span4'),
            Div(Field('json_path', rows='1', css_class='span4'), css_class='span4'),

            Div(MultiField(_('Result flattening'), Field('as_nested_list'), Field('as_dict_list')), css_class='span2'),
            Div(Field('renderer', rows='3', css_class='span1'), css_class='span1'),

            Div(Field('query_string', rows='3', css_class='span7'), css_class='span7'),

            Div(
                FormActions(
                    Submit('save_changes', _('Commit'), css_class="btn-primary"),
                    #Submit('clear', _('Clear')),
                ),
                css_class='span2'),
            css_class='controls controls-row'),
    )

    def capture_request(self, request):
        self.query = Query(None)
        self.query.parse_query(parse_request(request))

        initial = {
            'filters': u'&'.join(['%(field)s__%(filter_name)s=%(original_value)s' % filter for filter in self.query.filters]),
            'as_nested_list': self.query.as_nested_list,
            'as_dict_list': self.query.as_dict_list,
            'json_path': self.query.json_path,
            'join_type': self.query.join_type,
            'groups': u'&'.join(self.query.groups),
            'aggregates': u'&'.join(self.query.aggregates),
        }

        logger.debug('initial: %s' % initial)

        for field, value in initial.items():
            try:
                self.fields[field].initial = value
            except KeyError:
                pass

        self.fields['result'].initial = _('No results')

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(ClientForm, self).__init__(*args, **kwargs)
        self.fields['source'].queryset = Source.allowed.for_user(request.user)

        if self.is_valid():
            new_data = self.data.copy()
            new_data['query_string'] = self.compose_query_string()
            self.data = new_data

    def compose_query_string(self):
        cleaned_data = self.data
        result = []

        if cleaned_data.get('filters'):
            result.append(cleaned_data['filters'])

        if cleaned_data.get('groups'):
            result.append('_group_by=%s' % cleaned_data['groups'])

        if cleaned_data.get('aggregates'):
            for aggregate in cleaned_data['aggregates'].split(','):
                try:
                    result.append('_aggregate__%s=%s' % tuple(aggregate.split('=')))
                except TypeError:
                    pass

        if cleaned_data.get('json_path'):
            result.append('_json_path=%s' % cleaned_data['json_path'])

        if cleaned_data.get('as_nested_list'):
            result.append('_as_nested_list')

        if cleaned_data.get('as_dict_list'):
            result.append('_as_dict_list')

        result.append('_format=%s' % cleaned_data['renderer'])

        result.append('_join_type=%s' % JOIN_TYPES[int(cleaned_data['join_type'])])

        query_string = self.unescape_html('&'.join(result))

        if cleaned_data.get('source'):
            query_string = cleaned_data['server'] + reverse('source-get_all', args=[cleaned_data['source']]) + '?' + query_string
            if 'http://' not in cleaned_data['server']:
                query_string = 'http://' + query_string

        return query_string

    def unescape_html(self, string):
        return htmlparser.unescape(string).replace('%5B', '[').replace('%5D', ']')
