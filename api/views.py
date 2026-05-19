from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404

# попередня версія коду для порівняння: https://github.com/sunmeat/django_drf3/blob/master/api/views.py

from .models import Artist, Album, Track, Genre
from .serializers import ( # імпортуємо серіалізатори
    ArtistSerializer,
    AlbumReadSerializer,
    AlbumWriteSerializer,
    TrackReadSerializer,
    TrackWriteSerializer,
    GenreSerializer,
)

# =====================================================
# виконавці
# =====================================================

@api_view(['GET'])
def artist_list(request):
    artists = Artist.objects.all()
    serializer = ArtistSerializer(artists, many=True) # завдяки серіалізатору можна перетворити список об'єктів Artist в список словників, які можуть бути легко перетворені в JSON
    return Response(serializer.data) # обсяг коду суттєво зменшується, бо не потрібно вручну створювати словник для кожного виконавця


@api_view(['GET'])
def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk) # get_object_or_404 - це зручна функція, яка намагається отримати об'єкт за заданими параметрами (в даному випадку pk), і якщо об'єкт не знайдено, вона автоматично повертає відповідь з кодом 404 Not Found
    serializer = ArtistSerializer(artist)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser]) # декоратор @permission_classes([IsAdminUser]) обмежує доступ до цього представлення лише для користувачів з правами адміністратора. якщо користувач не є адміністратором, він отримає відповідь з кодом 403 Forbidden
def artist_create(request):
    serializer = ArtistSerializer(data=request.data)

    if serializer.is_valid(): # !!!
    # в цей момент DRF запускає:
    # 1. Field-level validation
    # def validate_duration(self, value) тощо
    # викликається для кожного поля окремо
    # 2. Object-level validation
    # def validate(self, attrs)
    # викликається після field-level, працює з усіма даними разом
    # 3. якщо все ок, то можна save()

        serializer.save() # метод save() викликає метод create() серіалізатора, який створює новий об'єкт Artist на основі валідованих даних (serializer.validated_data) і зберігає його в базі даних
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def artist_update(request, pk):
    artist = get_object_or_404(Artist, pk=pk)

    serializer = ArtistSerializer(
        artist,
        data=request.data,
        partial=True # partial=True дозволяє оновлювати лише деякі поля об'єкта, не вимагаючи надання всіх полів (якщо False, то всі поля повинні бути надані для оновлення
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def artist_albums(request, pk):
    artist = get_object_or_404(Artist, pk=pk)

    albums = artist.albums.all()
    serializer = AlbumReadSerializer(albums, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def artist_tracks(request, pk):
    artist = get_object_or_404(Artist, pk=pk)

    tracks = artist.tracks.all()
    serializer = TrackReadSerializer(tracks, many=True)

    return Response(serializer.data)


# =====================================================
# альбоми
# =====================================================

@api_view(['GET'])
def album_list(request):
    albums = Album.objects.select_related('artist').prefetch_related('genres')
    serializer = AlbumReadSerializer(albums, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk)
    serializer = AlbumReadSerializer(album)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def album_create(request):
    serializer = AlbumWriteSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def album_update(request, pk):
    album = get_object_or_404(Album, pk=pk)

    serializer = AlbumWriteSerializer(
        album,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def album_tracks(request, pk):
    album = get_object_or_404(Album, pk=pk)

    tracks = album.tracks.all()
    serializer = TrackReadSerializer(tracks, many=True)

    return Response(serializer.data)


# =====================================================
# треки
# =====================================================

@api_view(['GET'])
def track_list(request):
    tracks = Track.objects.select_related('album').prefetch_related('artists', 'genres')
    serializer = TrackReadSerializer(tracks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def track_detail(request, pk):
    track = get_object_or_404(Track, pk=pk)
    serializer = TrackReadSerializer(track)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def track_create(request):
    serializer = TrackWriteSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def track_update(request, pk):
    track = get_object_or_404(Track, pk=pk)

    serializer = TrackWriteSerializer(
        track,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====================================================
# жанри
# =====================================================

@api_view(['GET'])
def genre_list(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def genre_tracks(request, pk):
    genre = get_object_or_404(Genre, pk=pk)

    tracks = genre.tracks.all()
    serializer = TrackReadSerializer(tracks, many=True)

    return Response(serializer.data)