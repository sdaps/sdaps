/* SDAPS
 * Copyright (C) 2008  Christoph Simon <post@christoph-simon.eu>
 * Copyright (C) 2008, 2011  Benjamin Berg <benjamin@sipsolutions.net>
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

/*#include <gdk-pixbuf/gdk-pixbuf.h>*/
#include <tiffio.h>
#include "image.h"
#include <math.h>
#include "surface.h"
#include "transform.h"

/* Some of the more important Magic Values */
gdouble sdaps_line_min_length = 20-2;
gdouble sdaps_line_max_length = 20+2;
gdouble sdaps_line_width = 1/72*25.4;
gdouble sdaps_corner_mark_search_distance = 50;
gdouble sdaps_line_coverage = 0.65;

gboolean sdaps_create_debug_surface = FALSE;
gint sdaps_debug_surface_ox;
gint sdaps_debug_surface_oy;
cairo_surface_t *sdaps_debug_surface = NULL;

static void
debug_surface_clear(void)
{
	if (sdaps_debug_surface != NULL) {
		cairo_surface_destroy(sdaps_debug_surface);
		sdaps_debug_surface = NULL;
	}
}

static cairo_surface_t*
debug_surface_create(gint x, gint y, gint width, gint height, gdouble r, gdouble g, gdouble b, gdouble a)
{
	cairo_t* cr;

	debug_surface_clear();

	if (!sdaps_create_debug_surface)
		return NULL;

	sdaps_debug_surface_ox = x;
	sdaps_debug_surface_oy = y;

	sdaps_debug_surface = cairo_image_surface_create (CAIRO_FORMAT_ARGB32, width, height);

	cr = cairo_create (sdaps_debug_surface);
	cairo_set_source_rgba (cr, r, g, b, a);
	cairo_set_operator (cr, CAIRO_OPERATOR_SOURCE);
	cairo_paint (cr);
	cairo_destroy (cr);

	cairo_surface_flush (sdaps_debug_surface);

	return sdaps_debug_surface;
}


void
disable_libtiff_warnings (void)
{
	TIFFSetWarningHandler(NULL);
}

cairo_surface_t*
get_a1_from_tiff (const char *filename, gint page, gboolean rotated)
{
	TIFF* tiff;
	cairo_surface_t *surface;
	guint32 *s_pixels;
	guint32 *t_pixels;
	guint32 *t_row;
	int s_stride, t_stride;
	int width, height;
	BARREL_VARS

	int x, y;

	tiff = TIFFOpen(filename, "r");
	if (tiff == NULL)
		return NULL;

	if (!TIFFSetDirectory(tiff, page)) {
		TIFFClose(tiff);
		return NULL;
	}

	TIFFGetField(tiff, TIFFTAG_IMAGEWIDTH, &width);
	TIFFGetField(tiff, TIFFTAG_IMAGELENGTH, &height);
	t_pixels = g_new(guint32, width * height);
	if (!rotated)
		TIFFReadRGBAImageOriented(tiff, width, height, t_pixels, ORIENTATION_TOPLEFT, 0);
	else
		TIFFReadRGBAImageOriented(tiff, width, height, t_pixels, ORIENTATION_BOTRIGHT, 0);

	surface = cairo_image_surface_create(CAIRO_FORMAT_A1, width, height);
	s_pixels = (guint32*) cairo_image_surface_get_data(surface);
	s_stride = cairo_image_surface_get_stride(surface);

	t_stride = width * sizeof(guint32);
	t_row = t_pixels;

	for (y = 0; y < height; y++) {
		guint32 *t_p = t_row;
		BARREL_START_ROW((char*)s_pixels + y * s_stride)
		for (x = 0; x < width; x++) {
			BARREL_STORE_BIT(!(TIFFGetR(*t_p) >> 7));
			/* SET_PIXEL(s_pixels, s_stride, x, y, !(TIFFGetR(*t_p) >> 7)); */
			t_p = t_p + 1;
		}
		BARREL_FLUSH
		t_row = (guint32*) ((char*) t_row + t_stride);
	}

	g_free(t_pixels);
	TIFFClose(tiff);

	cairo_surface_mark_dirty(surface);

	return surface;
}

