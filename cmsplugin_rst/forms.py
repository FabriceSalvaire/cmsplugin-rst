####################################################################################################

from django import forms

from .models import RstPluginModel, rst_help_text

####################################################################################################

class RstPluginForm(forms.ModelForm):

    body = forms.CharField(
                widget=forms.Textarea(attrs={
                    'rows':20,
                    'cols':80,
                    'style':'font-family:monospace'
                }),
                help_text=rst_help_text
            )

    class Meta:
        model = RstPluginModel
        fields = ["name", "header_level", "body"]
