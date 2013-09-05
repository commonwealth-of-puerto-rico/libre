from django.forms import ModelForm, widgets

from suit.widgets import AutosizedTextarea, EnclosedInput, NumberInput, SuitSplitDateTimeWidget


class SourceForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
            'query': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
        }


class SourceDatabaseForm(SourceForm):
    class Meta:
        widgets = {
            'query': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
        }


class SourceSpreadsheetForm(SourceForm):
    class Meta:
        widgets = {
            'limit': NumberInput(attrs={'class': 'input-mini'}),
            'path': EnclosedInput(prepend='icon-folder-open'),
            'url': EnclosedInput(prepend='icon-globe'),
            'sheet': NumberInput(attrs={'class': 'input-mini'}),
            'import_rows': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }


class SourceFixedWidthForm(SourceForm):
    class Meta:
        widgets = {
            'limit': NumberInput(attrs={'class': 'input-mini'}),
            'path': EnclosedInput(prepend='icon-folder-open'),
            'url': EnclosedInput(prepend='icon-globe'),
            'import_rows': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }


class SourceCSVForm(SourceForm):
    class Meta:
        widgets = {
            'limit': NumberInput(attrs={'class': 'input-mini'}),
            'path': EnclosedInput(prepend='icon-folder-open'),
            'url': EnclosedInput(prepend='icon-globe'),
            'import_rows': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }


class SourceWSForm(SourceForm):
    class Meta:
        widgets = {
            'wsdl_url': EnclosedInput(prepend='icon-globe'),
        }


class SourceShapeForm(SourceForm):
    class Meta:
        widgets = {
            'popup_template': AutosizedTextarea(attrs={'rows': 20, 'class': 'input-xlarge'}),
            'marker_template': AutosizedTextarea(attrs={'rows': 20, 'class': 'input-xlarge'}),
            'template_header': AutosizedTextarea(attrs={'rows': 20, 'class': 'input-xlarge'}),
            'limit': NumberInput(attrs={'class': 'input-mini'}),
            'path': EnclosedInput(prepend='icon-folder-open'),
            'url': EnclosedInput(prepend='icon-globe'),
        }


# Column Forms


class CSVColumnForm(ModelForm):
    class Meta:
        widgets = {
            'skip_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'import_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'name': widgets.TextInput(attrs={'class': 'input-small'}),
            'default': EnclosedInput(attrs={'class': 'input-mini'}),
            'data_type': widgets.Select(attrs={'class': 'input-small'}),
        }


class SpreadsheetColumnForm(ModelForm):
    class Meta:
        widgets = {
            'skip_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'import_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'name': widgets.TextInput(attrs={'class': 'input-small'}),
            'default': EnclosedInput(attrs={'class': 'input-mini'}),
            'data_type': widgets.Select(attrs={'class': 'input-small'}),
        }


class ShapefileColumnForm(ModelForm):
    class Meta:
        widgets = {
            'name': widgets.TextInput(attrs={'class': 'input-small'}),
            'new_name': widgets.TextInput(attrs={'class': 'input-small'}),
            'default': EnclosedInput(attrs={'class': 'input-mini'}),
            'data_type': widgets.Select(attrs={'class': 'input-small'}),
        }


class LeafletMarkerForm(ModelForm):
    class Meta:
        widgets = {
            'icon_anchor_x': widgets.TextInput(attrs={'class': 'input-small'}),
            'icon_anchor_y': widgets.TextInput(attrs={'class': 'input-small'}),
            'shadow_anchor_x': widgets.TextInput(attrs={'class': 'input-small'}),
            'shadow_anchor_y': widgets.TextInput(attrs={'class': 'input-small'}),
            'popup_anchor_x': widgets.TextInput(attrs={'class': 'input-small'}),
            'popup_anchor_y': widgets.TextInput(attrs={'class': 'input-small'}),
        }


class RESTResultColumnForm(ModelForm):
    class Meta:
        widgets = {
            'skip_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'import_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'name': widgets.TextInput(attrs={'class': 'input-small'}),
            'new_name': widgets.TextInput(attrs={'class': 'input-small'}),
            'default': EnclosedInput(attrs={'class': 'input-mini'}),
            'data_type': widgets.Select(attrs={'class': 'input-small'}),
        }


class WebServiceColumnForm(ModelForm):
    class Meta:
        widgets = {
            'skip_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'import_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'name': widgets.TextInput(attrs={'class': 'input-small'}),
            'new_name': widgets.TextInput(attrs={'class': 'input-small'}),
            'default': EnclosedInput(attrs={'class': 'input-mini'}),
            'data_type': widgets.Select(attrs={'class': 'input-small'}),
        }
