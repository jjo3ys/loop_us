# import json
# from elasticsearch import Elasticsearch 

# es = Elasticsearch([{'host':'localhost', 'port':'8000'}])

# es.indices.create(
#     index="user_api",
#     body={
#         "settings":{
#             "index":{
#                 "analysis":{
#                     "analyzer":{
#                         "my_analyzer":{
#                             "type":"custom",
#                             "tokenizer":"nori_tokenizer"
#                         }
#                     }
#                 }
#             }
#         },
#          "mappings":{
#             "properties":{
#                 "real_name":{
#                     "type":"text",
#                     "analyzer":"my_analyzer"
#                 },
#                 "departemnt":{
#                     "type":"text",
#                     "analyzer":"my_analyzer"
#                 },
#                 "id":{
#                     "type":"long"
#                 }
#             }
#         }
#     }
# )

# from django_elasticsearch_dsl import Document
# from django_elasticsearch_dsl.registries import registry
# from elasticsearch_dsl import analyzer

# from .models import Profile
# html_strip = analyzer('html_strip', tokenizer='nori_tokenizer')
# @registry.register_document
# class ProfileDocument(Document):
#     class Index:
#         name = 'profile'
#         settings = {'number_of_shards':1,
#                     'number_of_replicas':0}
    
#     class Django:
#         model = Profile

#         fields = ['id', 'real_name', 'department']
# from haystack import indexes
# from .models import Profile

# class ProfileIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True)
#     id = indexes.IntegerField(model_attr='id')
#     department = indexes.CharField(model_attr='department')
#     school = indexes.CharField(model_attr='school')
#     real_name = indexes.CharField(model_attr='real_name')

#     def get_model(self):
#         return Profile
    
#     def index_queryset(self, using=None):
#         return self.get_model().objects.all()