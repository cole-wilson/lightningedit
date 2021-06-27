from fuzzywuzzy import fuzz

old = "bob"
new = "bob"

threshold = 55
def _fuzzypos(word, string, precedence=0):
	string = string.split()
	enum = enumerate(map(lambda i:fuzz.ratio(word,i),string))
	maxi = sorted(filter(lambda i:i[1]<100,enum),key=lambda i:i[1])
	if len(maxi) == 0:
		return False
	top = maxi[-1][1] # the top ratio
	maxi = list(filter(lambda i:i[1]==top and i[1], maxi))[precedence]
	if maxi[1] < threshold:
		return None
	return maxi[0]

s_index = _fuzzypos(new.split()[0], old)
e_index = _fuzzypos(new.split()[-1], old, precedence=-1)
if s_index is None or e_index is None:
	print(old + " " + new)
if s_index is False or e_index is False:
	print(old)
section = " ".join(old.split()[s_index:e_index+1])
ratio = fuzz.partial_token_sort_ratio(section, new)
if ratio >= threshold:
	print(old.replace(section, new, 1))
else:
	print(old + " " + new)