/* SDAPS
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

#include <stdlib.h>
#include <glib.h>
#include <cairo.h>

/* Some of the more important Magic Values */
extern gdouble sdaps_line_min_length;
extern gdouble sdaps_line_max_length;
extern gdouble sdaps_line_width;
extern gdouble sdaps_corner_mark_search_distance;
extern gdouble sdaps_line_coverage;

extern gboolean sdaps_create_debug_surface;
extern gint sdaps_debug_surface_ox;
extern gint sdaps_debug_surface_oy;
extern cairo_surface_t *sdaps_debug_surface;

void
disable_libtiff_warnings (void);

cairo_surface_t*
get_a1_from_tiff (const char *filename, gint page, gboolean rotated);

gboolean
write_a1_to_tiff (const char *filename, cairo_surface_t *surf);

cairo_surface_t*
get_rgb24_from_tiff (const char *filename, gint page, gboolean rotated);

gint
get_tiff_page_count (const char *filename);

gboolean
get_tiff_resolution (const char *filename, gint page, gdouble *xresolution, gdouble *yresolution);

gboolean
check_tiff_monochrome (const char *filename);

gboolean
find_corner_marker(cairo_surface_t *surface, cairo_matrix_t *matrix, gint corner, gdouble *marker_x, gdouble *marker_y);

cairo_matrix_t*
calculate_matrix(cairo_surface_t *surface, cairo_matrix_t *matrix, gdouble mm_x, gdouble mm_y, gdouble mm_width, gdouble mm_height);

cairo_matrix_t*
calculate_correction_matrix_masked(cairo_surface_t *surface, cairo_surface_t *mask, cairo_matrix_t *matrix, gdouble mm_x, gdouble mm_y, gdouble *covered);

gboolean
find_box_corners(cairo_surface_t *surface, cairo_matrix_t *matrix, gdouble mm_x, gdouble mm_y, gdouble mm_width, gdouble mm_height,
                 gdouble *mm_x1, gdouble *mm_y1, gdouble *mm_x2, gdouble *mm_y2, gdouble *mm_x3, gdouble *mm_y3, gdouble *mm_x4, gdouble *mm_y4);

gdouble
get_coverage(cairo_surface_t *surface, cairo_matrix_t *matrix, gdouble mm_x, gdouble mm_y, gdouble mm_width, gdouble mm_height);

gdouble
get_masked_coverage(cairo_surface_t *surface, cairo_surface_t *mask, gint x, gint y);

gdouble
get_masked_coverage_without_lines(cairo_surface_t *surface, cairo_surface_t *mask, gint x, gint y, gdouble line_width, gint line_count);

guint
get_masked_white_area_count(cairo_surface_t *surface, cairo_surface_t *mask, gint x, gint y, gdouble min_size, gdouble max_size, gdouble *filled_area);

