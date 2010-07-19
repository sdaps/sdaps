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

/*#include <gdk-pixbuf/gdk-pixbuf.h>*/
#include <tiffio.h>
#include "image.h"
#include <string.h>

#if G_BYTE_ORDER == G_BIG_ENDIAN
#define SET_PIXEL(_pixels, _stride, _x, _y, _value) *(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4) = (*(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4) & (0xffffffff ^ (1 << (31 - (_x) % 32)))) | ((!!(_value)) << (31 - (_x) % 32))
#define GET_PIXEL(_pixels, _stride, _x, _y) (((*(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4)) >> (31 - (_x) % 32)) & 0x1)
#else
#define SET_PIXEL(_pixels, _stride, _x, _y, _value) *(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4) = (*(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4) & (0xffffffff ^ (1 << ((_x) % 32)))) | ((!!(_value)) << ((_x) % 32))
#define GET_PIXEL(_pixels, _stride, _x, _y) (((*(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4)) >> ((_x) % 32)) & 0x1)
#endif

cairo_surface_t*
get_a1_from_tiff (char *filename, gboolean rotated)
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

	TIFFGetField(tiff, TIFFTAG_IMAGEWIDTH, &width);
	TIFFGetField(tiff, TIFFTAG_IMAGELENGTH, &height);
	t_pixels = g_malloc(width * height *sizeof(uint32));
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
		for (x = 0; x < width; x++) {
			SET_PIXEL(s_pixels, s_stride, x, y, !(TIFFGetR(*t_p) >> 7));
			t_p = t_p + 1;
		}
		t_row = (guint32*) ((char*) t_row + t_stride);
	}

	g_free(t_pixels);
	TIFFClose(tiff);
	
	return surface;
}

void
get_pbm(cairo_surface_t *surface, void **data, int *length)
{
	int width, height;
	int s_stride;
	int d_stride;
	unsigned char* s_pixel;
	unsigned char* d_pixel;
	char *start;
	int x, y, i;

	*data = NULL;
	*length = 0;

	if (cairo_image_surface_get_format (surface) != CAIRO_FORMAT_A1)
		return;

	width = cairo_image_surface_get_width(surface);
	height = cairo_image_surface_get_height(surface);
	s_stride = cairo_image_surface_get_stride(surface);
	s_pixel = cairo_image_surface_get_data(surface);

	start = g_strdup_printf("P4\n%i %i\n", width, height);
	d_stride = (width + 7) / 8;
	*length = strlen(start) + height * d_stride;
	*data = g_malloc(*length);
	strcpy(*data, start);
	d_pixel = *data + strlen(start);
	g_free(start);
	
	for (i = 0; i < height * d_stride; i++) {
		*(d_pixel + i) = 0;
	}

	for (y = 0; y < height; y++) {
		for (x = 0; x < width; x++) {
			*(d_pixel + y*d_stride + x / 8) |= (GET_PIXEL(s_pixel, s_stride, x, y)) << (7 - x % 8);
		}	
	}
}

static gint
count_black_pixel(cairo_surface_t *surface, gint x, gint y, gint width, gint height)
{
	guint32 *pixels;
	int stride;
	int x_pos, y_pos;
	int img_width, img_height;
	int black_pixel = 0;

	pixels = (guint32*) cairo_image_surface_get_data(surface);
	img_width = cairo_image_surface_get_width(surface);
	img_height = cairo_image_surface_get_height(surface);
	stride = cairo_image_surface_get_stride(surface);

	if (y < 0) {
		height += y;
		y = 0;
	}
	if (x < 0) {
		width += x;
		x = 0;
	}
	if (x + width > img_width) {
		width = img_width - x;
	}
	if (y + height > img_height) {
		height = img_height - y;
	}

	for (y_pos = y; y_pos < y + height; y_pos++) {
		for (x_pos = x; x_pos < x + width; x_pos++) {
			black_pixel += GET_PIXEL(pixels, stride, x_pos, y_pos);
		}
	}

	return black_pixel;	
}

#define LINE_COVERAGE 0.65

