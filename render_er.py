from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy_schemadisplay import create_schema_graph
from PIL import Image, ImageOps, ImageDraw

from my_credentials import cstring2

engine = create_engine(cstring2)
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
metadata.bind = engine  # Must bind engine
metadata.reflect(bind=engine)

graph = create_schema_graph(
    metadata=metadata,
    show_datatypes=True,
    show_indexes=True,
    rankdir='LR',
    concentrate=False
)

graph.write_png('dbschema2.png')
image = Image.open('dbschema2.png')
if image.mode != 'RGB':
    image = image.convert('RGB')
inverted_image = ImageOps.invert(image)
inverted_image.save('dbschema2.png')

def add_rounded_corners(image, corner_radius):
    circle = Image.new('L', (corner_radius * 2, corner_radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, corner_radius * 2, corner_radius * 2), fill=255)
    
    alpha = Image.new('L', image.size, 255)
    w, h = image.size
    alpha.paste(circle.crop((0, 0, corner_radius, corner_radius)), (0, 0))
    alpha.paste(circle.crop((0, corner_radius, corner_radius, corner_radius * 2)), (0, h - corner_radius))
    alpha.paste(circle.crop((corner_radius, 0, corner_radius * 2, corner_radius)), (w - corner_radius, 0))
    alpha.paste(circle.crop((corner_radius, corner_radius, corner_radius * 2, corner_radius * 2)), (w - corner_radius, h - corner_radius))
    
    image.putalpha(alpha)
    return image

add_rounded_corners(Image.open('dbschema2.png'), 20).save('dbschema2.png')