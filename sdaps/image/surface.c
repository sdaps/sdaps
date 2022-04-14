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

#include "string.h"
#include "surface.h"

#define WORD_COUNT_BITS(x) __builtin_popcount(x)

cairo_surface_t*
surface_copy_partial(cairo_surface_t *surface, int x, int y, int width, int height)
{
	cairo_surface_t *result;
	cairo_t *cr;

	result = cairo_image_surface_create(cairo_image_surface_get_format(surface), width, height);
	cr = cairo_create(result);

	cairo_set_operator(cr, CAIRO_OPERATOR_SOURCE);
	/* In case the area is outside of the source image, fill with zeros. */
	cairo_set_source_rgba(cr, 0, 0, 0, 0);
	cairo_paint(cr);

	cairo_set_source_surface(cr, surface, -x, -y);
	cairo_paint(cr);

	cairo_destroy(cr);

	cairo_surface_flush(result);

	return result;
}

cairo_surface_t*
surface_copy(cairo_surface_t *surface)
{
	int width, height;
	width = cairo_image_surface_get_width(surface);
	height = cairo_image_surface_get_height(surface);

	return surface_copy_partial(surface, 0, 0, width, height);
}

cairo_surface_t*
surface_copy_masked(cairo_surface_t *surface, cairo_surface_t *mask, gint x, gint y)
{
	gint width, height;
	gint word_width;
	cairo_surface_t *result;
	gint result_stride, mask_stride;
	guint32 *result_pixels, *mask_pixels;

	width = cairo_image_surface_get_width(mask);
	height = cairo_image_surface_get_height(mask);

	result = surface_copy_partial(surface, x, y, width, height);

	result_pixels = (guint32*) cairo_image_surface_get_data(result);
	result_stride = cairo_image_surface_get_stride(result);
	mask_pixels = (guint32*) cairo_image_surface_get_data(mask);
	mask_stride = cairo_image_surface_get_stride(mask);

	word_width = (width + 31) / 32;
	for (y = 0; y < height; y++) {
		for (x = 0; x < word_width; x++) {
			result_pixels[x + y*result_stride/4] &= mask_pixels[x + y*mask_stride/4];
		}
	}

	cairo_surface_mark_dirty(result);

	return result;
}


cairo_surface_t*
surface_inverted_copy_masked(cairo_surface_t *surface, cairo_surface_t *mask, gint x, gint y)
{
	gint width, height;
	gint word_width;
	cairo_surface_t *result;
	gint result_stride, mask_stride;
	guint32 *result_pixels, *mask_pixels;

	width = cairo_image_surface_get_width(mask);
	height = cairo_image_surface_get_height(mask);

	result = surface_copy_partial(surface, x, y, width, height);

	result_pixels = (guint32*) cairo_image_surface_get_data(result);
	result_stride = cairo_image_surface_get_stride(result);
	mask_pixels = (guint32*) cairo_image_surface_get_data(mask);
	mask_stride = cairo_image_surface_get_stride(mask);

	word_width = (width + 31) / 32;
	for (y = 0; y < height; y++) {
		for (x = 0; x < word_width; x++) {
			result_pixels[x + y*result_stride/4] = ~result_pixels[x + y*result_stride/4] & mask_pixels[x + y*mask_stride/4];
		}
	}

	cairo_surface_mark_dirty(result);

	return result;
}


/* Generic pixel routines */
void
set_pixels_unchecked(guint32* pixels, guint32 stride, gint x, gint y, gint width, gint height, int value)
{
	gint x_pos, y_pos;

	for (y_pos = y; y_pos < y + height; y_pos++) {
		for (x_pos = x; x_pos < x + width; x_pos++) {
			SET_PIXEL(pixels, stride, x_pos, y_pos, value);
		}
	}
}

void
get_pbm(cairo_surface_t *surface, void **data, gssize *length)
{
	int width, height;
	int s_stride;
	int d_stride;
	unsigned char* s_pixel;
	unsigned char* d_pixel;
	char *start;
	int x, y;

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
	*data = g_malloc0(*length);
	strcpy(*data, start);
	d_pixel = *data + strlen(start);
	g_free(start);

	for (y = 0; y < height; y++) {
		for (x = 0; x < width; x++) {
			*(d_pixel + y*d_stride + x / 8) |= (GET_PIXEL(s_pixel, s_stride, x, y)) << (7 - x % 8);
		}
	}
}

gint
count_black_pixel(cairo_surface_t *surface, gint x, gint y, gint width, gint height)
{
	guint32 *pixels;
	guint stride;
	gint img_width, img_height;

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
	if ((width <= 0) || (height <= 0))
		return 0;
	if (x + width > img_width) {
		width = img_width - x;
	}
	if (y + height > img_height) {
		height = img_height - y;
	}

	return count_black_pixel_unchecked(pixels, stride, x, y, width, height);
}