static gboolean
follow_line(cairo_surface_t *surface,
            gint             x_start,
            gint             y_start,
            gint             x_dir,
            gint             y_dir,
            gint             line_width,
            gint             line_length,
            gdouble         *x1,
            gdouble         *y1,
            gdouble         *x2,
            gdouble         *y2)
{
	/* This function assumes that there is enough space in every direction and
	 * it will not run off the buffer. */
	gboolean found_segment;
	gboolean found_line = FALSE;
	gint x, y;
	gint start_x, start_y;
	gint end_x, end_y;
	gint length = 1;
	
	x = x_start;
	y = y_start;
	
	start_x = 100000; /* MAY NOT OVERFLOW WHEN ADDED UP! */
	start_y = 100000;
	end_x = 0;
	end_y = 0;
	
	found_segment = TRUE;

	/* go into the positive direction */
	while (found_segment) {
		gint offset;
		gint coverage = 0;
		x += x_dir;
		y += y_dir;
		
		found_segment = FALSE;
		for (offset = -5; (offset <= 5) && !found_segment; offset++) {
			gint old_coverage = coverage;
			coverage = count_black_pixel(surface,
			                             x + offset * y_dir - line_width / 2,
			                             y + offset * x_dir - line_width / 2,
			                             line_width,
			                             line_width);

			if ((old_coverage > (line_width * line_width) * LINE_COVERAGE) && (old_coverage > coverage)) {
				gint p_x, p_y;
				found_segment = TRUE;

				length += 1;

				p_x = x + offset * y_dir;
				p_y = y + offset * x_dir;
				
				if (start_x + start_y > p_x + p_y) {
					start_x = p_x;
					start_y = p_y;
				}
				if (end_x + end_y < p_x + p_y) {
					end_x = p_x;
					end_y = p_y;
				}
			}
		}
		x += offset * y_dir;
		y += offset * x_dir;
		
		if (length >= line_length * 1.5)
			goto FOLLOW_LINE_BAIL;
	}
	
	x = x_start;
	y = y_start;
	found_segment = TRUE;

	/* go into the negative direction */
	while (found_segment) {
		gint offset;
		gint coverage = 0;
		x -= x_dir;
		y -= y_dir;
		
		found_segment = FALSE;
		for (offset = -5; (offset <= 5) && !found_segment; offset++) {
			gint old_coverage = coverage;
			coverage = count_black_pixel(surface,
			                             x + offset * y_dir - line_width / 2,
			                             y + offset * x_dir - line_width / 2,
			                             line_width,
			                             line_width);

			if ((old_coverage > (line_width * line_width) * LINE_COVERAGE) && (old_coverage > coverage)) {
				gint p_x, p_y;
				found_segment = TRUE;

				length += 1;

				p_x = x + offset * y_dir;
				p_y = y + offset * x_dir;
				
				if (start_x + start_y > p_x + p_y) {
					start_x = p_x;
					start_y = p_y;
				}
				if (end_x + end_y < p_x + p_y) {
					end_x = p_x;
					end_y = p_y;
				}
			}
		}
		x += offset * y_dir;
		y += offset * x_dir;
		
		if (length >= line_length * 1.5)
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
				w1_x = x + offset * y_dir + 0.5 * y_dir;
				w1_y = y + offset * x_dir + 0.5 * x_dir;
			} else {
				gdouble seg_x, seg_y;
				seg_x = x + offset * y_dir + 0.5 * y_dir;
				seg_y = y + offset * x_dir + 0.5 * x_dir;
				
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
				w2_x = x + offset * y_dir + 0.5 * y_dir;
				w2_y = y + offset * x_dir + 0.5 * x_dir;
			} else {
				gdouble seg_x, seg_y;
				seg_x = x + offset * y_dir + 0.5 * y_dir;
				seg_y = y + offset * x_dir + 0.5 * x_dir;
				
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
	
	u = ((l2b_x - l2a_x)*(l1a_y - l2a_y) - (l2b_y - l2a_y)*(l1a_x - l2a_x)) / ((l2b_y - l2a_y)*(l1b_x-l1a_x) - (l2b_x - l2a_x)*(l1b_y - l1a_y));
	*result_x = l1a_x + u*(l1b_x - l1a_x);
	*result_y = l1a_y + u*(l1b_y - l1a_y);
}


static gboolean
find_corner_marker(cairo_surface_t *surface,
                   gint             x_start,
                   gint             y_start,
                   gint             x_dir,
                   gint             y_dir,
                   gint             line_width,
                   gint             line_length,
                   gdouble         *x_result,
                   gdouble         *y_result)
{
	gint x, y;
	gint distance = 0;
	gint search;
	gboolean found = FALSE;
	gint coverage = 0;
	gint width;
	
	width = cairo_image_surface_get_width(surface);

	x = x_start + (x_dir * (width / 6 + 1));
	y = y_start + y_dir;
	
	while (!found && (distance < 600)) {
		distance += 1;

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
				/* XXX: TODO: Put this into a separate function! */
				gdouble h_x1, h_x2, h_y1, h_y2;
				gboolean h_found_line;
				gdouble v_x1, v_x2, v_y1, v_y2;
				gboolean v_found_line;
				
				h_found_line = follow_line(surface, x, y - y_dir, x_dir, 0,
				                           line_width, line_length,
				                           &h_x1, &h_y1, &h_x2, &h_y2);

				v_found_line = follow_line(surface, x, y - y_dir, 0, y_dir,
				                           line_width, line_length,
				                           &v_x1, &v_y1, &v_x2, &v_y2);

				if (!(h_found_line || v_found_line))
					continue;

				if (!h_found_line) {
					h_found_line = follow_line(surface, v_x1, v_y1, x_dir, 0,
					                           line_width, line_length,
					                           &h_x1, &h_y1, &h_x2, &h_y2);
				}
				if (!h_found_line) {
					h_found_line = follow_line(surface, v_x2, v_y2, x_dir, 0,
					                           line_width, line_length,
					                           &h_x1, &h_y1, &h_x2, &h_y2);
				}

				if (!v_found_line) {
					v_found_line = follow_line(surface, h_x1, h_y1, 0, y_dir,
					                           line_width, line_length,
					                           &v_x1, &v_y1, &v_x2, &v_y2);
				}
				if (!v_found_line) {
					v_found_line = follow_line(surface, h_x2, h_y2, 0, y_dir,
					                           line_width, line_length,
					                           &v_x1, &v_y1, &v_x2, &v_y2);
				}
				
				if (!v_found_line || !h_found_line)
					continue;

				calc_intersection(h_x1, h_y1, h_x2, h_y2,
				                  v_x1, v_y1, v_x2, v_y2,
				                  x_result, y_result);
				return TRUE;
			}
		}

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
				gdouble h_x1, h_x2, h_y1, h_y2;
				gboolean h_found_line;
				gdouble v_x1, v_x2, v_y1, v_y2;
				gboolean v_found_line;
				
				h_found_line = follow_line(surface, x - x_dir, y, 1, 0,
				                           line_width, line_length,
				                           &h_x1, &h_y1, &h_x2, &h_y2);

				v_found_line = follow_line(surface, x - x_dir, y, 0, 1,
				                           line_width, line_length,
				                           &v_x1, &v_y1, &v_x2, &v_y2);

				if (!(h_found_line || v_found_line))
					continue;

				if (!h_found_line) {
					h_found_line = follow_line(surface, v_x1, v_y1, 1, 0,
					                           line_width, line_length,
					                           &h_x1, &h_y1, &h_x2, &h_y2);
				}
				if (!h_found_line) {
					h_found_line = follow_line(surface, v_x2, v_y2, 1, 0,
					                           line_width, line_length,
					                           &h_x1, &h_y1, &h_x2, &h_y2);
				}

				if (!v_found_line) {
					v_found_line = follow_line(surface, h_x1, h_y1, 0, 1,
					                           line_width, line_length,
					                           &v_x1, &v_y1, &v_x2, &v_y2);
				}
				if (!v_found_line) {
					v_found_line = follow_line(surface, h_x2, h_y2, 0, 1,
					                           line_width, line_length,
					                           &v_x1, &v_y1, &v_x2, &v_y2);
				}
				
				if (!v_found_line || !h_found_line)
					continue;

				calc_intersection(h_x1, h_y1, h_x2, h_y2,
				                  v_x1, v_y1, v_x2, v_y2,
				                  x_result, y_result);
				return TRUE;
			}
		}
	}
	
	return FALSE;
}