gboolean
write_a1_to_tiff (const char *filename, cairo_surface_t *surf)
{
	TIFF *tiff;
	gint width, height;
	gint stride;
	gint y;
	guint32 stripsize;
	guint8 *data;

	g_assert(cairo_image_surface_get_format(surf) == CAIRO_FORMAT_A1);

	width = cairo_image_surface_get_width(surf);
	height = cairo_image_surface_get_height(surf);
	stride = cairo_image_surface_get_stride(surf);
	data = (guint8*) cairo_image_surface_get_data(surf);

	/* We create a new TIFF file if it doesn't exist yet, otherwise we append
	 * to it. */
	tiff = TIFFOpen(filename, "a");
	if (tiff == NULL)
		return FALSE;

#if G_BYTE_ORDER == G_LITTLE_ENDIAN
	/* Reverse *ALL* bits ... */
	TIFFReverseBits(data, stride*(height-1) + (width+7)/8);
#endif

	/* Setup the new image. */
	TIFFSetField(tiff, TIFFTAG_IMAGEWIDTH, width);
	TIFFSetField(tiff, TIFFTAG_IMAGELENGTH, height);
	TIFFSetField(tiff, TIFFTAG_BITSPERSAMPLE, 1);
	TIFFSetField(tiff, TIFFTAG_SAMPLESPERPIXEL, 1);
	TIFFSetField(tiff, TIFFTAG_PLANARCONFIG, PLANARCONFIG_SEPARATE);

	stripsize = TIFFDefaultStripSize(tiff, -1);

	TIFFSetField(tiff, TIFFTAG_ROWSPERSTRIP, stripsize);
	TIFFSetField(tiff, TIFFTAG_COMPRESSION, COMPRESSION_CCITTFAX4);
	TIFFSetField(tiff, TIFFTAG_GROUP4OPTIONS, 0);
	TIFFSetField(tiff, TIFFTAG_FAXMODE, FAXMODE_CLASSF);
	TIFFSetField(tiff, TIFFTAG_THRESHHOLDING, THRESHHOLD_BILEVEL);
	TIFFSetField(tiff, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISWHITE);

	for (y = 0; y < height; y++) {
		if (TIFFWriteScanline(tiff, data + y * stride, y, 0) == -1)
			goto BAIL_WRITE_A1;
	}

#if G_BYTE_ORDER == G_LITTLE_ENDIAN
	/* Undo reversal again. */
	TIFFReverseBits(data, stride*(height-1) + (width+7)/8);
#endif
	TIFFClose(tiff);

	return TRUE;

BAIL_WRITE_A1:

#if G_BYTE_ORDER == G_LITTLE_ENDIAN
	/* Undo reversal again. */
	TIFFReverseBits(data, stride*(height-1) + (width+7)/8);
#endif
	TIFFClose(tiff);

	return FALSE;
}

cairo_surface_t*
get_rgb24_from_tiff (const char *filename, gint page, gboolean rotated)
{
	TIFF* tiff;
	cairo_surface_t *surface;
	guint32 *s_pixels;
	guint32 *t_pixels;
	guint32 *t_row;
	int s_stride, t_stride;
	int width, height;

	int x, y;

	tiff = TIFFOpen(filename, "r");
	if (tiff == NULL)
		return NULL;

	if (!TIFFSetDirectory(tiff, page)) {
		TIFFClose(tiff);
		return NULL;
	}

	TIFFGetField(tiff, TIFFTAG_IMAGEWIDTH, &width);
	TIFFGetField(tiff, TIFFTAG_IMAGELENGTH, &height);
	t_pixels = g_new(guint32, width * height);
	if (!rotated)
		TIFFReadRGBAImageOriented(tiff, width, height, t_pixels, ORIENTATION_TOPLEFT, 0);
	else
		TIFFReadRGBAImageOriented(tiff, width, height, t_pixels, ORIENTATION_BOTRIGHT, 0);

	surface = cairo_image_surface_create(CAIRO_FORMAT_RGB24, width, height);
	s_pixels = (guint32*) cairo_image_surface_get_data(surface);
	s_stride = cairo_image_surface_get_stride(surface);

	t_stride = width * sizeof(guint32);
	t_row = t_pixels;

	for (y = 0; y < height; y++) {
		guint32 *t_p = t_row;

		for (x = 0; x < width; x++) {
			*((guint32*) (((guint8*) s_pixels) + 4 * x + y * s_stride)) = (TIFFGetR(*t_p) << 16) | (TIFFGetG(*t_p) << 8) | TIFFGetB(*t_p);
			t_p = t_p + 1;
		}
		t_row = (guint32*) ((char*) t_row + t_stride);
	}

	g_free(t_pixels);
	TIFFClose(tiff);

	cairo_surface_mark_dirty(surface);

	return surface;
}

gint
get_tiff_page_count (const char *filename)
{
	TIFF* tiff;
	gint pages;

	tiff = TIFFOpen(filename, "r");
	if (tiff == NULL)
		return 0;

	pages = TIFFNumberOfDirectories(tiff);

	TIFFClose(tiff);

	return pages;
}

gboolean
get_tiff_resolution (const char *filename, gint page, gdouble *xresolution, gdouble *yresolution)
{
	TIFF* tiff;
	float xres = 0.0;
	float yres = 0.0;
	guint16 unit = RESUNIT_NONE;

	tiff = TIFFOpen(filename, "r");
	if (tiff == NULL)
		return FALSE;

	if (!TIFFSetDirectory(tiff, page)) {
		TIFFClose(tiff);
		return FALSE;
	}

	TIFFGetField(tiff, TIFFTAG_XRESOLUTION, &xres);
	TIFFGetField(tiff, TIFFTAG_YRESOLUTION, &yres);
	TIFFGetField(tiff, TIFFTAG_RESOLUTIONUNIT, &unit);

	if (unit == RESUNIT_CENTIMETER) {
		*xresolution = xres / 10.0;
		*yresolution = yres / 10.0;
	} else if (unit == RESUNIT_INCH) {
		*xresolution = xres / 25.4;
		*yresolution = yres / 25.4;
	} else {
		/* Nothing good, pass back zeros */
		*xresolution = 0;
		*yresolution = 0;
	}

	TIFFClose(tiff);
	return TRUE;
}

