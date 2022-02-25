from rio_tiler.io import COGReader
from rio_tiler.profiles import img_profiles
from rio_tiler.colormap import cmap
from aiohttp import web
import logging
from json import dumps
import numpy as np
from io import BytesIO

# file_path_template = 's3://nugent-ornl/cogs/SPIDI/20220217-1600/{}/{}.tif'
file_path_template = './data/SPIDI/20220217-1600/{}/{}.tif'

routes = web.RouteTableDef()

@routes.get('/')
async def handle(request):

    return web.Response(text='hello')

@routes.get('/colormaps')
async def tile(request):

    logging.info(cmap.list())
    return web.json_response(dumps(cmap.list()))

@routes.get('/threatpoly/{dataset:(ICEACCUM|QPF|SNOW|SPIA|TEMP|WDIR|WSPD)}')
async def threatpoly(request):
    return web.json_response(text='hello')

@routes.get('/array/{dataset:(ICEACCUM|QPF|SNOW|SPIA|TEMP|WDIR|WSPD)}')
async def array(request):
    # todo
    # allow slices or select by poly

    dataset = request.match_info.get('dataset')

    forecast = request.query.get('forecast')
    file = file_path_template.format(dataset, forecast)
    if 'file' in request.query:
        file = request.query.get('file')

    with COGReader(file) as cog:
        img = cog.read()
        buff = img.render(img_format="npy")
        arr = np.load(BytesIO(buff))
        logging.info(arr)

@routes.get('/tiles/{dataset:(ICEACCUM|QPF|SNOW|SPIA|TEMP|WDIR|WSPD)}'
            '/{z}/{x}/{y}.{ext:(png|jpg)}')
async def tile(request):
    z = request.match_info.get('z')
    y = request.match_info.get('y')
    x = request.match_info.get('x')
    ext = request.match_info.get('ext')
    dataset = request.match_info.get('dataset')

    cm = cmap.get('cfastie')
    if 'colormap' in request.query and \
        request.query.get('colormap') in cmap.list():

        cm = cmap.get(request.query.get('colormap'))

    forecast = request.query.get('forecast')
    file = file_path_template.format(dataset, forecast)
    if 'file' in request.query:
        file = request.query.get('file')

    # file = 's3://nugent-ornl/cogs/SPIDI/20220217-1600/QPF/20220126-0000.tif'

    # SUPER SLOW
    # file = create_presigned_url('nugent-ornl',
    #                             'cogs/SPIDI/20220217-1600/QPF/20220126-0000.tif')

    with COGReader(file) as cog:
        stats = cog.statistics()
        logging.info(stats)
        tile = cog.tile(int(x), int(y), int(z), tilesize=256)

        min = stats['1'].dict().get('min')
        max = stats['1'].dict().get('max')
        tile = tile.post_process(
            in_range=((min, max),),
            out_range=((0, 255),)
        )

    content_type = 'image/png'
    image_format = 'PNG'
    if ext == 'jpg':
        content_type ='image/jpeg'
        image_format = 'JPEG'
    content = tile.render(colormap=cm, img_format=image_format,
                          **img_profiles.get(ext))

    return web.Response(body=content, content_type=content_type)

import boto3
from botocore.exceptions import ClientError

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', )
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, port=5000)


