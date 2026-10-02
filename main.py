import warnings
from gps_class import GPSVis

warnings.filterwarnings('ignore')

vis = GPSVis(data_path='Data/data.csv',map_path='Photos/map.png',points=(45.8357, 15.9645, 45.6806, 16.1557))

vis.create_image(color=(0, 0, 255), width=3)
vis.plot_map(output='save')

key = input("Wait")