gboolean
check_tiff_monochrome (const char *filename)
{
	TIFF* tiff;
	gboolean monochrome = TRUE;

	tiff = TIFFOpen(filename, "r");
	if (tiff == NULL)
		return FALSE;

	do {
		guint16 bits_per_sample;
		TIFFGetField(tiff, TIFFTAG_BITSPERSAMPLE, &bits_per_sample);
		if (bits_per_sample != 1)
			monochrome = FALSE;
	} while (TIFFReadDirectory(tiff) && monochrome);

	if (!TIFFLastDirectory(tiff)) {
		/* This should never ever happen ... */
		monochrome = FALSE;
	}

	TIFFClose(tiff);

	return monochrome;
}

#define LINE_COVERAGE sdaps_line_coverage

static gint
transform_distance_to_pixel(cairo_matrix_t *matrix, gdouble distance)
{
	gdouble dx, dy;

	dx = distance;
	dy = distance;
	cairo_matrix_transform_distance(matrix, &dx, &dy);
	return (gint) ceil(MAX(dx, dy));
}

static gboolean
follow_line(cairo_surface_t *surface,
            gint             x_start,
            gint             y_start,
            gint             x_dir,
            gint             y_dir,
            gint             line_width,
            gint             line_length,
            gint             line_max_length,
            gdouble         *x1,
            gdouble         *y1,
            gdouble         *x2,
            gdouble         *y2)
{
	gboolean found_segment;
	gboolean found_line = FALSE;
	gint x, y;
	gint start_x, start_y;
	gint end_x, end_y;
	double length = 0;
	gint search_length_left;

	/* Large default values to begin with. These may not overflow when added up! */
	start_x = 100000;
	start_y = 100000;
	end_x = 0;
	end_y = 0;

	found_segment = TRUE;

	/* ****** Positive Direction */

	x = x_start;
	y = y_start;

	search_length_left = 2*line_width;
	while (found_segment || search_length_left > 0) {
		gint offset;
		gint found_offset = 0;
		gint coverage;
		gint max_coverage = 0;

		search_length_left -= 1;

		x += x_dir;
		y += y_dir;

		found_segment = FALSE;
		for (offset = -line_width; offset <= line_width; offset++) {
			gint coverage_1, coverage_2, coverage_3;

			coverage_1 = count_black_pixel(surface,
			                               x + offset * y_dir - line_width / 2,
			                               y + offset * x_dir - line_width / 2,
			                               line_width,
			                               line_width);
			coverage_2 = count_black_pixel(surface,
			                               x - line_width*x_dir + offset * y_dir - line_width / 2,
			                               y - line_width*y_dir + offset * x_dir - line_width / 2,
			                               line_width,
			                               line_width);
			coverage_3 = count_black_pixel(surface,
			                               x + line_width*x_dir + offset * y_dir - line_width / 2,
			                               y + line_width*y_dir + offset * x_dir - line_width / 2,
			                               line_width,
			                               line_width);

			if (coverage_1 < (line_width * line_width) * LINE_COVERAGE)
				continue;

			if (coverage_2 < (line_width * line_width) * LINE_COVERAGE)
				continue;

			if (coverage_3 < (line_width * line_width) * LINE_COVERAGE)
				continue;

			coverage = coverage_1 + coverage_2 + coverage_3;

			if ((coverage >= (3*line_width * line_width) * LINE_COVERAGE) && (coverage > max_coverage)) {
				gint p_x, p_y, cov_area;

				/* Is this really a "line", ie. is the surrounding area *not* dark. */
				cov_area = count_black_pixel(surface,
				                             x + offset * y_dir - line_width - line_width / 2,
				                             y + offset * x_dir - line_width - line_width / 2,
				                             line_width * 3, line_width * 3);

				if ((abs(x - start_x + y - start_y) > line_width*1.5) && cov_area >= 2*coverage)
					continue;

				found_segment = TRUE;
				found_offset = offset;
				max_coverage = coverage;
				search_length_left = 0;

				p_x = x - line_width*ABS(x_dir) + offset * y_dir;
				p_y = y - line_width*ABS(y_dir) + offset * x_dir;

				if (ABS(start_x * x_dir + start_y * y_dir) > ABS(p_x * x_dir + p_y * y_dir)) {
					start_x = p_x;
					start_y = p_y;
				}

				p_x = x + line_width*ABS(x_dir) + offset * y_dir;
				p_y = y + line_width*ABS(y_dir) + offset * x_dir;

				if (ABS(end_x * x_dir + end_y * y_dir) < ABS(p_x * x_dir + p_y * y_dir)) {
					end_x = p_x;
					end_y = p_y;
				}
			}
		}

		x += found_offset * y_dir;
		y += found_offset * x_dir;

		length = sqrt((start_x - end_x)*(start_x - end_x) + (start_y - end_y)*(start_y - end_y));
		if (length >= line_max_length)
			goto FOLLOW_LINE_BAIL;
	}

	/* ****** Negative Direction */

	x = x_start;
	y = y_start;

	found_segment = TRUE;

	search_length_left = 2*line_width;
	while (found_segment || search_length_left > 0) {
		gint offset;
		gint found_offset = 0;
		gint coverage;
		gint max_coverage = 0;
		search_length_left -= 1;

		x -= x_dir;
		y -= y_dir;

		found_segment = FALSE;
		for (offset = -line_width; (offset <= line_width) && !found_segment; offset++) {
			gint coverage_1, coverage_2, coverage_3;

			coverage_1 = count_black_pixel(surface,
			                               x + offset * y_dir - line_width / 2,
			                               y + offset * x_dir - line_width / 2,
			                               line_width,
			                               line_width);
			coverage_2 = count_black_pixel(surface,
			                               x - line_width*x_dir + offset * y_dir - line_width / 2,
			                               y - line_width*y_dir + offset * x_dir - line_width / 2,
			                               line_width,
			                               line_width);
			coverage_3 = count_black_pixel(surface,
			                               x + line_width*x_dir + offset * y_dir - line_width / 2,
			                               y + line_width*y_dir + offset * x_dir - line_width / 2,
			                               line_width,
			                               line_width);

			if (coverage_1 < (line_width * line_width) * LINE_COVERAGE)
				continue;

			if (coverage_2 < (line_width * line_width) * LINE_COVERAGE)
				continue;

			if (coverage_3 < (line_width * line_width) * LINE_COVERAGE)
				continue;

			coverage = coverage_1 + coverage_2 + coverage_3;

			if ((coverage >= (3*line_width * line_width) * LINE_COVERAGE) && (coverage > max_coverage)) {
				gint p_x, p_y, cov_area;

				/* Is this really a "line", ie. is the surrounding area *not* dark. */
				cov_area = count_black_pixel(surface,
				                             x + offset * y_dir - line_width - line_width / 2,
				                             y + offset * x_dir - line_width - line_width / 2,
				                             line_width * 3, line_width * 3);

				if ((abs(x - start_x + y - start_y) > line_width*1.5) && cov_area >= 2*coverage)
					continue;

				found_segment = TRUE;
				found_offset = offset;
				max_coverage = coverage;
				search_length_left = 0;

				p_x = x - line_width*ABS(x_dir) + offset * y_dir;
				p_y = y - line_width*ABS(y_dir) + offset * x_dir;

				if (ABS(start_x * x_dir + start_y * y_dir) > ABS(p_x * x_dir + p_y * y_dir)) {
					start_x = p_x;
					start_y = p_y;
				}

				p_x = x + line_width*ABS(x_dir) + offset * y_dir;
				p_y = y + line_width*ABS(y_dir) + offset * x_dir;

				if (ABS(end_x * x_dir + end_y * y_dir) < ABS(p_x * x_dir + p_y * y_dir)) {
					end_x = p_x;
					end_y = p_y;
				}
			}
		}

		x += found_offset * y_dir;
		y += found_offset * x_dir;

		length = sqrt((start_x - end_x)*(start_x - end_x) + (start_y - end_y)*(start_y - end_y));
		if (length >= line_max_length)
			goto FOLLOW_LINE_BAIL;
	}

	found_line = length >= line_length;

	if (found_line) {
		gint offset;
		gdouble w1_x, w1_y;
		gdouble w2_x, w2_y;
		gdouble weight;

		x = (start_x * 3 + end_x) / 4;
		y = (start_y * 3 + end_y) / 4;
		w1_x = 0;
		w1_y = 0;
		weight = 0;

		for (offset = - 3 - line_width; offset <= 3 + line_width; offset++) {
			gint seg_weight;
			seg_weight = count_black_pixel(surface,
			                               x + offset * y_dir - MAX(ABS((line_length / 2 - line_width * 2) * x_dir), 1) / 2,
			                               y + offset * x_dir - MAX(ABS((line_length / 2 - line_width * 2) * y_dir), 1) / 2,
			                               MAX(ABS((line_length / 2 - line_width * 2) * x_dir), 1),
			                               MAX(ABS((line_length / 2 - line_width * 2) * y_dir), 1));

			if (weight == 0) { /* this prevents a division by zero if seg_weight is 0 too. */
				weight = seg_weight;
				w1_x = x + offset * y_dir + 0.5;
				w1_y = y + offset * x_dir + 0.5;
			} else {
				gdouble seg_x, seg_y;
				seg_x = x + offset * y_dir + 0.5;
				seg_y = y + offset * x_dir + 0.5;

				w1_x = w1_x * weight / (weight + seg_weight) + seg_x * seg_weight / (weight + seg_weight);
				w1_y = w1_y * weight / (weight + seg_weight) + seg_y * seg_weight / (weight + seg_weight);
				weight += seg_weight;
			}
		}

		x = (start_x + end_x * 3) / 4;
		y = (start_y + end_y * 3) / 4;
		w2_x = 0;
		w2_y = 0;
		weight = 0;

		for (offset = - 3 - line_width; offset <= 3 + line_width; offset++) {
			gint seg_weight;
			seg_weight = count_black_pixel(surface,
			                               x + offset * y_dir - MAX(ABS((line_length / 2 - line_width * 2) * x_dir), 1) / 2,
			                               y + offset * x_dir - MAX(ABS((line_length / 2 - line_width * 2) * y_dir), 1) / 2,
			                               MAX(ABS((line_length / 2 - line_width * 2) * x_dir), 1),
			                               MAX(ABS((line_length / 2 - line_width * 2) * y_dir), 1));

			if (weight == 0) { /* this prevents a division by zero if seg_weight is 0 too. */
				weight = seg_weight;
				w2_x = x + offset * y_dir + 0.5;
				w2_y = y + offset * x_dir + 0.5;
			} else {
				gdouble seg_x, seg_y;
				seg_x = x + offset * y_dir + 0.5;
				seg_y = y + offset * x_dir + 0.5;

				w2_x = w2_x * weight / (weight + seg_weight) + seg_x * seg_weight / (weight + seg_weight);
				w2_y = w2_y * weight / (weight + seg_weight) + seg_y * seg_weight / (weight + seg_weight);
				weight += seg_weight;
			}
		}

		/* got two points, now extrapolate them to the line start/end. */
		*x1 = w1_x - (w2_x - w1_x) / 2.0;
		*y1 = w1_y - (w2_y - w1_y) / 2.0;
		*x2 = w2_x - (w1_x - w2_x) / 2.0;
		*y2 = w2_y - (w1_y - w2_y) / 2.0;
	}

FOLLOW_LINE_BAIL:

	return found_line;
}

