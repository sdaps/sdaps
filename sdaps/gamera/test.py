
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

#classified = cknn.group_and_update_list_automatic(ccs,
#    #grouping_function=classify.BoundingBoxGroupingFunction(15),
#    grouping_function=classify.ShapedGroupingFunction(15),
#    max_parts_per_group=4)

ccs.sort(key=lambda img: img.offset_x)
i = 0
while i < len(ccs) - 1:
    if ccs[i].offset_x + ccs[i].ncols >= ccs[i+1].offset_x:
        # We can merge the two
        if not isinstance(ccs[i], core.MlCc):
            ccs[i] = core.MlCc(img, ccs[i].label, ccs[i])

        ccs[i].add_label(ccs[i+1].label, ccs[i+1])
        ccs.pop(i+1)

    else:
        i += 1

added, removed = cknn.classify_list_automatic(ccs)
print added, removed
classified = ccs

classified.sort(key=lambda img: img.offset_x)


for c in classified:
    print c.id_name

# Merge the groups display
for i in xrange(len(classified)):
    if isinstance(classified[i], core.MlCc):
        classified[i] = classified[i].convert_to_cc()

colored = img.graph_color_ccs(classified, None, 1)
#colored = img.color_ccs()

surface = convert.to_surface(colored)

debug.show_surface(surface)


