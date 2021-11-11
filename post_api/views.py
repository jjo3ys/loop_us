from django.shortcuts import render
from project_api.models import Project
from project_api.serializers import ProjectSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import json

from .serializers import PostingContentsSerializer, PostingSerializer, PostingContentsImageSerializer

from .models import Posting, PostingContents


# Create your views here.

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def posting_upload(request, proj_idx):
    if request.method == "POST":
        postingSZ = PostingSerializer(data={
            'author': request.user.id,
            'project': proj_idx,
            'title' : request.data['title'], 
            'thumbnail' : request.FILES.get('thumbnail')
        })
        if postingSZ.is_valid():
            print("PostingContentSZ.errors:", postingSZ.errors)
            postingSZ.save()
        else:
            return Response('유효하지 않은 형식입니다.', status=status.HTTP_404_NOT_FOUND)
        postingContList = json.JSONDecoder().decode(request.data['posting_contents'])

        return_list = []
        i = 0

        for line in postingContList:
            if line['type'] == 'title' or line['type'] == 'content':
                PostingContentSZ = PostingContentsSerializer(data={
                    'posting': postingSZ.data['id'],
                    'contentType': line['type'],
                    'content': line['contents']
            })
                if PostingContentSZ.is_valid():
                    print("String PostingContentSZ.errors:", PostingContentSZ.errors)
                    PostingContentSZ.save()

                else:
                    return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)

                return_list.append(
                    {
                        "type": PostingContentSZ.data['contentType'],
                        "contents": PostingContentSZ.data['content'],
                        "date": PostingContentSZ.data['date'],
                    }
                )

            elif line['type'] == 'imageURL':
                PostingContentSZ = PostingContentsSerializer(data={
                    'posting': postingSZ.data['id'],
                    'contentType': line['type'],
                    'content': line['contents']
            })
                if PostingContentSZ.is_valid():
                    print('imageFILE')
                    print("ImageURL PostingContentSZ.errors:", PostingContentSZ.errors)
                    PostingContentSZ.save()
                else:
                    return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)

                try:
                    return_list.append(
                    {
                        "type": PostingContentSZ.data['contentType'],
                        "contents": PostingContentSZ.data['content'],
                        "date": PostingContentSZ.data['date'],
                    }
                )
                except:
                    return Response('Error', status=status.HTTP_403_FORBIDDEN)
            elif line['type'] == 'imageFILE':
                PostingContentSZ = PostingContentsSerializer(data={
                    'posting': postingSZ.data['id'],
                    'contentType': line['type'],
                    'content': line['contents']
            })
                if PostingContentSZ.is_valid():
                    print("imageFILE PostingContentSZ.errors:", PostingContentSZ.errors)
                    PostingContentSZ.save()
                else:
                    return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)
                print(i)
                postingContImg = request.FILES.getlist('image')[i]
                print(postingContImg)
                print(len(postingContImg))
                print('위에 순서나온다!')
                i = i + 1
                PostingContentImgSZ = PostingContentsImageSerializer(data={
                    'author': request.user.id,
                    'PostingContents': postingSZ.data['id'],
                    'image': postingContImg})
                PostingContentImgSZ.is_valid()
                print("imageFILEImageDB PostingContentImgSZ.errors:", PostingContentImgSZ.errors)

                try:
                    if PostingContentImgSZ.is_valid():
                        PostingContentImgSZ.save()
                    else:
                        print("데이터가 저장되지 않았습니다.")
                except:
                    return Response('유효하지 않은 image 형식입니다.??', status=status.HTTP_403_FORBIDDEN)
       
                return_list.append(
                    {
                        "type": PostingContentSZ.data['contentType'],
                        "contents": PostingContentImgSZ.data['image'],
                        "date": PostingContentSZ.data['date']
                    }
                )
                 # return Response('upload completed\nresponse_values:', return_list)
        return Response(return_list)
            

        # except:
        #     return Response('Request isn\'t valid.', status=status.HTTP_404_NOT_FOUND)

    else:
        return Response('Request iasn\'t valid', status=status.HTTP_404_NOT_FOUND)    

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def posting_list_load(request, proj_idx):
    if request.method == 'GET':
        try:
            postings = Posting.objects.filter(project=proj_idx)    
        except Posting.DoesNotExist:
            return Response('The postings aren\'t valid', status=status.HTTP_404_NOT_FOUND)

        postingSZ = PostingSerializer(postings, many=True)

        return_dict = {
            'posting_list' : postingSZ.data
        }
        return Response(return_dict)
    else:
        return Response('Request isn\'t valid.', status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def specific_posting_load(request, posting_idx):
    if request.method == 'GET':
        try:
            posting = Posting.objects.get(id=posting_idx)

        except Posting.DoesNotExist:
            return Response('The posting isn\'t valid', status=status.HTTP_404_NOT_FOUND)

        try:
            postingContents = 'default'
            postingContents = PostingContents.objects.filter(posting=posting_idx)
        
            if postingContents == 'default':
                return Response('Empty posting')
                

        except PostingContents.DoesNotExist:
            return Response('Contents aren\'t valid.', status=status.HTTP_404_NOT_FOUND)
    
    
        postingSZ = PostingSerializer(posting)

        return_dict = {
            'posting_info': postingSZ.data,
        }

        return Response(return_dict)

    else:
        return Response('Request isn\'t valid.', status=status.HTTP_404_NOT_FOUND)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def specific_posting_update(request, posting_idx):
    # if str(request.user.id) == user_idx:
    postingcont = PostingContents.objects.filter(posting=posting_idx)
    postingcont.delete()
    
    try:
        ContentsList = json.JSONDecoder().decode(request.data['posting_list'])
        return_list = []
        i = 0
        for line in ContentsList:
            if line['type'] == 'title' or line['type'] == 'content':
                PostingContentSZ = PostingContentsSerializer(data={
                    'posting': posting_idx,
                    'contentType': line['type'],
                    'content': line['contents']
            })
                if PostingContentSZ.is_valid():
                    print("String PostingContentSZ.errors:", PostingContentSZ.errors)
                    PostingContentSZ.save()

                else:
                    return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)

                return_list.append(
                    {
                        "type": PostingContentSZ.data['contentType'],
                        "contents": PostingContentSZ.data['content'],
                        "date": PostingContentSZ.data['date'],
                    }
                )

            elif line['type'] == 'imageURL':
                PostingContentSZ = PostingContentsSerializer(data={
                    'posting': posting_idx,
                    'contentType': line['type'],
                    'content': line['contents']
            })
                if PostingContentSZ.is_valid():
                    print('imageFILE')
                    print("ImageURL PostingContentSZ.errors:", PostingContentSZ.errors)
                    PostingContentSZ.save()
                else:
                    return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)

                try:
                    return_list.append(
                    {
                        "type": PostingContentSZ.data['contentType'],
                        "contents": PostingContentSZ.data['content'],
                        "date": PostingContentSZ.data['date'],
                    }
                )
                except:
                    return Response('Error', status=status.HTTP_403_FORBIDDEN)
            elif line['type'] == 'imageFILE':
                PostingContentSZ = PostingContentsSerializer(data={
                    'posting': posting_idx,
                    'contentType': line['type'],
                    'content': line['contents']
            })
                if PostingContentSZ.is_valid():
                    print("imageFILE PostingContentSZ.errors:", PostingContentSZ.errors)
                    PostingContentSZ.save()
                else:
                    return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)
                print(i)
                postingContImg = request.FILES.getlist('image')[i]
                print(postingContImg)
                print(len(postingContImg))
                print('위에 순서나온다!')
                i = i + 1
                PostingContentImgSZ = PostingContentsImageSerializer(data={
                    'author': request.user.id,
                    'PostingContents': posting_idx,
                    'image': postingContImg})
                PostingContentImgSZ.is_valid()
                print("imageFILEImageDB PostingContentImgSZ.errors:", PostingContentImgSZ.errors)

                try:
                    if PostingContentImgSZ.is_valid():
                        PostingContentImgSZ.save()
                    else:
                        print("데이터가 저장되지 않았습니다.")
                except:
                    return Response('유효하지 않은 image 형식입니다.??', status=status.HTTP_403_FORBIDDEN)
       
                return_list.append(
                    {
                        "type": PostingContentSZ.data['contentType'],
                        "contents": PostingContentImgSZ.data['image'],
                        "date": PostingContentSZ.data['date']
                    }
                )
    except PostingContents.DoesNotExist:
        return Response('Contents aren\'t valid.', status=status.HTTP_404_NOT_FOUND)
    return Response(return_list)