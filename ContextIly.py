import contextily as cx
import matplotlib.pyplot as plt

# 1. Definieer de grenzen in WGS84 (Longitude/Latitude)
# Formaat: West (min_lon), Zuid (min_lat), Oost (max_lon), Noord (max_lat)
# Voorbeeld: Amsterdam Centrum
west, south, east, north = 4.88, 52.35, 4.92, 52.38

# 2. Download de kaarttegels (tiles) en zet ze om naar een afbeelding array
# ll=True geeft aan dat de invoercoördinaten Longitude/Latitude zijn
image, extent = cx.bounds2img(
    w=west, 
    s=south, 
    e=east, 
    n=north, 
    zoom=14, 
    source=cx.providers.CartoDB.Positron(apikey="..."),
    ll=True
)

# 3. Plot de afbeelding met Matplotlib
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(image, extent=extent)

# Verwijder de assen en marges voor een schone PNG
ax.set_axis_off()
plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
plt.margins(0, 0)

# 4. Sla de kaart op als PNG
output_filename = "PDF/plattegrond.png"
fig.savefig(output_filename, bbox_inches='tight', pad_inches=0, dpi=300)
print(f"Kaart succesvol opgeslagen als {output_filename}")
key = input("Wait")