static void
calc_intersection(gdouble  l1a_x,    gdouble l1a_y,
                  gdouble  l1b_x,    gdouble l1b_y,
                  gdouble  l2a_x,    gdouble l2a_y,
                  gdouble  l2b_x,    gdouble l2b_y,
                  gdouble *result_x, gdouble *result_y)
{
	gdouble u;

	u = ((l2b_x - l2a_x)*(l1a_y - l2a_y) - (l2b_y - l2a_y)*(l1a_x - l2a_x)) / ((l2b_y - l2a_y)*(l1b_x - l1a_x) - (l2b_x - l2a_x)*(l1b_y - l1a_y));
	*result_x = l1a_x + u*(l1b_x - l1a_x);
	*result_y = l1a_y + u*(l1b_y - l1a_y);
}

#define DIST(x1, y1, x2, y2) sqrt(((x1) - (x2))*((x1) - (x2)) + ((y1) - (y2))*((y1) - (y2)))

static gboolean
test_corner_marker(cairo_surface_t *surface,
                   gint             x,
                   gint             y,
                   gint             x_dir,
                   gint             y_dir,
                   gint             line_width,
                   gint             line_length,
                   gint             line_max_length,
                   gdouble         *x_result,
                   gdouble         *y_result)
{
	gdouble h_x1, h_x2, h_y1, h_y2;
	gboolean h_found_line;
	gdouble v_x1, v_x2, v_y1, v_y2;
	gboolean v_found_line;
	gint width, height;

	/* We just try to find both right away, even though we can only
	 * expect to find one of them. */
	h_found_line = follow_line(surface, x, y, x_dir, 0,
	                           line_width, line_length, line_max_length,
	                           &h_x1, &h_y1, &h_x2, &h_y2);

	v_found_line = follow_line(surface, x, y, 0, y_dir,
	                           line_width, line_length, line_max_length,
	                           &v_x1, &v_y1, &v_x2, &v_y2);

	if (!(h_found_line || v_found_line))
		return FALSE;

	if (!h_found_line) {
		if (y_dir < 0)
			h_found_line = follow_line(surface, v_x1, v_y1, x_dir, 0,
			                           line_width, line_length, line_max_length,
			                           &h_x1, &h_y1, &h_x2, &h_y2);
		else
			h_found_line = follow_line(surface, v_x2, v_y2, x_dir, 0,
			                           line_width, line_length, line_max_length,
			                           &h_x1, &h_y1, &h_x2, &h_y2);
	}

	if (!v_found_line) {
		if (x_dir < 0)
			v_found_line = follow_line(surface, h_x1, h_y1, 0, y_dir,
			                           line_width, line_length, line_max_length,
			                           &v_x1, &v_y1, &v_x2, &v_y2);
		else
			v_found_line = follow_line(surface, h_x2, h_y2, 0, y_dir,
			                           line_width, line_length, line_max_length,
			                           &v_x1, &v_y1, &v_x2, &v_y2);
	}

	if (!v_found_line || !h_found_line)
		return FALSE;

	/* Check that two of the endpoints are close together. */
	if ((DIST(h_x1, h_y1, v_x1, v_y1) > line_width * 3) &&
	    (DIST(h_x1, h_y1, v_x2, v_y2) > line_width * 3) &&
	    (DIST(h_x2, h_y2, v_x1, v_y1) > line_width * 3) &&
	    (DIST(h_x2, h_y2, v_x2, v_y2) > line_width * 3))
		return FALSE;

	calc_intersection(h_x1, h_y1, h_x2, h_y2,
	                  v_x1, v_y1, v_x2, v_y2,
	                  x_result, y_result);

	/* Check that the resulting position is not on the border of the image. */
	width = cairo_image_surface_get_width (surface);
	height = cairo_image_surface_get_height (surface);

	if (*x_result - 3*line_width <= 0)
		return FALSE;
	if (*x_result + 3*line_width >= width)
		return FALSE;

	if (*y_result - 3*line_width <= 0)
		return FALSE;
	if (*y_result + 3*line_width >= height)
		return FALSE;

	return TRUE;
}

