
# Load SDAPS and initialize it (paths)
import sys
orig_argv = sys.argv[:]
sys.path = ['.'] + sys.path
import sdaps
sdaps.init(True)

# Initialize gamera
from gamera import core
core.init_gamera()

#from gamera.toolkits.ocr.classes import Page

# Load sdaps modules
from sdaps import image
from sdaps.gamera import convert, debug
from gamera import knn
from gamera import classify

##############

# Load surface, filter it and convert to gamera format
surface = image.get_a1_from_tiff(orig_argv[1], int(orig_argv[2]), int(orig_argv[3]))
image.kfill_modified(surface, 3)
img = convert.from_surface(surface, 10, 865, 1000, 70)


ccs = img.cc_analysis()


cknn = knn.kNNInteractive([],
   ["aspect_ratio","moments","volume16regions","nrows_feature",
    "compactness", "skeleton_features"],
   0)
cknn.from_xml_filename(orig_argv[4])

classified = cknn.group_and_update_list_automatic(ccs,
    grouping_function=classify.ShapedGroupingFunction(0),
    max_parts_per_group=1)

classified.sort(key=lambda img: img.offset_x)

for c in classified:
    print c.id_name

colored = img.graph_color_ccs(classified, None, 1)
surface = convert.to_surface(colored)

debug.show_surface(surface)


