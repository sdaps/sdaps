/* SDAPS
 * Copyright (C) 2008  Christoph Simon <post@christoph-simon.eu>
 * Copyright (C) 2008  Benjamin Berg <benjamin@sipsolutions.net>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "image.h"
#include "transform.h"
#include "surface.h"
#include <Python.h>
#include <py3cairo.h>
#include <cairo.h>

static PyObject *wrap_get_a1_from_tiff(PyObject *self, PyObject *args);
static PyObject *wrap_write_a1_to_tiff(PyObject *self, PyObject *args);
static PyObject *wrap_get_rgb24_from_tiff(PyObject *self, PyObject *args);
static PyObject *wrap_find_corner_marker(PyObject *self, PyObject *args);
static PyObject *wrap_calculate_matrix(PyObject *self, PyObject *args);
static PyObject *wrap_calculate_correction_matrix_masked(PyObject *self, PyObject *args);
static PyObject *wrap_find_box_corners(PyObject *self, PyObject *args);
static PyObject *wrap_get_coverage(PyObject *self, PyObject *args);
static PyObject *wrap_get_masked_coverage(PyObject *self, PyObject *args);
static PyObject *wrap_get_masked_coverage_without_lines(PyObject *self, PyObject *args);
static PyObject *wrap_get_masked_white_area_count(PyObject *self, PyObject *args);
static PyObject *wrap_get_pbm(PyObject *self, PyObject *args);
static PyObject *sdaps_set_magic_values(PyObject *self, PyObject *args);
static PyObject *enable_debug_surface_creation(PyObject *self, PyObject *args);
static PyObject *get_debug_surface(PyObject *self, PyObject *args);
static PyObject *wrap_get_tiff_page_count(PyObject *self, PyObject *args);
static PyObject *wrap_get_tiff_resolution(PyObject *self, PyObject *args);
static PyObject *wrap_check_tiff_monochrome(PyObject *self, PyObject *args);
static PyObject *wrap_kfill_modified(PyObject *self, PyObject *args);

static PyMethodDef image_methods[] = {
	{"get_a1_from_tiff",  wrap_get_a1_from_tiff, METH_VARARGS, "Creates a cairo A1 surface from a monochrome tiff file."},
	{"write_a1_to_tiff",  wrap_write_a1_to_tiff, METH_VARARGS, "Appends a new page to an existing tiff file or create a new tiff file containing the pixel data from the surface."},
	{"get_rgb24_from_tiff",  wrap_get_rgb24_from_tiff, METH_VARARGS, "Creates a cairo RGB24 surface from a (monochrome) tiff file."},
	{"get_tiff_page_count",  wrap_get_tiff_page_count, METH_VARARGS, "Returns the number of pages a multipage tiff contains."},
	{"get_tiff_resolution", wrap_get_tiff_resolution, METH_VARARGS, "Retrieves the resolution from the given page of the tiff file (in dots per mm)."},
	{"check_tiff_monochrome",  wrap_check_tiff_monochrome, METH_VARARGS, "Check whether all pages of the tiff are monochrome."},
	{"find_corner_marker",  wrap_find_corner_marker, METH_VARARGS, "Searches for a corner marker. The third parameter should be an integer specifying the corner (1: top left, 2: top right, 3: bottom right, 4: bottom left."},
	{"calculate_matrix",  wrap_calculate_matrix, METH_VARARGS, "Calculates the transformation matrix transform the image into the survey coordinate system."},
	{"calculate_correction_matrix_masked",  wrap_calculate_correction_matrix_masked, METH_VARARGS, "Calculates a corrected transformation matrix for the mask at the given the top left corner."},
	{"find_box_corners",  wrap_find_box_corners, METH_VARARGS, "Tries to find the actuall corners of a box in the milimeter space."},
	{"get_coverage",  wrap_get_coverage, METH_VARARGS, "Calculates the black coverage in the given area."},
	{"get_masked_coverage",  wrap_get_masked_coverage, METH_VARARGS, "Calculates the black coverage in the given mask."},
	{"get_masked_coverage_without_lines",  wrap_get_masked_coverage_without_lines, METH_VARARGS, "First removes the number of requested lines with the specified stroke width using a hough transformation. Then calculates the coverage. Works on the masked area."},
	{"get_masked_white_area_count",  wrap_get_masked_white_area_count, METH_VARARGS, "Returns the number and overall size of white areas that are larger than the given percentage of the overall size. Works on the masked area."},
	{"get_pbm",  wrap_get_pbm, METH_VARARGS, "Returns a byte string that contains a binary PBM data representation of the cairo A1 surface."},
	{"set_magic_values",  sdaps_set_magic_values, METH_VARARGS, "Sets some magic values for recognition."},
	{"enable_debug_surface_creation",  enable_debug_surface_creation, METH_VARARGS, "Sets whether debug images should be created."},
	{"get_debug_surface",  get_debug_surface, METH_VARARGS, "Returns the last created debug surface. Call immediately after a function that may create such a surface."},
	{"kfill_modified",  wrap_kfill_modified, METH_VARARGS, "Run the modified KFill algorithm over the given A1 surface."},
	{NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef image_module = {
  PyModuleDef_HEAD_INIT,
  "image",
  NULL,
  0,
  image_methods,
  0,  /* m_reload */
  0,  /* m_traverse */
  0,  /* m_clear */
  0,  /* m_free */
};

