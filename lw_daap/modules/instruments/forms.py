# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Rafael Salas Robledo
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.

"""Instrument forms."""

from __future__ import absolute_import

from invenio.base.i18n import _
from invenio.utils.forms import InvenioBaseForm, InvenioForm as Form

from wtforms import HiddenField, StringField, TextAreaField,\
    SelectMultipleField, validators

from lw_daap.modules.invenio_deposit import fields
from lw_daap.modules.deposit import fields as zfields
from lw_daap.modules.invenio_deposit.filter_utils import sanitize_html, \
    strip_string
from datetime import date
from invenio.config import CFG_DATACITE_DOI_PREFIX, CFG_SITE_NAME, \
    CFG_SITE_SUPPORT_EMAIL

from lw_daap.modules.invenio_deposit.validation_utils \
    import DOISyntaxValidator, invalid_doi_prefix_validator, list_length, \
    pid_validator, required_if, \
    unchangeable

from .field_widgets import date_widget, DynamicHiddenListWidget

class SearchForm(Form):
    """Search Form."""
    p = StringField(
        validators=[validators.DataRequired()]
    )

class DeleteInstrumentForm(Form):
    delete = HiddenField(default='yes', validators=[validators.DataRequired()])

class InstrumentForm(Form):

    """Instrument Form."""

    field_sets = [
        ('Information', [
            'instrument', 'access_right', 'embargo_date', 'license', 'access_conditions', 'access_groups'
        ], {'classes': 'in'}),
    ]

    field_placeholders = {
    }

    field_state_mapping = {
    }

    #
    # Methods
    #
    def get_field_icon(self, name):
        """Return field icon."""
        return self.field_icons.get(name, '')

    def get_field_by_name(self, name):
        """Return field by name."""
        try:
            return self._fields[name]
        except KeyError:
            return None

    def get_field_placeholder(self, name):
        """Return field placeholder."""
        return self.field_placeholders.get(name, "")

    def get_field_state_mapping(self, field):
        """Return field state mapping."""
        try:
            return self.field_state_mapping[field.short_name]
        except KeyError:
            return None

    def has_field_state_mapping(self, field):
        """Check if field has state mapping."""
        return field.short_name in self.field_state_mapping

    def has_autocomplete(self, field):
        """Check if filed has autocomplete."""
        return hasattr(field, 'autocomplete')

    field_icons = {
        'instrument': 'fa fa-md fa-fw',
        'embargo_date': 'fa fa-calendar fa-fw',
        'license': 'fa fa-certificate fa-fw',
        'access_conditions': 'fa fa-pencil fa-fw',
        'access_groups': 'fa fa-group fa-fw'
    }

    instrument = fields.TitleField(
        validators=[
            validators.DataRequired(),
            validators.Length(min=5),
        ],
        description='Required.',
        filters=[
            strip_string,
        ],
        export_key='instrument',
        icon='fa fa-md fa-fw',
    )
    access_right = zfields.AccessRightField(
        label="Access right",
        description="Required. Open access uploads have considerably higher "
        "visibility on %s." % CFG_SITE_NAME,
        default="open",
        validators=[validators.DataRequired()]
    )
    embargo_date = fields.Date(
        label=_('Embargo date'),
        icon='fa fa-calendar fa-fw',
        description='Required only for Embargoed Access uploads.'
        'The date your upload will be made publicly available '
        'in case it is under an embargo period from your publisher.',
        default=date.today(),
        validators=[
            required_if('access_right', ['embargoed']),
            validators.optional()
        ],
        widget=date_widget,
        widget_classes='input-small',
        hidden=True,
        disabled=True,
    )
    license = zfields.LicenseField(
        validators=[
            required_if('access_right', ['embargoed', 'open', ]),
            validators.DataRequired()
        ],
        default='cc-zero',
        domain_data=True,
        domain_content=True,
        domain_software=True,
        description='Required. The selected license applies to all of your '
        'files displayed in the bottom of the form. If you want to upload '
        'some files under a different license, please do so in two separate'
        ' uploads. If you think a license missing is in the list, please '
        'inform us at %s.' % CFG_SITE_SUPPORT_EMAIL,
        filters=[
            strip_string,
        ],
        placeholder="Start typing a license name or abbreviation...",
        icon='fa fa-certificate fa-fw',
    )
    access_conditions = fields.TextAreaField(
        label=_('Conditions'),
        icon='fa fa-pencil fa-fw',
        description='Specify the conditions under which you grant users '
        'access to the files in your upload. User requesting '
        'access will be asked to justify how they fulfil the '
        'conditions. Based on the justification, you decide '
        'who to grant/deny access. You are not allowed to '
        'charge users for granting access to data hosted on '
        'Dataset.',
        default="",
        validators=[
            required_if('access_right', ['restricted']),
            validators.optional()
        ],
        widget=CKEditorWidget(
            toolbar=[
                ['PasteText', 'PasteFromWord'],
                ['Bold', 'Italic', 'Strike', '-',
                 'Subscript', 'Superscript', ],
                ['NumberedList', 'BulletedList', 'Blockquote'],
                ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'RemoveFormat'],
                ['Mathjax', 'SpecialChar', 'ScientificChar'], ['Source'],
                ['Maximize'],
            ],
            disableNativeSpellChecker=False,
            extraPlugins='scientificchar,mathjax,blockquote',
            removePlugins='elementspath',
            removeButtons='',
            # Must be set, otherwise MathJax tries to include MathJax via the
            # http on CDN instead of https.
            mathJaxLib='https://cdn.mathjax.org/mathjax/latest/MathJax.js?'
            'config=TeX-AMS-MML_HTMLorMML'
        ),
        filters=[
            sanitize_html(allowed_tag_whitelist=(
                CFG_HTML_BUFFER_ALLOWED_TAG_WHITELIST + ('span',)
            )),
            strip_string,
        ],
        hidden=True,
        disabled=True,
    )

    access_groups = fields.DynamicFieldList(
        fields.FormField(
            AccessGroupsForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget()),
            description=("Optional. Specify the groups you "
                         "will grant the access"),
        ),
        validators=[
            # required_if('access_right', ['restricted']),
            validators.optional()
        ],
        label=_('Access groups'),
        description='Optional. Specify the groups you will grant the access.',
        default="",
        widget=TagListWidget(template="{{title}}"),
        widget_classes=' dynamic-field-list',
        icon='fa fa-group fa-fw',
        hidden=True,
        disabled=True,
    )

    """Instrument Upload Form."""
    #
    # Form configuration
    #
    _title = _('New instrument')
    _drafting = False   # enable and disable drafting

    #
    # Grouping of fields
    #
    groups = [
        ('<i class="fa fa-info"></i> Instrument information', [
            'instrument', 'access_right', 'embargo_date', 'license', 'access_conditions', 'access_groups'
        ], {
            # 'classes': '',
            'indication': 'optional',
        }),
    ]

class EditInstrumentForm(InstrumentForm):
    pass

class IntegrateForm(Form):
    records = SelectMultipleField('records', coerce=int)
    integrate = HiddenField(default='no',
                            validators=[validators.DataRequired()])