/*****************************************************************************
 * calculate_matrix
 *
 * This function calculates the matrix based on the corner markers.
 * NB: The corner markers are lines with the end points on the positions
 *     passed into this function.
 *     This is different to boxes, where the coordinates are the bounding
 *     box of the checkbox!
 *
 *****************************************************************************/
cairo_matrix_t*
calculate_matrix(cairo_surface_t *surface,
                          gdouble mm_x,
                          gdouble mm_y,
                          gdouble mm_width,
                          gdouble mm_height)
{
	gint width, height;
	gint line_width = 5; /* XXX: Guestimation! 5? */
	gint line_length = 230; /* XXX: Guestimation! */
	gdouble x_topleft, y_topleft;
	gdouble x_topright, y_topright;
	gdouble x_bottomleft, y_bottomleft;
	gdouble x_bottomright, y_bottomright;
	gdouble x_center, y_center;
	gdouble dx, dy;
	gdouble length_squared;
	cairo_matrix_t *result;
	
	width = cairo_image_surface_get_width (surface);
	height = cairo_image_surface_get_height (surface);
	
	if (!find_corner_marker(surface, 0, 0, 1, 1, line_width, line_length, &x_topleft, &y_topleft))
		return NULL;
	if (!find_corner_marker(surface, width - 1, 0, -1, 1, line_width, line_length, &x_topright, &y_topright))
		return NULL;
	if (!find_corner_marker(surface, 0, height - 1, 1, -1, line_width, line_length, &x_bottomleft, &y_bottomleft))
		return NULL;
	if (!find_corner_marker(surface, width - 1, height - 1,-1, -1, line_width, line_length, &x_bottomright, &y_bottomright))
		return NULL;

	/* Corners are known, now calculate the matrix. */
	
	result = g_malloc(sizeof(cairo_matrix_t));

	/* X-Axis *********************/
	dx = ((x_topright - x_topleft) + (x_bottomright - x_bottomleft)) / 2.0;
	dy = ((y_topright - y_topleft) + (y_bottomright - y_bottomleft)) / 2.0;
	length_squared = dx*dx + dy*dy;

	result->xx = dx / length_squared * mm_width;
	result->yx = -dy / length_squared * mm_width; /* negative for some reason, no idea why right now ... */

	/* Y-Axis *********************/
	dx = ((x_bottomright - x_topright) + (x_bottomleft - x_topleft)) / 2.0;
	dy = ((y_bottomright - y_topright) + (y_bottomleft - y_topleft)) / 2.0;
	
	length_squared = dx*dx + dy*dy;
	result->xy = -dx / length_squared * mm_height; /* negative for some reason, no idea why right now ... */
	result->yy = dy / length_squared * mm_height;

	/* Center everything between the markers. */
	x_center = (x_bottomleft + x_bottomright + x_topleft + x_topright) / 4.0;
	y_center = (y_bottomleft + y_bottomright + y_topleft + y_topright) / 4.0;
	/* top/left corner (based on the center) */
	result->x0 = mm_width / 2.0 + mm_x;
	result->y0 = mm_height / 2.0 + mm_y;

	dx = x_center * result->xx + y_center * result->xy;
	dy = x_center * result->yx + y_center * result->yy;
	result->x0 -= dx;
	result->y0 -= dy;

	return result;
}


