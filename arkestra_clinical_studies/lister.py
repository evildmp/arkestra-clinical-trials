from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from arkestra_utilities.generic_lister import (
    ArkestraGenericLister, ArkestraGenericList, ArkestraGenericFilterList,
    ArkestraGenericFilterSet
    )
from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE

from .models import Study


# we're going to have a list of Studies that we can search, filter and paginate
# the ArkestraGenericFilterSet provides us with some of that machinery
class StudiesFilterSet(ArkestraGenericFilterSet):
    # the fields we want to be able to filter on
    fields = ["date", "status", "studytype"]


class StudiesListMixin(object):
    def set_items_for_entity(self):
        # if we're not in MULTIPLE_ENTITY_MODE, just leave self.items alone
        if MULTIPLE_ENTITY_MODE and self.entity:
            # we want to include any item that has any relationship with any
            # of the descendants of the entity we're looking at
            # get a list of all those entities
            entities = self.entity.get_descendants(
                include_self=True
                ).values_list('id', flat=True)

            # get the Studies that have a relationship with any item in that list
            self.items = self.items.filter(
                Q(hosted_by__in=entities) | Q(publish_to__in=entities) |
                Q(funding_body__in=entities) | Q(sponsor__in=entities) |
                Q(clinical_centre__in=entities)
                ).distinct()


# the class that produces the list of items, based on ArkestraGenericFilterList
class StudiesList(StudiesListMixin, ArkestraGenericFilterList):
    # it must have a filter_set class
    filter_set = StudiesFilterSet
    # the model we're listing
    model = Study
    # the text search fields - each one is a dictionary
    search_fields = [
        {
            # the field as its name appears in the URL: ?text=
            "field_name": "text",
            # a label for the field
            "field_label": "Search title/summary",
            # the placeholder text in the search widget
            "placeholder": "Search",
            # the model fields we want to search through
            "search_keys": [
                "title__icontains",
                "summary__icontains",
                ],
            },
        ]
    # we want to override the generic list item template
    item_template = "clinical_studies/study_list_item.html"

    # we need our own build() method to override the generic one
    def build(self):
        # get the listable (by default, published and shown in lists) items
        self.items = self.model.objects.listable_objects()
        # we'll limit the items according to the appropriate entity - the
        # method that does this is defined in the StudiesListMixin
        self.set_items_for_entity()
        # and limit by search terms
        self.filter_on_search_terms()
        # and set up the filter for rendering
        self.itemfilter = self.filter_set(self.items, self.request.GET)



# the Lister class is the one that determines which lists to display, along
# with the surrounding furniture - in the case of Studies, it's just one List,
# but we could have more
class StudiesLister(ArkestraGenericLister):
    # a list of available List classes
    listkinds = [("studies", StudiesList)]
    # the List classes we want to use
    display = "studies"


class StudiesMenuList(StudiesListMixin, ArkestraGenericList):
    model = Study
    heading_text = _(u"News")

    def build(self):
        # get the listable (by default, published and shown in lists) items
        self.items = self.model.objects.listable_objects()
        # we'll limit the items according to the appropriate entity - the
        # method that does this is defined in the StudiesListMixin
        self.set_items_for_entity()


class StudiesMenuLister(ArkestraGenericLister):
    listkinds = [("studies", StudiesMenuList)]
    display = "studies"
