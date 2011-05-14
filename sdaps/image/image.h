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

cairo_surface_t*
get_a1_from_tiff (char *filename, gboolean rotated);

cairo_matrix_t*
calculate_matrix(cairo_surface_t *surface, gdouble mm_x, gdouble mm_y, gdouble mm_width, gdouble mm_height);

cairo_matrix_t*
calculate_correction_matrix(cairo_surface_t *surface, cairo_matrix_t *matrix, gdouble mm_x, gdouble mm_y, gdouble mm_width, gdouble mm_height);

gboolean
find_box_corners(cairo_surface_t *surface, cairo_matrix_t *matrix, gdouble mm_x, gdouble mm_y, gdouble mm_width, gdouble mm_height,
                 gdouble *mm_x1, gdouble *mm_y1, gdouble *mm_x2, gdouble *mm_y2, gdouble *mm_x3, gdouble *mm_y3, gdouble *mm_x4, gdouble *mm_y4);

float
get_coverage(cairo_surface_t *surface, cairo_matrix_t *matrix, gdouble mm_x, gdouble mm_y, gdouble mm_width, gdouble mm_height);

void
get_pbm(cairo_surface_t *surface, void **data, int *length);

