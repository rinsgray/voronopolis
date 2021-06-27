from hexalattice.hexalattice import *
import numpy as np
hex_centers, _ = create_hex_grid(nx=30,
                                 ny=30,
                                 do_plot=False)
x_hex_coords = hex_centers[:, 0]
y_hex_coords = hex_centers[:, 1]

image_path = 'voronoi.jpg'     # Works with .png, .jpg, .tif
colors = sample_colors_from_image_by_grid(image_path, x_hex_coords, y_hex_coords)

plot_single_lattice_custom_colors(x_hex_coords, y_hex_coords,
                                      face_color=colors,
                                      edge_color=colors,
                                      min_diam=0.9,
                                      plotting_gap=0.05,
                                      rotate_deg=0)
plt.axis('off')
plt.savefig('hex_voronoi.jpg',dpi=300,bbox_inches='tight',pad_inches=0)