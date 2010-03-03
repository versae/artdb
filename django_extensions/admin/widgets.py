from django import forms
from django.conf import settings
from django.core import urlresolvers
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.template.loader import render_to_string


class ForeignKeySearchInput(forms.Select):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input
    instead in a <select> box.
    """
    # Set in subclass to render the widget with a different template
    widget_template = None
    # Set this to the patch of the search view
    search_path = '../autocomplete/'

    class Media:
        css = {
            'all': ('django_extensions/css/jquery.autocomplete.css', ),
        }
        js = (
            'django_extensions/js/jquery.js',
            'django_extensions/js/jquery.bgiframe.min.js',
            'django_extensions/js/jquery.ajaxQueue.js',
            'django_extensions/js/jquery.autocomplete.js',
            'django_extensions/js/RelatedObjectLookups.js',
        )

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        obj = self.rel.to._default_manager.get(**{key: value})
        return truncate_words(obj, 14)

    def __init__(self, rel, search_fields, admin_site_name=None, attrs=None):
        self.admin_site_name = admin_site_name
        self.search_fields = search_fields
        self.rel = rel
        super(ForeignKeySearchInput, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        output = [super(ForeignKeySearchInput, self).render(name, value,
                                                            attrs)]
        opts = self.rel.to._meta
        app_label = opts.app_label
        model_name = opts.object_name.lower()
        related_url = '../../../%s/%s/' % (app_label, model_name)
        params = self.url_parameters()
        if params:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v)
                                      for k, v in params.items()])
        else:
            url = ''
        # Call the TextInput render method directly to have more control
        output = [forms.Select.render(self, name, value, attrs)]
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        if self.admin_site_name:
            admin_related_url = urlresolvers.reverse("%s:%s_%s_change" \
                                                     % (self.admin_site_name,
                                                        app_label,
                                                        model_name),
                                                     args=("[?]", ))
        else:
            admin_related_url = ""
        context = {
            'url': url,
            'related_url': related_url,
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
            'search_path': self.search_path,
            'search_fields': ','.join(self.search_fields),
            'model_name': model_name,
            'app_label': app_label,
            'label': label,
            'name': name,
            'admin_related_url': admin_related_url,
        }
        output.append(render_to_string(self.widget_template or (
            'django_extensions/widgets/%s/%s/foreignkey_searchinput.html' \
            % (app_label, model_name),
            'django_extensions/widgets/%s/foreignkey_searchinput.html' \
            % app_label,
            'django_extensions/widgets/foreignkey_searchinput.html',
        ), context))
        output.reverse()
        return mark_safe(u''.join(output))

    def url_parameters(self):
        params = {}
        if self.rel.limit_choices_to:
            items = []
            for k, v in self.rel.limit_choices_to.items():
                if isinstance(v, list):
                    v = ','.join([str(x) for x in v])
                else:
                    v = str(v)
                items.append((k, v))
            params.update(dict(items))
        return params


class ManyToManySearchInput(forms.SelectMultiple):
    """
    A Widget for displaying ManyToManyFields in an autocomplete search input
    instead in a <select> box.
    """
    # Set in subclass to render the widget with a different template
    widget_template = None
    # Set this to the patch of the search view
    search_path = '../autocomplete/'

    class Media:
        css = {
            'all': ('django_extensions/css/jquery.autocomplete.css', ),
        }
        js = (
            'django_extensions/js/jquery.js',
            'django_extensions/js/jquery.bgiframe.min.js',
            'django_extensions/js/jquery.ajaxQueue.js',
            'django_extensions/js/jquery.autocomplete.js',
            'django_extensions/js/RelatedObjectLookups.js',
        )

    def __init__(self, rel, search_fields, admin_site_name=None, attrs=None):
        self.admin_site_name = admin_site_name
        self.search_fields = search_fields
        self.rel = rel
        super(ManyToManySearchInput, self).__init__(attrs=attrs)

    def label_for_value(self, value):
        return ''

    def render(self, name, value, attrs=None, choices=()):
        if attrs is None:
            attrs = {}
        output = [super(ManyToManySearchInput, self).render(name, value, attrs,
                                                            choices)]
        opts = self.rel.to._meta
        app_label = opts.app_label
        model_name = opts.object_name.lower()
        related_url = '../../../%s/%s/' % (app_label, model_name)
        params = self.url_parameters()
        if params:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v)
                                      for k, v in params.items()])
        else:
            url = ''
        # Call the SelectMultiple render method directly to have more control
        output = [forms.SelectMultiple.render(self, name, value, attrs,
                                              choices)]
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        if self.admin_site_name:
            admin_related_url = urlresolvers.reverse("%s:%s_%s_change" \
                                                     % (self.admin_site_name,
                                                        app_label,
                                                        model_name),
                                                     args=("[?]", ))
        else:
            admin_related_url = ""
        context = {
            'url': url,
            'related_url': related_url,
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
            'search_path': self.search_path,
            'search_fields': ','.join(self.search_fields),
            'model_name': model_name,
            'app_label': app_label,
            'label': label,
            'name': name,
            'admin_related_url': admin_related_url,
        }
        output.append(render_to_string(self.widget_template or (
            'django_extensions/widgets/%s/%s/manytomany_searchinput.html' \
            % (app_label, model_name),
            'django_extensions/widgets/%s/manytomany_searchinput.html' \
            % app_label,
            'django_extensions/widgets/manytomany_searchinput.html',
        ), context))
        output.reverse()
        return mark_safe(u''.join(output))

    def url_parameters(self):
        params = {}
        if self.rel.limit_choices_to:
            items = []
            for k, v in self.rel.limit_choices_to.items():
                if isinstance(v, list):
                    v = ','.join([str(x) for x in v])
                else:
                    v = str(v)
                items.append((k, v))
            params.update(dict(items))
        return params