PyMODINIT_FUNC
PyInit_image(void)
{
	PyObject *m;

	m = PyModule_Create(&image_module);
	if (m == NULL)
		return NULL;

	if (import_cairo() < 0)
		return NULL;

	/* supress warnings from libtiff. */
	disable_libtiff_warnings ();

	return m;
}


static PyObject *
wrap_get_a1_from_tiff(PyObject *self, PyObject *args)
{
	cairo_surface_t *surface;
	const char *filename = NULL;
	gboolean rotated;
	gint page;

	if (!PyArg_ParseTuple(args, "sii", &filename, &page, &rotated))
		return NULL;

	surface = get_a1_from_tiff(filename, page, rotated);

	if (surface) {
		return PycairoSurface_FromSurface(surface, NULL);
	} else {
		PyErr_SetString(PyExc_AssertionError, "The image surface could not be created! Broken or non 1bit tiff file?");
		return NULL;
	}
}

static PyObject *
wrap_write_a1_to_tiff(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	const char *filename = NULL;

	if (!PyArg_ParseTuple(args, "sO!", &filename,
	                                   &PycairoImageSurface_Type, &py_surface))
		return NULL;

	if (!write_a1_to_tiff(filename, py_surface->surface)) {
		PyErr_SetString(PyExc_AssertionError, "Error writing new page to TIFF file (append/create)!");
		return NULL;
	}

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
wrap_get_rgb24_from_tiff(PyObject *self, PyObject *args)
{
	cairo_surface_t *surface;
	const char *filename = NULL;
	gboolean rotated;
	gint page;

	if (!PyArg_ParseTuple(args, "sii", &filename, &page, &rotated))
		return NULL;

	surface = get_rgb24_from_tiff(filename, page, rotated);

	if (surface) {
		return PycairoSurface_FromSurface(surface, NULL);
	} else {
		PyErr_SetString(PyExc_AssertionError, "The image surface could not be created! Broken or non 1bit tiff file?");
		return NULL;
	}
}

static PyObject *
wrap_get_tiff_page_count(PyObject *self, PyObject *args)
{
	const char *filename = NULL;
	gint pages;

	if (!PyArg_ParseTuple(args, "s", &filename))
		return NULL;

	pages = get_tiff_page_count(filename);

	if (pages >= 1) {
		return Py_BuildValue("i", pages);
	} else {
		PyErr_SetString(PyExc_AssertionError, "Could not retrieve the page count of the tiff image.");
		return NULL;
	}
}

static PyObject *
wrap_get_tiff_resolution(PyObject *self, PyObject *args)
{
	const char *filename = NULL;
	gint page;
	gdouble xresolution, yresolution;

	if (!PyArg_ParseTuple(args, "si", &filename, &page))
		return NULL;

	if (get_tiff_resolution(filename, page, &xresolution, &yresolution)) {
		return Py_BuildValue("dd", xresolution, yresolution);
	} else {
		PyErr_SetString(PyExc_AssertionError, "Could not retrieve the resolution for the tiff file and page.");
		return NULL;
	}
}

static PyObject *
wrap_check_tiff_monochrome(PyObject *self, PyObject *args)
{
	const char *filename = NULL;
	gboolean monochrome;

	if (!PyArg_ParseTuple(args, "s", &filename))
		return NULL;

	monochrome = check_tiff_monochrome(filename);

	return Py_BuildValue("i", monochrome);
}

static PyObject *
wrap_find_corner_marker(PyObject *self, PyObject *args)
{
	PyObject *result;
	PycairoSurface *py_surface;
	PycairoMatrix *py_matrix;
	gint corner;
	gdouble corner_x, corner_y;
	gboolean success;

	if (!PyArg_ParseTuple(args, "O!O!i",
	                      &PycairoImageSurface_Type, &py_surface,
	                      &PycairoMatrix_Type, &py_matrix, &corner))
		return NULL;

	success = find_corner_marker(py_surface->surface, &py_matrix->matrix, corner, &corner_x, &corner_y);

	if (success) {
		result = Py_BuildValue("dd", corner_x, corner_y);
		return result;
	} else {
		PyErr_SetString(PyExc_AssertionError, "Could not find corner marker!");
		return NULL;
	}
}

static PyObject *
wrap_calculate_matrix(PyObject *self, PyObject *args)
{
	PyObject *result;
	PycairoSurface *py_surface;
	PycairoMatrix *py_matrix;
	cairo_matrix_t *matrix;
	float mm_x, mm_y, mm_width, mm_height;

	if (!PyArg_ParseTuple(args, "O!O!ffff",
	                      &PycairoImageSurface_Type, &py_surface,
	                      &PycairoMatrix_Type, &py_matrix,
	                      &mm_x, &mm_y, &mm_width, &mm_height))
		return NULL;

	matrix = calculate_matrix(py_surface->surface, &py_matrix->matrix, mm_x, mm_y, mm_width, mm_height);

	if (matrix) {
		result = PycairoMatrix_FromMatrix(matrix);
		g_free(matrix);
		return result;
	} else {
		PyErr_SetString(PyExc_AssertionError, "Could not calculate the matrix!");
		return NULL;
	}
}

static PyObject *
wrap_calculate_correction_matrix_masked(PyObject *self, PyObject *args)
{
	PyObject *result;
	PycairoSurface *py_surface;
	PycairoSurface *py_mask;
	PycairoMatrix *py_matrix;
	cairo_matrix_t *correction_matrix;
	float mm_x, mm_y;
	gdouble covered;

	if (!PyArg_ParseTuple(args, "O!O!O!ff",
	                      &PycairoImageSurface_Type, &py_surface,
	                      &PycairoImageSurface_Type, &py_mask,
	                      &PycairoMatrix_Type, &py_matrix,
	                      &mm_x, &mm_y))
		return NULL;

	correction_matrix = calculate_correction_matrix_masked(py_surface->surface, py_mask->surface, &py_matrix->matrix, mm_x, mm_y, &covered);

	if (correction_matrix) {
		result = PycairoMatrix_FromMatrix(correction_matrix);
		g_free(correction_matrix);
		return Py_BuildValue("Nd", result, covered);
	} else {
		PyErr_SetString(PyExc_AssertionError, "Could not calculate the corrected matrix!");
		return NULL;
	}
}

static PyObject *
wrap_find_box_corners(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	PycairoMatrix *py_matrix;
	gdouble mm_x, mm_y, mm_width, mm_height;
	gdouble mm_x1, mm_y1, mm_x2, mm_y2, mm_x3, mm_y3, mm_x4, mm_y4;
	gboolean success;

	if (!PyArg_ParseTuple(args, "O!O!dddd",
	                      &PycairoImageSurface_Type, &py_surface,
	                      &PycairoMatrix_Type, &py_matrix,
	                      &mm_x, &mm_y, &mm_width, &mm_height))
		return NULL;

	success = find_box_corners(py_surface->surface, &py_matrix->matrix, mm_x, mm_y, mm_width, mm_height,
	                           &mm_x1, &mm_y1, &mm_x2, &mm_y2, &mm_x3, &mm_y3, &mm_x4, &mm_y4);

	if (success) {
		return Py_BuildValue("(dd)(dd)(dd)(dd)", mm_x1, mm_y1, mm_x2, mm_y2, mm_x3, mm_y3, mm_x4, mm_y4);
	} else {
		PyErr_SetString(PyExc_AssertionError, "Could not find all the corners!");
		return NULL;
	}
}

static PyObject *
wrap_get_coverage(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	PycairoMatrix *py_matrix;
	gdouble mm_x, mm_y, mm_width, mm_height;
	gdouble coverage;

	if (!PyArg_ParseTuple(args, "O!O!dddd",
	                      &PycairoImageSurface_Type, &py_surface,
	                      &PycairoMatrix_Type, &py_matrix,
	                      &mm_x, &mm_y, &mm_width, &mm_height))
		return NULL;

	coverage = get_coverage(py_surface->surface, &py_matrix->matrix, mm_x, mm_y, mm_width, mm_height);

	return Py_BuildValue("d", coverage);
}

static PyObject *
wrap_get_masked_coverage(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	PycairoSurface *py_mask;
	gint x, y;
	gdouble coverage;

	if (!PyArg_ParseTuple(args, "O!O!ii",
	                      &PycairoImageSurface_Type, &py_surface,
	                      &PycairoImageSurface_Type, &py_mask,
	                      &x, &y))
		return NULL;

	coverage = get_masked_coverage(py_surface->surface, py_mask->surface, x, y);

	return Py_BuildValue("d", coverage);
}

static PyObject *
wrap_get_masked_coverage_without_lines(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	PycairoSurface *py_mask;
	gint x, y;
	gdouble line_width;
	gint line_count;
	gdouble coverage;

	if (!PyArg_ParseTuple(args, "O!O!iidi",
	                      &PycairoImageSurface_Type, &py_surface,
	                      &PycairoImageSurface_Type, &py_mask,
	                      &x, &y, &line_width, &line_count))
		return NULL;

	coverage = get_masked_coverage_without_lines(py_surface->surface, py_mask->surface, x, y, line_width, line_count);

	return Py_BuildValue("d", coverage);
}

static PyObject *
wrap_get_masked_white_area_count(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	PycairoSurface *py_mask;
	gint x, y;
	gdouble min_size, max_size;
	gdouble filled_area;
	int count;

	if (!PyArg_ParseTuple(args, "O!O!iidd",
	                      &PycairoImageSurface_Type, &py_surface,
	                      &PycairoImageSurface_Type, &py_mask,
	                      &x, &y, &min_size, &max_size))
		return NULL;

	count = get_masked_white_area_count(py_surface->surface, py_mask->surface, x, y, min_size, max_size, &filled_area);

	return Py_BuildValue("id", count, filled_area);
}

static PyObject *
wrap_get_pbm(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	PyObject* result;
	int length = 0;
	void *data = NULL;

	if (!PyArg_ParseTuple(args, "O!",
	                      &PycairoImageSurface_Type, &py_surface))
		return NULL;

	get_pbm(py_surface->surface, &data, &length);

	result = Py_BuildValue("y#", data, length);
	g_free (data);
	return result;
}

static PyObject *sdaps_set_magic_values(PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, "ddddd",
	                      &sdaps_line_min_length,
	                      &sdaps_line_max_length,
	                      &sdaps_line_width,
	                      &sdaps_corner_mark_search_distance,
	                      &sdaps_line_coverage))
		return NULL;

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *enable_debug_surface_creation(PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, "i",
	                      &sdaps_create_debug_surface))
		return NULL;

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *get_debug_surface(PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL;

	if ((!sdaps_create_debug_surface) || (sdaps_debug_surface == NULL)) {
		Py_INCREF(Py_None);
		return Py_None;
	} else {
		PyObject *result;
		PyObject *pysurface;

		cairo_surface_reference(sdaps_debug_surface);
		pysurface = (PyObject*) PycairoSurface_FromSurface(sdaps_debug_surface, NULL);

		if (pysurface == NULL)
			return NULL;

		result =  Py_BuildValue("Nii",
		                        pysurface,
		                        sdaps_debug_surface_ox,
		                        sdaps_debug_surface_oy);

		if (result == NULL)
			Py_DECREF(pysurface);

		return result;
	}
}


static PyObject *
wrap_kfill_modified(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	gint k;

	if (!PyArg_ParseTuple(args, "O!i",
	                      &PycairoImageSurface_Type, &py_surface, &k))
		return NULL;

	if (cairo_image_surface_get_format (py_surface->surface) != CAIRO_FORMAT_A1) {
		PyErr_SetString(PyExc_AssertionError, "This function only works with A1 surfaces currently!");
		return NULL;
	}

	kfill_modified(py_surface->surface, k);

	Py_INCREF(Py_None);
	return Py_None;
}

