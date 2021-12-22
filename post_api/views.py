from django.shortcuts import render
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer as ProfileSerializer
from project_api.serializers import ProjectSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import json

from .serializers import PostingContentsSerializer, PostingSerializer, PostingContentsImageSerializer, LikeSerializer

from .models import Post, Contents, ContentsImage, Like


# Create your views here.
@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def posting_upload(request, proj_idx):
    post_obj = Post.objects.create(user_id=request.user.id, 
                                   project_id=proj_idx,
                                   title=request.data['title'],
                                   thumbnail=request.FILES.get('thumbnail'))


    for image in request.FILES.getlist('image'):
        ContentsImage.objects.create(post_id=post_obj.id,
                                     image=image)

    images = PostingContentsImageSerializer(ContentsImage.objects.filter(post_id=post_obj.id), many=True).data
    image_id = 0
    contents = []
    
    for d in json.loads(request.data['contents']):
        if type(d['insert']) == dict:
            d['insert'] = {"image":images[image_id]['image']}
            image_id += 1
        contents.append(d)

    Contents.objects.create(post_id=post_obj.id,
                            content=contents)

    return Response(PostingSerializer(post_obj).data, status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def posting_upload1(request, proj_idx):
    postingSZ = PostingSerializer(data={
        'user': request.user.id,
        'project': proj_idx,
        'title' : request.data['title'], 
        'thumbnail' : request.FILES.get('thumbnail')
    })
    if postingSZ.is_valid():
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
                PostingContentSZ.save()
            else:
                return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)
            postingContImg = request.FILES.getlist('image')[i]
            i = i + 1
            PostingContentImgSZ = PostingContentsImageSerializer(data={
                'user': request.user.id,
                'PostingContents': postingSZ.data['id'],
                'image': postingContImg})
            PostingContentImgSZ.is_valid()

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

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def posting_list_load(request, proj_idx):
    if request.method == 'GET':
        try:
            postings = Post.objects.filter(project=proj_idx)    
        except Post.DoesNotExist:
            return Response('The postings aren\'t valid', status=status.HTTP_404_NOT_FOUND)

        postingSZ = PostingSerializer(postings, many=True)

        return_dict = {
            'posting_list' : postingSZ.data
        }

        for posting in return_dict['posting_list']:
            posting.update({'like_num': len(posting['like'])})
        return Response(return_dict)
    else:
        return Response('Request isn\'t valid.', status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def specific_posting_load(request, posting_idx):
    if request.method == 'GET':
        user_id = request.user.id
        try:
            posting = Post.objects.get(id=posting_idx)

        except Post.DoesNotExist:
            return Response('The posting isn\'t valid', status=status.HTTP_404_NOT_FOUND)

        try:
            postingContents = 'default'
            postingContents = Contents.objects.filter(posting=posting_idx)
        
            if postingContents == 'default':
                return Response('Empty posting')
                

        except Contents.DoesNotExist:
            return Response('Contents aren\'t valid.', status=status.HTTP_404_NOT_FOUND)
    
    
        postingSZ = PostingSerializer(posting)
        profile_obj = Profile.objects.get(user_id=posting.user_id)
        profile = ProfileSerializer(profile_obj).data
        return_dict = {
            'posting_info': postingSZ.data,
        }
        return_dict.update(profile)

        return Response(return_dict)

    else:
        return Response('Request isn\'t valid.', status=status.HTTP_404_NOT_FOUND)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def specific_posting_update(request, posting_idx):
    # if str(request.user.id) == user_idx:
    postingcont = Contents.objects.filter(posting=posting_idx)
    postingcont.delete()
    
    return_list = []

    try:
        ContentsList = json.JSONDecoder().decode(request.data['contents_list'])
        i = 0
        for line in ContentsList:
            if line['type'] == 'title' or line['type'] == 'content':
                PostingContentSZ = PostingContentsSerializer(data={
                    'posting': posting_idx,
                    'contentType': line['type'],
                    'content': line['contents']
            })
                if PostingContentSZ.is_valid():
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
                    PostingContentSZ.save()
                else:
                    return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)
                postingContImg = request.FILES.getlist('image')[i]
                i = i + 1
                PostingContentImgSZ = PostingContentsImageSerializer(data={
                    'user': request.user.id,
                    'PostingContents': posting_idx,
                    'image': postingContImg})
                PostingContentImgSZ.is_valid()

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
    except Contents.DoesNotExist:
        return Response('Contents aren\'t valid.', status=status.HTTP_404_NOT_FOUND)
    return Response(return_list)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def like(request, type, idx):

    if type == 'posting':
        try:
            like_valid = Like.objects.get(posting=idx, user=request.user.id)
            like_valid.delete()
            return Response('disliked posting', status=status.HTTP_202_ACCEPTED)
        except:
            Like.objects.create(posting=idx, user=request.user.id)
            return Response('liked posting', status=status.HTTP_202_ACCEPTED)