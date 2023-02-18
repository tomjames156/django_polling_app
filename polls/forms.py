from django import forms

class SearchForm(forms.Form):
    """Creates a search form"""
    search_text = forms.CharField(max_length=10)#label="Searching for: ", max_length=10)