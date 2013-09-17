from django.forms import ModelForm

from suit.widgets import AutosizedTextarea, EnclosedInput, NumberInput


class OriginForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xxlarge'}),
        }


class OriginPathForm(OriginForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xxlarge'}),
            'path': EnclosedInput(prepend='icon-folder-open', attrs={'class': 'input-xxlarge'}),
        }


class OriginUploadedFileForm(OriginForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xxlarge'}),
            'path': EnclosedInput(prepend='icon-folder-open', attrs={'class': 'input-xxlarge'}),
        }


class OriginURLFileForm(OriginForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xxlarge'}),
            'url': EnclosedInput(prepend='icon-globe', attrs={'class': 'input-xxlarge'}),
        }


class OriginRESTAPIForm(OriginForm):
    class Meta(OriginForm.Meta):
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xxlarge'}),
            'url': EnclosedInput(prepend='icon-globe', attrs={'class': 'input-xxlarge'}),
        }


class OriginSOAPWebServiceForm(OriginForm):
    class Meta(OriginForm.Meta):
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xxlarge'}),
            'wsdl_url': EnclosedInput(prepend='icon-globe'),
            'parameters': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xxlarge'}),
        }


class OriginPythonScriptForm(OriginForm):
    class Meta(OriginForm.Meta):
        widgets = {
            'script_text': AutosizedTextarea(attrs={'rows': 5, 'class': 'input-xxlarge'}),
        }