static gboolean
real_find_corner_marker(cairo_surface_t *surface,
                        gint             x_start,
                        gint             y_start,
                        gint             x_dir,
                        gint             y_dir,
                        gint             search_distance,
                        gint             line_width,
                        gint             line_length,
                        gint             line_max_length,
                        gdouble         *x_result,
                        gdouble         *y_result)
{
	gint x, y;
	gint distance = 0;
	gint search;
	gboolean found = FALSE;
	gint coverage = 0;

	while (!found && (distance < search_distance)) {
		distance += line_length / 4;

		/* Try searching from the top/bottom. */
		coverage = 0;
		x = x_start + (x_dir * line_width) / 2 + x_dir * distance;
		y = y_start + (y_dir * line_width) / 2;

		for (search = 0; search < distance; search++) {
			gint old_coverage = coverage;

			y += y_dir;

			coverage = count_black_pixel(surface,
			                             x - line_width / 2,
			                             y - line_width / 2,
			                             line_width,
			                             line_width);

			if ((old_coverage > (line_width * line_width) * LINE_COVERAGE) && (old_coverage > coverage)) {
				if (test_corner_marker(surface, x, y, -x_dir, -y_dir,
				                       line_width, line_length, line_max_length,
				                       x_result, y_result))
					return TRUE;
			}
		}

		/* Try searching from the left/right. */
		coverage = 0;
		x = x_start + x_dir * line_width / 2;
		y = y_start + y_dir * line_width / 2 + y_dir * distance;

		for (search = 0; search < distance; search++) {
			gint old_coverage = coverage;

			x += x_dir;

			coverage = count_black_pixel(surface,
			                             x - line_width / 2,
			                             y - line_width / 2,
			                             line_width,
			                             line_width);

			if ((old_coverage > (line_width * line_width) * LINE_COVERAGE) && (old_coverage > coverage)) {
				if (test_corner_marker(surface, x, y, -x_dir, -y_dir,
				                       line_width, line_length, line_max_length,
				                       x_result, y_result))
					return TRUE;
			}
		}
	}

	return FALSE;
}



