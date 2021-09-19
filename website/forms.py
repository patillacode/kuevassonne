from django import forms

from .models import ExpansionInGame, Image, Player, PlayerInGame, Record


class CreatePlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': (
                        'appearance-none focus:outline-none text-white bg-transparent'
                    ),
                    'placeholder': 'Nombre del jugador',
                }
            )
        }


class CreatePlayerInGameForm(forms.ModelForm):
    class Meta:
        model = PlayerInGame
        fields = ('player', 'color')
        widgets = {
            'player': forms.Select(
                attrs={
                    'class': (
                        'inline-flex justify-center w-full rounded-md border'
                        ' border-gray-300 shadow-sm px-4 py-2 bg-white text-sm'
                        ' font-medium text-gray-700 hover:bg-gray-50 focus:outline-none'
                        ' focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100'
                        ' focus:ring-yellow-500'
                    )
                }
            ),
            'color': forms.Select(
                attrs={
                    'class': (
                        'inline-flex justify-center w-full rounded-md border'
                        ' border-gray-300 shadow-sm px-4 py-2 bg-white text-sm'
                        ' font-medium text-gray-700 hover:bg-gray-50 focus:outline-none'
                        ' focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100'
                        ' focus:ring-yellow-500'
                    )
                }
            ),
        }


class CreateExpansionInGameForm(forms.ModelForm):
    class Meta:
        model = ExpansionInGame
        fields = ('expansion', 'use_rules', 'use_tiles')
        widgets = {
            'expansion': forms.Select(
                attrs={
                    'class': (
                        'inline-flex justify-center w-full rounded-md border'
                        ' border-gray-300 shadow-sm px-4 py-2 bg-white text-sm'
                        ' font-medium text-gray-700 hover:bg-gray-50 focus:outline-none'
                        ' focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100'
                        ' focus:ring-yellow-500'
                    )
                }
            )
        }


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image', 'name')
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': (
                        'appearance-none focus:outline-none text-white bg-transparent w-full my-2'
                    ),
                    'placeholder': 'Nombre de la imagen (opcional)',
                }
            ),
            'image': forms.ClearableFileInput(
                attrs={
                    'class': (
                        'appearance-none focus:outline-none text-white bg-transparent w-full my-2'
                    ),
                }
            ),
        }


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ('name', 'image', 'description', 'game')
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': (
                        'appearance-none focus:outline-none text-white bg-transparent w-full my-2'
                    ),
                    'placeholder': 'Nombre del récord',
                }
            ),
            'image': forms.ClearableFileInput(
                attrs={
                    'class': (
                        'appearance-none focus:outline-none text-white bg-transparent w-full my-2'
                    ),
                }
            ),
            'game': forms.Select(
                attrs={
                    'class': (
                        'inline-flex justify-center w-full rounded-md border'
                        ' border-gray-300 shadow-sm mx-auto px-4 py-2 bg-white text-sm'
                        ' focus:outline-none text-black'
                    )
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': (
                        'w-full p-2 text-gray-700 border rounded-lg focus:outline-none'
                        ' mx-auto mb-4'
                    ),
                    'placeholder': 'Descripción del récord...',
                }
            ),
        }