gint
count_black_pixel_unchecked(guint32* pixels, guint32 stride, gint x, gint y, gint width, gint height)
{
	gint y_pos;
	guint black_pixel = 0;

	for (y_pos = y; y_pos < y + height; y_pos++) {

		guint32 start_mask;
		guint32 end_mask;
		int start;
		int end;
		int pos;

#if G_BYTE_ORDER == G_BIG_ENDIAN
		start_mask = 0xffffffff >> (x & 0x1f);
		end_mask = (0xffffffff << (-(x + width) & 0x1f));
#else
		start_mask = 0xffffffff << (x & 0x1f);
		end_mask = (0xffffffff >> (-(x + width) & 0x1f));
#endif
		start = x >> 5;
		end = (x + width - 1) >> 5;

		if (start == end) {
			black_pixel += WORD_COUNT_BITS(pixels[start + y_pos * stride / 4] & start_mask & end_mask);
		} else {
			black_pixel += WORD_COUNT_BITS(pixels[start + y_pos * stride / 4] & start_mask);
			for (pos = start + 1; pos < end; pos++) {
				black_pixel += WORD_COUNT_BITS(pixels[pos + y_pos * stride / 4]);
			}
			black_pixel += WORD_COUNT_BITS(pixels[end + y_pos * stride / 4] & end_mask);
		}
	}

	return black_pixel;
}

gint
count_black_pixel_masked(cairo_surface_t *surface, cairo_surface_t *mask, gint x, gint y)
{
	guint32 *pixels;
	guint32 *mask_pixels;
	guint stride;
	guint mask_stride;
	gint width, height;
	gint img_width, img_height;

	width = cairo_image_surface_get_width(mask);
	height = cairo_image_surface_get_height(mask);
	mask_pixels = (guint32*) cairo_image_surface_get_data(mask);
	mask_stride = cairo_image_surface_get_stride(mask);

	pixels = (guint32*) cairo_image_surface_get_data(surface);
	img_width = cairo_image_surface_get_width(surface);
	img_height = cairo_image_surface_get_height(surface);
	stride = cairo_image_surface_get_stride(surface);

	/* Ignore if the mask is not completely in the image ... */
	if (y < 0) {
		return 0;
	}
	if (x < 0) {
		return 0;
	}
	if ((width <= 0) || (height <= 0))
		return 0;
	if (x + width > img_width) {
		return 0;
	}
	if (y + height > img_height) {
		return 0;
	}

	return count_black_pixel_masked_unchecked(pixels, stride, mask_pixels, mask_stride, x, y, width, height);
}

gint
count_black_pixel_masked_unchecked(guint32* pixels, guint32 stride, guint32 *mask_pixels, guint32 mask_stride, gint x, gint y, gint width, gint height)
{
	gint y_pos;
	guint black_pixel = 0;

	for (y_pos = 0; y_pos < height; y_pos++) {
		guint32 end_mask;
		guint32 curr_pixels;
		int end;
		int pos;

#if G_BYTE_ORDER == G_BIG_ENDIAN
		end_mask = (0xffffffff << (-(x + width) & 0x1f));
#else
		end_mask = (0xffffffff >> (-(x + width) & 0x1f));
#endif
		end = (width - 1) >> 5;

		for (pos = 0; pos <= end; pos++) {
			/* Note that a shift of 32 is not defined, it may also be 0. */
#if G_BYTE_ORDER == G_BIG_ENDIAN
			curr_pixels = pixels[(x / 32) + pos + (y_pos + y) * stride / 4] << (x % 32);
			curr_pixels |= pixels[((x + 31) / 32) + pos + (y_pos + y) * stride / 4] >> (32 - (x % 32));
#else
			curr_pixels = pixels[(x / 32) + pos + (y_pos + y) * stride / 4] >> (x % 32);
			curr_pixels |= pixels[((x + 31) / 32) + pos + (y_pos + y) * stride / 4] << (32 - (x % 32));
#endif

			curr_pixels &= mask_pixels[pos + y_pos * mask_stride / 4];

			if (pos == end)
				curr_pixels &= end_mask;

			black_pixel += WORD_COUNT_BITS(curr_pixels);
		}
	}

	return black_pixel;
}

#if 0
/* This function is for debugging purposes. */
void
a1_surface_write_to_png(cairo_surface_t* surface, gchar* filename)
{
	guint img_width, img_height;
	cairo_surface_t *tmp_surface;
	cairo_t *cr;

	img_width = cairo_image_surface_get_width(surface);
	img_height = cairo_image_surface_get_height(surface);

	tmp_surface = cairo_image_surface_create(CAIRO_FORMAT_RGB24, img_width, img_height);

	cr = cairo_create(tmp_surface);
	cairo_set_source_rgb(cr, 1, 1, 1);
	cairo_paint(cr);
	cairo_set_source_rgb(cr, 0, 0, 0);
	cairo_mask_surface(cr, surface, 0, 0);

	cairo_surface_write_to_png(tmp_surface, filename);

	cairo_destroy(cr);
	cairo_surface_destroy(tmp_surface);
}
#endif



