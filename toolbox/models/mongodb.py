from mongoengine import Document, StringField, EmbeddedDocument, EmbeddedDocumentField, BooleanField, ListField
import toolbox.config as config


class WidgetData(EmbeddedDocument):
    display_widget: BooleanField = BooleanField()
    display_fields: ListField = ListField(StringField())
    widget_type: StringField = StringField()


class Widgets(EmbeddedDocument):
    memory: WidgetData = EmbeddedDocumentField(WidgetData)
    system: WidgetData = EmbeddedDocumentField(WidgetData)
    partitions: WidgetData = EmbeddedDocumentField(WidgetData)
    cpu: WidgetData = EmbeddedDocumentField(WidgetData)
    network: WidgetData = EmbeddedDocumentField(WidgetData)
    gpu: WidgetData = EmbeddedDocumentField(WidgetData)


class DashboardProfiles(Document):
    meta = {'collection': config.DASHB_DB_COL}
    profile_name: StringField = StringField(required=True)
    widgets: Widgets = EmbeddedDocumentField(Widgets)


