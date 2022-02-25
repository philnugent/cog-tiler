import parquet_test as pt
import rio_utils as ru
from datetime import datetime

datasets = {
    'ICEACCUM': {
        'nc_file': 'iceaccum.nc',
        'variable': 'Ice_Accumulation_surface_6_Hour_Accumulation',
        'color_map': 'cfastie'
    },
    'QPF': {
        'nc_file': 'qpf.nc',
        'variable': 'Total_precipitation_surface_6_Hour_Accumulation',
        'color_map': 'cfastie'
    }
    ,
    'SNOW': {
        'nc_file': 'snow.nc',
        'variable': 'Total_snowfall_surface_6_Hour_Accumulation',
        'color_map': 'cfastie'
    },
    'SPIA': {
        'nc_file': 'spia.nc',
        'variable': 'SPIA',
        'color_map': 'cfastie'
    },
    'TEMP': {
        'nc_file': 'temp.nc',
        'variable': 'Temperature_height_above_ground',
        'color_map': 'cfastie'
    },
    'WDIR': {
        'nc_file': 'wdir.nc',
        'variable': 'Wind_direction_from_which_blowing_height_above_ground',
        'color_map': 'cfastie'
    },
    'WSPD': {
        'nc_file': 'wspd.nc',
        'variable': 'Wind_speed_height_above_ground',
        'color_map': 'cfastie'
    }
}

data_path = 'data/naerm_rt'


if __name__ == '__main__':

    for key in datasets:
        print()
        print(key)
        nc_file = '{}/{}/{}'.format(data_path, key, datasets[key]['nc_file'])
        variable = datasets[key]['variable']

        forecast_hour = datetime.now().replace(microsecond=0, second=0, minute=0)
        forecast_hour = forecast_hour.strftime("%Y%m%d-%H%M")
        out_path = './data/SPIDI/{}/{}/'.format(forecast_hour, key)

        #ru.describe(nc_file, variable)

        #ru.compare(nc_file, variable)

        ru.process(nc_file, variable, out_path)