#if 0

/* The following code was an attempt at calculating the correction matrix.
 * It may turn out to work well for large boxes, however for small ones it
 * fails sometimes. */

static gboolean
find_edge(cairo_surface_t  *surface,
          gint              x,
          gint              y,
          gint              x_dir,
          gint              y_dir,
          gint              test_dist,
          gint              test_length,
          gint              test_width,
          gdouble          *edge_x,
          gdouble          *edge_y)
{
	gint i;
	gint black_pixel = 0;
	
	for (i = -test_dist; i < test_dist; i++) {
		gint old_black_pixel = black_pixel;
		
		black_pixel = count_black_pixel(surface,
		                                x + x_dir * i - (ABS(y_dir) * test_length + ABS(x_dir) * test_width) / 2,
		                                y + y_dir * i - (ABS(x_dir) * test_length + ABS(y_dir) * test_width) / 2,
		                                MAX(ABS(y_dir) * test_length, test_width),
		                                MAX(ABS(x_dir) * test_length, test_width));

		if ((old_black_pixel > LINE_COVERAGE * test_length * test_width) &&
		    (old_black_pixel > black_pixel) &&
		    (black_pixel <= LINE_COVERAGE * test_length * test_width)) {
			/* Assume we found the edge, return current position */
			*edge_x = x + x_dir * i - (ABS(y_dir) * test_length) / 2 + 0.5;
			*edge_y = y + y_dir * i - (ABS(x_dir) * test_length) / 2 + 0.5;
			return TRUE;
		}
	}
	
	return FALSE;
}

