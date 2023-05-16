from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy_schemadisplay import create_schema_graph

# Create a SQLAlchemy engine and session
engine = create_engine('sqlite:///amazun.db')
Session = sessionmaker()
session = Session()

metadata = MetaData()
metadata.bind = engine # Must bind engine
metadata.reflect(bind=engine)

graph = create_schema_graph(metadata=metadata,
                            show_datatypes=True,
                            show_indexes=True,
                            rankdir='LR',
                            concentrate=False)

graph.write_png('dbschema2.png')