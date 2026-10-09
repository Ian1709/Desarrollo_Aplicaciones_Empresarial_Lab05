from django.contrib import admin

from .models import Article, Author, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'num_articles')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='noticias')
    def num_articles(self, obj):
        return obj.articles.count()


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'num_articles')
    search_fields = ('name', 'email', 'bio')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='noticias')
    def num_articles(self, obj):
        return obj.articles.count()


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'categorias', 'published_at')
    list_filter = ('published_at', 'author', 'categories')
    search_fields = ('title', 'summary', 'body', 'author__name')
    date_hierarchy = 'published_at'
    filter_horizontal = ('categories',)
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'summary', 'body')}),
        ('Publicación', {'fields': ('author', 'categories', 'published_at')}),
        ('Imagen', {'fields': ('featured_image',)}),
    )

    @admin.display(description='categorías')
    def categorias(self, obj):
        return ', '.join(c.name for c in obj.categories.all()) or '—'