/* Find corner marker */
gboolean
find_corner_marker(cairo_surface_t *surface,
                   cairo_matrix_t  *matrix,
                   gint             corner,
                   gdouble         *marker_x,
                   gdouble         *marker_y)
{
	gint width, height;
	gint line_width;
	gint line_length;
	gint line_max_length;
	gint dx, dy;
	gint start_x, start_y;
	gint search_distance;

	line_width = transform_distance_to_pixel(matrix, sdaps_line_width);
	line_length = transform_distance_to_pixel(matrix, sdaps_line_min_length);
	line_max_length = transform_distance_to_pixel(matrix, sdaps_line_max_length);
	search_distance = transform_distance_to_pixel(matrix, sdaps_corner_mark_search_distance);

	width = cairo_image_surface_get_width (surface);
	height = cairo_image_surface_get_height (surface);

	switch (corner) {
		case 1:
			dx = 1;
			dy = 1;
			start_x = 0;
			start_y = 0;
			break;
		case 2:
			dx = -1;
			dy = 1;
			start_x = width;
			start_y = 0;
			break;
		case 3:
			dx = -1;
			dy = -1;
			start_x = width;
			start_y = height;
			break;
		case 4:
			dx = 1;
			dy = -1;
			start_x = 0;
			start_y = height;
			break;
		default:
			g_assert_not_reached();
	}

	return real_find_corner_marker(surface, start_x, start_y, dx, dy, search_distance, line_width, line_length, line_max_length, marker_x, marker_y);
}

cairo_matrix_t*
calculate_correction_matrix_masked(cairo_surface_t  *surface,
                                   cairo_surface_t  *mask,
                                   cairo_matrix_t   *matrix,
                                   gdouble           mm_x,
                                   gdouble           mm_y,
                                   gdouble          *covered)
{
	gdouble tmp_x, tmp_y;
	gint px_x, px_y, px_width, px_height;
	cairo_matrix_t inverse;
	cairo_matrix_t *result = NULL;
	gint test_dist;
	gint x_offset, y_offset;
	gint x_cov;
	gint y_cov;
	gint coverage = 0;

	inverse = *matrix;
	cairo_matrix_invert(&inverse);

	tmp_x = mm_x;
	tmp_y = mm_y;
	cairo_matrix_transform_point(matrix, &tmp_x, &tmp_y);
	px_x = tmp_x;
	px_y = tmp_y;

	/* Shut up the compiler. */
	x_cov = px_x;
	y_cov = px_y;

	px_width = cairo_image_surface_get_width(mask);
	px_height = cairo_image_surface_get_height(mask);

	test_dist = MIN(px_width, px_height) / 2;

	/* Top */
	for (x_offset = -test_dist; x_offset <= test_dist; x_offset++) {
		for (y_offset = -test_dist; y_offset <= test_dist; y_offset++) {
			gint new_cov;

			new_cov = count_black_pixel_masked(surface, mask, px_x + x_offset, px_y + y_offset);
			if (coverage < new_cov) {
				coverage = new_cov;
				x_cov = px_x + x_offset;
				y_cov = px_y + y_offset;
			}
		}
	}

	tmp_x = x_cov;
	tmp_y = y_cov;
	cairo_matrix_transform_point(&inverse, &tmp_x, &tmp_y);

	result = g_new(cairo_matrix_t, 1);
	cairo_matrix_init_identity(result);

	/* Just a translation */
	result->x0 = tmp_x - mm_x;
	result->y0 = tmp_y - mm_y;

	*covered = coverage / (gdouble) count_black_pixel(mask, 0, 0, px_width, px_height);

	return result;
}

