from django.forms import ModelForm, widgets

from suit.widgets import AutosizedTextarea, EnclosedInput, NumberInput


class SourceForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
            'limit': NumberInput(attrs={'class': 'input-mini'}),
        }


class SourceSpreadsheetForm(SourceForm):
    class Meta:
        widgets = {
            'sheet': NumberInput(attrs={'class': 'input-mini'}),
            'import_rows': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }


class SourceFixedWidthForm(SourceForm):
    class Meta:
        widgets = {
            'import_rows': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }


class SourceCSVForm(SourceForm):
    class Meta:
        widgets = {
            'import_rows': AutosizedTextarea(attrs={'rows': 1, 'class': 'input-xlarge'}),
        }


class SourceShapeForm(SourceForm):
    class Meta:
        widgets = {
            'popup_template': AutosizedTextarea(attrs={'rows': 20, 'class': 'input-xlarge'}),
            'marker_template': AutosizedTextarea(attrs={'rows': 20, 'class': 'input-xlarge'}),
            'template_header': AutosizedTextarea(attrs={'rows': 20, 'class': 'input-xlarge'}),
        }


# Column Forms

class FixedWidthColumnForm(ModelForm):
    class Meta:
        widgets = {
            'skip_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'import_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'name': widgets.TextInput(attrs={'class': 'input-small'}),
            'size': widgets.TextInput(attrs={'class': 'input-small'}),
            'default': EnclosedInput(attrs={'class': 'input-mini'}),
            'data_type': widgets.Select(attrs={'class': 'input-small'}),
        }


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
            'name': widgets.TextInput(attrs={'class': 'input-small'}),
            'default': EnclosedInput(attrs={'class': 'input-mini'}),
            'data_type': widgets.Select(attrs={'class': 'input-small'}),
            'skip_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'import_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
        }


class ShapefileColumnForm(ModelForm):
    class Meta:
        widgets = {
            'name': widgets.TextInput(attrs={'class': 'input-small'}),
            'new_name': widgets.TextInput(attrs={'class': 'input-small'}),
            'default': EnclosedInput(attrs={'class': 'input-mini'}),
            'data_type': widgets.Select(attrs={'class': 'input-small'}),
            'skip_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'import_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
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


class SimpleSourceColumnForm(ModelForm):
    class Meta:
        widgets = {
            'skip_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'import_regex': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-small'}),
            'name': widgets.TextInput(attrs={'class': 'input-small'}),
            'new_name': widgets.TextInput(attrs={'class': 'input-small'}),
            'default': EnclosedInput(attrs={'class': 'input-mini'}),
            'data_type': widgets.Select(attrs={'class': 'input-small'}),
        }
