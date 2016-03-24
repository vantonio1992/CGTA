# -*- coding: utf-8 -*-

from django import forms

CLASS_TYPES = (("Output Image (DNN)", "DNN"), ("Output Image (Bayes)", "Bayes"))

class DocumentForm(forms.Form):
	class_type = forms.ChoiceField(choices = CLASS_TYPES, widget = forms.RadioSelect(), help_text = "Type of Classification:")
	uploadfile = forms.ImageField(
		label='Select an image:'
    )
