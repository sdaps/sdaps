/* SDAPS
 * Copyright (C) 2008  Christoph Simon <christoph.simon@gmx.eu>
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
#include <Python.h>
#include <pycairo.h>
#include <cairo.h>

static PyObject *wrap_get_a1_from_tiff(PyObject *self, PyObject *args);
static PyObject *wrap_get_rgb24_from_tiff(PyObject *self, PyObject *args);
static PyObject *wrap_calculate_matrix(PyObject *self, PyObject *args);
static PyObject *wrap_calculate_correction_matrix(PyObject *self, PyObject *args);
static PyObject *wrap_find_box_corners(PyObject *self, PyObject *args);
static PyObject *wrap_get_coverage(PyObject *self, PyObject *args);
static PyObject *wrap_get_pbm(PyObject *self, PyObject *args);
static PyObject *sdaps_set_magic_values(PyObject *self, PyObject *args);
static PyObject *wrap_get_tiff_page_count(PyObject *self, PyObject *args);
static PyObject *wrap_check_tiff_monochrome(PyObject *self, PyObject *args);

Pycairo_CAPI_t *Pycairo_CAPI;

static PyMethodDef EvaluateMethods[] = {
	{"get_a1_from_tiff",  wrap_get_a1_from_tiff, METH_VARARGS, "Creates a cairo A1 surface from a monochrome tiff file."},
	{"get_rgb24_from_tiff",  wrap_get_rgb24_from_tiff, METH_VARARGS, "Creates a cairo RGB24 surface from a (monochrome) tiff file."},
	{"get_tiff_page_count",  wrap_get_tiff_page_count, METH_VARARGS, "Returns the number of pages a multipage tiff contains."},
	{"check_tiff_monochrome",  wrap_check_tiff_monochrome, METH_VARARGS, "Check whether all pages of the tiff are monochrome."},
	{"calculate_matrix",  wrap_calculate_matrix, METH_VARARGS, "Calculates the transformation matrix transform the image into the survey coordinate system."},
	{"calculate_correction_matrix",  wrap_calculate_correction_matrix, METH_VARARGS, "Calculates a corrected transformation matrix for the box at the given position (argument should be the bounding box)."},
	{"find_box_corners",  wrap_find_box_corners, METH_VARARGS, "Tries to find the actuall corners of a box in the milimeter space."},
	{"get_coverage",  wrap_get_coverage, METH_VARARGS, "Calculates the black coverage in the given area."},
	{"get_pbm",  wrap_get_pbm, METH_VARARGS, "Returns a string that contains a binary PBM data representation of the cairo A1 surface."},
	{"set_magic_values",  sdaps_set_magic_values, METH_VARARGS, "Sets some magic values for recognition."},
	{NULL, NULL, 0, NULL} /* Sentinel */
};

static int
initpycairo(void)
{ 
	Pycairo_IMPORT;
	if (Pycairo_CAPI == NULL)
		return 0;

	return 1;
}

PyMODINIT_FUNC
initimage(void)
{
	PyObject *m;

	/* Return if pycairo cannot be initilized. */
	if (!initpycairo())
		return;

	m = Py_InitModule("image", EvaluateMethods);
}


static PyObject *
wrap_get_a1_from_tiff(PyObject *self, PyObject *args)
{
	cairo_surface_t *surface;
	char *filename = NULL;
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
wrap_get_rgb24_from_tiff(PyObject *self, PyObject *args)
{
	cairo_surface_t *surface;
	char *filename = NULL;
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
	char *filename = NULL;
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
wrap_check_tiff_monochrome(PyObject *self, PyObject *args)
{
	char *filename = NULL;
	gboolean monochrome;

	if (!PyArg_ParseTuple(args, "s", &filename))
		return NULL;

	monochrome = check_tiff_monochrome(filename);

	return Py_BuildValue("i", monochrome);
}

static PyObject *
wrap_calculate_matrix(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	cairo_matrix_t *matrix;
	float mm_x, mm_y, mm_width, mm_height;
	
	if (!PyArg_ParseTuple(args, "O!ffff", &PycairoImageSurface_Type, &py_surface, &mm_x, &mm_y, &mm_width, &mm_height))
		return NULL;
	
	matrix = calculate_matrix(py_surface->surface, mm_x, mm_y, mm_width, mm_height);

	if (matrix) {
		return PycairoMatrix_FromMatrix(matrix);
	} else {
		PyErr_SetString(PyExc_AssertionError, "Could not calculate the matrix!");
		return NULL;
	}
}

static PyObject *
wrap_calculate_correction_matrix(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	PycairoMatrix *py_matrix;
	cairo_matrix_t *correction_matrix;
	float mm_x, mm_y, mm_width, mm_height;
	
	if (!PyArg_ParseTuple(args, "O!O!ffff", &PycairoImageSurface_Type, &py_surface, &PycairoMatrix_Type, &py_matrix, &mm_x, &mm_y, &mm_width, &mm_height))
		return NULL;
	
	correction_matrix = calculate_correction_matrix(py_surface->surface, &py_matrix->matrix, mm_x, mm_y, mm_width, mm_height);

	if (correction_matrix) {
		return PycairoMatrix_FromMatrix(correction_matrix);
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

	if (!PyArg_ParseTuple(args, "O!O!dddd", &PycairoImageSurface_Type, &py_surface, &PycairoMatrix_Type, &py_matrix, &mm_x, &mm_y, &mm_width, &mm_height))
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
	float mm_x, mm_y, mm_width, mm_height;
	float coverage;
	
	if (!PyArg_ParseTuple(args, "O!O!ffff", &PycairoImageSurface_Type, &py_surface, &PycairoMatrix_Type, &py_matrix, &mm_x, &mm_y, &mm_width, &mm_height))
		return NULL;
	
	coverage = get_coverage(py_surface->surface, &py_matrix->matrix, mm_x, mm_y, mm_width, mm_height);

	return Py_BuildValue("f", coverage);
}

static PyObject *
wrap_get_pbm(PyObject *self, PyObject *args)
{
	PycairoSurface *py_surface;
	PyObject* result;
	int length = 0;
	void *data = NULL;
	
	if (!PyArg_ParseTuple(args, "O!", &PycairoImageSurface_Type, &py_surface))
		return NULL;
	
	get_pbm(py_surface->surface, &data, &length);

	result = Py_BuildValue("s#", data, length);
	g_free (data);
	return result;
}

static PyObject *sdaps_set_magic_values(PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, "iiiid",
	                      &sdaps_line_min_length,
	                      &sdaps_line_max_length,
	                      &sdaps_line_width,
	                      &sdaps_corner_mark_search_distance,
	                      &sdaps_line_coverage))
		return NULL;

	Py_INCREF(Py_None);
	return Py_None;
}

