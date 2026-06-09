from scraper.load_speedhome import load_speedhome_from_har

df = load_speedhome_from_har()

print(df.head())

print("\nShape:")
print(df.shape)