gboolean
find_box_corners(cairo_surface_t  *surface,
                 cairo_matrix_t   *matrix,
                 gdouble           mm_x,
                 gdouble           mm_y,
                 gdouble           mm_width,
                 gdouble           mm_height,
                 gdouble          *mm_x1,
                 gdouble          *mm_y1,
                 gdouble          *mm_x2,
                 gdouble          *mm_y2,
                 gdouble          *mm_x3,
                 gdouble          *mm_y3,
                 gdouble          *mm_x4,
                 gdouble          *mm_y4)
{
	cairo_matrix_t inverse;
	gdouble px_x1, px_y1, px_x2, px_y2, px_x3, px_y3, px_x4, px_y4;
	gdouble px_width, px_height;
	gint line_width;
	gint line_length;
	gint line_max_length;
	gint search_distance;

	line_width = transform_distance_to_pixel(matrix, sdaps_line_width);

	inverse = *matrix;
	cairo_matrix_invert(&inverse);

	/* Assume that the image is loaded rotated and pixel with/height is positive. */
	px_x1 = mm_x;
	px_y1 = mm_y;
	px_x2 = mm_x + mm_width;
	px_y2 = mm_y;
	px_x3 = mm_x + mm_width;
	px_y3 = mm_y + mm_height;
	px_x4 = mm_x;
	px_y4 = mm_y + mm_height;

	px_width = mm_width;
	px_height = mm_height;

	cairo_matrix_transform_point(matrix, &px_x1, &px_y1);
	cairo_matrix_transform_point(matrix, &px_x2, &px_y2);
	cairo_matrix_transform_point(matrix, &px_x3, &px_y3);
	cairo_matrix_transform_point(matrix, &px_x4, &px_y4);

	cairo_matrix_transform_distance(matrix, &px_width, &px_height);

	line_length = MIN(10*line_width, MIN(px_width, px_height)) - line_width;
	line_max_length = MAX(10*line_width, MAX(px_width, px_height)) + 5*line_width;
	search_distance = line_length;
	/* We have the corner pixel positions, now try to find them. */

	if (!real_find_corner_marker(surface, px_x1 - 4*line_width, px_y1 - 4*line_width, 1, 1, search_distance, line_width, line_length, line_max_length, &px_x1, &px_y1))
		return FALSE;
	if (!real_find_corner_marker(surface, px_x2 + 4*line_width, px_y2 - 4*line_width, -1, 1, search_distance, line_width, line_length, line_max_length, &px_x2, &px_y2))
		return FALSE;
	if (!real_find_corner_marker(surface, px_x3 + 4*line_width, px_y3 + 4*line_width, -1, -1, search_distance, line_width, line_length, line_max_length, &px_x3, &px_y3))
		return FALSE;
	if (!real_find_corner_marker(surface, px_x4 - 4*line_width, px_y4 + 4*line_width, 1, -1, search_distance, line_width, line_length, line_max_length, &px_x4, &px_y4))
		return FALSE;

	/* Found the corners, convert them back and return. */
	*mm_x1 = px_x1;
	*mm_y1 = px_y1;
	*mm_x2 = px_x2;
	*mm_y2 = px_y2;
	*mm_x3 = px_x3;
	*mm_y3 = px_y3;
	*mm_x4 = px_x4;
	*mm_y4 = px_y4;

	cairo_matrix_transform_point(&inverse, mm_x1, mm_y1);
	cairo_matrix_transform_point(&inverse, mm_x2, mm_y2);
	cairo_matrix_transform_point(&inverse, mm_x3, mm_y3);
	cairo_matrix_transform_point(&inverse, mm_x4, mm_y4);

	return TRUE;
}

gdouble
get_coverage(cairo_surface_t *surface,
             cairo_matrix_t  *matrix,
             gdouble          mm_x,
             gdouble          mm_y,
             gdouble          mm_width,
             gdouble          mm_height)
{
	gint x, y, width, height;
	gdouble tmp_x, tmp_y;
	gint black, all;

	/* Transform to pixel. */
	tmp_x = mm_x;
	tmp_y = mm_y;
	cairo_matrix_transform_point(matrix, &tmp_x, &tmp_y);
	x = tmp_x;
	y = tmp_y;

	tmp_x = mm_width;
	tmp_y = mm_height;
	cairo_matrix_transform_distance(matrix, &tmp_x, &tmp_y);
	width = tmp_x;
	height = tmp_y;

	black = count_black_pixel(surface, x, y, width, height);
	all = width * height;

	if (sdaps_create_debug_surface) {
		cairo_surface_t *surf = debug_surface_create(x, y, width, height, 0, 0, 0, 0);
		cairo_t *cr = cairo_create(surf);

		cairo_set_source_rgba(cr, 1, 0, 0, 0.5);
		cairo_paint(cr);

		cairo_destroy(cr);
		cairo_surface_flush(surf);
	}

	return black / (gdouble) all;
}

