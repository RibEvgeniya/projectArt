from django import forms
from .models import Post, Comment, Grade, Tag
from django.utils.text import slugify


class PostForm(forms.ModelForm):
    tags_input = forms.CharField(required=False, label='Теги (через запятую)')

    # Поля для JSON контента
    text_content = forms.CharField(widget=forms.Textarea, required=False, label='Текст')
    materials = forms.CharField(required=False, label='Материалы')
    technique = forms.CharField(required=False, label='Техника')
    size = forms.CharField(required=False, label='Размер')
    stages = forms.CharField(widget=forms.Textarea, required=False, label='Этапы работы')
    duration = forms.CharField(required=False, label='Длительность')
    difficulty = forms.ChoiceField(
        choices=[('beginner', 'Начинающий'), ('intermediate', 'Средний'), ('advanced', 'Продвинутый')], required=False)

    class Meta:
        model = Post
        fields = ['title', 'category', 'content_type', 'featured_image', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        post = super().save(commit=False)
        content = {}
        ct = post.content_type
        if ct:
            if ct.slug == 'finished':
                content['text'] = self.cleaned_data.get('text_content', '')
                content['materials'] = self.cleaned_data.get('materials', '')
                content['technique'] = self.cleaned_data.get('technique', '')
                content['size'] = self.cleaned_data.get('size', '')
            elif ct.slug == 'process':
                stages = self.cleaned_data.get('stages', '').split('\n')
                content['stages'] = [s.strip() for s in stages if s.strip()]
            elif ct.slug == 'tutorial':
                content['duration'] = self.cleaned_data.get('duration', '')
                content['difficulty'] = self.cleaned_data.get('difficulty', '')
                stages = self.cleaned_data.get('stages', '').split('\n')
                content['stages'] = [s.strip() for s in stages if s.strip()]
        post.content = content
        if commit:
            post.save()
            tags = [t.strip().lower() for t in self.cleaned_data.get('tags_input', '').split(',') if t.strip()]
            post.tags.clear()
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name, slug=slugify(tag_name))
                post.tags.add(tag)
        return post


class CommentForm(forms.ModelForm):
    composition = forms.IntegerField(min_value=1, max_value=5, required=False, label='Композиция')
    technique = forms.IntegerField(min_value=1, max_value=5, required=False, label='Техника')
    color = forms.IntegerField(min_value=1, max_value=5, required=False, label='Цвет')
    overall = forms.IntegerField(min_value=1, max_value=5, required=False, label='Общее впечатление')

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ваш комментарий...'})}