cairo_matrix_t*
calculate_correction_matrix(cairo_surface_t  *surface,
                            cairo_matrix_t   *matrix,
                            gdouble           mm_x,
                            gdouble           mm_y,
                            gdouble           mm_width,
                            gdouble           mm_height)
{
	gdouble tmp_x, tmp_y;
	gint px_x, px_y, px_width, px_height;
	gdouble x, y, width, height;
	cairo_matrix_t inverse;
	cairo_matrix_t *result = NULL;
	gint test_length = 30;
	gint test_dist = 8; /* search +- 8px (which should be more then enough) */
	gint test_width = 5;
	gint test_count;
	gint i;
	GArray *top = g_array_new(FALSE, FALSE, sizeof(gdouble));
	GArray *bottom = g_array_new(FALSE, FALSE, sizeof(gdouble));
	GArray *left = g_array_new(FALSE, FALSE, sizeof(gdouble));
	GArray *right = g_array_new(FALSE, FALSE, sizeof(gdouble));
	
	inverse = *matrix;
	cairo_matrix_invert(&inverse);
	
	tmp_x = mm_x;
	tmp_y = mm_y;
	cairo_matrix_transform_point(matrix, &tmp_x, &tmp_y);
	px_x = tmp_x;
	px_y = tmp_y;

	tmp_x = mm_width;
	tmp_y = mm_height;
	cairo_matrix_transform_distance(matrix, &tmp_x, &tmp_y);
	px_width = tmp_x + 0.5;
	px_height = tmp_y + 0.5;

	/* Top */
	test_count = px_width / test_length;
	if (test_count == 0)
		return NULL;

	for (i = 0; i < test_count; i++) {
		gdouble edge_x = 0, edge_y = 0;
		gboolean found_edge;
		
		found_edge = find_edge(surface,
		                       (px_width - test_length * test_count) / 2 + test_length / 2 + px_x + test_length * i,
		                       px_y,
		                       0, -1,
		                       test_dist, test_length, test_width,
		                       &edge_x, &edge_y);

		cairo_matrix_transform_point(&inverse, &edge_x, &edge_y);
		if (found_edge)
			g_array_append_val(top, edge_y);
	}

	for (i = 0; i < test_count; i++) {
		gdouble edge_x = 0, edge_y = 0;
		gboolean found_edge;
		
		found_edge = find_edge(surface,
		                       (px_width - test_length * test_count) / 2 + test_length / 2 + px_x + test_length * i,
		                       px_y + px_height,
		                       0, 1,
		                       test_dist, test_length, test_width,
		                       &edge_x, &edge_y);

		cairo_matrix_transform_point(&inverse, &edge_x, &edge_y);
		if (found_edge)
			g_array_append_val(bottom, edge_y);
	}

	test_count = px_height / test_length;
	if (test_count == 0)
		return NULL;

	for (i = 0; i < test_count; i++) {
		gdouble edge_x = 0, edge_y = 0;
		gboolean found_edge;
		
		found_edge = find_edge(surface,
		                       px_x,
		                       (px_height - test_length * test_count) / 2 + test_length / 2 + px_y + test_length * i,
		                       -1, 0,
		                       test_dist, test_length, test_width,
		                       &edge_x, &edge_y);

		cairo_matrix_transform_point(&inverse, &edge_x, &edge_y);
		if (found_edge)
			g_array_append_val(left, edge_x);
	}

	for (i = 0; i < test_count; i++) {
		gdouble edge_x = 0, edge_y = 0;
		gboolean found_edge;
		
		found_edge = find_edge(surface,
		                       px_x + px_width,
		                       (px_height - test_length * test_count) / 2 + test_length / 2 + px_y + test_length * i,
		                       1, 0,
		                       test_dist, test_length, test_width,
		                       &edge_x, &edge_y);

		cairo_matrix_transform_point(&inverse, &edge_x, &edge_y);
		if (found_edge)
			g_array_append_val(right, edge_x);
	}
	if ((top->len == 0) || (bottom->len == 0))
		return NULL;
	if ((left->len == 0) || (right->len == 0))
		return NULL;
	
	result = g_malloc(sizeof(cairo_matrix_t));
	cairo_matrix_init_identity(result);
	
	x = g_array_index(left, gdouble, 0);
	width = g_array_index(right, gdouble, 0) - x;
	y = g_array_index(top, gdouble, 0);
	height = g_array_index(bottom, gdouble, 0) - y;
	
	result->xx = width / mm_width;
	result->yy = height / mm_height;
	result->x0 = x - mm_x * width / mm_width;
	result->y0 = y - mm_y * height / mm_height;
	
	return result;
}