gdouble
get_masked_coverage(cairo_surface_t *surface,
                    cairo_surface_t *mask,
                    gint             x,
                    gint             y)
{
	gint width, height;
	gint black, all;

	width = cairo_image_surface_get_width(mask);
	height = cairo_image_surface_get_height(mask);

	all = count_black_pixel(mask, 0, 0, width, height);
	black = count_black_pixel_masked(surface, mask, x, y);

	if (sdaps_create_debug_surface) {
		cairo_surface_t *surf = debug_surface_create(x, y, width, height, 0, 0, 0, 0);
		cairo_t *cr = cairo_create(surf);

		cairo_set_source_rgba(cr, 1, 0, 0, 0.5);
		cairo_mask_surface(cr, mask, 0, 0);

		cairo_destroy(cr);
		cairo_surface_flush(surf);
	}

	return black / (gdouble) all;
}

/* First removes the number of lines, and then calculates the coverage of what
 * is left. */
gdouble
get_masked_coverage_without_lines(cairo_surface_t *surface,
                                  cairo_surface_t *mask,
                                  gint             x,
                                  gint             y,
                                  gdouble          line_width,
                                  gint             line_count)
{
	cairo_surface_t *tmp_surface;
	cairo_surface_t *debug_surf;
	gint width, height;
	gdouble result;
	gint i, all;

	width = cairo_image_surface_get_width(mask);
	height = cairo_image_surface_get_height(mask);

	all = count_black_pixel(mask, 0, 0, width, height);

	tmp_surface = surface_copy_masked(surface, mask, x, y);

	debug_surf = debug_surface_create(x, y, width, height, 0, 0, 0, 0);
	if (debug_surf) {
		cairo_t *cr;
		cr = cairo_create(debug_surf);
		cairo_set_source_rgba(cr, 0, 0, 1, 0.5);
		cairo_mask_surface(cr, mask, 0, 0);

		cairo_destroy(cr);
		cairo_surface_flush(debug_surf);
	}

#if 0
	/* Something like this could be used to filter the image first.
	 * Obviously, for that to work, the size of the surface needs to be
	 * adjusted accordingly. */
	kfill_modified(tmp_surface, 5);

	cr = cairo_create(tmp_surface);
	cairo_set_fill_rule(cr, CAIRO_FILL_RULE_EVEN_ODD);
	cairo_rectangle(cr, 0, 0, width+4, height+4);
	cairo_rectangle(cr, 2, 2, width, height);
	cairo_set_source_rgba(cr, 0, 0, 0, 0);
	cairo_set_operator(cr, CAIRO_OPERATOR_SOURCE);
	cairo_fill(cr);
	cairo_destroy(cr);
	cairo_surface_flush(tmp_surface);
#endif

	/* Remove the requested number of lines. */
	for (i = 0; i < line_count; i++)
		remove_maximum_line(tmp_surface, debug_surf, line_width);

	result = count_black_pixel(tmp_surface, 0, 0, width, height) / (gdouble) all;

	cairo_surface_destroy(tmp_surface);

	return result;
}

guint
get_masked_white_area_count(cairo_surface_t *surface,
                            cairo_surface_t *mask,
                            gint             x,
                            gint             y,
                            gdouble          min_size,
                            gdouble          max_size,
                            gdouble         *filled_area)
{
	cairo_surface_t *tmp_surface;
	cairo_surface_t *backup_surface;
	cairo_surface_t *debug_surf;
	cairo_t *backup_cr;
	gint width, height;
	guint result = 0;
	guint min_size_px;
	guint max_size_px;
	guint all;

	width = cairo_image_surface_get_width(mask);
	height = cairo_image_surface_get_height(mask);

	all = count_black_pixel(mask, 0, 0, width, height);

	min_size_px = all * min_size;
	max_size_px = all * max_size;

	tmp_surface = surface_inverted_copy_masked(surface, mask, x, y);

	/* Debug images */
	debug_surf = debug_surface_create(x, y, width, height, 0, 0, 0, 0);
	if (debug_surf != NULL) {
		cairo_t *debug_cr;

		backup_surface = surface_copy(tmp_surface);
		backup_cr = cairo_create(backup_surface);
		cairo_set_operator(backup_cr, CAIRO_OPERATOR_SOURCE);

		debug_cr = cairo_create(debug_surf);
		cairo_set_source_rgba(debug_cr, 0, 0, 1, 0.5);
		cairo_mask_surface(debug_cr, tmp_surface, 0, 0);

		cairo_destroy(debug_cr);
		cairo_surface_flush(debug_surf);
	}

	*filled_area = 0;

	for (y = 0; y < height; y++) {
		for (x = 0; x < width; x++) {
			if (debug_surf != NULL) {
				cairo_set_source_surface(backup_cr, tmp_surface, 0, 0);
				cairo_paint(backup_cr);
			}

			guint area = flood_fill(tmp_surface, NULL, x, y, 1);
			if ((area >= min_size_px) && (area <= max_size_px)) {
				result += 1;
				*filled_area += area / ((gdouble) all);

				/* Flood fill again, this time also mark the area on the debug surface. */
				if (debug_surf)
					flood_fill(backup_surface, debug_surf, x, y, 1);
			}
		}
	}

	if (debug_surf != NULL) {
		cairo_surface_destroy(backup_surface);
		cairo_destroy(backup_cr);
	}

	cairo_surface_destroy(tmp_surface);

	return result;
}


