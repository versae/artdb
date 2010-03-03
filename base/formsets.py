# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.forms import formsets, widgets
from django.forms.fields import BooleanField
from django.forms.models import BaseInlineFormSet
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from base.widgets import AnchorWidget

BLANK_FORM = 'BLANK_FORM'


class BaseDynamicInlineFormSet(BaseInlineFormSet):
    __metaclass__ = widgets.MediaDefiningClass

    class Media:
        js = ("%sjs/BaseDynamicFormSet.js" % settings.MEDIA_URL, )

    def __init__(self, *args, **kwargs):
        addition_text = kwargs.pop('addition_text', None)
        addition_js = kwargs.pop('addition_js', '')
        super(BaseDynamicInlineFormSet, self).__init__(*args, **kwargs)
        if not addition_text:
            if len(self.forms):
                addition_text = _('Add another')
            else:
                addition_text = _('Add')
        if self.can_delete:
            dynamic_addition = {}
            form_id = self.management_form.auto_id % self.management_form.prefix
            # Javascript actions
            js_delete = "javascript:{BaseDynamicFormSet.markAsDeleted('%s-%s-', '%s');}"
            js_add = "javascript:{BaseDynamicFormSet.addOther('%s', '%s', '%s', '%s', '%s', '%s');}"
            # Deletion field
            widget = AnchorWidget(attrs={'href': mark_safe(js_add % (form_id,
                                                                     self.__hash__(),
                                                                     BLANK_FORM,
                                                                     formsets.INITIAL_FORM_COUNT,
                                                                     formsets.TOTAL_FORM_COUNT,
                                                                     addition_js))},
                                  text_shown=addition_text)
            dynamic_addition.update({'addition_field': widget.render(name="%s-%s"
                                                                          % (self.management_form.prefix,
                                                                             formsets.DELETION_FIELD_NAME))})
            # Add blank form
            blank_widget = widgets.CheckboxInput(attrs={'onchange': mark_safe(js_delete
                                                                    % (form_id, BLANK_FORM,
                                                                       formsets.DELETION_FIELD_NAME))})
            blank_field = BooleanField(label=_('Delete'), required=False, widget=blank_widget)
            blank_form = self.form(prefix="%s-%s" % (self.management_form.prefix, BLANK_FORM))
            blank_form.fields.update({"%s" % formsets.DELETION_FIELD_NAME: blank_field})
            # Get all as_<tag> methods for forms
            as_methods = [m for m in dir(blank_form) if (m.startswith('as_')
                                                         and callable(getattr(blank_form, m)))]
            for as_method in as_methods:
                field_as = forms.CharField(initial=simplejson.dumps(getattr(blank_form, as_method)()),
                                           widget=forms.HiddenInput)
                self.management_form.fields.update({'%s-%s' % (BLANK_FORM, as_method): field_as})
                self_hash = self.__hash__()
                dynamic_addition[as_method] = mark_safe("""
                    <noscript id="%s"></noscript>
                    <script language="javascript" type="text/javascript">
                    BaseDynamicFormSet.asMethod["%s"] = "%s";
                    </script>""" % (self_hash, self_hash, as_method))
            setattr(self, 'dynamic_addition', dynamic_addition)

    def add_fields(self, form, index):
        super(BaseDynamicInlineFormSet, self).add_fields(form, index)
        if self.can_delete:
            form_id = self.management_form.auto_id % self.management_form.prefix
            js_delete = "javascript:{BaseDynamicFormSet.markAsDeleted('%s-%s-', '%s');}"
            widget = widgets.CheckboxInput(attrs={'onchange': mark_safe(js_delete
                                                              % (form_id, index,
                                                              formsets.DELETION_FIELD_NAME))})
            form.fields[formsets.DELETION_FIELD_NAME].widget = widget
