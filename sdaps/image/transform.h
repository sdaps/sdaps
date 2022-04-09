/* SDAPS
 * Copyright (C) 2012  Benjamin Berg <benjamin@sipsolutions.net>
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

#if 0
void
thinzs_np(cairo_surface_t *surface);
#endif

void
kfill_modified(cairo_surface_t* surface, gint k);

guint
flood_fill(cairo_surface_t *surface, cairo_surface_t *debug_surf, gint x, gint y, guint orig_color);

void
remove_maximum_line(cairo_surface_t *surface, cairo_surface_t *debug_surf, gdouble width);


