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

#if G_BYTE_ORDER == G_BIG_ENDIAN
#define SET_PIXEL(_pixels, _stride, _x, _y, _value) *(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4) = (*(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4) & (0xffffffff ^ (1 << (31 - (_x) % 32)))) | ((!!(_value)) << (31 - (_x) % 32))
#define GET_PIXEL(_pixels, _stride, _x, _y) (((*(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4)) >> (31 - (_x) % 32)) & 0x1)

#define BARREL_VARS guint32* _barrel_curr_pos; guint _barrel_bits; guint32 _barrel_value_storage;
#define BARREL_START_ROW(_row_ptr) _barrel_value_storage = 0; _barrel_bits = 0; _barrel_curr_pos = (guint32*)(_row_ptr);
#define BARREL_STORE_BIT(_value) _barrel_bits++; _barrel_value_storage = (_value) | _barrel_value_storage << 1; if (_barrel_bits == 32) { *_barrel_curr_pos = _barrel_value_storage; _barrel_curr_pos++; _barrel_bits = 0; };
#define BARREL_FLUSH if (_barrel_bits > 0) { *_barrel_curr_pos = _barrel_value_storage << (32-_barrel_bits); _barrel_curr_pos++; _barrel_bits = 0; }

#else
#define SET_PIXEL(_pixels, _stride, _x, _y, _value) *(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4) = (*(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4) & (0xffffffff ^ (1 << ((_x) % 32)))) | ((!!(_value)) << ((_x) % 32))
#define GET_PIXEL(_pixels, _stride, _x, _y) (((*(guint32*)((char*)(_pixels) + (_stride) * (_y) + (_x) / 32 * 4)) >> ((_x) % 32)) & 0x1)

#define BARREL_VARS guint32* _barrel_curr_pos; guint _barrel_bits; guint32 _barrel_value_storage;
#define BARREL_START_ROW(_row_ptr) _barrel_value_storage = 0; _barrel_bits = 0; _barrel_curr_pos = (guint32*)(_row_ptr);
#define BARREL_STORE_BIT(_value) _barrel_bits++; _barrel_value_storage = (_value) << 31 | _barrel_value_storage >> 1; if (_barrel_bits == 32) { *_barrel_curr_pos = _barrel_value_storage; _barrel_curr_pos++; _barrel_bits = 0; };
#define BARREL_FLUSH if (_barrel_bits > 0) { *_barrel_curr_pos = _barrel_value_storage >> (32-_barrel_bits); _barrel_curr_pos++; _barrel_bits = 0; }
#endif


cairo_surface_t*
surface_copy_partial(cairo_surface_t *surface, int x, int y, int width, int height);

cairo_surface_t*
surface_copy(cairo_surface_t *surface);

#if 0
void
a1_surface_write_to_png(cairo_surface_t* surface, gchar* filename);

void
thinzs_np(cairo_surface_t *surface);

void
kfill_modified(cairo_surface_t* surface, gint k);
#endif

guint
flood_fill(cairo_surface_t *surface, gint x, gint y, gint orig_color);

void
remove_maximum_line(cairo_surface_t *surface, gdouble width);

static gint
count_black_pixel(cairo_surface_t *surface, gint x, gint y, gint width, gint height);

static gint
count_black_pixel_unchecked(guint32* pixels, guint32 stride, gint x, gint y, gint width, gint height);

static void
set_pixels_unchecked(guint32* pixels, guint32 stride, gint x, gint y, gint width, gint height, int value);

/* Defined here so that it can be inlined in both image.c and transform.c.
 * Maybe there is a saner way (that does not result in compiler warnings)? */
static gint
count_black_pixel(cairo_surface_t *surface, gint x, gint y, gint width, gint height)
{
	guint32 *pixels;
	guint stride;
	guint img_width, img_height;

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

	return count_black_pixel_unchecked(pixels, stride, x, y, width, height);
}

static gint
count_black_pixel_unchecked(guint32* pixels, guint32 stride, gint x, gint y, gint width, gint height)
{
	guint x_pos, y_pos;
	guint black_pixel = 0;

	for (y_pos = y; y_pos < y + height; y_pos++) {
		for (x_pos = x; x_pos < x + width; x_pos++) {
			black_pixel += GET_PIXEL(pixels, stride, x_pos, y_pos);
		}
	}

	return black_pixel;
}

static void
set_pixels_unchecked(guint32* pixels, guint32 stride, gint x, gint y, gint width, gint height, int value)
{
	guint x_pos, y_pos;

	for (y_pos = y; y_pos < y + height; y_pos++) {
		for (x_pos = x; x_pos < x + width; x_pos++) {
			SET_PIXEL(pixels, stride, x_pos, y_pos, value);
		}
	}
}