#endif


/* This will only work for small boxes! */
cairo_matrix_t*
calculate_correction_matrix(cairo_surface_t  *surface,
                            cairo_matrix_t   *matrix,
                            gdouble           mm_x,
                            gdouble           mm_y,
                            gdouble           mm_width,
                            gdouble           mm_height)
{
	gdouble tmp_x, tmp_y;
	gint px_x, px_y, px_width, px_height;
	cairo_matrix_t inverse;
	cairo_matrix_t *result = NULL;
	gint test_dist = 10;
	gint line_width = 5;
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

	tmp_x = mm_width;
	tmp_y = mm_height;
	cairo_matrix_transform_distance(matrix, &tmp_x, &tmp_y);
	px_width = tmp_x + 0.5;
	px_height = tmp_y + 0.5;

	/* Top */
	
	for (x_offset = -test_dist; x_offset <= test_dist; x_offset++) {
		for (y_offset = -test_dist; y_offset <= test_dist; y_offset++) {
			gint new_cov;
			new_cov  = count_black_pixel(surface, /* top */
			                             px_x + x_offset,
			                             px_y + y_offset,
			                             px_width, line_width);
			new_cov += count_black_pixel(surface, /* bottom */
			                             px_x + x_offset,
			                             px_y + y_offset + px_height - line_width,
			                             px_width, line_width);
			new_cov += count_black_pixel(surface, /* left */
			                             px_x + x_offset,
			                             px_y + y_offset + line_width,
			                             line_width, px_height - 2*line_width);
			new_cov += count_black_pixel(surface, /* right */
			                             px_x + x_offset + px_width - line_width,
			                             px_y + y_offset + line_width,
			                             line_width, px_height - 2*line_width);

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
	
	result = g_malloc(sizeof(cairo_matrix_t));
	cairo_matrix_init_identity(result);

	/* Just a translation */	
	result->x0 = tmp_x - mm_x;
	result->y0 = tmp_y - mm_y;
	
	return result;
}

float
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
	
	return black / (double) all;
}

