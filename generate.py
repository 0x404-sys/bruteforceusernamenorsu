# Realistic large username generator (PERSONAL REFERENCE ONLY)

first_name = "john"
last_name = "doe"
nickname = "jd"
alt_name = "jdoe"

numbers = [str(i) for i in range(1, 501)]  # 1–500, covers 123-style numbers
years = ["2022", "06", "2025"]              # common years/numbers you might use
separators = ["", "_", "."]

bases = [
    first_name,
    first_name + last_name,
    nickname,
    alt_name,
    last_name + first_name
]

usernames = set()

# Base only
for base in bases:
    usernames.add(base)

# Base + separator + numbers / years
for base in bases:
    for sep in separators:
        for num in numbers + years:
            usernames.add(base + sep + num)

# Extra realistic patterns
usernames.add(first_name + last_name + "123")
usernames.add(first_name + "123")
usernames.add(first_name + "2025")
usernames.add(nickname + "2022")
usernames.add(alt_name + "2022")
usernames.add(alt_name + "06")

# Save to file
with open("username_ideas.txt", "w") as f:
    for u in sorted(usernames):
        f.write(u + "\n")

print(f"Generated {len(usernames)} realistic username ideas.")
print("Saved to username_ideas.txt")
