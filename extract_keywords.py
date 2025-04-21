import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Load the CSV file
faq_df = pd.read_csv("data/faqs.csv")

# Define custom Filipino stopwords
filipino_stopwords = set([
    "akin", "aking", "ako", "alin", "am", "amin", "aming", "ang", "ano", "anumang", "apat", "at",
    "atin", "ating", "ay", "bababa", "bago", "bakit", "bawat", "bilang", "dahil", "dalawa", "dapat",
    "din", "dito", "doon", "gagawin", "gayunman", "ginagawa", "ginawa", "ginawang", "gumawa",
    "gusto", "habang", "hanggang", "hindi", "huwag", "iba", "ibaba", "ibabaw", "ibig", "ikaw",
    "ilagay", "ilalim", "ilan", "inyong", "isa", "isang", "itaas", "ito", "iyo", "iyon", "iyong",
    "ka", "kahit", "kailangan", "kailanman", "kami", "kanila", "kanilang", "kanino", "kanya",
    "kanyang", "kapag", "kapwa", "karamihan", "katiyakan", "katulad", "kaya", "kaysa", "ko", "kong",
    "kulang", "kumuha", "kung", "laban", "lahat", "lamang", "likod", "lima", "maaari", "maaaring",
    "maging", "mahusay", "makita", "marami", "marapat", "masyado", "may", "mayroon", "mga",
    "minsan", "mismo", "mula", "muli", "na", "nabanggit", "naging", "nagkaroon", "nais", "nakita",
    "namin", "napaka", "narito", "nasaan", "ng", "ngayon", "ni", "nila", "nilang", "nito", "niya",
    "niyang", "noon", "o", "pa", "paano", "pababa", "paggawa", "pagitan", "pagkakaroon",
    "pagkatapos", "palabas", "pamamagitan", "panahon", "pangalawa", "para", "paraan", "pareho",
    "pataas", "pero", "pumunta", "pumupunta", "sa", "saan", "sabi", "sabihin", "sarili", "sila",
    "sino", "siya", "tatlo", "tayo", "tulad", "tungkol", "una", "walang"
])


# Combine with English stopwords
english_stopwords = set(stopwords.words('english'))
combined_stopwords = filipino_stopwords.union(english_stopwords)

# Keyword extraction function
def extract_keywords(text):
    text = str(text).lower().translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    return [word for word in tokens if word.isalpha() and word not in combined_stopwords]

# Apply to the DataFrame
faq_df["keywords"] = faq_df["Questions"].apply(extract_keywords)

# Save to new CSV (optional)
faq_df.to_csv("data/FAQs_with_keywords.csv", index=False)

print("Keywords extracted successfully!")