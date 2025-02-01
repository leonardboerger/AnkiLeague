from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Felder in der Listenansicht
    list_display = ('anki_uid', 'name')
    
    # Suchfelder
    search_fields = ('name', 'anki_uid')
    
    # Filteroptionen
    list_filter = ('name',)
    
    # Felder im Bearbeitungsformular
    fields = ('anki_uid', 'name')
    
    # Schreibgeschützte Felder
    readonly_fields = ('anki_uid',)
    
    # Standard-Sortierung
    ordering = ('name',)
    
    # Anzahl der Einträge pro Seite
    list_per_page = 20
    
    # Zeigt die UUID im Detail an
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Beim Bearbeiten eines bestehenden Objekts
            return self.readonly_fields + ('anki_uid',)
        return self.readonly_fields