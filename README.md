TODO:
- Explore numpy tiles


## Transformer
### TODO:
- validate COGS
- get from and push to S3

### Running
Create virtual env and install requiements
Have sample SPIDI data at ./data/

```
python3  main.py
```

## Tile Server

### Running
create virtual env and install requiements

```
python3  server.py
```

http://0.0.0.0:5000/tiles/TEMP/2/0/1.png?colormap=gist_rainbow&forecast=20220126-0500

### Resources
Look at serverless with lambda
https://github.com/cogeotiff/rio-tiler
https://devseed.com/titiler/intro/
https://kylebarron.dev/blog/cog-mosaic/overview


## Notebooks
```
conda create -n playground python=3.9 numpy notebook nb_conda_kernels
```
